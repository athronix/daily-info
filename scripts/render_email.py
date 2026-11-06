#!/usr/bin/env python3
"""P1 · 邮件正文自动渲染（本地生成，不发送）。

把 assets/templates/email.html 的占位符用唯一事实源 digest.json 填满，产出：

  data/digest/<date>/email.html          可直接作为 agent-mail 正文的 HTML
  data/digest/<date>/email-subject.txt   主题行
  data/digest/<date>/email-meta.json     收件人策略 / 附件 / 长度 / 扫描结果（供分发编排读取）

补齐 docs/10 §7 里「邮件正文自动渲染 email.html 占位符未实现」这一项。
所有外部文本 html.escape，链接只接受 http(s)；发布前跑凭据扫描，命中即拒发。
站点未上线（URL 仍为占位域名）时不输出死链，改为提示正文自包含。

  python scripts/render_email.py --date 2026-11-05 [--site-url https://<真实域名>]
"""
from __future__ import annotations

import argparse
import html
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (ROOT, add_date_arg, day_dir, load_config, read_json, run_log,
                    setup_logging, write_text_idempotent, LOG)
from make_digest import scan_credentials

PLACEHOLDER_HOST = "daily-info.local"


def _link(url: str) -> str:
    u = str(url or "")
    if not u.startswith(("http://", "https://")):
        return ""
    return f'<a href="{html.escape(u, quote=True)}" style="color:#3f7d63;">{html.escape(u)}</a>'


def themes_html(themes: list[dict]) -> str:
    if not themes:
        return "<p>暂无可靠数据：本期无主线。</p>"
    rows = []
    for t in themes:
        rows.append(f"<li><strong>{html.escape(str(t.get('title','')))}</strong> · "
                    f"{html.escape(str(t.get('why','')))}</li>")
    return "<ol style=\"padding-left:20px;margin:0;\">" + "".join(rows) + "</ol>"


def section_block(sec: dict) -> str:
    e = html.escape
    rows = [f"<h3 style=\"font-size:15px;margin:20px 0 8px;color:#3f7d63;\">"
            f"{e(str(sec.get('label', sec.get('key',''))))}</h3>"]
    for it in sec.get("items", []):
        link = _link(it.get("url", ""))
        title = e(str(it.get("title", "")))
        rows.append(
            "<div style=\"border-top:1px solid #e5e8e2;padding:10px 0;font-size:13px;line-height:1.75;\">"
            f"<strong>{link or title}</strong><br>"
            f"{e(str(it.get('fact_anchor','')))}<br>"
            f"<span style=\"color:#8d968e;\">读数 {e(' / '.join(it.get('numbers') or []))} · "
            f"相关方 {e(' / '.join(it.get('entities') or []))} · {e(str(it.get('source','')))}</span><br>"
            f"{e(str(it.get('why_matters','')))}<br>"
            f"影响：{e(str(it.get('impact','')))}<br>"
            f"下一步：{e(str(it.get('next_action','')))}"
            "</div>")
    return "".join(rows)


