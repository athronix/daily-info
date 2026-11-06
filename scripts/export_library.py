#!/usr/bin/env python3
"""P1 · 资料库沉淀包导出（本地 staging，不上传、不发送）。

把唯一事实源 data/digest/<date>/digest.json 投影成一组可离线阅读、可直接上传资料库的终态产物：

  data/library/<YYYY>/<MM>/
    digest-<date>.md        人读叙事（直接复制 digest.md）
    brief-<date>.md         推送短简报
    index-<date>.html       自包含离线快照（内联 CSS + 数据，不依赖站点相对路径）
    items-<date>.csv        当日条目索引（id / 标题 / 分类 / 分数 / URL / 数字 / 实体）
    no-number-<date>.csv    数据质量诊断：入选簇中「原文无实质数字」的条目，供补摘要
    _manifest-<date>.json   文件清单 + sha256 + 口径标记

设计约束：
  - 只放终态产物，不放 raw / normalized / candidate 中间层（docs/08 §6）。
  - 所有外部文本 html.escape；链接只接受 http(s)。
  - 幂等：按字节比对，内容不变不重写；manifest 用 digest.generated_at 而非实时时间戳。
  - 不调用任何外部 API。上传资料库由 Agent 在用户授权后读取 _manifest 执行。

  python scripts/export_library.py --date 2026-11-05 [--dry-run]
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import html
import io
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (DATA_DIR, PUBLIC_DIR, ROOT, add_date_arg, day_dir, read_json,
                    run_log, setup_logging, write_bytes_idempotent, LOG)
from make_digest import NUMBER_RE, original_text, scan_credentials

CSV_HEADER = ["id", "date", "section", "title", "category", "source", "score",
              "published_at", "numbers", "entities", "url", "evidence_urls"]
AUDIT_HEADER = ["cluster_id", "member_id", "source", "title", "summary", "url", "reason"]


def csv_bytes(header: list[str], rows: list[list]) -> bytes:
    buf = io.StringIO(newline="")
    w = csv.writer(buf, lineterminator="\r\n")
    w.writerow(header)
    for row in rows:
        w.writerow(["" if v is None else str(v) for v in row])
    # utf-8-sig 便于 Excel / 资料库表格直接打开
    return buf.getvalue().encode("utf-8-sig")


def item_rows(digest: dict) -> list[list]:
    rows = []
    for sec in digest.get("sections", []):
        for it in sec.get("items", []):
            rows.append([
                it.get("id", ""), digest.get("date", ""), sec.get("key", ""),
                it.get("title", ""), it.get("category", ""), it.get("source", ""),
                it.get("score", ""), it.get("published_at", ""),
                " | ".join(it.get("numbers") or []),
                " | ".join(it.get("entities") or []),
                it.get("url", ""),
                " | ".join(it.get("evidence_urls") or []),
            ])
    return rows


def audit_rows(date: str) -> list[list]:
    """入选簇中「原文 title+summary+metrics 无任何数字」的条目。

    这是白名单收紧后的配套诊断：这些条目无法提供可核验读数，会被 make_digest 拒绝入报。
    输出它们是为了「先补上游摘要」，而不是放宽校验阈值。
    """
    pi = read_json(day_dir("candidate", date) / "prompt-input.json", {})
    clusters = read_json(day_dir("candidate", date) / "clusters.json", {})
    by_id = {}
    for c in clusters.get("clusters", []):
        for m in c.get("members", []):
            by_id[m["id"]] = m
        by_id[c["cluster_id"]] = c["members"][0]
    selected = [c.get("cluster_id") for c in pi.get("clusters", [])]
    rows = []
    for cid in selected:
        m = by_id.get(cid)
        if not m:
            continue
        text = original_text(m)
        if NUMBER_RE.search(text):
            continue
        rows.append([
            cid, m.get("id", ""), m.get("source_name", ""), m.get("title", ""),
            (m.get("summary_raw") or "")[:300], m.get("url", ""),
            "原文 title+summary_raw+metrics 无数字（采集时间戳不计入）",
        ])
    return rows


def render_snapshot(d: dict) -> str:
    """自包含离线快照：内联样式 + escape 过的文本，不加载任何外部资源。"""
    e = html.escape
    L = [
        "<!DOCTYPE html><html lang=\"zh-CN\"><head><meta charset=\"utf-8\">",
        f"<title>{e(d.get('date',''))} 每日信息 · 离线快照</title>",
        "<style>body{margin:0;background:#f7f8f6;color:#1f2521;font-family:-apple-system,"
        "BlinkMacSystemFont,'Segoe UI','PingFang SC','Microsoft YaHei',sans-serif;}"
        ".wrap{max-width:760px;margin:0 auto;padding:28px 18px;}"
        ".card{background:#fff;border:1px solid #e5e8e2;border-radius:14px;padding:26px 28px;margin-bottom:16px;}"
        "h1{font-size:23px;line-height:1.45;margin:0 0 12px;}"
        "h2{font-size:16px;margin:22px 0 10px;color:#3f7d63;}"
        ".meta{font-size:12px;color:#8d968e;}"
        ".lead{font-size:14px;line-height:1.9;border-left:3px solid #3f7d63;padding-left:14px;}"
        "li{font-size:14px;line-height:1.85;margin-bottom:12px;}"
        "a{color:#3f7d63;word-break:break-all;}"
        ".note{background:#f1f3ef;padding:16px 18px;border-radius:8px;font-size:13.5px;line-height:1.9;}"
        "table{border-collapse:collapse;width:100%;font-size:12px;}"
        "td,th{border:1px solid #e5e8e2;padding:6px 8px;text-align:left;}"
        "</style></head><body><div class=\"wrap\">",
        f"<div class=\"meta\">每日信息 · 离线快照 · {e(d.get('date',''))} · 自包含页面，不依赖站点数据文件</div>",
        "<div class=\"card\">",
        f"<h1>{e(d.get('headline',''))}</h1>",
        f"<div class=\"meta\">生成于 {e(str(d.get('generated_at','')))} · AI 状态 "
        f"{e(str(d.get('quality',{}).get('ai_status','')))} · 入报 "
        f"{d.get('stats',{}).get('published_items',0)} 条</div>",
        f"<p class=\"lead\">{e(d.get('lead',''))}</p>",
    ]
    if d.get("themes"):
        L.append("<h2>今日主线</h2><ul>")
        for t in d["themes"]:
            L.append(f"<li><strong>{e(t.get('title',''))}</strong> · {e(t.get('why',''))}"
                     f" <span class=\"meta\">（{t.get('verified_by',0)} 条佐证）</span></li>")
        L.append("</ul>")
    for sec in d.get("sections", []):
        L.append(f"<h2>{e(sec.get('label', sec.get('key','')))}</h2><ul>")
        for it in sec.get("items", []):
            L.append(f"<li><strong>{e(it.get('title',''))}</strong><br>"
                     f"{e(it.get('fact_anchor',''))}<br>"
                     f"<span class=\"meta\">{e(it.get('source',''))} · "
                     f"读数 {e(' / '.join(it.get('numbers') or []))} · "
                     f"相关方 {e(' / '.join(it.get('entities') or []))}</span><br>"
                     f"{e(it.get('why_matters',''))}<br>{e(it.get('impact',''))}<br>"
                     f"下一步：{e(it.get('next_action',''))}<br>")
            for u in (it.get("evidence_urls") or [])[:2]:
                if str(u).startswith(("http://", "https://")):
                    L.append(f"→ <a href=\"{e(str(u))}\" rel=\"noopener noreferrer\">{e(str(u))}</a><br>")
            L.append("</li>")
        L.append("</ul>")
    if d.get("editor_note"):
        L.append(f"<h2>编者观察</h2><div class=\"note\">{e(d['editor_note'])}</div>")
    if d.get("watch_signals"):
        L.append("<h2>待验证信号</h2><table><tr><th>信号</th><th>阈值</th><th>判定</th></tr>")
        for w in d["watch_signals"]:
            L.append(f"<tr><td>{e(w.get('signal',''))}</td><td>{e(w.get('threshold',''))}</td>"
                     f"<td>{e(w.get('judgement',''))}</td></tr>")
        L.append("</table>")
    L.append("<div class=\"meta\" style=\"margin-top:22px;line-height:1.9;\">"
             "外部事实未独立验证；内容仅供参考，不构成投资建议。"
             "取不到可靠数据处标注「暂无可靠数据」。本页由确定性脚本自唯一事实源生成。</div>")
    L.append("</div></div></body></html>")
    return "\n".join(L)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--dry-run", action="store_true", help="只打印计划，不写任何文件")
    ap.add_argument("--out-root", default=str(DATA_DIR / "library"), help="沉淀 staging 根目录")
    args = ap.parse_args()
    setup_logging(args.verbose)

    date = args.date
    ddir = day_dir("digest", date)
    digest = read_json(ddir / "digest.json", {})
    if not digest:
        LOG.error("缺少 %s，先跑 make_digest.py", ddir / "digest.json")
        return 2
    yyyy, mm = date[:4], date[5:7]
    out = Path(args.out_root) / yyyy / mm
    files: dict[str, bytes] = {}

    for src_name, out_name in [("digest.md", f"digest-{date}.md"),
                               ("brief.md", f"brief-{date}.md")]:
        p = ddir / src_name
        if p.exists():
            files[out_name] = p.read_bytes()
    html_text = render_snapshot(digest)
    leaks = scan_credentials(html_text)
    if leaks:
        LOG.error("快照疑似含凭据（%d 处），拒绝导出", len(leaks))
        return 2
    files[f"index-{date}.html"] = html_text.encode("utf-8")
    items = item_rows(digest)
    files[f"items-{date}.csv"] = csv_bytes(CSV_HEADER, items)
    audit = audit_rows(date)
    files[f"no-number-{date}.csv"] = csv_bytes(AUDIT_HEADER, audit)

    manifest = {
        "date": date,
        "generated_at": digest.get("generated_at"),
        "source_of_truth": str((ddir / "digest.json").relative_to(ROOT)).replace("\\", "/"),
        "content_spec_version": digest.get("quality", {}).get("content_spec_version"),
        "number_whitelist_scope": digest.get("quality", {}).get("number_whitelist_scope"),
        "stats": {k: digest.get("stats", {}).get(k) for k in
                  ("published_items", "seven_element_pass", "items_with_numbers",
                   "rejected_no_number", "unique_reference_domains")},
        "manifest_self": f"_manifest-{date}.json",
        "described_files": len(files),
        "files": [{"name": n, "bytes": len(b), "sha256": hashlib.sha256(b).hexdigest()}
                  for n, b in sorted(files.items())],
        "note": "本地 staging 产物；上传资料库、发送邮件等外部动作需用户授权后由 Agent 执行",
    }
    files[f"_manifest-{date}.json"] = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode("utf-8")

    if args.dry_run:
        print(f"[dry-run] 将写入 {out}（{len(files)} 个文件）：")
        for n, b in sorted(files.items()):
            print(f"  {n:34s} {len(b):>8} bytes")
        print(f"  条目索引 {len(items)} 行 · 无数字诊断 {len(audit)} 行")
        return 0

    changed = 0
    for name, data in sorted(files.items()):
        changed += int(write_bytes_idempotent(out / name, data))
    run_log("export_library", date=date, files=len(files), changed=changed,
            items=len(items), no_number=len(audit))
    LOG.info("资料库沉淀包：%s · %d 文件 / 变更 %d · 条目 %d / 无数字诊断 %d",
             out, len(files), changed, len(items), len(audit))
    print(f"沉淀包就绪：{out} · {len(files)} 文件（变更 {changed}）")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
