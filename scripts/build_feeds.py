#!/usr/bin/env python3
"""订阅层：由 digest.json 生成 Atom 1.0 全文源、JSON Feed 1.1、多 profile 分源。

借鉴 docs-feed 的三条硬约束，并补上它的缺口：
  1. 稳定 entry id（内容不变 → 订阅阅读器不误报更新）；
  2. 全量确定性重建 + 字节比较幂等写入（no_change_no_write）；
  3. 发布前凭据扫描 + HTML 消毒（docs-feed 只有 bleach，不扫正文密钥 → 会二次扩散）。
另外：docs-feed 无历史留存、单 feed；这里按 profile 拆 5 个订阅入口并保留每日 digest.json 归档。
"""
from __future__ import annotations

import argparse
import html
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (PUBLIC_DIR, add_date_arg, load_config, read_json,
                    run_log, setup_logging, write_json, LOG)

ATOM = "http://www.w3.org/2005/Atom"
CREDENTIAL_PATTERNS = [
    re.compile(r"(?i)\b(API[_ -]?KEY|SECRET|ACCESS[_ -]?TOKEN|PASSWORD)\s*[:=]\s*\S{6,}"),
    re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"credential\.helper"),
]


def xml_text(s: str) -> str:
    """剔除 XML 1.0 非法控制字符（docs-feed 同款防御）。"""
    return "".join(c for c in (s or "") if c in "\t\n\r" or ord(c) >= 0x20
                   and not 0xD800 <= ord(c) <= 0xDFFF and ord(c) not in (0xFFFE, 0xFFFF))


def safe_html(item: dict, d: dict) -> str:
    """只允许自建的固定标签；所有外部文本一律 escape，杜绝 script / onerror / javascript:。

    v2：渲染七要素（事实锚点/关键数字/相关方/影响/下一步动作），并把原文链接外置成独立行，
    对齐 daily-rss 2026-11 的链接改版与 docs/12 的内容规范。
    """
    e = html.escape
    parts = []
    if item.get("fact_anchor"):
        parts.append(f"<p><strong>{e(item['fact_anchor'])}</strong></p>")
    if item.get("numbers") or item.get("entities"):
        bits = []
        if item.get("numbers"):
            bits.append("关键数字：" + " / ".join(str(x) for x in item["numbers"][:5]))
        if item.get("entities"):
            bits.append("相关方：" + " / ".join(str(x) for x in item["entities"][:6]))
        parts.append(f"<p>{e(' · '.join(bits))}</p>")
    if item.get("summary"):
        parts.append(f"<p>{e(item['summary'][:300])}</p>")
    if item.get("why_matters"):
        parts.append(f"<p><strong>为什么值得看：</strong>{e(item['why_matters'])}</p>")
    if item.get("impact"):
        parts.append(f"<p><strong>对我意味着什么：</strong>{e(item['impact'])}</p>")
    if item.get("next_action"):
        parts.append(f"<p><strong>下一步：</strong>{e(item['next_action'])}</p>")
    parts.append(f"<p>来源：{e(item.get('source', ''))}"
                 + (f" · 发布于 {e(str(item.get('published_at', ''))[:16])} UTC" if item.get("published_at") else "")
                 + f" · 归类：{e(item.get('category', ''))}</p>")
    if item.get("confidence") in ("inference", "unverified"):
        parts.append(f"<p>证据状态：{e('推断' if item['confidence'] == 'inference' else '未独立验证')}</p>")
    urls = [u for u in (item.get("evidence_urls") or []) if str(u).startswith("http")]
    if not urls and str(item.get("url", "")).startswith("http"):
        urls = [item["url"]]
    for u in urls[:5]:
        parts.append(f'<p>→ <a href="{e(u)}" rel="noopener noreferrer">{e(u)}</a></p>')
    return "".join(parts)


