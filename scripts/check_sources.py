#!/usr/bin/env python3
"""信源体检：并发探测每个源的 HTTP 状态 / Content-Type / 是否真为 feed 内容。

用途：
  1. 每周「信源体检」定时任务调用，输出 reports/source-health-YYYY-MM-DD.md；
  2. --update 把实测健康状态回写 config/sources.json；
  3. 采集前快速过滤已失效源，避免把 404/HTML 当 feed 解析。

实测背景（2026-11-04）：参考仓库 daily-rss README 里的 github-trends-atom 已 404，
LangChain Blog RSS 已 302 到 HTML，anthropic.com/rss.xml 不存在，VentureBeat 返回 429。
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from common import (CONFIG_DIR, ROOT, add_date_arg, decode_payload, load_config,
                    redact_credentials, resolve_credentials, setup_logging, write_json)


def probe(source: dict, timeout: int, ua: str) -> dict:
    # 体检同样走凭据解析：未设置 ${VAR} 的 header 会被丢弃，回退匿名探测
    raw_url = source["url"]
    original = source
    source = resolve_credentials(source)

    def safe(text: str) -> str:
        return redact_credentials(text, original)

    url = source["url"]
    result = {"id": source["id"], "name": source["name"], "url": raw_url,
              "tier": source["tier"], "enabled": source.get("enabled", False)}
    # kind=cli 的源（Folo 基线）无 HTTP 端点可探，改看最近一次 fetch_folo 产物
    if source.get("kind") == "cli":
        from common import DATA_DIR, read_json
        for dd in sorted((DATA_DIR / "raw").glob("*/folo-timeline.json"), reverse=True):
            rec = read_json(dd, {})
            if rec.get("parse_ok"):
                result.update(status=200, content_type="application/json (CLI)",
                              ok=True, looks_like_feed=True,
                              note=f"最近成功采集 {dd.parent.name}：{rec.get('item_count', 0)} 条")
                return result
            result.update(status=0, ok=False,
                          reason=(rec.get("error") or "CLI 无成功采集记录")[:120])
            return result
        result.update(status=0, ok=False, reason="尚无采集记录（等待 FOLO_TOKEN 登录）")
        return result
    if "{since7d}" in url:
        from datetime import timedelta
        d = (datetime.now(timezone.utc) - timedelta(days=7)).date().isoformat()
        url = url.replace("{since7d}", d)
    if "{symbol}" in url:
        url = url.replace("{symbol}", "AAPL")
    try:
        method = source.get("method", "GET").upper()
        hdr = {"User-Agent": ua, "Accept": "*/*"}
        hdr.update(source.get("headers") or {})
        body = None
        if method == "POST":
            body = json.dumps(source.get("body") or {}).encode("utf-8")
            hdr.setdefault("Content-Type", "application/json")
        req = urllib.request.Request(url, data=body, headers=hdr, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = decode_payload(r.read(262144), r.headers)
            ctype = r.headers.get("Content-Type", "")
            result.update(status=r.status, content_type=ctype, final_url=safe(r.geturl()),
                          bytes_sample=len(body), ok=True)
            head = body.lstrip()[:200].decode("utf-8", "replace").lower()
            result["looks_like_feed"] = head.startswith(("<?xml", "<rss", "<feed", "<rdf:", "{", "["))
            if source["kind"] in ("rss", "atom", "git_atom") and not result["looks_like_feed"]:
                result["ok"] = False
                result["reason"] = f"声明为 {source['kind']} 但响应体不像 XML/JSON feed"
    except Exception as exc:  # noqa: BLE001 - 体检需吞掉所有网络异常
        result.update(ok=False, status=getattr(exc, "code", 0),
                      reason=f"{type(exc).__name__}: {exc}"[:160])
    return result


def render_markdown(results: list[dict], date: str) -> str:
    ok = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]
    lines = [
        f"# 信源健康报告 · {date}", "",
        f"- 探测总数：{len(results)}",
        f"- 正常：{len(ok)}",
        f"- 异常/禁用：{len(bad)}",
        f"- 生成时间：{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}",
        "", "## 异常明细", "",
        "| 源 | 状态 | 类型 | 原因 |", "| --- | --- | --- | --- |",
    ]
    for r in bad:
        lines.append(f"| {r['id']} | {r.get('status', '-')} | {r.get('content_type', '-')[:24]} | "
                     f"{r.get('reason', r.get('note', 'disabled'))} |")
    lines += ["", "## 全部探测结果", "", "| 源 | Tier | 状态 | Content-Type | Feed? |",
              "| --- | --- | --- | --- | --- |"]
    for r in sorted(results, key=lambda x: (x["tier"], x["id"])):
        lines.append(f"| {r['id']} | {r['tier']} | {r.get('status', '-')} | "
                     f"{r.get('content_type', '-')[:30]} | {'Y' if r.get('looks_like_feed') else 'N'} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--update", action="store_true", help="把实测健康状态回写 sources.json")
    ap.add_argument("--timeout", type=int, default=20)
    ap.add_argument("--concurrency", type=int, default=10)
    args = ap.parse_args()
    setup_logging(args.verbose)

    cfg = load_config("sources.json")
    ua = cfg["defaults"]["user_agent"]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        results = list(pool.map(lambda s: probe(s, args.timeout, ua), cfg["sources"]))

    report_dir = ROOT / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / f"source-health-{args.date}.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (report_dir / f"source-health-{args.date}.md").write_text(
        render_markdown(results, args.date), encoding="utf-8")
    ok = sum(1 for r in results if r["ok"])
    print(f"信源体检完成：{ok}/{len(results)} 正常 → reports/source-health-{args.date}.md")

    if args.update:
        by_id = {r["id"]: r for r in results}
        for s in cfg["sources"]:
            r = by_id.get(s["id"])
            if not r:
                continue
            s.setdefault("health", {})["checked_at"] = args.date
            s["health"]["status"] = r.get("status", 0)
            if r.get("content_type"):
                s["health"]["content_type"] = r["content_type"].split(";")[0]
            if r.get("final_url") and r["final_url"] != s["url"]:
                s["health"]["redirect_to"] = r["final_url"]
        if write_json(CONFIG_DIR / "sources.json", cfg):
            print("已回写 config/sources.json 的 health 字段")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
