#!/usr/bin/env python3
"""合成层 v2：AI 结构化产出 + 规则候选集 → 唯一事实源 digest.json + 丰富的人读日报。

输入：
  data/candidate/<date>/clusters.json      规则层完整簇（事实白名单）
  data/digest/<date>/ai-review.json        Agent 按 assets/prompts/daily-digest.md 写回
输出：
  data/digest/<date>/digest.json           唯一事实源（站点/feed/邮件/资料库共用）
  data/digest/<date>/digest.md             人读版日报
  data/digest/<date>/brief.md              推送短简报（<=1500 字）

v2 核心（依据 docs/12 内容规范研究 + config/content-spec.json）：
  每条内容必须含七要素：fact_anchor / numbers / entities / evidence_urls /
  why_matters / impact / next_action。
  ★ 防编造白名单（v1.1 收紧，见 content-spec.json）：numbers / entities 只取自该条目原文
    title + summary_raw + metrics 值；evidence_urls 只取同簇成员 URL。
    published_at 属于元数据，不计入「原文」——防止用发布时间里的年份冒充可核验读数。
    找不到即丢弃并记 warning；原文全文无任何实质数字的条目直接拒绝入报（宁可少一条）。
  ★ 展示层借鉴 daily-rss 2026-11 改版：链接独立成行 → https://...
  ★ 顶层新增 lead（数据化导语）、watch_signals（可证伪信号）、数据概览、参考来源汇总。
--fallback 走纯规则降级出报，保证定时任务永不空跑。
"""
from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from urllib.parse import urlsplit

from common import (ROOT, add_date_arg, day_dir, load_config, now_utc, read_json,
                    run_log, setup_logging, write_json, LOG)

CREDENTIAL_PATTERNS = [
    re.compile(r"(?i)\b(API[_ -]?KEY|SECRET|ACCESS[_ -]?TOKEN|PASSWORD)\s*[:=]\s*\S{6,}"),
    re.compile(r"\b(ghp|gho|ghu|ghs|ghr)_[A-Za-z0-9]{20,}\b"),
    re.compile(r"\bgithub_pat_[A-Za-z0-9_]{20,}\b"),
    re.compile(r"\bsk-[A-Za-z0-9]{20,}\b"),
    re.compile(r"-----BEGIN [A-Z ]*PRIVATE KEY-----"),
    re.compile(r"credential\.helper"),
]
NUMBER_RE = re.compile(r"\d[\d,.]*%?")
URL_IN_TEXT_RE = re.compile(r"https?://\S+")


def scan_credentials(text: str) -> list[str]:
    return [p.pattern for p in CREDENTIAL_PATTERNS if p.search(text or "")]


def _norm(s: str) -> str:
    return re.sub(r"\s+", "", str(s or "")).lower()


def _in_original(value: str, haystack: str) -> bool:
    """值是否逐字出现在原文（忽略空白与大小写），用于 numbers / entities 白名单。"""
    v = _norm(value)
    return bool(v) and v in _norm(haystack)


def original_text(member: dict) -> str:
    """「原文」白名单的唯一口径：标题 + 摘要 + metrics 值。

    刻意不含 published_at / fetched_at 等元数据字段。日期里的年份、月份、时分秒
    是采集侧时间戳，不是新闻内容里的读数；把它们算进原文会让「每条都有可核验数字」
    变成形式通过（2026-11-05 实测 9/32 条仅靠 2026 过关）。
    指标类数字（HN 分数、评论数、Folo aiScore 等）来自原文结构体，属于实质读数。
    """
    return " ".join([str(member.get("title") or ""),
                     str(member.get("summary_raw") or ""),
                     json.dumps(member.get("metrics") or {}, ensure_ascii=False)])


def domain_of(url: str) -> str:
    try:
        host = urlsplit(url).netloc.lower()
        return host[4:] if host.startswith("www.") else host
    except ValueError:
        return ""


