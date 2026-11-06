#!/usr/bin/env python3
"""P1 · 站点本地端到端验收（IPv6 ::1 回环，只读，不启动常驻服务）。

对应 docs/11 §P1 验收标准：「站点首屏、日期切换、搜索、5 个 Atom 链接全部可用」。
用一次性本地 HTTP 服务实发 HTTP 请求（不是只读文件），验证：

  /                         200 + HTML 首屏骨架
  /data/index.json          200 + dates / feeds 字段
  /data/latest.json         200 + date 与业务日期一致
  /data/<date>.json         200 + date 一致
  /feed.atom / /all.atom    200 + XML 可解析 + entry > 0
  5 个 profile Atom         200 + XML 可解析 + entry id 唯一
  /feed.json                200 + JSON Feed items > 0
  前端能力（静态源码检查）  #q 搜索框 / input 监听 / dates 切换 / state.q 过滤
                          日期 + 分类双维导航 / 默认最新日期 / 订阅引导面板（不直跳 .atom）

网络约定：绑定 IPv6 `::1`，urllib 显式禁用代理（ProxyHandler({})），
规避本机 TUN 对 IPv4 127.0.0.1 裸 TCP 的拦截（见 pitfalls P17 与用户环境约定）。
`.atom` 的 Content-Type 由 python http.server 返回 application/octet-stream，
属已知 P17 事项，记录为 WARN 不判 FAIL；上线时需配 application/atom+xml。

  python scripts/check_release.py --date 2026-11-05
报告：reports/release-check-<date>.md
"""
from __future__ import annotations

import argparse
import json
import re
import socket
import sys
import threading
import urllib.request
import xml.etree.ElementTree as ET
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (PUBLIC_DIR, ROOT, add_date_arg, run_log, setup_logging, LOG)

REPORT_DIR = ROOT / "reports"
NS = "{http://www.w3.org/2005/Atom}"


class V6Server(ThreadingHTTPServer):
    address_family = socket.AF_INET6
    daemon_threads = True
    allow_reuse_address = True


class QuietHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(PUBLIC_DIR), **kwargs)

    def log_message(self, fmt, *args):
        pass


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    args = ap.parse_args()
    setup_logging(args.verbose)
    date = args.date

    server = V6Server(("::1", 0), QuietHandler)
    port = server.server_address[1]
    th = threading.Thread(target=server.serve_forever, daemon=True)
    th.start()
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    base = f"http://[::1]:{port}"

    results: list[dict] = []

    def get(path: str):
        with opener.open(base + path, timeout=5) as r:
            return r.status, r.headers.get("Content-Type", ""), r.read()

    def rec(name: str, ok: bool, detail: str, level: str = "CHECK") -> None:
        results.append({"name": name, "ok": ok, "level": level, "detail": detail})

    try:
        # 首屏
        code, ctype, body = get("/")
        html_text = body.decode("utf-8", errors="replace")
        rec("首屏 /", code == 200 and "<html" in html_text.lower() and "app" in html_text,
            f"status={code} type={ctype} bytes={len(body)}")
        # 前端能力（静态源码检查，无浏览器时验证实现存在）
        for label, needle in [("搜索框 #q", 'id="q"'),
                              ("搜索 input 监听", "addEventListener('input'"),
                              ("搜索过滤 state.q", "state.q"),
                              ("日期切换 dates", "state.index.dates"),
                              ("读取 index.json", "data/index.json"),
                              ("按日期加载切片", "data/'+date+'.json'"),
                              ("日期导航 #days", 'id="days"'),
                              ("分类导航 #cats", 'id="cats"'),
                              ("分类筛选 state.cat", "state.cat"),
                              ("默认打开最新日期", "idx.dates[0].date"),
                              ("双维度 URL hash", "writeHash"),
                              ("订阅引导面板", 'id="sub-modal"'),
                              ("订阅按钮是 button", 'id="subscribe" type="button"'),
                              ("订阅地址绝对化", "new URL(u,location.href)"),
                              ("一键复制订阅地址", 'class="copy"')]:
            rec(f"前端能力 · {label}", needle in html_text, f"源码含 {needle!r}")
        rec("前端能力 · 订阅入口不再直跳 .atom",
            not re.search(r'<a[^>]*class="btn"[^>]*href="feed\.atom"', html_text),
            "顶栏无 <a class=btn href=feed.atom> 直链")
        rec("前端能力 · 保留阅读器自动发现",
            'rel="alternate" type="application/atom+xml"' in html_text,
            "head 内 rel=alternate 仍在")

        # 索引与切片
        code, _, body = get("/data/index.json")
        idx = json.loads(body)
        dates = idx.get("dates", [])
        rec("/data/index.json", code == 200 and len(dates) > 0 and len(idx.get("feeds", [])) >= 5,
            f"status={code} dates={len(dates)} feeds={len(idx.get('feeds', []))}")
        rec("索引含当日", any(x.get("date") == date for x in dates),
            f"dates={[x.get('date') for x in dates][:5]}")
        code, _, body = get("/data/latest.json")
        latest = json.loads(body)
        rec("/data/latest.json", code == 200 and latest.get("date") == date,
            f"status={code} date={latest.get('date')}")
        code, _, body = get(f"/data/{date}.json")
        day = json.loads(body)
        rec(f"/data/{date}.json", code == 200 and day.get("date") == date,
            f"status={code} date={day.get('date')} sections={len(day.get('sections', []))}")

        # Atom：主入口 + 5 个 profile
        atom_paths = ["/feed.atom", "/all.atom", "/high-signal.atom",
                      "/tech.atom", "/invest.atom", "/docs.atom"]
        for path in atom_paths:
            code, ctype, body = get(path)
            try:
                root = ET.fromstring(body)
                eids = [e.text for e in root.findall(f"{NS}entry/{NS}id")]
                ok = code == 200 and len(eids) == len(set(eids))
                if path in ("/feed.atom", "/all.atom"):
                    ok = ok and len(eids) > 0
                detail = f"status={code} entries={len(eids)} unique={len(set(eids))} type={ctype}"
            except ET.ParseError as ex:
                ok, detail = False, f"status={code} XML 解析失败：{ex}"
            rec(path, ok, detail)
            if "xml" not in ctype.lower():
                rec(f"{path} MIME（P17 已知事项）", True,
                    f"本地 http.server 返回 {ctype}；上线时需配 application/atom+xml", level="WARN")

        # JSON Feed
        code, _, body = get("/feed.json")
        feed = json.loads(body)
        rec("/feed.json", code == 200 and len(feed.get("items", [])) > 0,
            f"status={code} items={len(feed.get('items', []))} version={feed.get('version')}")
    except Exception as ex:  # noqa: BLE001 - 端到端检查要如实报告任何异常
        rec("端到端请求", False, f"{type(ex).__name__}: {ex}")
    finally:
        server.shutdown()
        server.server_close()
        th.join(timeout=3)

    checks = [r for r in results if r["level"] == "CHECK"]
    warns = [r for r in results if r["level"] == "WARN"]
    failed = [r for r in checks if not r["ok"]]
    lines = [f"# 站点端到端验收 · {date}", "",
             f"绑定 `http://[::1]:{port}`（IPv6 回环 + 禁用代理），共 {len(checks)} 项检查，"
             f"通过 {len(checks) - len(failed)}，失败 {len(failed)}，提示 {len(warns)}。", "",
             "| 检查 | 结论 | 明细 |", "| --- | --- | --- |"]
    for r in checks:
        lines.append(f"| {r['name']} | {'PASS' if r['ok'] else 'FAIL'} | {r['detail']} |")
    if warns:
        lines += ["", "## 已知事项（不判失败）", ""]
        for r in warns:
            lines.append(f"- {r['name']}：{r['detail']}")
    lines += ["", "> 本检查只验证本地静态站可访问与数据切片自洽，不代表站点已上线、"
              "也不代表外部事实已核实。上线动作需用户授权后执行。"]
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    (REPORT_DIR / f"release-check-{date}.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    run_log("check_release", date=date, checks=len(checks), failed=len(failed), warns=len(warns))
    LOG.info("站点端到端：%d/%d 通过，失败 %d，提示 %d → reports/release-check-%s.md",
             len(checks) - len(failed), len(checks), len(failed), len(warns), date)
    print(f"站点端到端：{len(checks) - len(failed)}/{len(checks)} 通过，violations={len(failed)}")
    for r in failed:
        print("  FAIL", r["name"], r["detail"])
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
