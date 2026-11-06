#!/usr/bin/env python3
"""P1 · 统一分发编排（核验闸门 + 幂等 + 本地 payload 准备，默认不对外发送）。

一句话定位：**确定性脚本负责「准备到只差授权」，外部发送一律由 Agent 在用户明确授权后执行。**

闸门（缺一不可，任一失败即整体拒绝分发）：
  1. reports/verify-<date>.json 存在且 violations == 0；
  2. digest.json 存在，quality.ai_status 合法；降级日报只准备、不生成实发待办；
  3. 待发布文本通过凭据扫描（email.html / library 快照 / brief.md）；
  4. 各通道要求的本地产物齐全。

  python scripts/push_daily.py --date 2026-11-05              # 默认 dry-run，只出计划
  python scripts/push_daily.py --date 2026-11-05 --apply       # 生成本地 payload + 幂等记录 + 待授权清单
  python scripts/push_daily.py --date 2026-11-05 --apply --force   # 忽略同日幂等记录重做

产物：
  reports/push-plan-<date>.md               可读分发计划
  data/state/pending-dispatch-<date>.json   待 Agent 调用的外部动作清单（幂等）
  data/state/push-log.jsonl                 分发幂等记录（append-only）

本脚本不调用 agent-mail / 企微 / 资料库 / 站点发布等任何外部工具。
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (DATA_DIR, PUBLIC_DIR, ROOT, add_date_arg, append_jsonl, day_dir,
                    load_config, now_utc, read_json, read_jsonl, run_log,
                    setup_logging, write_json, LOG)
from make_digest import scan_credentials

STATE_DIR = DATA_DIR / "state"
REPORT_DIR = ROOT / "reports"

EXTERNAL = {
    "site": {"tool": "workbuddy_sites_deploy", "desc": "对 public/ 执行「发布为网站」，得到在线链接"},
    "atom": {"tool": "随站点发布", "desc": "站点上线后 <域名>/feed.atom 即为订阅地址"},
    "jsonfeed": {"tool": "随站点发布", "desc": "站点上线后 <域名>/feed.json 供程序消费"},
    "email": {"tool": "mcp__agent-mail__SendMessage", "desc": "收件人用 GetMe 动态获取，正文 email.html，附件见 email-meta.json"},
    "library": {"tool": "LibraryUpload", "desc": "按 _manifest 上传终态产物到「我的文档/每日信息/<YYYY>/<MM>/」"},
    "wecom": {"tool": "WeCom 机器人（WebSocket 长连接）", "desc": "brief.md 短简报；需先在企微里给机器人发过一条消息"},
}


def gate(date: str) -> tuple[bool, dict, list[str]]:
    """核验闸门：只读，返回 (通过, 报告摘要, 阻塞原因列表)。"""
    blocks = []
    rep = read_json(REPORT_DIR / f"verify-{date}.json", {})
    if not rep:
        blocks.append(f"缺少 reports/verify-{date}.json（先跑 verify_digest.py）")
    elif rep.get("date") not in (None, date):
        blocks.append(f"核验报告日期不匹配：报告={rep.get('date')} 请求={date}（禁止复用旧报告）")
    elif rep.get("violations", 1) != 0 or rep.get("passed") != rep.get("total_checks"):
        blocks.append(f"核验未通过：{rep.get('passed')}/{rep.get('total_checks')}，"
                      f"violations={rep.get('violations')}")
    d = read_json(day_dir("digest", date) / "digest.json", {})
    degraded = d.get("quality", {}).get("ai_status") == "degraded"
    if isinstance(rep, dict) and not rep.get("violations", 1):
        # 防止复用「同日期但口径收紧前」的旧报告：必须含 v1.1 新增的 V8 口径闸门。
        # 降级日报的 V8 整段按设计跳过，此处豁免但记日志，由 pending-dispatch 标注人工复核。
        names = {c.get("check", "") for c in rep.get("checks", [])}
        required = f"V8[{date}] 数字白名单口径排除元数据"
        if required not in names and not degraded:
            blocks.append(f"核验报告缺少 v1.1 口径闸门（{required}），可能是收紧前旧报告，"
                          "请重跑 verify_digest.py")
        if degraded:
            LOG.warning("降级日报：V8 口径闸门按设计跳过，分发准备保留但外部动作需人工复核")
    if not d:
        blocks.append("缺少 digest.json")
        return False, rep, blocks
    status = d.get("quality", {}).get("ai_status")
    if status not in ("ok", "degraded", "unknown"):
        blocks.append(f"ai_status 非法：{status}")
    texts = []
    for name in ("brief.md", "email.html"):
        p = day_dir("digest", date) / name
        if p.exists():
            texts.append(p.read_text(encoding="utf-8", errors="replace"))
    staging = DATA_DIR / "library" / date[:4] / date[5:7] / f"index-{date}.html"
    if staging.exists():
        texts.append(staging.read_text(encoding="utf-8", errors="replace"))
    hits = scan_credentials("\n".join(texts))
    if hits:
        blocks.append(f"待发布文本疑似含凭据特征：{hits[:3]}")
    return not blocks, rep, blocks


def channel_files(cid: str, date: str) -> list[Path]:
    d = day_dir("digest", date)
    lib = DATA_DIR / "library" / date[:4] / date[5:7]
    if cid == "site":
        return [PUBLIC_DIR / "index.html", PUBLIC_DIR / "data" / "index.json",
                PUBLIC_DIR / "data" / "latest.json", PUBLIC_DIR / "data" / f"{date}.json"]
    if cid == "atom":
        return [PUBLIC_DIR / f"{n}.atom" for n in
                ("all", "feed", "high-signal", "tech", "invest", "docs")]
    if cid == "jsonfeed":
        return [PUBLIC_DIR / "feed.json"]
    if cid == "email":
        return [d / "email.html", d / "email-subject.txt", d / "email-meta.json",
                d / "digest.md", PUBLIC_DIR / "feed.atom"]
    if cid == "wecom":
        return [d / "brief.md"]
    if cid == "library":
        return [lib / f"digest-{date}.md", lib / f"brief-{date}.md",
                lib / f"index-{date}.html", lib / f"items-{date}.csv",
                lib / f"no-number-{date}.csv", lib / f"_manifest-{date}.json"]
    return []


def build_plan(date: str, cfg: dict, apply_mode: bool) -> list[dict]:
    plan = []
    for ch in cfg.get("channels", []):
        cid = ch.get("id")
        files = channel_files(cid, date)
        missing = [str(p.relative_to(ROOT)).replace("\\", "/") for p in files if not p.exists()]
        if not ch.get("enabled", False):
            status = "disabled"
        elif missing:
            status = "will_prepare" if apply_mode else "pending_prepare"
        else:
            status = "ready_local"
        plan.append({
            "channel": cid,
            "label": ch.get("label", cid),
            "status": status,
            "missing": missing,
            "files": [str(p.relative_to(ROOT)).replace("\\", "/") for p in files if p.exists()],
            "external_tool": EXTERNAL.get(cid, {}).get("tool", ""),
            "external_desc": EXTERNAL.get(cid, {}).get("desc", ""),
            "requires_authorization": ch.get("enabled", False) and cid in
                                      ("site", "email", "library", "wecom"),
        })
    return plan


def prepare_local(date: str) -> bool:
    """执行本地可完成的 payload 生成；任一失败即返回 False。"""
    tasks = [
        ["export_library.py", "--date", date],
        ["render_email.py", "--date", date],
    ]
    ok = True
    for args in tasks:
        cmd = [sys.executable, str(ROOT / "scripts" / args[0]), *args[1:]]
        r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True,
                           encoding="utf-8", errors="replace")
        if r.stdout.strip():
            print(r.stdout.strip())
        if r.returncode != 0:
            LOG.error("%s 失败（退出码 %d）：%s", args[0], r.returncode, (r.stderr or "")[-500:])
            ok = False
    return ok


def pending_dispatch(date: str, plan: list[dict], rep: dict, digest: dict) -> dict:
    actions = []
    for row in plan:
        if row["status"] in ("disabled", "pending_prepare"):
            actions.append({"channel": row["channel"], "status": row["status"],
                            "tool": row["external_tool"], "reason": "通道关闭或本地产物未就绪"})
            continue
        if not row["requires_authorization"]:
            # atom / jsonfeed 不作为独立外部动作，但要说明「外部可订阅」依附于站点上线
            status = "requires_site_publish" if row["channel"] in ("atom", "jsonfeed") else "local_only"
            actions.append({"channel": row["channel"], "status": status,
                            "tool": row["external_tool"], "note": row["external_desc"]})
            continue
        payload = {"files": row["files"]}
        if row["channel"] == "email":
            meta = read_json(day_dir("digest", date) / "email-meta.json", {})
            payload.update({"subject": meta.get("subject", ""),
                            "to_policy": meta.get("to_hint", ""),
                            "body_path": f"data/digest/{date}/email.html",
                            "attachments": meta.get("attachments", []),
                            "body_chars": meta.get("body_chars", 0)})
        elif row["channel"] == "library":
            yyyy, mm = date[:4], date[5:7]
            payload.update({"target": f"我的文档/每日信息/{yyyy}/{mm}/",
                            "manifest": f"data/library/{yyyy}/{mm}/_manifest-{date}.json"})
        elif row["channel"] == "site":
            payload.update({"project_dir": "public"})
        elif row["channel"] == "wecom":
            payload.update({"body_path": f"data/digest/{date}/brief.md"})
        actions.append({"channel": row["channel"], "status": "pending_authorization",
                        "tool": row["external_tool"], "desc": row["external_desc"],
                        "payload": payload})
    return {
        "date": date,
        "generated_at": digest.get("generated_at"),
        "verify": {"passed": rep.get("passed"), "total": rep.get("total_checks"),
                   "violations": rep.get("violations")},
        "ai_status": digest.get("quality", {}).get("ai_status"),
        "degraded_note": "降级日报只准备本地产物，外部动作需人工复核" if
                         digest.get("quality", {}).get("ai_status") == "degraded" else None,
        "requires_user_authorization": True,
        "script_does_not_dispatch": True,
        "actions": actions,
    }


def write_report(date: str, plan: list[dict], rep: dict, blocks: list[str], apply_mode: bool) -> None:
    L = [f"# 分发计划 · {date}", "",
         f"核验：`{rep.get('passed', 0)}/{rep.get('total_checks', 0)}`，"
         f"violations=`{rep.get('violations', 'N/A')}` · 模式：`{'apply' if apply_mode else 'dry-run'}`", ""]
    if blocks:
        L += ["## ⛔ 闸门阻塞", ""] + [f"- {b}" for b in blocks] + [""]
    L += ["| 通道 | 状态 | 本地产物 | 外部动作 | 需授权 |",
          "| --- | --- | --- | --- | --- |"]
    for r in plan:
        L.append(f"| {r['label']} | `{r['status']}` | {len(r['files'])} 个"
                 f"{'（缺 ' + str(len(r['missing'])) + '）' if r['missing'] else ''} | "
                 f"{r['external_tool']} | {'是' if r['requires_authorization'] else '否'} |")
    L += ["", "## 状态说明", "",
          "- `ready_local`：本地 payload 齐全，只差外部动作。",
          "- `will_prepare` / `pending_prepare`：本次将（或需要）由 `export_library.py` / `render_email.py` 生成。",
          "- `disabled`：配置里该通道关闭，不参与分发。", "",
          "> 脚本不发送邮件、不推送企微、不上传资料库、不发布站点。"
          "外部动作清单见 `data/state/pending-dispatch-<date>.json`，需用户明确授权后由 Agent 执行。",
          "> 幂等：`data/state/push-log.jsonl` 按「日期 + 通道」去重；重跑不重复记录。"]
    p = REPORT_DIR / f"push-plan-{date}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    text = "\n".join(L) + "\n"
    if not p.exists() or p.read_text(encoding="utf-8") != text:
        p.write_text(text, encoding="utf-8")
    LOG.info("分发计划 → %s", p)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--apply", action="store_true",
                    help="生成本地 payload + 写幂等记录 + 待授权清单（默认 dry-run）")
    ap.add_argument("--force", action="store_true", help="忽略同日幂等记录")
    args = ap.parse_args()
    setup_logging(args.verbose)

    date = args.date
    cfg = load_config("subscriptions.json")
    ok, rep, blocks = gate(date)
    digest = read_json(day_dir("digest", date) / "digest.json", {})
    plan = build_plan(date, cfg, args.apply)
    write_report(date, plan, rep, blocks, args.apply)
    print(f"[{'apply' if args.apply else 'dry-run'}] 核验 "
          f"{rep.get('passed', 0)}/{rep.get('total_checks', 0)} · "
          f"violations={rep.get('violations', 'N/A')} · 闸门={'通过' if ok else '阻塞'}")
    for r in plan:
        print(f"  {r['channel']:10s} {r['status']:16s} 本地产物 {len(r['files'])} 个"
              f"{' · 缺 ' + str(len(r['missing'])) if r['missing'] else ''}")
    if not ok:
        LOG.error("分发闸门阻塞，未执行任何分发：%s", "; ".join(blocks))
        return 1
    if not args.apply:
        print("dry-run 结束：未写 push-log，未生成待授权清单，未调用任何外部工具。")
        return 0

    if not prepare_local(date):
        LOG.error("本地 payload 生成失败，分发中止")
        return 1
    # 重新检查闸门（本地生成物可能含凭据）与计划
    ok2, rep2, blocks2 = gate(date)
    if not ok2:
        LOG.error("payload 生成后闸门复核失败：%s", "; ".join(blocks2))
        return 1
    plan = build_plan(date, cfg, True)
    write_report(date, plan, rep2, [], True)

    pending = pending_dispatch(date, plan, rep2, digest)
    write_json(STATE_DIR / f"pending-dispatch-{date}.json", pending)

    log_path = STATE_DIR / "push-log.jsonl"
    existing = read_jsonl(log_path)
    seen = {(x.get("date"), x.get("channel")) for x in existing
            if x.get("status") in ("prepared", "dispatched")}
    added = 0
    for r in plan:
        if r["status"] == "disabled":
            continue
        key = (date, r["channel"])
        if key in seen and not args.force:
            continue
        append_jsonl(log_path, {
            "ts": now_utc().isoformat().replace("+00:00", "Z"),
            "date": date, "channel": r["channel"], "status": "prepared",
            "local_status": r["status"], "authorization": "pending",
            "verify_violations": rep2.get("violations"),
        })
        added += 1
    run_log("push_daily", date=date, mode="apply", channels=len(plan), log_added=added)
    print(f"本地 payload 就绪；push-log 新增 {added} 条（幂等去重后）。")
    print(f"待授权清单 → {STATE_DIR / f'pending-dispatch-{date}.json'}")
    print("未调用任何外部工具：邮件 / 企微 / 资料库 / 站点上线仍需你明确授权。")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
