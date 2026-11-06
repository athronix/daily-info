#!/usr/bin/env python3
"""Folo 基线采集器：把用户人工筛选的 Folo 订阅池拉进 data/raw/<date>/。

定位（2026-11-05）：Folo 是 RSS 阅读器的 Agent 化入口（官方 skill：https://api.folo.is/skill.md）。
与自动抓取源的差异是**信噪比**——池子里每一条都是用户亲手订阅的，作为日报的「基线层」：
同题竞争时优先采信 Folo 版（已在人看的信息），自动源做增量发现。

链路：npx --yes folocli@latest timeline --limit 100 [--cursor …] 翻页，
响应为官方稳定信封 {ok, data:{entries, nextCursor, hasNext}}（输出契约见 skill.md）。
认证：FOLO_TOKEN 从 ~/.workbuddy/.env 经 common.load_dotenv 注入子进程环境；
无 token 时 CLI 返回 UNAUTHORIZED —— 本脚本据此**软失败**（整源降级，不阻断日报）。

字段解析取宽容模式（title/url/summary/feed 多种命名尝试），真实 payload 同批落盘
payload/folo-timeline.json 供首次登录后校准。不做任何写操作（不标已读、不改订阅），
只读采集符合「外部账号最小侵入」原则。
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (DATA_DIR, add_date_arg, append_jsonl, day_dir, load_dotenv,
                    now_utc, redact_credentials, run_log, setup_logging,
                    write_json, LOG)  # noqa: E402

CLI = ["npx", "--yes", "folocli@latest"]
SOURCE_ID = "folo-timeline"
MAX_PAGES = 5  # 5×100 条上限，一天一次的量足够


def run_cli(args: list[str], timeout: int = 90) -> dict:
    """执行 folocli，返回解析后的信封 JSON。

    npx 会在 stdout/stderr 掺 `npm notice` 噪音（实测在 JSON *之后* 也有一段），
    因此不能用「尾部 JSON」正则；改为从第一个 `{` 起 raw_decode 取首个完整对象。
    """
    env = dict(os.environ)
    env["NO_PROXY"] = env.get("NO_PROXY", "") + ",localhost,127.0.0.1"
    cmd = CLI + args + ["--format", "json"]
    # Windows：npx 是 .cmd 垫片，CreateProcess 直接 exec 会 WinError 2；首元素换成 npx.cmd
    if os.name == "nt" and cmd[0] == "npx":
        cmd = ["npx.cmd"] + cmd[1:]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                          timeout=timeout, env=env, shell=False)
    decoder = json.JSONDecoder()
    for stream in (proc.stdout or "", proc.stderr or ""):
        idx = stream.find("{")
        while idx != -1:
            try:
                obj, _ = decoder.raw_decode(stream[idx:])
                if isinstance(obj, dict) and "ok" in obj:
                    return obj
            except json.JSONDecodeError:
                pass
            idx = stream.find("{", idx + 1)
    raise RuntimeError(f"CLI 无 JSON 信封 rc={proc.returncode}: "
                       f"{((proc.stdout or '') + (proc.stderr or ''))[-200:]!r}")


# Folo timeline 行结构（2026-11-05 实测校准）：每行是
#   {read, view, aiScore, from[], entries:{条目对象}, feeds:{feed对象},
#    subscriptions:{category,title}, settings}
# view：0=Articles 1=Social 2=Pictures 3=Videos 4=Audios 5=Notifications
ARTICLE_VIEW = 0
FOLLOWED_VIEWS = {ARTICLE_VIEW}  # 基线层只要文章，图片/视频噪音丢弃


def entry_to_item(row: dict) -> dict | None:
    """把一行 timeline 记录映射为内部 Item；非文章 view 或缺题缺链返回 None。"""
    if row.get("view") not in FOLLOWED_VIEWS:
        return None
    e = row.get("entries")
    if isinstance(e, list):  # 防御：万一信封形态变化
        e = e[0] if e else {}
    if not isinstance(e, dict):
        return None
    title = (e.get("title") or "").strip()
    url = (e.get("url") or "").strip()
    if not title or not url.startswith("http"):
        return None
    summary = (e.get("summary") or e.get("description") or "").strip()
    summary = re.sub(r"<[^>]+>", " ", summary)
    feed = row.get("feeds") or {}
    author = (e.get("author") or feed.get("title") or "Folo").strip()
    category = (row.get("subscriptions") or {}).get("category") or ""
    ai_score = row.get("aiScore")
    return {"guid": e.get("id") or e.get("guid") or url,
            "title": title[:300], "url": url,
            "summary": (summary + (f" 〔Folo分类:{category}〕" if category else ""))[:800],
            "published_raw": e.get("publishedAt") or e.get("insertedAt") or "",
            "author": author,
            "metrics": {"folo_category": category, "folo_ai_score": ai_score,
                        "folo_read": row.get("read", False)}}


def main() -> int:
    ap = argparse.ArgumentParser(description="Folo 基线采集（只读 timeline）")
    add_date_arg(ap)
    ap.add_argument("--max-pages", type=int, default=MAX_PAGES)
    args = ap.parse_args()
    setup_logging(args.verbose)

    load_dotenv()
    record = {"source_id": SOURCE_ID, "source_name": "Folo 订阅池基线", "tier": "A",
              "kind": "cli", "url": "folocli timeline (api.folo.is)",
              "fetched_at": now_utc().isoformat().replace("+00:00", "Z"),
              "category_hint": None, "weight": 1.2,
              "items": [], "parse_ok": False, "error": None, "status": 0}
    out_dir = day_dir("raw", args.date)
    out_dir.mkdir(parents=True, exist_ok=True)

    try:
        if not os.environ.get("FOLO_TOKEN"):
            # 先探测是否已有 CLI 本地登录态
            who = run_cli(["whoami"], timeout=120)
            if not who.get("ok"):
                raise RuntimeError("UNAUTHORIZED: 未设置 FOLO_TOKEN 且 CLI 无本地登录态。"
                                   "登录：npx --yes folocli@latest login（浏览器）"
                                   "或在 ~/.workbuddy/.env 加 FOLO_TOKEN=<session token>")
        entries: list[dict] = []
        cursor = None
        for _ in range(max(1, args.max_pages)):
            cli_args = ["timeline", "--limit", "100"]
            if cursor:
                cli_args += ["--cursor", cursor]
            resp = run_cli(cli_args)
            if not resp.get("ok"):
                raise RuntimeError(f"timeline 失败: {resp.get('error', {}).get('code')}"
                                   f"/{resp.get('error', {}).get('message', '')[:80]}")
            data = resp.get("data") or {}
            page = data.get("entries") or []
            if isinstance(page, dict):  # 兼容按 feedId 分组形态
                page = [x for lst in page.values() for x in (lst if isinstance(lst, list) else [lst])]
            entries.extend(page)
            if not data.get("hasNext"):
                break
            cursor = data.get("nextCursor")
            if not cursor:
                break
        record["status"] = 200
        record["raw_count"] = len(entries)
        for e in entries:
            if isinstance(e, dict):
                it = entry_to_item(e)
                if it:
                    record["items"].append(it)
        record["parse_ok"] = bool(record["items"])
        record["item_count"] = len(record["items"])
        # 真实 payload 落盘一份（脱敏后）供字段校准与排障
        (out_dir / "payload").mkdir(exist_ok=True)
        (out_dir / "payload" / "folo-timeline.json").write_text(
            redact_credentials(json.dumps(entries[:200], ensure_ascii=False), {}),
            encoding="utf-8")
    except Exception as exc:  # noqa: BLE001 — 整源降级
        record["error"] = redact_credentials(f"{type(exc).__name__}: {exc}", {})[:200]
        LOG.warning("Folo 采集降级：%s", record["error"])

    write_json(out_dir / f"{SOURCE_ID}.json", record)
    append_jsonl(DATA_DIR / "state" / "run-log.jsonl",
                 {"ts": record["fetched_at"], "event": "fetch_folo", "date": args.date,
                  "items": record["item_count"] if record["parse_ok"] else 0,
                  "error": record["error"]})
    print(f"[{args.date}] Folo 基线：{record['item_count'] if record['parse_ok'] else 0} 条"
          + (f"（降级：{record['error'][:60]}）" if record["error"] else ""))
    return 0 if record["parse_ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