def build_index(clusters_doc: dict):
    by_id, source_urls, cluster_urls = {}, set(), {}
    for c in clusters_doc.get("clusters", []):
        urls = [m.get("url", "") for m in c.get("members", []) if m.get("url")]
        urls = [u for u in urls if u.startswith("http")]
        cluster_urls[c["cluster_id"]] = urls
        for m in c.get("members", []):
            by_id[m["id"]] = m
            cluster_urls.setdefault(m.get("cluster_id") or "", urls)
            if m.get("url", "").startswith("http"):
                source_urls.add(m["url"])
        by_id[c["cluster_id"]] = c["members"][0]
    return by_id, source_urls, cluster_urls


def digest_from_ai(date: str, clusters_doc: dict, ai: dict, taxonomy: dict, spec: dict) -> dict:
    by_id, source_urls, cluster_urls = build_index(clusters_doc)
    rules = spec["quality_rules"]
    warnings: list[str] = []
    sections: list[dict] = []
    used_ids: set[str] = set()
    all_numbers: set[str] = set()
    rejected_no_number = 0
    published_ids: set[str] = set()

    for sec in ai.get("sections", []):
        items = []
        for ref in sec.get("items", []):
            rid = ref.get("id") or ref.get("cluster_id")
            m = by_id.get(rid)
            if not m:
                warnings.append(f"unknown_id:{rid}")
                continue
            if rid in used_ids:
                warnings.append(f"duplicate_id:{rid}")
                continue
            used_ids.add(rid)

            # 原文口径（v1.1 收紧）：标题 + 摘要 + metrics 值；published_at 不算原文
            original = original_text(m)
            # ① 数字白名单：AI 给的每个值必须出现在原文
            numbers, dropped_n = [], 0
            for value in (ref.get("numbers") or [])[:spec["item_seven_elements"]["numbers"]["max_count"]]:
                if _in_original(value, original):
                    numbers.append(str(value).strip())
                else:
                    dropped_n += 1
            if dropped_n:
                warnings.append(f"invented_numbers_dropped:{rid}:{dropped_n}")
            if not numbers:
                # 兜底仍只从原文取，绝不再回退到时间戳
                found = NUMBER_RE.findall(original)
                if found:
                    numbers.append(found[0][:30])
                    warnings.append(f"fallback_number_from_original:{rid}")
            if not numbers:
                # 硬闸门：无任何实质读数 → 拒绝入报，不靠空数字凑七要素
                warnings.append(f"rejected_no_substantive_number:{rid}")
                rejected_no_number += 1
                continue
            all_numbers.update(numbers)

            # ② 实体白名单
            entities, dropped_e = [], []
            for value in (ref.get("entities") or [])[:6]:
                if _in_original(value, original):
                    entities.append(str(value).strip()[:40])
                else:
                    dropped_e.append(str(value).strip()[:40])
            if dropped_e:
                warnings.append(f"invented_entities_dropped:{rid}:{'|'.join(dropped_e)}")
            if not entities:
                entities = [m.get("source_name", "") or "未知来源"]

            # ③ 佐证 URL 白名单：只取同簇成员 URL；留空则用该条目自身 url
            allowed = set(cluster_urls.get(m.get("cluster_id"), []) or
                          cluster_urls.get(rid, [])) or {m.get("url", "")}
            ev = [u for u in (ref.get("evidence_urls") or []) if u in allowed][:5]
            if ref.get("evidence_urls") and len(ev) < len(ref["evidence_urls"]):
                warnings.append(f"invented_urls_ignored:{rid}")
            if not ev:
                ev = [m.get("url", "")] if m.get("url", "").startswith("http") else []

            # ④ 事实锚点：去 URL、截断
            anchor = URL_IN_TEXT_RE.sub("", str(ref.get("fact_anchor", ""))).strip()
            anchor = anchor[:spec["item_seven_elements"]["fact_anchor"]["max_chars"]] or m.get("title", "")

            # ⑤ 下一步动作：禁空话
            action = str(ref.get("next_action", "")).strip()[:160]
            vague = [w for w in rules["forbid_vague_next_action"] if w in action]
            if vague:
                warnings.append(f"vague_next_action:{rid}:{vague[0]}")
                action = ""

            items.append({
                "id": rid,
                "title": m.get("title", ""),
                "url": m.get("url", ""),
                "source": m.get("source_name", ""),
                "published_at": m.get("published_at"),
                "score": m.get("score"),
                "category": m.get("category", sec.get("key", "")),
                "cluster_id": m.get("cluster_id"),
                "summary": (m.get("summary_raw") or "")[:taxonomy["quality_rules"]["max_summary_chars"]],
                "why_matters": str(ref.get("why_matters", ""))[:120],
                "fact_anchor": anchor,
                "numbers": numbers,
                "entities": entities,
                "evidence_urls": ev,
                "impact": str(ref.get("impact", ""))[:160],
                "next_action": action,
                "signal_type": ref.get("signal_type"),
                "confidence": ref.get("confidence", "fact"),
            })
            published_ids.add(rid)
        if items:
            sections.append({"key": sec.get("key", "misc"),
                             "label": sec.get("label", sec.get("key", "其他")),
                             "items": items})

    themes = []
    for t in ai.get("themes", []):
        # 佐证只允许指向真正入报的条目；被白名单拒绝的簇不得继续充当主题证据
        cids = [x for x in t.get("cluster_ids", []) if x in published_ids]
        themes.append({"title": str(t.get("title", ""))[:40],
                       "why": str(t.get("why", ""))[:200], "cluster_ids": cids,
                       "verified_by": len(cids)})

    # ⑥ lead：必须含数字且数字能在当天原文中出现
    lead = str(ai.get("lead") or "")[:220]
    lead_ok = bool(NUMBER_RE.search(lead)) and any(
        _in_original(n, " ".join(all_numbers)) for n in NUMBER_RE.findall(lead)[:3])
    if not lead_ok:
        warnings.append("lead_number_not_traceable" if lead else "lead_missing")
        seed = " ".join(sorted(all_numbers)[:3])
        lead = f"今日共 {sum(len(s['items']) for s in sections)} 条入选" + (f"，关键读数 {seed}。" if seed else "。")

    watch = []
    for w in ai.get("watch_signals", []):
        if all(w.get(k) for k in ("signal", "threshold", "judgement")):
            watch.append({"signal": str(w["signal"])[:80],
                          "threshold": str(w["threshold"])[:80],
                          "judgement": str(w["judgement"])[:120]})

    headline = str(ai.get("headline") or "")[:80]
    editor_note = str(ai.get("editor_note") or "")
    brief = str(ai.get("brief") or "")
    leaks = scan_credentials("\n".join([headline, lead, editor_note, brief,
                                        json.dumps(sections, ensure_ascii=False)]))
    if leaks:
        raise SystemExit(f"[BLOCK] AI 产物疑似含凭据（{len(leaks)} 处），拒绝发布：{leaks}")

    flat = [it for s in sections for it in s["items"]]
    domains = Counter(domain_of(u) for it in flat for u in it["evidence_urls"])
    passed = sum(1 for it in flat if _seven_ok(it))
    digest = {
        "date": date,
        "headline": headline,
        "headline_short": headline[:28],
        "lead": lead,
        "generated_at": now_utc().isoformat().replace("+00:00", "Z"),
        "themes": themes,
        "sections": sections,
        "editor_note": editor_note,
        "brief": brief,
        "watch_signals": watch,
        "reference_summary": [{"domain": k, "count": v} for k, v in domains.most_common(15)],
        "stats": {
            "sources_ok": clusters_doc.get("sources_ok", 0),
            "sources_total": clusters_doc.get("sources_total", 0),
            "total_items": clusters_doc.get("total_items", 0),
            "clusters": clusters_doc.get("total_clusters", 0),
            "selected": clusters_doc.get("selected", 0),
            "published_items": len(flat),
            "seven_element_pass": passed,
            "seven_element_ratio": round(passed / max(1, len(flat)), 3),
            "items_with_numbers": sum(1 for it in flat if it["numbers"]),
            "substantive_number_ratio": round(
                sum(1 for it in flat if it["numbers"]) / max(1, len(flat)), 3),
            "rejected_no_number": rejected_no_number,
            "unique_reference_domains": len(domains),
        },
        "quality": {
            "ai_status": "ok",
            "missing_data_marker": rules["missing_data_marker"],
            "warnings": warnings,
            "id_whitelist": True,
            "url_whitelist": True,
            "number_whitelist": True,
            "number_whitelist_scope": spec["verification"]["number_whitelist_scope"],
            "number_whitelist_excludes": spec["verification"]["number_whitelist_excludes"],
            "entity_whitelist": True,
            "credential_scan": "clean",
            "content_spec_version": spec["version"],
        },
        "demo": bool(ai.get("demo")),
    }
    return digest


