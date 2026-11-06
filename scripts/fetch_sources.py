#!/usr/bin/env python3
"""采集层：按 config/sources.json 并发抓取，落盘为可重放的原始快照。

分层约定：
  data/raw/<date>/<source-id>.json   每条含 raw items + 抓取元信息（不存大段原始 HTML）
  data/raw/<date>/payload/           仅 --save-payload 时保存原始响应，便于排障/复现
  data/state/http-cache.json         ETag / Last-Modified 条件请求缓存

失败策略：单源失败只记录并跳过，绝不中断整轮；失败率写入 run-log 供降级判定。
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timedelta, timezone
from pathlib import Path

from common import (DATA_DIR, add_date_arg, append_jsonl, day_dir, decode_payload,
                    load_config, now_utc, parse_feed, parse_html_items,
                    json_api_items, read_json, redact_credentials,
                    resolve_credentials, run_log, setup_logging, write_json, LOG)

# 同主机节流：gnews 恢复源 30+ 个都打 news.google.com，并发直上会触发整域限流。
# 按 defaults["min_interval_sec"] 在同主机串行排队（不同主机仍并发）。
_host_lock = threading.Lock()
_host_last: dict[str, float] = {}


def throttle_host(url: str, min_interval: float) -> None:
    host = urllib.parse.urlsplit(url).netloc.lower()
    if not host or min_interval <= 0:
        return
    while True:
        with _host_lock:
            now = time.monotonic()
            wait = _host_last.get(host, 0.0) + min_interval - now
            if wait <= 0:
                _host_last[host] = now
                return
        time.sleep(min(wait, 2.0))


def build_url(source: dict, date: str) -> str:
    url = source["url"]
    if "{since7d}" in url:
        # OpenAlex 等 API 只接受 YYYY-MM-DD，不能带时间部分
        d = (datetime.fromisoformat(date) - timedelta(days=7)).date().isoformat()
        url = url.replace("{since7d}", d)
    if "{symbol}" in url:
        url = url.replace("{symbol}", "AAPL")
    return url


def fetch_one(source: dict, args, defaults: dict, cache: dict) -> dict:
    sid = source["id"]
    # 凭据只从进程环境变量注入；落盘记录与缓存键都用带 ${VAR} 占位的原始 URL（脱敏）
    raw_url = source["url"]
    original = source
    resolved = resolve_credentials(source)
    url = build_url(resolved, args.date)

    def safe_error(text: str) -> str:
        # 异常文本可能带完整 URL（内含 mailto / token），写日志与落盘前必须还原成占位
        return redact_credentials(text, original)
    ua = defaults["user_agent"]
    cache_key = f"{sid}|{raw_url}"
    method = source.get("method", "GET").upper()
    headers = {"User-Agent": ua, "Accept": "*/*"}
    headers.update(resolved.get("headers") or {})
    post_body = None
    if method == "POST":
        post_body = json.dumps(resolved.get("body") or {}).encode("utf-8")
        headers.setdefault("Content-Type", "application/json")
    # 条件请求只对 GET 有意义；POST 型接口（智源社区 / Notion）每轮都要取最新
    if method == "GET" and cache.get(cache_key, {}).get("etag"):
        headers["If-None-Match"] = cache[cache_key]["etag"]
    if method == "GET" and cache.get(cache_key, {}).get("last_modified"):
        headers["If-Modified-Since"] = cache[cache_key]["last_modified"]

    record = {
        "source_id": sid, "source_name": source["name"], "tier": source["tier"],
        "kind": source["kind"], "url": raw_url, "fetched_at": now_utc().isoformat().replace("+00:00", "Z"),
        "category_hint": source.get("category_hint"), "weight": source.get("weight", 1.0),
        "items": [], "parse_ok": False, "error": None, "status": 0,
    }
    payload = None
    for attempt in range(1, defaults["retries"] + 2):
        try:
            throttle_host(url, defaults.get("min_interval_sec", 0))
            req = urllib.request.Request(url, data=post_body, headers=headers, method=method)
            with urllib.request.urlopen(req, timeout=defaults["timeout_sec"]) as r:
                record["status"] = r.status
                payload = decode_payload(r.read(4 * 1024 * 1024), r.headers)
                record["etag"] = r.headers.get("ETag")
                record["last_modified"] = r.headers.get("Last-Modified")
            break
        except urllib.error.HTTPError as exc:
            # 304 是条件请求的正常语义：复用上次快照，不算失败
            if exc.code == 304 and cache.get(cache_key, {}).get("last_file"):
                prior = read_json(Path(cache[cache_key]["last_file"]), {})
                if prior.get("items"):
                    record["items"] = prior["items"]
                    record["parse_ok"] = True
                    record["cache_hit"] = True
                    record["status"] = 304
                    record["item_count"] = len(record["items"])
                    return record
                # 快照已被清理 → 去掉条件头强制重新抓取
                headers.pop("If-None-Match", None)
                headers.pop("If-Modified-Since", None)
                cache.pop(cache_key, None)
                continue
            record["error"] = safe_error(f"{type(exc).__name__}: {exc}")[:200]
            record["status"] = exc.code
            if attempt <= defaults["retries"]:
                time.sleep(defaults["backoff_sec"] * attempt)
        except Exception as exc:  # noqa: BLE001
            record["error"] = safe_error(f"{type(exc).__name__}: {exc}")[:200]
            record["status"] = getattr(exc, "code", 0)
            if attempt <= defaults["retries"]:
                time.sleep(defaults["backoff_sec"] * attempt)
    if payload is None:
        LOG.warning("采集失败 %-28s %s", sid, record["error"])
        return record

    try:
        kind = source["kind"]
        if kind in ("rss", "atom", "git_atom"):
            record["items"] = parse_feed(payload)
        elif kind == "json_api":
            record["items"] = json_api_items(payload, source)
        elif kind == "html":
            record["items"] = parse_html_items(payload, source)
        else:
            raise ValueError(f"未知 kind: {kind}")
        record["parse_ok"] = True
        record["item_count"] = len(record["items"])
    except Exception as exc:  # noqa: BLE001 - 整源降级
        record["error"] = safe_error(f"parse failed: {type(exc).__name__}: {exc}")[:200]
        LOG.warning("解析失败 %-28s %s", sid, record["error"])

    if args.save_payload:
        pdir = day_dir("raw", args.date) / "payload"
        pdir.mkdir(parents=True, exist_ok=True)
        ext = "json" if source["kind"] == "json_api" else ("html" if source["kind"] == "html" else "xml")
        (pdir / f"{sid}.{ext}").write_bytes(payload)

    if record.get("etag") or record.get("last_modified"):
        cache[cache_key] = {"etag": record.get("etag"),
                            "last_modified": record.get("last_modified"),
                            "last_file": str(day_dir("raw", args.date) / f"{sid}.json")}
    return record


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--only", help="只抓指定源，逗号分隔，便于单源调试")
    ap.add_argument("--save-payload", action="store_true", help="保存原始响应体")
    ap.add_argument("--offline", action="store_true", help="不联网，仅汇总已有 raw 快照")
    args = ap.parse_args()
    setup_logging(args.verbose)

    cfg = load_config("sources.json")
    defaults = cfg["defaults"]
    raw_dir = day_dir("raw", args.date)
    cache_path = DATA_DIR / "state" / "http-cache.json"
    cache = read_json(cache_path, {}) or {}
    only = set(args.only.split(",")) if args.only else None
    # kind=cli 的源（如 Folo 基线）由专用采集器 fetch_folo.py 负责，不属 HTTP 抓取面
    enabled = [s for s in cfg["sources"]
               if s.get("enabled") and s["tier"] != "X" and s.get("kind") != "cli"
               and (not only or s["id"] in only)]

    if args.offline:
        records = [read_json(raw_dir / f"{s['id']}.json", {}) for s in enabled]
        records = [r for r in records if r]
    else:
        with concurrent.futures.ThreadPoolExecutor(max_workers=defaults["concurrency"]) as pool:
            records = list(pool.map(lambda s: fetch_one(s, args, defaults, cache), enabled))
        for r in records:
            write_json(raw_dir / f"{r['source_id']}.json", r)
        write_json(cache_path, cache)

    ok = [r for r in records if r.get("parse_ok")]
    failed = [r for r in records if not r.get("parse_ok")]
    summary = {
        "date": args.date, "fetched_at": now_utc().isoformat().replace("+00:00", "Z"),
        "enabled": len(enabled), "ok": len(ok), "failed": len(failed),
        "total_items": sum(len(r.get("items", [])) for r in ok),
        "failed_sources": [{"id": r["source_id"], "error": r.get("error")} for r in failed],
    }
    write_json(raw_dir / "_summary.json", summary)
    append_jsonl(DATA_DIR / "state" / "run-log.jsonl",
                 {"ts": summary["fetched_at"], "event": "fetch", **summary})
    print(f"[{args.date}] 采集 {summary['ok']}/{summary['enabled']} 源成功，"
          f"原始条目 {summary['total_items']} 条，失败 {summary['failed']} 源")
    for f in summary["failed_sources"]:
        print(f"  ! {f['id']}: {f['error']}")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
