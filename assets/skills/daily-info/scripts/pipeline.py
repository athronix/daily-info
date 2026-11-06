#!/usr/bin/env python3
"""skill 入口：一条命令查看状态 / 跑流水线 / 核验 / 体检，无需记住各脚本参数。

  python pipeline.py status                     # 只读：最近日期、产物、核验状态
  python pipeline.py run --offline-demo          # 离线全链路 smoke
  python pipeline.py run                         # 真实跑（先跑规则层，AI 文件缺失则降级）
  python pipeline.py check --all                 # 独立核验
  python pipeline.py health                     # 信源体检（只读）
  python pipeline.py week                       # 周复盘输入打包

本脚本只是薄封装，所有逻辑仍在项目 scripts/ 下，避免 skill 与项目出现两套实现。
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

SKILL_ROOT = Path(__file__).resolve().parents[1]
ROOT = Path("D:/Users/towyq/Documents/Projects/personal-daily-info")
SCRIPTS = ROOT / "scripts"


def call(script: str, *args: str) -> int:
    if not (SCRIPTS / script).exists():
        print(f"[ERROR] 找不到 {SCRIPTS / script}；请确认工作目录已指向 personal-daily-info")
        return 2
    r = subprocess.run([sys.executable, str(SCRIPTS / script), *args], cwd=str(ROOT))
    return r.returncode


def status() -> int:
    import json
    digests = sorted((ROOT / "data" / "digest").glob("*/digest.json"))
    print(f"工作目录：{ROOT}")
    print(f"skill 目录：{SKILL_ROOT}")
    print(f"归档日报：{len(digests)} 天")
    for p in digests[-5:]:
        d = json.loads(p.read_text(encoding="utf-8"))
        q = d.get("quality", {})
        print(f"  {d['date']}  {d['headline'][:34]:<36} "
              f"入报 {d.get('stats', {}).get('published_items', 0):>3} 条  "
              f"ai={q.get('ai_status')}  warnings={len(q.get('warnings', []))}")
    reports = sorted((ROOT / "reports").glob("verify-*.md"))
    if reports:
        print(f"最近核验报告：{reports[-1].name}")
        line = next((l for l in reports[-1].read_text(encoding="utf-8").splitlines()
                     if "violations" in l), "")
        print("  " + line.strip())
    print(f"站点数据：{'存在' if (ROOT / 'public/data/index.json').exists() else '缺失'}")
    print(f"订阅文件：{len(list((ROOT / 'public').glob('*.atom')))} 个 Atom")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("status")
    run = sub.add_parser("run")
    run.add_argument("--offline-demo", action="store_true")
    run.add_argument("--date")
    chk = sub.add_parser("check")
    chk.add_argument("--all", action="store_true")
    sub.add_parser("health")
    sub.add_parser("week")
    a = ap.parse_args()

    if a.cmd == "status":
        return status()
    if a.cmd == "run":
        args = (["--offline-demo"] if a.offline_demo else []) + (["--date", a.date] if a.date else [])
        return call("run_daily.py", *args)
    if a.cmd == "check":
        return call("verify_digest.py", *(["--all-dates"] if a.all else []))
    if a.cmd == "health":
        return call("check_sources.py")
    if a.cmd == "week":
        return call("pack_week.py")
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
