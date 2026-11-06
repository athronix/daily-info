#!/usr/bin/env python3
"""独立核验闸门：发布前对 digest / feed / site 产物做只读校验，输出可审计报告。

校验项（对应 docs/09 验收清单）：
  V1 结构完整性：必填字段、ai_status 合法、stats 计数一致
  V2 可追溯性：每条入报 item 的 id 与 url 必须存在于规则层 clusters.json（防 AI 编造）
  V3 安全：凭据正则扫描 digest.md / brief.md / feed.atom / feed.json / public/data/*.json
  V4 订阅：Atom 可 XML 解析、entry id 唯一、updated/published 合法、无 script/onerror/javascript:
  V5 幂等：连续两次构建产物字节一致
  V6 站点：index.json / latest.json / <date>.json 均存在且日期一致
  V7 降级标记：ai_status=degraded 时 headline 必须有 [降级] 前缀且不出现 editor_note
退出码 0=全通过；1=存在 violation。报告写 reports/verify-<date>.{json,md}
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (DATA_DIR, PUBLIC_DIR, ROOT, add_date_arg, day_dir, load_config,
                    read_json, read_jsonl, setup_logging, LOG)

CREDENTIAL_PATTERNS = [
    ("api_key", re.compile(r"(?i)\b(API[_ -]?KEY|SECRET|ACCESS[_ -]?TOKEN|PASSWORD)\s*[:=]\s*\S{6,}")),
    ("github_token", re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b")),
    ("github_pat", re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b")),
    ("openai_key", re.compile(r"\bsk-[A-Za-z0-9]{20,}\b")),
    ("private_key", re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----")),
    ("credential_helper", re.compile(r"credential\.helper")),
]
BAD_HTML = re.compile(r"(?i)(<script\b|onerror\s*=|javascript:|<iframe\b)")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--all-dates", action="store_true", help="核验全部归档日期")
    ap.add_argument("--no-idempotency", action="store_true", help="跳过 V5 二次构建比对")
    args = ap.parse_args()
    setup_logging(args.verbose)

    checks: list[dict] = []

    def chk(name: str, ok: bool, detail: str = "") -> None:
        checks.append({"check": name, "ok": bool(ok), "detail": detail})
        (LOG.info if ok else LOG.error)("%s %s %s", "PASS" if ok else "FAIL", name, detail)

    dates = sorted(p.parent.name for p in (DATA_DIR / "digest").glob("*/digest.json"))
    if not args.all_dates and args.date in dates:
        dates = [args.date]
    if not dates:
        chk("V0 存在 digest", False, "未找到任何 digest.json")
        return _report(args.date, checks)

    blobs: list[tuple[str, str]] = []
    for date in dates:
        d = read_json(day_dir("digest", date) / "digest.json", {})
        clusters = read_json(day_dir("candidate", date) / "clusters.json", {})
        # V1
        required = ["date", "headline", "generated_at", "sections", "stats", "quality"]
        chk(f"V1[{date}] 必填字段", all(k in d for k in required),
            ",".join(k for k in required if k not in d))
        chk(f"V1[{date}] ai_status 合法",
            d.get("quality", {}).get("ai_status") in ("ok", "degraded", "unknown"))
        published = sum(len(s.get("items", [])) for s in d.get("sections", []))
        chk(f"V1[{date}] stats 自洽", d.get("stats", {}).get("published_items") == published,
            f"stats={d.get('stats', {}).get('published_items')} vs 实际={published}")

        # V2
        ids, urls = set(), set()
        for c in clusters.get("clusters", []):
            ids.add(c["cluster_id"])
            for m in c.get("members", []):
                ids.add(m["id"])
                urls.add(m.get("url", ""))
        bad = []
        for s in d.get("sections", []):
            for it in s.get("items", []):
                if it.get("id") not in ids:
                    bad.append(f"id:{it.get('id')}")
                if it.get("url") not in urls:
                    bad.append(f"url:{it.get('url')[:60]}")
                if not str(it.get("url", "")).startswith("http"):
                    bad.append(f"non_http:{it.get('id')}")
        chk(f"V2[{date}] id/url 白名单", not bad, f"violations={len(bad)} {bad[:3]}")
        chk(f"V2[{date}] 无重复条目",
            len([it["id"] for s in d.get("sections", []) for it in s.get("items", [])]) ==
            len({it["id"] for s in d.get("sections", []) for it in s.get("items", [])}))

        # V7
        degraded = d.get("quality", {}).get("ai_status") == "degraded"
        if degraded:
            chk(f"V7[{date}] 降级标记", d.get("headline", "").startswith("[降级]")
                and not d.get("editor_note"))

        # V8 内容丰富度：实在 / 具体 / 有效 / 丰富（依据 config/content-spec.json + docs/12）
        spec = load_config("content-spec.json")
        if degraded:
            chk(f"V8[{date}] 内容丰富度", True, "skipped：降级日报只验降级标记")
            # 保持报告结构稳定：降级时也显式记录口径闸门被跳过，
            # 否则 push_daily.gate 会把「缺检查项」误判为复用了收紧前的旧报告。
            chk(f"V8[{date}] 数字白名单口径排除元数据", True,
                "skipped：降级日报，V8 丰富度整段跳过；分发需人工复核")
        else:
            req = spec["verification"]
            flat = [it for s in d.get("sections", []) for it in s.get("items", [])]
            required = ("fact_anchor", "numbers", "entities", "evidence_urls",
                        "why_matters", "impact", "next_action")
            ok_items = [it for it in flat if all(it.get(k) for k in required)]
            ratio = len(ok_items) / max(1, len(flat))
            chk(f"V8[{date}] 七要素达标率", ratio >= req["min_seven_element_pass_ratio"],
                f"{len(ok_items)}/{len(flat)} = {round(ratio * 100, 1)}% "
                f"(阈值 {round(req['min_seven_element_pass_ratio'] * 100)}%)")
            with_num = [it for it in flat if it.get("numbers")]
            num_ratio = len(with_num) / max(1, len(flat))
            chk(f"V8[{date}] 含可核验数字条目比",
                num_ratio >= req["min_items_with_numbers_ratio"],
                f"{len(with_num)}/{len(flat)} = {round(num_ratio * 100, 1)}%")
            lead = d.get("lead", "")
            chk(f"V8[{date}] 数据化导语含数字",
                not req["require_lead_number"] or bool(re.search(r"\d", lead)),
                f"lead={lead[:40]}")
            signals = d.get("watch_signals", [])
            chk(f"V8[{date}] 待验证信号清单",
                not req["require_watch_signals"] or len(signals) >= spec["watch_signals"]["min"],
                f"count={len(signals)}（阈值 {spec['watch_signals']['min']}）")
            vague = [w for w in spec["quality_rules"]["forbid_vague_next_action"]
                     if any(w in (it.get("next_action") or "") for it in flat)]
            chk(f"V8[{date}] 下一步动作无空话", not vague, f"命中={vague[:3]}")
            note = d.get("editor_note", "")
            ecfg = spec["editor_note"]
            chk(f"V8[{date}] 编者观察字数", ecfg["min_chars"] <= len(note) <= ecfg["max_chars"],
                f"{len(note)} 字（要求 {ecfg['min_chars']}-{ecfg['max_chars']}）")
            tcfg = spec["themes"]
            themes = d.get("themes", [])
            chk(f"V8[{date}] 主题数与佐证",
                tcfg["min"] <= len(themes) <= tcfg["max"] and
                all(len(t.get("cluster_ids", [])) >= spec["themes"]["min_evidence_clusters"]
                    for t in themes),
                f"themes={len(themes)} min_evidence={min((len(t.get('cluster_ids', [])) for t in themes), default=0)}")
            chk(f"V8[{date}] 数字/实体/URL 均来自原文",
                d.get("quality", {}).get("number_whitelist") is True and
                d.get("quality", {}).get("entity_whitelist") is True,
                "make_digest.py 白名单校验标记")

            # v1.1 口径闸门：数字白名单必须排除 published_at 等采集元数据，
            # 防止「用日期年份冒充可核验读数」的虚高统计回退。历史归档只记不改写。
            vcfg = spec["verification"]
            effective = vcfg["number_whitelist_effective_from"]
            if date >= effective:
                scope = d.get("quality", {}).get("number_whitelist_scope")
                excludes = d.get("quality", {}).get("number_whitelist_excludes", [])
                chk(f"V8[{date}] 数字白名单口径排除元数据",
                    scope == vcfg["number_whitelist_scope"] and
                    all(x in excludes for x in vcfg["number_whitelist_excludes"]),
                    f"scope={scope} excludes={excludes}")
                sub = d.get("stats", {}).get("substantive_number_ratio")
                real = round(num_ratio, 3)
                chk(f"V8[{date}] 实质数字比自洽",
                    sub is not None and abs(sub - real) < 0.002,
                    f"stats={sub} vs 实算={real}")
                rejected = d.get("stats", {}).get("rejected_no_number", 0)
                logged = sum(1 for w in d.get("quality", {}).get("warnings", [])
                             if w.startswith("rejected_no_substantive_number:"))
                chk(f"V8[{date}] 无数字条目拒绝留痕",
                    rejected == logged, f"stats={rejected} warnings={logged}")
            else:
                chk(f"V8[{date}] 数字白名单口径（历史归档豁免）", True,
                    f"date<{effective}，保留旧口径产物，不回写历史")

        for name in ("digest.md", "brief.md"):
            p = day_dir("digest", date) / name
            if p.exists():
                blobs.append((f"{date}/{name}", p.read_text(encoding="utf-8")))

    # V3
    for p in sorted(PUBLIC_DIR.glob("*.atom")) + sorted(PUBLIC_DIR.glob("*.json")) \
            + sorted((PUBLIC_DIR / "data").glob("*.json")):
        blobs.append((str(p.relative_to(PUBLIC_DIR)), p.read_text(encoding="utf-8", errors="replace")))
    hits = [f"{name}:{label}" for name, text in blobs
            for label, pat in CREDENTIAL_PATTERNS if pat.search(text)]
    bad_html = [name for name, text in blobs if BAD_HTML.search(text)]
    chk("V3 凭据扫描", not hits, f"violations={len(hits)} {hits[:3]}")
    chk("V3 危险 HTML", not bad_html, f"files={bad_html[:3]}")

    # V4
    atom_files = sorted(PUBLIC_DIR.glob("*.atom"))
    chk("V4 Atom 文件存在", len(atom_files) >= 2, f"count={len(atom_files)}")
    for p in atom_files:
        try:
            root = ET.parse(p).getroot()
            ns = "{http://www.w3.org/2005/Atom}"
            eids = [e.text for e in root.findall(f"{ns}entry/{ns}id")]
            # 主入口必须非空；分流 profile 当日无符合条件条目属正常（视图允许为空）
            primary = p.name in ("all.atom", "feed.atom")
            ok = len(eids) == len(set(eids)) and (len(eids) > 0 or not primary)
            detail = f"entries={len(eids)} unique={len(set(eids))}"
            if not eids:
                detail += " · 分流视图当日为空（允许）"
            chk(f"V4 {p.name} 解析/ID 唯一", ok, detail)
        except ET.ParseError as exc:
            chk(f"V4 {p.name} 解析", False, str(exc))

    # V6
    index = read_json(PUBLIC_DIR / "data" / "index.json", {})
    latest = read_json(PUBLIC_DIR / "data" / "latest.json", {})
    chk("V6 站点索引", bool(index.get("dates")), f"days={len(index.get('dates', []))}")
    chk("V6 latest 一致", latest.get("date") == index.get("dates", [{}])[0].get("date"),
        f"latest={latest.get('date')} index0={index.get('dates', [{}])[0].get('date')}")
    for d in index.get("dates", [])[:3]:
        chk(f"V6 日切片 {d['date']}", (PUBLIC_DIR / "data" / f"{d['date']}.json").exists())
    for f in index.get("feeds", []):
        chk(f"V6 订阅地址 {f['url']}", (PUBLIC_DIR / str(f["url"]).lstrip("/")).exists(),
            "索引里的 profile 产物文件必须真实存在（防 P05 口径漂移）")

    # V5：再次执行确定性构建器，比对全部产物字节哈希（幂等写入保证无副作用）
    if args.no_idempotency:
        chk("V5 幂等", True, "skipped by --no-idempotency")
    else:
        def snapshot() -> dict[str, str]:
            files = sorted(PUBLIC_DIR.glob("*.atom")) + sorted(PUBLIC_DIR.glob("*.json")) \
                + sorted((PUBLIC_DIR / "data").glob("*.json"))
            return {str(p.relative_to(PUBLIC_DIR)): hashlib.sha256(p.read_bytes()).hexdigest()
                    for p in files}

        before = snapshot()
        for builder in ("build_feeds.py", "build_site.py"):
            r = subprocess.run([sys.executable, str(ROOT / "scripts" / builder), "--date", args.date],
                               cwd=str(ROOT), capture_output=True, text=True,
                               encoding="utf-8", errors="replace")
            if r.returncode != 0:
                chk(f"V5 二次构建 {builder}", False, (r.stderr or "")[-200:])
        after = snapshot()
        diff = [k for k in set(before) | set(after) if before.get(k) != after.get(k)]
        chk("V5 幂等（二次构建字节一致）", not diff,
            f"files={len(before)} changed={len(diff)} {diff[:3]}")

    return _report(args.date, checks)


def _report(date: str, checks: list[dict]) -> int:
    violations = [c for c in checks if not c["ok"]]
    result = {"date": date, "total_checks": len(checks), "passed": len(checks) - len(violations),
              "violations": len(violations), "checks": checks}
    rdir = ROOT / "reports"
    rdir.mkdir(parents=True, exist_ok=True)
    (rdir / f"verify-{date}.json").write_text(json.dumps(result, ensure_ascii=False, indent=2),
                                              encoding="utf-8")
    lines = [f"# 交付物核验报告 · {date}", "",
             f"- 检查项：{result['total_checks']}",
             f"- 通过：{result['passed']}",
             f"- **violations：{result['violations']}**", "",
             "| 检查 | 结果 | 说明 |", "| --- | --- | --- |"]
    for c in checks:
        lines.append(f"| {c['check']} | {'PASS' if c['ok'] else 'FAIL'} | {c['detail']} |")
    (rdir / f"verify-{date}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"核验完成：{result['passed']}/{result['total_checks']} 通过，"
          f"violations={result['violations']} → reports/verify-{date}.md")
    return 0 if not violations else 1


if __name__ == "__main__":
    raise SystemExit(main())
