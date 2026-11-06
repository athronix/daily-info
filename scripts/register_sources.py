#!/usr/bin/env python3
"""把 probe_candidates.py 体检通过的候选源，幂等登记进 config/sources.json。

纪律：
  - 只登记 reports/candidate-probe-<date>.json 里 ok=true 的候选，未体检的 URL 绝不启用；
  - 体检发现「两个 URL 返回完全相同内容」时显式跳过其中一个，避免重复采集；
  - 权重按信噪比分层：官方/研究类加权，消费类泛资讯降权——靠打分控噪，不靠删源；
  - 幂等：重复运行不会重复追加；已存在 id 直接跳过。

零第三方依赖。
"""
from __future__ import annotations

import argparse
import json
from collections import Counter
from pathlib import Path

from common import CONFIG_DIR, ROOT, add_date_arg, load_config, setup_logging, write_json

# 体检发现与其它源返回同一份内容：IEEE Spectrum 两个入口相同；
# TLDR webdev 与 engineering 当前指向同一份 newsletter，保留 webdev 与 tech。
SKIP = {
    "ieee-spectrum-alt": "与 ieee-spectrum 返回完全相同的 30 条，避免重复",
    "tldr-engineering": "与 tldr-webdev 当前返回同一份 newsletter，避免重复",
}

TIER_BY_KIND = {"rss": "A", "atom": "A", "git_atom": "A",
                "json_api": "B", "html": "C"}

DEFAULT_WEIGHT = {
    "ai-models": 1.0, "agent-engineering": 0.9, "dev-tools": 0.6,
    "research-papers": 0.9, "docs-changelog": 1.0, "industry-capital": 0.9,
    "market-invest": 0.9, "security-governance": 0.9, "community": 0.6,
    "deep-read": 1.0,
}

# 显式权重：高质量一手源加权，量大/泛消费源降权。
WEIGHTS = {
    "anthropic-news-community": 1.2, "google-research-blog": 1.1,
    "mistral-news": 1.1, "nvidia-blog": 1.0, "aws-ml-blog": 0.9,
    "lilianweng": 1.2, "martinfowler": 1.1, "nautilus": 0.9, "platformer": 1.0,
    "bair-blog": 1.1, "nature": 1.1, "science-news": 1.1,
    "ieee-spectrum": 1.1, "semiengineering": 1.1, "eetimes": 1.0,
    "nasa-news": 0.9, "bbc-science": 0.8, "scientificamerican": 0.8,
    "arxiv-cs-lg": 0.7, "arxiv-cs-cv": 0.7, "sciencedaily-all": 0.6,
    "scitechdaily": 0.7, "newscientist": 0.9, "semiwiki": 0.8,
    "ars-science": 0.9, "the-decoder": 0.9, "techmeme": 1.0,
    "sifted": 1.0, "eu-startups": 0.9, "yc-blog": 0.9,
    "techcrunch-startups": 1.0, "payloadspace": 0.9, "fastcompany": 0.6,
    "inc42": 0.7, "guardian-ai": 0.8, "tmtpost": 0.7,
    "google-news-cn-funding": 0.7, "google-news-hk-ipo": 0.8,
    "google-news-chip": 0.8, "google-news-opensource": 0.8,
    "tldr-webdev": 1.0, "tldr-tech": 1.0,
    "thenewstack": 0.9, "cncf-blog": 0.9, "stackoverflow-blog": 0.8,
    "lwn": 0.9, "devto": 0.7, "hackaday": 0.7, "oschina": 0.6,
    "gh-releases-ollama": 1.1, "gh-releases-vscode": 1.1,
    "gh-releases-langchain": 1.1, "hf-spaces-new": 0.8,
    "krebsonsecurity": 1.0, "thehackernews": 0.9, "darkreading": 0.9,
    "therecord": 0.9, "helpnetsecurity": 0.8,
    # 泛消费/泛科技：可用但信噪比低，降权让打分自然淘汰
    "mashable": 0.4, "cnet": 0.5, "techradar": 0.5, "extremetech": 0.5,
    "techrepublic": 0.5, "zdnet": 0.5, "core77": 0.5, "yankodesign": 0.5,
    "kickstarter-blog": 0.4, "newatlas": 0.6, "engadget": 0.6,
    "tomshardware": 0.6, "reddit-opensource": 0.6,
}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--dry-run", action="store_true", help="只打印将登记的条目，不落盘")
    args = ap.parse_args()
    setup_logging(args.verbose)

    probe_path = ROOT / "reports" / f"candidate-probe-{args.date}.json"
    probe = json.loads(probe_path.read_text(encoding="utf-8"))
    all_probe = {p["id"]: p for p in probe}
    ok = {p["id"]: p for p in probe if p["ok"]}
    candidates = json.loads((CONFIG_DIR / "candidates.json").read_text(encoding="utf-8"))["candidates"]
    cfg = load_config("sources.json")
    existing = {s["id"] for s in cfg["sources"]}

    added: list[dict] = []
    skipped: list[tuple[str, str]] = []
    for c in candidates:
        cid = c["id"]
        if cid in SKIP:
            skipped.append((cid, SKIP[cid]))
            continue
        if cid in existing:
            skipped.append((cid, "已登记"))
            continue
        p = ok.get(cid)
        if not p:
            reason = (all_probe.get(cid) or {}).get("reason", "未体检")
            skipped.append((cid, f"体检未通过：{reason}"))
            continue
        cat = c["cat"]
        entry = {
            "id": cid,
            "name": c["name"],
            "url": c["url"],
            "kind": c["kind"],
            "tier": TIER_BY_KIND[c["kind"]],
            "category_hint": cat,
            "lang": c["lang"],
            "weight": WEIGHTS.get(cid, DEFAULT_WEIGHT.get(cat, 0.7)),
            "enabled": True,
            "health": {"status": p.get("status"),
                       "content_type": p.get("content_type"),
                       "checked_at": args.date},
            "note": (f"2026-11-05 候选体检通过（{p.get('parsed_items')} 条可解析）；"
                     f"来源：{c.get('from', '网络检索')}"),
        }
        added.append(entry)

    if args.dry_run:
        print(f"将登记 {len(added)} 个源；跳过 {len(skipped)} 个")
        for e in added:
            print(f"  + {e['id']:<32} {e['tier']} w={e['weight']} {e['category_hint']}")
        return 0

    cfg["sources"].extend(added)
    write_json(CONFIG_DIR / "sources.json", cfg)

    tiers = Counter(e["tier"] for e in added)
    cats = Counter(e["category_hint"] for e in added)
    print(f"已登记 {len(added)} 个新源（Tier {dict(tiers)}），跳过 {len(skipped)} 个")
    print("按分类：" + " / ".join(f"{k}={v}" for k, v in cats.most_common()))
    enabled = sum(1 for s in cfg["sources"] if s.get("enabled") and s["tier"] != "X")
    print(f"sources.json 现有 {len(cfg['sources'])} 源，启用 {enabled} 个")
    for cid, why in skipped:
        if why != "已登记":
            print(f"  - {cid}: {why}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
