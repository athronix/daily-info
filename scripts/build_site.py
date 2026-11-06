#!/usr/bin/env python3
"""展示站数据层：把每天唯一事实源 digest.json 投影成静态站点可直接 fetch 的 JSON 切片。

  public/data/index.json    归档索引（日期 + headline + stats），站点首屏先读它
  public/data/latest.json   最新一天完整日报
  public/data/<date>.json   每天一份完整日报，站点按日期切换，无需后端

静态 HTML 只读这些 JSON，做到「改数据不改代码」。全部幂等写入。
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (DATA_DIR, PUBLIC_DIR, add_date_arg, load_config,
                    read_json, run_log, setup_logging, write_json, LOG)


def collect_digests() -> list[dict]:
    root = DATA_DIR / "digest"
    out = []
    for path in sorted(root.glob("*/digest.json")):
        d = read_json(path, {})
        if d.get("date"):
            out.append(d)
    return sorted(out, key=lambda x: x["date"])


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    args = ap.parse_args()
    setup_logging(args.verbose)

    digests = collect_digests()
    if not digests:
        LOG.error("未找到任何 digest.json，请先运行 build_digest / run_daily.py --offline-demo")
        return 1
    data_dir = PUBLIC_DIR / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    writes = 0
    for d in digests:
        writes += int(write_json(data_dir / f"{d['date']}.json", d))
    index = {
        "site": {"title": "每日信息", "subtitle": "挖掘 · 聚合 · 研判 · 订阅",
                 "timezone": "Asia/Shanghai", "version": "1.0.0"},
        # 确定性：取最新 digest 的 generated_at，绝不用 now_utc()（否则二次构建字节不同，破坏幂等）
        "generated_at": digests[-1].get("generated_at"),
        "dates": [{
            "date": d["date"],
            "headline": d.get("headline", ""),
            "lead": d.get("lead", ""),
            "demo": bool(d.get("demo")),
            "stats": d.get("stats", {}),
            "section_count": len(d.get("sections", [])),
            "item_count": sum(len(s.get("items", [])) for s in d.get("sections", [])),
            "ai_status": d.get("quality", {}).get("ai_status", "unknown"),
            "seven_element_ratio": d.get("stats", {}).get("seven_element_ratio", 0),
            "theme_count": len(d.get("themes", [])),
            "watch_signal_count": len(d.get("watch_signals", [])),
            "reference_domains": d.get("stats", {}).get("unique_reference_domains", 0),
        } for d in reversed(digests)],
        "feeds": [{"id": p["id"], "label": p["label"], "url": p["entry"]}
                  for p in load_config("subscriptions.json")["profiles"]],
    }
    writes += int(write_json(data_dir / "index.json", index))
    writes += int(write_json(data_dir / "latest.json", digests[-1]))
    run_log("build_site", date=args.date, days=len(digests), writes=writes)
    print(f"站点数据构建完成：{len(digests)} 天，变更写入 {writes} 个文件 → public/data/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
