#!/usr/bin/env python3
"""归一化层：raw → 统一 Item schema，做时间窗过滤、URL 规范化、规则分类。

输出 data/normalized/<date>/items.jsonl（一行一条 Item）
     data/normalized/<date>/_summary.json
并把首次出现的 canonical_url 写入 data/state/seen.db（SQLite），供 novelty 打分与跨天去重。
"""
from __future__ import annotations

import argparse
import json
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (DATA_DIR, add_date_arg, canonical_url, day_dir, item_id,
                    load_config, now_utc, parse_when, read_json, read_jsonl,
                    run_log, setup_logging, strip_html, write_json, LOG)

TOKEN_RE = re.compile(r"[\u4e00-\u9fff]|[a-z0-9][a-z0-9+#.\-]*", re.I)


def tokenize(text: str) -> set[str]:
    text = (text or "").lower()
    words = TOKEN_RE.findall(text)
    out = set(words)
    han = "".join(c for c in text if "\u4e00" <= c <= "\u9fff")
    out.update(han[i:i + 2] for i in range(len(han) - 1))
    return {t for t in out if len(t) > 1 or "\u4e00" <= t <= "\u9fff"}


def classify(title: str, summary: str, hint: str, taxonomy: dict) -> tuple[str, list[str], list[str]]:
    text = f"{title} {summary[:400]}".lower()
    hit_rules: list[str] = []
    scores: dict[str, float] = {}
    for cat in taxonomy["categories"]:
        hits = sum(1 for kw in cat["keywords_zh"] + cat["keywords_en"] if kw.lower() in text)
        if hits:
            scores[cat["key"]] = min(hits, 5) * 0.12 + cat["weight"] * 0.1
            hit_rules.append(f"{cat['key']}:{hits}")
    focus = taxonomy["tags"]["user_focus"]
    focus_hit = any(kw.lower() in text for kw in focus["keywords"])
    if hint and hint in scores:
        scores[hint] += 0.25
    category = max(scores, key=scores.get) if scores else hint or taxonomy["fallback_category"]
    tags = []
    if focus_hit:
        tags.append("user_focus")
    if any(k in text for k in ["release", "changelog", "版本", "发布"]):
        tags.append("release")
    if any(k in text for k in ["funding", "raises", "融资", "并购"]):
        tags.append("funding")
    if any(k in text for k in ["arxiv", "论文", "paper"]):
        tags.append("research")
    return category, tags, hit_rules


def init_db(in_memory: bool = False) -> sqlite3.Connection:
    """demo 模式用内存库：重复跑离线 smoke 结果稳定，且不污染真实 seen.db。"""
    if in_memory:
        conn = sqlite3.connect(":memory:")
    else:
        db = DATA_DIR / "state" / "seen.db"
        db.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(db)
    conn.execute("""CREATE TABLE IF NOT EXISTS seen (
        item_key TEXT PRIMARY KEY, first_seen TEXT NOT NULL,
        title TEXT, source_id TEXT, repeat_count INTEGER DEFAULT 1)""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_first_seen ON seen(first_seen)")
    return conn


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--window-hours", type=int, default=None)
    ap.add_argument("--demo", action="store_true", help="内存态 seen.db，保证离线演示可重放")
    args = ap.parse_args()
    setup_logging(args.verbose)

    src_cfg = load_config("sources.json")
    taxonomy = load_config("taxonomy.json")
    window = args.window_hours or src_cfg["window_hours"]
    now = now_utc()
    cutoff = now - timedelta(hours=window)
    future = now + timedelta(minutes=30)
    by_id = {s["id"]: s for s in src_cfg["sources"]}

    raw_dir = day_dir("raw", args.date)
    out_dir = day_dir("normalized", args.date)
    conn = init_db(in_memory=args.demo)
    rows, stats = [], {"raw": 0, "kept": 0, "dropped_no_url": 0,
                       "dropped_old": 0, "dropped_dup_in_batch": 0, "new_to_seen": 0}
    batch_keys: set[str] = set()

    for raw_file in sorted(raw_dir.glob("*.json")):
        if raw_file.name.startswith("_"):
            continue
        raw = read_json(raw_file, {})
        if not raw.get("parse_ok"):
            continue
        sid = raw.get("source_id", raw_file.stem)
        src = by_id.get(sid, {})
        for entry in raw.get("items", []):
            stats["raw"] += 1
            url = canonical_url(entry.get("url") or "")
            if not url or not url.startswith("http"):
                stats["dropped_no_url"] += 1
                continue
            published = parse_when(entry.get("published_raw"))
            if published:
                dt = datetime.fromisoformat(published.replace("Z", "+00:00"))
                if dt < cutoff or dt > future:
                    stats["dropped_old"] += 1
                    continue
            key = item_id(url, entry.get("guid", ""))
            if key in batch_keys:
                stats["dropped_dup_in_batch"] += 1
                continue
            batch_keys.add(key)

            title = strip_html(entry.get("title"), 300) or url
            summary = strip_html(entry.get("summary"), 1200)
            category, tags, hit_rules = classify(title, summary,
                                                 src.get("category_hint", ""), taxonomy)
            prev = conn.execute("SELECT repeat_count FROM seen WHERE item_key=?", (key,)).fetchone()
            if prev:
                conn.execute("UPDATE seen SET repeat_count=repeat_count+1 WHERE item_key=?", (key,))
                repeat = prev[0] + 1
            else:
                conn.execute("INSERT INTO seen(item_key,first_seen,title,source_id) VALUES(?,?,?,?)",
                             (key, now.isoformat().replace("+00:00", "Z"), title[:200], sid))
                repeat = 1
                stats["new_to_seen"] += 1

            rows.append({
                "id": key,
                "source_id": sid,
                "source_name": src.get("name", sid),
                "source_tier": src.get("tier", "A"),
                "source_weight": src.get("weight", 1.0),
                "title": title,
                "url": url,
                "canonical_url": url,
                "guid": entry.get("guid", ""),
                "author": entry.get("author") or None,
                "published_at": published,
                "fetched_at": raw.get("fetched_at"),
                "lang": src.get("lang", "en"),
                "summary_raw": summary,
                "category": category,
                "category_hint": src.get("category_hint", ""),
                "tags": tags,
                "matched_rules": hit_rules,
                "metrics": entry.get("metrics", {}),
                "repeat_count": repeat,
                "tokens": sorted(tokenize(f"{title} {summary[:300]}"))[:120],
                "cluster_id": None,
                "score": None,
                "ai": None,
            })
            stats["kept"] += 1
    conn.commit()
    conn.close()

    out_file = out_dir / "items.jsonl"
    with out_file.open("w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    write_json(out_dir / "_summary.json", {"date": args.date, "window_hours": window,
                                          "window_from": cutoff.isoformat(), **stats,
                                          "by_category": _count(rows, "category"),
                                          "by_source": _count(rows, "source_id")})
    run_log("normalize", date=args.date, **stats)
    print(f"[{args.date}] 归一 {stats['raw']} → {stats['kept']} 条"
          f"（新增 {stats['new_to_seen']}，窗口外 {stats['dropped_old']}，重复 {stats['dropped_dup_in_batch']}）")
    return 0


def _count(rows: list[dict], key: str) -> dict:
    out: dict[str, int] = {}
    for r in rows:
        out[r[key]] = out.get(r[key], 0) + 1
    return dict(sorted(out.items(), key=lambda x: -x[1]))


if __name__ == "__main__":
    raise SystemExit(main())