def collect_entries(cfg) -> list[dict]:
    root = PUBLIC_DIR.parent / "data" / "digest"
    out: list[dict] = []
    for path in sorted(root.glob("*/digest.json")):
        d = read_json(path, {})
        if not d.get("date"):
            continue
        for sec in d.get("sections", []):
            for it in sec.get("items", []):
                if not it.get("url", "").startswith("http"):
                    continue
                out.append({**it, "date": d["date"], "generated_at": d.get("generated_at"),
                            "section": sec.get("label", ""), "digest": d,
                            "ai_status": d.get("quality", {}).get("ai_status", "unknown")})
    return out[-cfg["retention"]["feed_max_entries"] * 4:]


def match_filter(item: dict, expr: str, taxonomy: dict) -> bool:
    expr = (expr or "").strip()
    m = re.match(r"score\s*>=\s*([\d.]+)", expr)
    if m:
        return float(item.get("score") or 0) >= float(m.group(1))
    m = re.match(r"category\s*==\s*([\w-]+)", expr)
    if m:
        return item.get("category") == m.group(1)
    m = re.match(r"category\s+in\s+\[([^\]]+)\]", expr)
    if m:
        allowed = {x.strip() for x in m.group(1).split(",")}
        return item.get("category") in allowed
    m = re.match(r"category\s+in\s+taxonomy\.groups\.(\w+)", expr)
    if m:
        grp = next((g for g in taxonomy["groups"] if g["key"] == m.group(1)), None)
        return bool(grp) and item.get("category") in grp["categories"]
    LOG.warning("无法解析的订阅过滤表达式，放行全部：%s", expr)
    return True


def build_atom(entries: list[dict], cfg: dict, label: str, profile_id: str, base_url: str) -> bytes:
    feed = ET.Element(f"{{{ATOM}}}feed", {"{http://www.w3.org/XML/1998/namespace}lang": "zh-CN"})
    ET.SubElement(feed, f"{{{ATOM}}}id").text = xml_text(f"tag:daily-info.local,2026:{profile_id}")
    ET.SubElement(feed, f"{{{ATOM}}}title").text = xml_text(f"每日信息 · {label}")
    ET.SubElement(feed, f"{{{ATOM}}}subtitle").text = xml_text(
        "挖掘 · 聚合 · 研判 · 订阅；每条附原文链接；内容仅供参考，不构成投资建议")
    ET.SubElement(feed, f"{{{ATOM}}}link", {"rel": "self", "type": "application/atom+xml",
                                            "href": f"{base_url}/{profile_id}.atom"})
    ET.SubElement(feed, f"{{{ATOM}}}link", {"rel": "alternate", "type": "text/html",
                                            "href": f"{base_url}/index.html"})
    ET.SubElement(feed, f"{{{ATOM}}}updated").text = xml_text(
        entries[0]["generated_at"] if entries else "2026-01-01T00:00:00Z")
    author = ET.SubElement(feed, f"{{{ATOM}}}author")
    ET.SubElement(author, f"{{{ATOM}}}name").text = "Personal Daily Info"

    for it in entries:
        entry = ET.SubElement(feed, f"{{{ATOM}}}entry")
        stable = f"tag:daily-info.local,{it['date']}:{it.get('cluster_id') or it['id']}"
        ET.SubElement(entry, f"{{{ATOM}}}id").text = xml_text(stable)
        ET.SubElement(entry, f"{{{ATOM}}}title").text = xml_text(
            f"[{it['section']}] {it['title']}"[:200])
        ET.SubElement(entry, f"{{{ATOM}}}link", {"rel": "alternate", "type": "text/html",
                                                 "href": xml_text(it["url"])})
        ET.SubElement(entry, f"{{{ATOM}}}published").text = xml_text(
            it.get("published_at") or it["generated_at"])
        ET.SubElement(entry, f"{{{ATOM}}}updated").text = xml_text(it["generated_at"])
        ET.SubElement(entry, f"{{{ATOM}}}category", {"term": xml_text(it.get("category", "")),
                                                     "label": xml_text(it["section"])})
        ET.SubElement(entry, f"{{{ATOM}}}summary", {"type": "text"}).text = xml_text(
            (it.get("summary") or it.get("why_matters") or it["title"])[:300])
        ET.SubElement(entry, f"{{{ATOM}}}content", {"type": "html"}).text = xml_text(
            safe_html(it, it["digest"]))
    ET.indent(feed, space="  ")
    data = ET.tostring(feed, encoding="utf-8", xml_declaration=True) + b"\n"
    ET.fromstring(data)  # 自校验
    return data