def _seven_ok(it: dict) -> bool:
    required = ("fact_anchor", "numbers", "entities", "evidence_urls",
                "why_matters", "impact", "next_action")
    return all(it.get(k) for k in required) and bool(it.get("url"))


def digest_fallback(date: str, clusters_doc: dict, taxonomy: dict, spec: dict) -> dict:
    """纯规则降级：只列原文标题+摘要，不写研判；七要素留空，V8 会跳过丰富度检查。"""
    by_cat: dict[str, list[dict]] = {}
    for c in clusters_doc.get("clusters", [])[:20]:
        m = c["members"][0]
        numbers = NUMBER_RE.findall(original_text(m))[:2]
        by_cat.setdefault(c["category"], []).append({
            "id": m["id"], "title": m["title"], "url": m["url"],
            "source": m["source_name"], "published_at": m.get("published_at"),
            "score": c["score"], "category": c["category"],
            "cluster_id": c["cluster_id"],
            "summary": (m.get("summary_raw") or "")[:200],
            "why_matters": "", "fact_anchor": m["title"][:120],
            "numbers": numbers, "entities": [m.get("source_name", "")],
            "evidence_urls": [m["url"]] if m.get("url", "").startswith("http") else [],
            "impact": "", "next_action": "",
            "signal_type": None, "confidence": "fact",
        })
    labels = {c["key"]: c["label"] for c in taxonomy["categories"]}
    sections = [{"key": k, "label": labels.get(k, k), "items": v} for k, v in by_cat.items()]
    flat = [it for s in sections for it in s["items"]]
    return {
        "date": date,
        "headline": "[降级] " + (clusters_doc.get("clusters", [{}])[0].get("representative_title", "每日信息")[:60]
                                if clusters_doc.get("clusters") else "今日无可用数据"),
        "headline_short": "[降级] 每日信息",
        "lead": "暂无可靠数据：AI 研判不可用，本期仅列规则层精选条目。",
        "generated_at": now_utc().isoformat().replace("+00:00", "Z"),
        "themes": [], "sections": sections,
        "editor_note": "",
        "brief": f"{date} 降级出报：AI 研判不可用，仅列规则层精选条目。",
        "watch_signals": [],
        "reference_summary": [],
        "stats": {"sources_ok": clusters_doc.get("sources_ok", 0),
                  "sources_total": clusters_doc.get("sources_total", 0),
                  "total_items": clusters_doc.get("total_items", 0),
                  "clusters": clusters_doc.get("total_clusters", 0),
                  "selected": clusters_doc.get("selected", 0),
                  "published_items": len(flat),
                  "seven_element_pass": 0, "seven_element_ratio": 0.0,
                  "items_with_numbers": sum(1 for it in flat if it["numbers"]),
                  "substantive_number_ratio": round(
                      sum(1 for it in flat if it["numbers"]) / max(1, len(flat)), 3),
                  "rejected_no_number": 0,
                  "unique_reference_domains": 0},
        "quality": {"ai_status": "degraded", "warnings": ["ai_review_missing"],
                    "missing_data_marker": taxonomy["quality_rules"]["missing_data_marker"],
                    "id_whitelist": True, "url_whitelist": True,
                    "number_whitelist": True,
                    "number_whitelist_scope": spec["verification"]["number_whitelist_scope"],
                    "number_whitelist_excludes": spec["verification"]["number_whitelist_excludes"],
                    "entity_whitelist": True,
                    "credential_scan": "clean", "content_spec_version": spec["version"]},
        "demo": False,
    }