def render(digest: dict, template: str, site_url: str, max_chars: int) -> tuple[str, int]:
    e = html.escape
    st = digest.get("stats", {})
    q = digest.get("quality", {})
    flat = [(s, it) for s in digest.get("sections", []) for it in s.get("items", [])]
    online = PLACEHOLDER_HOST not in site_url
    if online:
        site_link = f'<a href="{e(site_url, quote=True)}" style="color:#3f7d63;">在线阅读完整日报 →</a>'
        feed_link = f'<a href="{e(site_url.rstrip("/") + "/feed.atom", quote=True)}" style="color:#3f7d63;">订阅 Atom</a>'
    else:
        site_link = "站点尚未上线，完整内容见本邮件正文"
        feed_link = "订阅源见附件 feed.atom"

    secs = digest.get("sections", [])
    omitted = 0
    while True:
        body = template
        values = {
            "{date}": e(str(digest.get("date", ""))),
            "{headline}": e(str(digest.get("headline", ""))),
            "{item_count}": str(st.get("published_items", len(flat))),
            "{theme_count}": str(len(digest.get("themes", []))),
            "{sources_ok}": str(st.get("sources_ok", 0)),
            "{sources_total}": str(st.get("sources_total", 0)),
            "{ai_status}": e(str(q.get("ai_status", ""))),
            "{themes_html}": themes_html(digest.get("themes", [])),
            "{sections_html}": "".join(section_block(s) for s in secs) +
                              (f"<p style=\"color:#8d968e;\">因邮件长度上限省略 {omitted} 个板块，"
                               "完整内容见附件 digest.md。</p>" if omitted else ""),
            "{editor_note}": e(str(digest.get("editor_note", ""))).replace("\n", "<br>"),
        }
        for k, v in values.items():
            body = body.replace(k, v)
        # 链接整段替换，必须在通用占位符替换之后、且不能先把 {site_url} 替换掉，
        # 否则模板里的 <a href="{site_url}"> 会变成真实 URL 而匹配不到。
        # 未上线时输出纯文本提示，不留下占位死链。
        body = body.replace(
            '<a href="{site_url}" style="color:#3f7d63;">在线阅读完整日报 →</a>', site_link)
        body = body.replace(
            '&nbsp;·&nbsp;<a href="{feed_url}" style="color:#3f7d63;">订阅 Atom</a>',
            ("&nbsp;·&nbsp;" + feed_link) if online else "")
        # 兜底：模板若改版导致整段匹配失败，也不能把花括号占位符带进邮件
        body = body.replace("{site_url}", e(site_url, quote=True))
        body = body.replace("{feed_url}", e(site_url.rstrip("/") + "/feed.atom", quote=True))
        if "{site_url}" in body or "{feed_url}" in body:
            raise SystemExit("[BLOCK] 邮件模板仍有未替换占位符")
        if len(body) <= max_chars or len(secs) <= 1:
            break
        secs = secs[:-1]
        omitted += 1
    return body, omitted


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--site-url", default="https://daily-info.local",
                    help="站点在线地址；未上线时保持默认，邮件不输出占位死链")
    ap.add_argument("--max-chars", type=int, default=0,
                    help="覆盖配置里的 max_body_chars（0=用配置值），用于容量实测")
    args = ap.parse_args()
    setup_logging(args.verbose)

    cfg = load_config("subscriptions.json")
    email_cfg = next((c for c in cfg["channels"] if c["id"] == "email"), {})
    max_chars = args.max_chars or int(email_cfg.get("max_body_chars", 12000))
    tpl_path = ROOT / str(email_cfg.get("template", "assets/templates/email.html"))
    template = tpl_path.read_text(encoding="utf-8")

    ddir = day_dir("digest", args.date)
    digest = read_json(ddir / "digest.json", {})
    if not digest:
        LOG.error("缺少 %s，先跑 make_digest.py", ddir / "digest.json")
        return 2
    body, omitted = render(digest, template, args.site_url, max_chars)
    leaks = scan_credentials(body)
    if leaks:
        LOG.error("邮件正文疑似含凭据（%d 处），拒绝生成", len(leaks))
        return 2
    if len(body) > max_chars:
        LOG.error("邮件正文 %d 字超过上限 %d", len(body), max_chars)
        return 2

    subject = str(email_cfg.get("subject", "[每日信息] {date} · {headline_short}")).format(
        date=digest.get("date", ""), headline_short=str(digest.get("headline_short", ""))[:20])
    attach = [str(ROOT / a) for a in email_cfg.get("attach", [])]
    attach.append(str(ddir / "digest.md"))
    meta = {
        "date": args.date,
        "generated_at": digest.get("generated_at"),
        "subject": subject,
        "to_policy": str(email_cfg.get("to", ["SELF_AGENT_MAIL_ADDRESS"])[0]),
        "to_hint": "收件人用 agent-mail GetMe 动态获取，不硬编码地址",
        "attachments": [a for a in attach if Path(a).exists()],
        "body_chars": len(body),
        "max_body_chars": max_chars,
        "omitted_sections": omitted,
        "site_online": PLACEHOLDER_HOST not in args.site_url,
        "credential_scan": "clean",
        "dispatch": "pending_authorization",
        "note": "本脚本只生成本地 payload；实际发送由 Agent 在用户授权后调用 agent-mail",
    }
    changed = sum([
        int(write_text_idempotent(ddir / "email.html", body)),
        int(write_text_idempotent(ddir / "email-subject.txt", subject + "\n")),
        int(write_text_idempotent(ddir / "email-meta.json",
                                  json.dumps(meta, ensure_ascii=False, indent=2) + "\n")),
    ])
    run_log("render_email", date=args.date, body_chars=len(body),
            omitted_sections=omitted, changed=changed)
    if omitted:
        LOG.warning("邮件因长度上限省略 %d 个板块，违反全量投影原则；请检查 max_body_chars", omitted)
    LOG.info("邮件正文：%d 字（上限 %d），省略板块 %d，站点在线=%s",
             len(body), max_chars, omitted, meta["site_online"])
    print(f"邮件 payload 就绪：{ddir / 'email.html'} · {len(body)} 字 / 变更 {changed}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