def build_jsonfeed(entries: list[dict], base_url: str) -> dict:
    return {
        "version": "https://jsonfeed.org/version/1.1",
        "title": "每日信息",
        "home_page_url": f"{base_url}/index.html",
        "feed_url": f"{base_url}/feed.json",
        "description": "挖掘 · 聚合 · 研判 · 订阅",
        "language": "zh-CN",
        "items": [{
            "id": f"tag:daily-info.local,{it['date']}:{it.get('cluster_id') or it['id']}",
            "url": it["url"],
            "title": it["title"],
            "summary": ((it.get("fact_anchor") or it.get("title") or "")
                        + (" — " + it["why_matters"] if it.get("why_matters") else ""))[:300],
            "content_html": safe_html(it, it["digest"]),
            "date_published": it.get("published_at") or it["generated_at"],
            "date_modified": it["generated_at"],
            "tags": [it.get("category", ""), it["section"]],
            "_daily_info": {"score": it.get("score"), "source": it.get("source"),
                            "cluster_id": it.get("cluster_id"), "ai_status": it["ai_status"]},
        } for it in entries],
    }


def write_bytes_idempotent(path: Path, data: bytes) -> bool:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists() and path.read_bytes() == data:
        return False
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_bytes(data)
    tmp.replace(path)
    return True


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--base-url", default="https://daily-info.local", help="站点公开地址，用于 feed self link")
    args = ap.parse_args()
    setup_logging(args.verbose)

    cfg = load_config("subscriptions.json")
    taxonomy = load_config("taxonomy.json")
    entries = collect_entries(cfg)
    if not entries:
        LOG.error("没有 digest 条目，请先运行 make_digest.py")
        return 1

    # 发布前安全闸门：任何待发布文本命中凭据特征 → 整体拒发，保留旧产物
    blob = json.dumps(entries, ensure_ascii=False, default=str)
    leaks = [p.pattern for p in CREDENTIAL_PATTERNS if p.search(blob)]
    if leaks:
        LOG.error("凭据扫描命中 %d 处，拒绝生成订阅文件（保留旧产物）", len(leaks))
        return 2

    max_entries = cfg["retention"]["feed_max_entries"]
    writes = 0
    counts = {}
    for profile in cfg["profiles"]:
        picked = [it for it in entries if match_filter(it, profile["filter"], taxonomy)][-max_entries:]
        picked = list(reversed(picked))
        counts[profile["id"]] = len(picked)
        atom = build_atom(picked, cfg, profile["label"], profile["id"], args.base_url)
        writes += int(write_bytes_idempotent(PUBLIC_DIR / f"{profile['id']}.atom", atom))
        if profile["id"] == "all":
            writes += int(write_bytes_idempotent(PUBLIC_DIR / "feed.atom", atom))
            writes += int(write_json(PUBLIC_DIR / "feed.json", build_jsonfeed(picked, args.base_url)))

    write_json(PUBLIC_DIR / "data" / "feeds.json", {
        # 确定性：取最新条目的 generated_at，不用 now_utc()，保证二次构建字节一致
        "generated_at": entries[-1]["generated_at"] if entries else None,
        "base_url": args.base_url, "counts": counts,
        "profiles": [{"id": p["id"], "label": p["label"], "url": f"{args.base_url}/{p['id']}.atom",
                      "filter": p["filter"]} for p in cfg["profiles"]]})
    run_log("build_feeds", date=args.date, writes=writes, counts=counts)
    print(f"订阅构建完成：{len(entries)} 条候选 → " + ", ".join(f"{k}={v}" for k, v in counts.items())
          + f"；变更写入 {writes} 个文件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
