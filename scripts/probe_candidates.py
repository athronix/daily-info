#!/usr/bin/env python3
"""候选信源批量体检：只有「HTTP 200 + 响应体是真 feed + 解析器能出条目」才判可接入。

与 check_sources.py 的分工：
  - check_sources.py   体检已登记的 config/sources.json；
  - probe_candidates.py 体检 config/candidates.json 里「尚未决定是否登记」的候选，
    额外跑一次 parse_feed / JSON 结构判定，区分「200 但不是 feed」「是 feed 但 0 条目」。

输出：
  reports/candidate-probe-<date>.json  机器可读，供后续脚本消费
  reports/candidate-probe-<date>.md    人工复核表（可用 / 不可用 分列）

纪律：未通过体检的 URL 禁止直接写进 sources.json 并启用；被拒原因必须留在报告里。
零第三方依赖。
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from common import CONFIG_DIR, ROOT, add_date_arg, parse_feed, setup_logging


def probe(c: dict, timeout: int, ua: str) -> dict:
    rec = dict(c)
    url = c["url"]
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua, "Accept": "*/*"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            body = r.read(2 * 1024 * 1024)
            rec.update(
                status=r.status,
                content_type=(r.headers.get("Content-Type") or "").split(";")[0],
                final_url=r.geturl(),
                bytes=len(body),
            )
            head = body.lstrip()[:200].decode("utf-8", "replace").lower()
            looks = head.startswith(("<?xml", "<rss", "<feed", "<rdf:", "{", "["))
            rec["looks_like_feed"] = looks
            if c.get("kind") in ("rss", "atom", "git_atom"):
                if not looks:
                    rec["ok"] = False
                    rec["reason"] = "声明为 feed 但响应体不是 XML/JSON"
                else:
                    try:
                        items = parse_feed(body)
                        rec["parsed_items"] = len(items)
                        if items:
                            rec["sample_title"] = (items[0].get("title") or "")[:90]
                            rec["sample_date"] = (items[0].get("published_raw") or "")[:40]
                        rec["ok"] = len(items) > 0
                        if not items:
                            rec["reason"] = "XML 合法但解析出 0 条目"
                    except Exception as exc:  # noqa: BLE001
                        rec["ok"] = False
                        rec["reason"] = f"parse_feed 失败: {type(exc).__name__}: {exc}"[:150]
            elif c.get("kind") == "json_api":
                if not looks:
                    rec["ok"] = False
                    rec["reason"] = "声明为 JSON API 但响应体不是 JSON"
                else:
                    try:
                        data = json.loads(body.decode("utf-8", "replace"))
                        if isinstance(data, list):
                            n = len(data)
                        elif isinstance(data, dict):
                            n = len(next((data[k] for k in ("items", "results", "hits", "data")
                                          if isinstance(data.get(k), list)), []))
                        else:
                            n = 0
                        rec["parsed_items"] = n
                        rec["ok"] = n > 0
                        if not n:
                            rec["reason"] = "JSON 合法但没有列表字段"
                    except Exception as exc:  # noqa: BLE001
                        rec["ok"] = False
                        rec["reason"] = f"JSON 解析失败: {exc}"[:150]
            else:
                rec["ok"] = False
                rec["reason"] = f"未知 kind: {c.get('kind')}"
    except urllib.error.HTTPError as exc:
        rec.update(ok=False, status=exc.code, reason=f"HTTP {exc.code}")
    except Exception as exc:  # noqa: BLE001
        rec.update(ok=False, status=0, reason=f"{type(exc).__name__}: {exc}"[:150])
    rec.setdefault("ok", False)
    rec.setdefault("reason", "")
    return rec


def render_markdown(results: list[dict], date: str) -> str:
    ok = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]
    lines = [
        f"# 候选信源体检报告 · {date}", "",
        f"- 候选总数：{len(results)}",
        f"- **可用（可登记）**：{len(ok)}",
        f"- 不可用：{len(bad)}",
        f"- 生成时间：{datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z')}",
        "- 判定标准：HTTP 200 + 响应体为 XML/JSON + 解析器产出 >= 1 条目",
        "", "## 一、可用候选（建议登记进 sources.json）", "",
        "| id | 名称 | 分类 | 条目数 | 状态 | 来源 | 样例标题 |",
        "| --- | --- | --- | ---: | --- | --- | --- |",
    ]
    for r in sorted(ok, key=lambda x: (x.get("cat", ""), x["id"])):
        lines.append(
            f"| `{r['id']}` | {r['name']} | {r.get('cat','-')} | {r.get('parsed_items','-')} | "
            f"{r.get('status','-')} | {r.get('from','-')} | {(r.get('sample_title') or '').replace('|','/')[:60]} |"
        )
    lines += ["", "## 二、不可用候选（留证据，勿反复重试）", "",
              "| id | URL | 状态 | 原因 |", "| --- | --- | --- | --- |"]
    for r in sorted(bad, key=lambda x: x["id"]):
        lines.append(f"| `{r['id']}` | {r['url'][:78]} | {r.get('status','-')} | "
                     f"{(r.get('reason') or '').replace('|','/')[:110]} |")
    lines += ["", "## 三、按分类统计可用源", "", "| 分类 | 可用数 |", "| --- | ---: |"]
    by_cat: dict[str, int] = {}
    for r in ok:
        by_cat[r.get("cat", "-")] = by_cat.get(r.get("cat", "-"), 0) + 1
    for k, v in sorted(by_cat.items(), key=lambda x: -x[1]):
        lines.append(f"| {k} | {v} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--timeout", type=int, default=15)
    ap.add_argument("--concurrency", type=int, default=16)
    ap.add_argument("--only", help="只测指定 id，逗号分隔")
    ap.add_argument("--candidates", default=str(CONFIG_DIR / "candidates.json"))
    args = ap.parse_args()
    setup_logging(args.verbose)

    data = json.loads(Path(args.candidates).read_text(encoding="utf-8"))
    candidates = data["candidates"] if isinstance(data, dict) else data
    if args.only:
        keep = set(args.only.split(","))
        candidates = [c for c in candidates if c["id"] in keep]
    cfg_ua = "Mozilla/5.0 (compatible; PersonalDailyInfo/1.0; +local)"
    ua = cfg_ua

    with concurrent.futures.ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        results = list(pool.map(lambda c: probe(c, args.timeout, ua), candidates))

    report_dir = ROOT / "reports"
    report_dir.mkdir(parents=True, exist_ok=True)
    (report_dir / f"candidate-probe-{args.date}.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
    (report_dir / f"candidate-probe-{args.date}.md").write_text(
        render_markdown(results, args.date), encoding="utf-8")

    ok = sum(1 for r in results if r["ok"])
    print(f"候选体检完成：{ok}/{len(results)} 可用 → reports/candidate-probe-{args.date}.md")
    for r in results:
        if r["ok"]:
            print(f"  + {r['id']:<32} {r.get('parsed_items',0):>4} 条  {r.get('sample_title','')[:48]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
