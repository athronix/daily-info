#!/usr/bin/env python3
"""留存策略：默认 --dry-run 只出报告；--apply 才删除过期中间层目录。

铁律：
  - 只处理 data/raw/<date>/ 与 data/normalized/<date>/ 下超过保留期的日期目录；
  - 永不触碰 data/digest/、data/candidate/、data/state/、public/、config/、reports/；
  - 目录名必须是严格 YYYY-MM-DD，且早于截止日期才入选；
  - --apply 需要显式参数，且每批最多 10 个目录，逐批校验；
  - 任何异常立即停止，不继续删。
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import DATA_DIR, ROOT, add_date_arg, load_config, setup_logging, LOG

DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")


def candidates(layer: str, days: int, today: str) -> list[Path]:
    root = DATA_DIR / layer
    if not root.exists():
        return []
    cutoff = date.fromisoformat(today) - timedelta(days=days)
    out = []
    for p in sorted(root.iterdir()):
        if not p.is_dir() or not DATE_RE.match(p.name):
            continue
        try:
            if date.fromisoformat(p.name) < cutoff:
                out.append(p)
        except ValueError:
            continue
    return out


def remove_tree(path: Path) -> tuple[int, int]:
    files = dirs = 0
    for cur, subdirs, names in os.walk(path, topdown=False):
        for n in names:
            os.remove(Path(cur) / n)
            files += 1
        for d in subdirs:
            os.rmdir(Path(cur) / d)
            dirs += 1
    os.rmdir(path)
    return files, dirs


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--apply", action="store_true", help="真正删除（默认只出报告）")
    ap.add_argument("--batch-size", type=int, default=10, help="每批最多删除的目录数")
    args = ap.parse_args()
    setup_logging(args.verbose)

    cfg = load_config("subscriptions.json")["retention"]
    plan = {"raw": candidates("raw", cfg["raw_days"], args.date),
            "normalized": candidates("normalized", cfg["normalized_days"], args.date)}
    lines = [f"# 留存清理报告 · {args.date}", "",
             f"模式：{'APPLY（执行删除）' if args.apply else 'DRY-RUN（只读，不删除）'}",
             f"策略：raw > {cfg['raw_days']} 天，normalized > {cfg['normalized_days']} 天；"
             f"digest / candidate / state / public / config / reports 永久保留", ""]
    total = 0
    for layer, dirs in plan.items():
        lines += [f"## {layer}（{len(dirs)} 个目录）", ""]
        for p in dirs:
            n = sum(1 for _ in p.rglob("*") if _.is_file())
            lines.append(f"- {p.relative_to(ROOT).as_posix()} · {n} 文件")
            total += 1
        lines.append("")
    lines += [f"合计待处理目录：{total}", ""]
    if not args.apply:
        lines += ["**本次未执行任何删除。** 用户确认后另跑 `python scripts/retention.py --apply`。", ""]
    rdir = ROOT / "reports"
    rdir.mkdir(parents=True, exist_ok=True)
    (rdir / f"retention-{args.date}.md").write_text("\n".join(lines), encoding="utf-8")

    if not args.apply:
        print(f"DRY-RUN：{total} 个过期目录 → reports/retention-{args.date}.md（未删除任何文件）")
        return 0

    deleted_files = deleted_dirs = 0
    for layer, dirs in plan.items():
        for i in range(0, len(dirs), args.batch_size):
            batch = dirs[i:i + args.batch_size]
            for p in batch:
                if not p.exists() or not DATE_RE.match(p.name):
                    LOG.error("批次校验失败，立即停止：%s", p)
                    return 1
            for p in batch:
                f, d = remove_tree(p)
                deleted_files += f
                deleted_dirs += d
            LOG.info("%s 第 %d 批完成：%d 目录 / %d 文件", layer, i // args.batch_size + 1,
                     len(batch), f)
    lines += [f"执行结果：删除 {deleted_dirs} 个目录 / {deleted_files} 个文件。", ""]
    (rdir / f"retention-{args.date}.md").write_text("\n".join(lines), encoding="utf-8")
    print(f"APPLY 完成：删除 {deleted_dirs} 个目录 / {deleted_files} 个文件")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
