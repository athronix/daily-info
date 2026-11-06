"""失败源三路链路恢复探测：从被拒源里挖可用替代通道。

背景（2026-11-05）：归档表里 78 个源检测未通过（探测被拒 49 + Tier X 失效留证 24 +
暂禁用 5）。其中很多**内容真实存在、只是没有官方 RSS**（如 ai.meta.com/blog）。
本脚本对每个失败源并测三条替代链路，实测「200 + 响应体是 feed + 能解析出条目」才算恢复成功：

  A. Google News RSS `site:<domain>` 查询 —— 通用兜底路由（实测对任意思想家域名有效）；
  B. RSSHub 公共镜像路由 —— rsshub.app 主站 403，镜像 rssforever.com 实测可用；
  C. HTML 列表页启发式解析 —— 直连博客列表页抠 <a>+日期（部分站有边缘/反爬）。

产出 reports/recover-probe-<date>.json + .md；不修改任何配置（登记由人工/后续脚本决定）。
"""
from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import time
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ROOT, add_date_arg, decode_payload, load_config, parse_feed,
                    setup_logging, write_json, LOG)  # noqa: E402

UA = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                    "(KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
      "Accept": "application/rss+xml,application/atom+xml,application/xml,text/xml,"
                "application/json,text/html;q=0.9,*/*;q=0.5"}

# RSSHub 公共实例（主站 403 已实测，镜像按可用性排序逐个回退）
RSSHUB_BASES = [
    "https://rsshub.rssforever.com",
    "https://rsshub.pseudoyu.com",
    "https://rsshub.ktachibana.party",
]

# 已知质量高、值得试 RSSHub 官方路由的失败源（路由表来自 RSSHub docs）
RSSHUB_ROUTES = {
    "meta-ai-blog-rss": "/meta/ai/blog",
    "36kr-feed": "/36kr/newsflashes",
    "36kr-newsflash": "/36kr/newsflashes",
    "jiqizhixin-rss": "/jiqizhixin",
    "linuxfoundation": "/linuxfoundation/blog",
    "infoq-cn-feed": "/infoq.cn/recommend",
    "trendhunter-rss": None,  # 无官方路由，只走 gnews
    "gizmodo": "/gizmodo",
    "coolhunting": None,
    "uncrate": None,
    "semianalysis": None,
    "schneier": "/schneier/blog",
    "bleepingcomputer": None,
    "securityweek": None,
    "spacenews": None,
    "restofworld": "/restofworld",
    "thegradient": "/thegradient",
    "the-gradient": "/thegradient",
    "qwen-blog": None,
    "xai-news": None,
    "deepseek-news": None,
    "pedaily": "/pedaily/fe/news",
    "zhitongcaijing": None,
    "tech-eu": None,
    "indiehackers-feed": None,
    "theregister": None,
}


def domain_of(url: str) -> str:
    m = re.match(r"https?://([^/]+)", url)
    host = (m.group(1) if m else "").lower()
    for pfx in ("www.", "m."):
        if host.startswith(pfx):
            host = host[len(pfx):]
    return host


def fetch(url: str, timeout: int = 22) -> tuple[int, str, bytes]:
    try:
        r = urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout)
        body = decode_payload(r.read(2 * 1024 * 1024), r.headers)
        return r.status, r.headers.get("Content-Type", ""), body
    except urllib.error.HTTPError as e:
        return e.code, "", b""
    except Exception as e:  # noqa: BLE001
        return 0, f"{type(e).__name__}:{str(e)[:60]}", b""


def try_feed(url: str, label: str) -> dict | None:
    st, ct, body = fetch(url)
    if st != 200 or not body:
        return {"route": label, "url": url, "ok": False, "status": st, "reason": ct or f"HTTP {st}"}
    try:
        items = parse_feed(body)
    except Exception as e:  # noqa: BLE001
        return {"route": label, "url": url, "ok": False, "status": 200,
                "reason": f"parse failed: {type(e).__name__}"}
    if not items:
        return {"route": label, "url": url, "ok": False, "status": 200, "reason": "0 条目"}
    return {"route": label, "url": url, "ok": True, "status": 200,
            "content_type": ct[:60], "items": len(items),
            "sample_title": (items[0].get("title") or "")[:90],
            "sample_date": items[0].get("published_raw") or items[0].get("published") or ""}


def gnews_route(url: str, zh: bool) -> str:
    dom = domain_of(url)
    lang = "hl=zh-CN&gl=CN&ceid=CN:zh-Hans" if zh else "hl=en-US&gl=US&ceid=US:en"
    q = urllib.parse.quote(f"site:{dom}")
    return f"https://news.google.com/rss/search?q={q}&{lang}"


def try_html_list(url: str) -> dict | None:
    """启发式：列表页中带日期的文章链接（title>25 字符且 href 同域）。"""
    st, ct, body = fetch(url)
    if st != 200 or b"<" not in body[:200]:
        return None
    html = body.decode("utf-8", "replace")
    dom = domain_of(url)
    pat = re.compile(
        r'<a[^>]+href="([^"]+)"[^>]*>([^<]{25,160})</a>', re.I)
    date_pat = re.compile(r"(20\d{2})[-/](\d{1,2})[-/](\d{1,2})|"
                          r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)", re.I)
    hits = []
    for href, title in pat.findall(html):
        if href.startswith("/") or dom.split("/")[0] in href:
            full = urllib.parse.urljoin(url, href)
            if re.search(r"\.(css|js|png|jpg|svg|ico)", full):
                continue
            if date_pat.search(html[max(0, html.find(title) - 400):html.find(title) + 400]):
                hits.append({"url": full, "title": " ".join(title.split())[:120]})
        if len(hits) >= 25:
            break
    if len(hits) < 5:
        return {"route": "html_list", "url": url, "ok": False, "status": st,
                "reason": f"启发式仅 {len(hits)} 条"}
    return {"route": "html_list", "url": url, "ok": True, "status": st,
            "items": len(hits), "sample_title": hits[0]["title"],
            "sample_url": hits[0]["url"]}


