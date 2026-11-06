#!/usr/bin/env python3
"""OPML 信源清单导入器：解析 → 三重实测 → 智能分流登记（幂等）。

用法：
    python scripts/import_opml.py --file docs/references/xxx.opml --date 2026-11-05 [--dry-run]

分流规则（与 2026-11-05 tech_and_finance_feeds.opml 实战一致）：
  1. 解析 OPML 全部 outline@xmlUrl，带分组名作为分类线索；
  2. 逐 URL 三重实测：HTTP 200 + 响应体是 feed + parse_feed 能出 ≥3 条；
  3. 通过的源按主机智能分流：
     - URL 规范化后与现有源相同 → 跳过（重复）；
     - 该主机已有**启用**源 → 跳过并提示（避免同域双份配额，如 Reddit/gnews 教训）；
       但启用态的 gnews 转载版（id 以 gnews- 开头）若被**官方原生 feed** 顶到同域，
       自动禁用 gnews 版并登记官方版（官方原文直链对溯源白名单更友好）；
     - 该主机只有 Tier X / 禁用源 → 登记为「复活」候选（新路径常有惊喜）；
     - 全新主机 → 直接登记；
  4. 未通过的源只写进报告，不登记。
kind 自动判定：URL 以 .atom 结尾或解析根为 feed → atom，否则 rss。
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
import xml.etree.ElementTree as ET
from collections import defaultdict
from pathlib import Path
from urllib.parse import urlsplit

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ROOT, add_date_arg, decode_payload, load_config, now_utc,
                    parse_feed, setup_logging, write_json, LOG)  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
      "Accept": "application/rss+xml,application/atom+xml,application/xml,text/xml,*/*"}

# OPML 分组关键词 → taxonomy category_hint（模糊匹配，命中不到用 fallback）
GROUP_HINTS = [
    (("ai", "模型", "llm", "machine learning"), "ai-models"),
    (("agent", "mcp"), "agent-engineering"),
    (("产品", "product", "design", "gadgets", "hardware"), "dev-tools"),
    (("投融资", "融资", "venture", "capital", "startup", "finance", "ipo", "财经", "港股"), "industry-capital"),
    (("市场", "markets", "trading"), "market-invest"),
    (("开源", "open source", "dev", "engineering", "blog", "foundation", "go", "rust"), "dev-tools"),
    (("学术", "科研", "nature", "science", "arxiv", "paper", "research"), "research-papers"),
    (("安全", "security", "privacy"), "security-governance"),
]


def hint_for(group: str, name: str) -> str:
    text = (group + " " + name).lower()
    for keys, cat in GROUP_HINTS:
        if any(k in text for k in keys):
            return cat
    return "community"


def norm(u: str) -> str:
    s = urlsplit(u)
    return s.netloc.lower().removeprefix("www.") + s.path.rstrip("/")


def host_of(u: str) -> str:
    return urlsplit(u).netloc.lower().removeprefix("www.")


def parse_opml(path: Path) -> list[dict]:
    root = ET.parse(path).getroot()
    out: list[dict] = []

    def walk(node, group):
        for o in node.findall("outline"):
            g = o.get("text") or o.get("title") or group
            u = o.get("xmlUrl")
            if u:
                out.append({"group": group or g, "name": g, "url": u})
            else:
                walk(o, g)
    walk(root.find("body"), "")
    return out


def probe_item(it: dict, timeout: int) -> dict:
    try:
        r = urllib.request.urlopen(urllib.request.Request(it["url"], headers=UA), timeout=timeout)
        body = decode_payload(r.read(2 * 1024 * 1024), r.headers)
        items = parse_feed(body)
        ok = len(items) >= 3
        return {**it, "status": r.status, "ok": ok, "parsed_items": len(items),
                "sample_title": (items[0].get("title") or "")[:70] if items else "",
                "reason": "" if ok else "解析条目 <3"}
    except Exception as e:  # noqa: BLE001
        return {**it, "status": getattr(e, "code", 0), "ok": False, "parsed_items": 0,
                "sample_title": "", "reason": f"{type(e).__name__}: {str(e)[:70]}"}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--file", required=True, help="OPML 文件路径")
    add_date_arg(ap)
    ap.add_argument("--timeout", type=int, default=22)
    ap.add_argument("--dry-run", action="store_true", help="只探测与分流，不写 sources.json")
    ap.add_argument("--weight", type=float, default=0.9)
    args = ap.parse_args()
    setup_logging(args.verbose)

    opml_path = Path(args.file)
    if not opml_path.is_absolute():
        opml_path = ROOT / opml_path
    entries = parse_opml(opml_path)
    LOG.info("OPML 解析：%d 个 feed URL", len(entries))

    cfg = load_config("sources.json")
    srcs = cfg["sources"]
    by_norm = {norm(s["url"]): s["id"] for s in srcs}
    live_hosts: dict[str, list[str]] = defaultdict(list)
    dead_hosts: dict[str, list[str]] = defaultdict(list)
    for s in srcs:
        (live_hosts if (s.get("enabled") and s["tier"] != "X") else dead_hosts)[host_of(s["url"])].append(s["id"])

    results, added, replaced, skipped, refused = [], [], [], [], []
    for e in entries:
        p = probe_item(e, args.timeout)
        results.append(p)
        h = host_of(e["url"])
        if not p["ok"]:
            refused.append(p)
            continue
        if norm(e["url"]) in by_norm:
            skipped.append((p, "URL 已登记")); continue
        gnews = [x for x in live_hosts.get(h, []) if x.startswith("gnews-")]
        if live_hosts.get(h) and not gnews:
            skipped.append((p, f"同域已有启用源 {live_hosts[h][:2]}")); continue
        if args.dry_run:
            added.append(p["name"]); continue
        kind = "atom" if e["url"].rstrip("/").endswith(".atom") else "rss"
        nid = "opml-" + (norm(e["url"]).split("/")[0][:24] + "-" + str(len(srcs)))
        tag = "复活（该域原仅 Tier X/禁用源）" if h in dead_hosts and h not in live_hosts or gnews else "新域直连"
        if gnews:
            for gid in gnews:
                g = next(s for s in srcs if s["id"] == gid)
                g["enabled"] = False
                g["note"] += f" 【2026-11-05 OPML 导入：官方原生 feed（{p['parsed_items']} 条/原文直链）顶替本转载版】"
                replaced.append(gid)
        srcs.append({"id": nid, "name": e["name"], "url": e["url"], "kind": kind,
                     "tier": "A" if p["parsed_items"] >= 10 else "B",
                     "category_hint": hint_for(e["group"], e["name"]),
                     "lang": "zh" if re_zh(e["name"]) else "en",
                     "weight": args.weight, "enabled": True,
                     "source_origin": opml_path.name,
                     "note": f"{now_utc().date().isoformat()} OPML 导入实测：{p['status']} 解析 "
                             f"{p['parsed_items']} 条（样题《{p['sample_title'][:30]}》）；{tag}",
                     "health": {"status": 200, "content_type": "application/xml",
                                "checked_at": args.date}})
        live_hosts[h].append(nid)
        by_norm[norm(e["url"])] = nid
        added.append(nid)
        time.sleep(0.3)

    rep_dir = ROOT / "reports"
    write_json(rep_dir / f"opml-import-{args.date}.json",
               {"file": opml_path.name, "parsed": len(entries),
                "passed": sum(1 for r in results if r["ok"]),
                "added": added, "replaced_gnews": replaced,
                "skipped": [(p["name"], why) for p, why in skipped],
                "refused": [{"name": r["name"], "status": r["status"], "reason": r["reason"]} for r in refused]})
    md = [f"# OPML 导入报告 · {args.file} · {args.date}", "",
          f"- 解析 URL：{len(entries)}　实测通过：**{sum(1 for r in results if r['ok'])}**",
          f"- 新登记：{len(added)}　顶替 gnews 转载版：{len(replaced)}　跳过（重复/同域）：{len(skipped)}　被拒：{len(refused)}", ""]
    md += [f"- 新登记：{a}" for a in added]
    md += ["", "## 跳过明细"] + [f"- {p['name']}（{why}）" for p, why in skipped]
    md += ["", "## 被拒明细"] + [f"- {r['name']} {r['status']} {r['reason'][:60]}" for r in refused]
    (rep_dir / f"opml-import-{args.date}.md").write_text("\n".join(md) + "\n", encoding="utf-8")

    if not args.dry_run:
        cfg["sources"] = srcs
        (ROOT / "config" / "sources.json").write_text(
            json.dumps(cfg, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    en = sum(1 for s in srcs if s.get("enabled") and s["tier"] != "X")
    print(f"parsed={len(entries)} passed={sum(1 for r in results if r['ok'])} "
          f"added={len(added)} replaced={len(replaced)} skipped={len(skipped)} refused={len(refused)} "
          f"| total={len(srcs)} enabled={en}{' (dry-run 未写入)' if args.dry_run else ''}")
    return 0


def re_zh(name: str) -> bool:
    import re
    return bool(re.search(r"[\u4e00-\u9fff]", name))


if __name__ == "__main__":
    raise SystemExit(main())