def render_markdown(d: dict) -> str:
    st = d["stats"]
    L = [f"# {d['headline']}", "", f"> {d.get('lead', '')}", "",
         f"> {d['date']} · 北京时间 · 生成于 {d['generated_at']}", "",
         "## 📌 今日速览", ""]
    quick = [it for s in d["sections"] for it in s["items"]]
    for it in quick[:6]:
        nums = f"（{', '.join(it['numbers'][:2])}）" if it.get("numbers") else ""
        L.append(f"- **{it.get('fact_anchor') or it['title']}**{nums}"
                 + (f" — {it['why_matters']}" if it.get("why_matters") else ""))
    if not quick:
        L.append(d["quality"]["missing_data_marker"])

    L += ["", "---", "", "## 🔥 今日主线", ""]
    if d["themes"]:
        for i, t in enumerate(d["themes"], 1):
            L.append(f"### {'一二三四五六七八九十'[i-1] if i <= 10 else i}、{t['title']}")
            L.append(f"{t['why']}（{t.get('verified_by', 0)} 条独立条目佐证）")
            L.append("")
    else:
        L += [d["quality"]["missing_data_marker"], ""]

    L += ["---", "", "## 🗂 分类聚合", ""]
    for sec in d["sections"]:
        L += [f"### {sec['label']}（{len(sec['items'])} 条）", ""]
        for it in sec["items"]:
            L.append(f"**{it.get('fact_anchor') or it['title']}**")
            meta = []
            if it.get("numbers"):
                meta.append("关键数字：" + " / ".join(it["numbers"]))
            if it.get("entities"):
                meta.append("相关方：" + " / ".join(it["entities"]))
            if it.get("source"):
                meta.append("来源：" + it["source"])
            if it.get("published_at"):
                meta.append(it["published_at"][:16].replace("T", " ") + " UTC")
            if it.get("score") is not None:
                meta.append(f"{it['score']} 分")
            if meta:
                L.append("- " + " · ".join(meta))
            if it.get("why_matters"):
                L.append(f"- 为什么值得看：{it['why_matters']}")
            if it.get("impact"):
                L.append(f"- 对我意味着什么：{it['impact']}")
            if it.get("next_action"):
                L.append(f"- 下一步：{it['next_action']}")
            if it.get("confidence") in ("inference", "unverified"):
                L.append(f"- 证据状态：{it['confidence']}（{'推断' if it['confidence']=='inference' else '未独立验证'}）")
            # 链接外置：独立成行，不与正文混排（daily-rss 2026-11 改版）
            for u in (it.get("evidence_urls") or [it["url"]]):
                if u.startswith("http"):
                    L.append(f"→ {u}")
            L.append("")

    L += ["---", "", "## 📊 今日数据概览", "",
          "| 指标 | 数值 |", "| --- | ---: |",
          f"| 信源可用 | {st.get('sources_ok', 0)} / {st.get('sources_total', 0)} |",
          f"| 原始条目 | {st.get('total_items', 0)} |",
          f"| 聚合簇 | {st.get('clusters', 0)} |",
          f"| 入选簇 | {st.get('selected', 0)} |",
          f"| 实际入报 | {st.get('published_items', 0)} |",
          f"| 七要素达标 | {st.get('seven_element_pass', 0)} / {st.get('published_items', 0)}"
          f"（{round(st.get('seven_element_ratio', 0) * 100, 1)}%） |",
          f"| 引用域名数 | {st.get('unique_reference_domains', 0)} |", ""]
    if d.get("reference_summary"):
        L += ["高频来源：" + "、".join(f"{r['domain']}({r['count']})"
                                    for r in d["reference_summary"][:8]), ""]
    if d.get("watch_signals"):
        L += ["---", "", "## 🔭 待验证信号（可证伪）", "",
              "| 信号 | 判定阈值 | 达到后判定 |", "| --- | --- | --- |"]
        for w in d["watch_signals"]:
            L.append(f"| {w['signal']} | {w['threshold']} | {w['judgement']} |")
        L.append("")
    if d.get("editor_note"):
        L += ["---", "", "## 💡 编者观察", "", d["editor_note"], ""]
    L += ["---", "",
          "*本日报由规则层采集/去重/打分 + AI 研判生成；每条附原文链接，关键数字须能在原文中找到。*",
          "*外部事实未独立验证，内容仅供参考，不构成投资建议；取不到可靠数据处标注「暂无可靠数据」。*", ""]
    return "\n".join(L)