def recover_one(f: dict) -> dict:
    out = {"id": f["id"], "name": f["name"], "orig_url": f["url"],
           "orig_reason": f.get("reason", ""), "category": f.get("category", ""),
           "attempts": []}
    zh = bool(re.search(r"(cn|com\.cn|tw|hk|jiqizhixin|36kr|pedaily|zhitongcaijing|sciencenet|technode|tmtpost|oschina)", f["url"]))
    # 路由 B：RSSHub 已知路由（先镜像后主站）
    route = RSSHUB_ROUTES.get(f["id"])
    if route:
        for base in RSSHUB_BASES:
            r = try_feed(base + route, f"rsshub:{route}")
            out["attempts"].append(r)
            if r and r.get("ok"):
                break
    # 路由 A：Google News site:（几乎通用）
    if not any(a.get("ok") for a in out["attempts"]):
        r = try_feed(gnews_route(f["url"], zh), "gnews_site")
        out["attempts"].append(r)
    # 路由 C：HTML 列表页（gnews 也没中才试，省流量）
    if not any(a.get("ok") for a in out["attempts"]) and f.get("html", True):
        r = try_html_list(f["url"])
        if r:
            out["attempts"].append(r)
    good = [a for a in out["attempts"] if a.get("ok")]
    out["recovered"] = bool(good)
    out["best"] = good[0] if good else None
    return out


def collect_failed(date: str) -> list[dict]:
    srcs = load_config("sources.json")["sources"]
    by_id = {s["id"]: s for s in srcs}
    items: list[dict] = []
    seen: set[str] = set()

    probe_p = ROOT / "reports" / f"candidate-probe-{date}.json"
    if probe_p.is_file():
        for p in json.loads(probe_p.read_text(encoding="utf-8")):
            if not p.get("ok") and p["id"] not in seen:
                seen.add(p["id"])
                items.append({"id": p["id"], "name": p["name"], "url": p["url"],
                              "reason": p.get("reason", "")[:60],
                              "category": p.get("cat", "")})
    for s in srcs:
        if s["id"] in seen:
            continue
        if s["tier"] == "X" or not s.get("enabled"):
            seen.add(s["id"])
            items.append({"id": s["id"], "name": s["name"], "url": s["url"],
                          "reason": (s.get("note") or "")[:60],
                          "category": s.get("category_hint", "")})
    return items


def main() -> int:
    ap = argparse.ArgumentParser(description="失败源三路链路恢复探测")
    add_date_arg(ap)
    ap.add_argument("--concurrency", type=int, default=4, help="并发（gnews 有配额，默认 4）")
    ap.add_argument("--limit", type=int, default=0, help="调试用：只测前 N 个")
    args = ap.parse_args()
    setup_logging(args.verbose)

    failed = collect_failed(args.date)
    if args.limit:
        failed = failed[:args.limit]
    LOG.info("待恢复探测：%d 个失败源", len(failed))

    results = []
    with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
        for i, r in enumerate(ex.map(recover_one, failed), 1):
            results.append(r)
            mark = "✅" if r["recovered"] else "  "
            LOG.info("[%02d/%02d] %s %-26s %s", i, len(failed), mark, r["id"],
                     (r["best"] or {}).get("route", "—") + f" {str((r['best'] or {}).get('items', 0)) if r['recovered'] else '未恢复'}"
                     if r["recovered"] else "未恢复")
            time.sleep(0.3)

    rec = [r for r in results if r["recovered"]]
    out_json = ROOT / "reports" / f"recover-probe-{args.date}.json"
    write_json(out_json, results)

    lines = [f"# 失败源链路恢复探测 · {args.date}", "",
             f"- 待恢复：{len(results)} 个（探测被拒 + Tier X + 暂禁用）",
             f"- **恢复成功：{len(rec)}**（{len(rec) * 100 // max(len(results), 1)}%）",
             f"- 仍不可用：{len(results) - len(rec)}", "",
             "## 恢复成功清单", ""]
    for r in sorted(rec, key=lambda v: v["category"]):
        b = r["best"]
        lines.append(f"| {r['name']} | {b['route']} | {b['url'][:88]} | "
                     f"{b.get('items', '?')} 条 | {b.get('sample_title', '')[:44]} |")
    lines += ["", "## 仍不可用清单", "",
              "| 源 | 原 URL | 原失败原因 | 尝试过的替代路由 |", "|---|---|---|---|"]
    for r in results:
        if r["recovered"]:
            continue
        tries = "; ".join(f"{a['route']}:{a.get('status')}/{str(a.get('reason', ''))[:30]}"
                          for a in r["attempts"]) or "无可试路由"
        lines.append(f"| {r['name']} | {r['orig_url'][:60]} | {r['orig_reason'][:36]} | {tries[:110]} |")
    out_md = ROOT / "reports" / f"recover-probe-{args.date}.md"
    out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"recovered {len(rec)}/{len(results)} → {out_md}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