def render_brief(d: dict) -> str:
    st = d["stats"]
    L = [f"**{d['headline']}**", "", d.get("lead", ""), "",
         f"{d['date']} · 入报 {st.get('published_items', 0)} 条"
         f" · 信源 {st.get('sources_ok', 0)}/{st.get('sources_total', 0)}", "",
         "今日主线："]
    for t in d["themes"][:5]:
        L.append(f"• {t['title']}")
    L += ["", "重点条目（含关键数字与下一步动作）："]
    n = 0
    for sec in d["sections"]:
        for it in sec["items"][:2]:
            nums = f"[{', '.join(it['numbers'][:2])}] " if it.get("numbers") else ""
            L.append(f"• {nums}{it.get('fact_anchor') or it['title']}")
            if it.get("next_action"):
                L.append(f"  → {it['next_action']}")
            L.append(f"  {it['url']}")
            n += 1
            if n >= 8:
                break
        if n >= 8:
            break
    if d.get("watch_signals"):
        L += ["", "待验证信号："]
        for w in d["watch_signals"][:3]:
            L.append(f"• {w['signal']}（{w['threshold']}）")
    if d["quality"]["ai_status"] == "degraded":
        L += ["", "（本期为降级出报，AI 研判不可用）"]
    L += ["", "内容仅供参考，外部事实未独立验证，不构成投资建议。"]
    return "\n".join(L)[:1500]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--fallback", action="store_true", help="强制走规则降级")
    args = ap.parse_args()
    setup_logging(args.verbose)

    taxonomy = load_config("taxonomy.json")
    spec = load_config("content-spec.json")
    cand = day_dir("candidate", args.date)
    clusters_doc = read_json(cand / "clusters.json", {})
    if not clusters_doc.get("clusters"):
        LOG.error("缺少 clusters.json，请先运行 dedupe_cluster.py")
        return 1
    raw_summary = read_json(day_dir("raw", args.date) / "_summary.json", {})
    clusters_doc["sources_ok"] = raw_summary.get("ok", 0)
    clusters_doc["sources_total"] = raw_summary.get("enabled", 0)

    ai = read_json(day_dir("digest", args.date) / "ai-review.json", {})
    if args.fallback or not ai:
        LOG.warning("AI 结构化产出缺失，走规则降级出报")
        d = digest_fallback(args.date, clusters_doc, taxonomy, spec)
    else:
        d = digest_from_ai(args.date, clusters_doc, ai, taxonomy, spec)

    out = day_dir("digest", args.date)
    changed = write_json(out / "digest.json", d)
    (out / "digest.md").write_text(render_markdown(d), encoding="utf-8")
    (out / "brief.md").write_text(render_brief(d), encoding="utf-8")
    run_log("digest", date=args.date, ai_status=d["quality"]["ai_status"],
            published_items=d["stats"]["published_items"],
            seven_ratio=d["stats"]["seven_element_ratio"], changed=changed)
    print(f"[{args.date}] digest 生成：{d['stats']['published_items']} 条 / {len(d['sections'])} 板块"
          f" / 七要素达标 {round(d['stats']['seven_element_ratio'] * 100, 1)}%"
          f" / ai_status={d['quality']['ai_status']}"
          f" / warnings={len(d['quality'].get('warnings', []))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
