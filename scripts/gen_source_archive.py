"""生成全量数据源归档表 docs/references/data-source.md。

合并四个数据层（全部只读，不修改任何配置）：
  1. config/sources.json                 —— 169 个登记源（在用/暂禁用/失效留证）
  2. reports/source-health-<date>.json   —— 登记源最近一次全量体检证据
  3. config/candidates.json              —— 122 个扩充候选池
  4. reports/candidate-probe-<date>.json —— 候选池三重体检证据（含被拒原因）

输出一张按内容类别分组的 Markdown 总表，列口径按用户要求：
  内容类别 | 资讯来源名称 | 相关URL | 资源来源技术类别 | 资讯质量星级 | 评价 |
  是否采纳 | 采纳方式 | 采纳决策原因 | 检测是否可用 | 检测证据
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, add_date_arg, load_config, setup_logging  # noqa: E402

OUT = ROOT / "docs" / "references" / "data-source.md"

# kind → 资源来源技术类别（api/website/feed）
KIND_TECH = {
    "rss": "Feed", "atom": "Feed", "git_atom": "Feed",
    "json_api": "API", "html": "Website", "cli": "CLI（Agent 工具链）",
}
# 特殊接入方式的标注覆盖
TECH_OVERRIDE = {
    "baai-hub": "API（逆向 POST JSON）",
    "folo-timeline": "CLI（Folo folocli，官方 Agent skill）",
    "aigc-link": "Website（渲染代理转 Markdown）",
    "github-trending": "Website（HTML 解析）",
    "anthropic-news": "Website（HTML 解析）",
    "sec-edgar-current": "Website（HTML 解析）",
    "hn-algolia": "API", "openalex": "API", "hf-daily-papers": "API",
    "sec-submissions-returns": "API", "yahoo-chart": "API",
    "hf-spaces-new": "API",
}

CAT_LABEL = {}


def load_all(date: str) -> dict:
    sources = load_config("sources.json")["sources"]
    health_p = ROOT / "reports" / f"source-health-{date}.json"
    probe_p = ROOT / "reports" / f"candidate-probe-{date}.json"
    health = json.loads(health_p.read_text(encoding="utf-8")) if health_p.is_file() else []
    probe = json.loads(probe_p.read_text(encoding="utf-8")) if probe_p.is_file() else []
    cands = load_config("candidates.json").get("candidates", [])
    tax = load_config("taxonomy.json")
    for c in tax.get("categories", []):
        CAT_LABEL[c["key"]] = c["label"]
    CAT_LABEL.setdefault(tax.get("fallback_category", "community"), "社区与观点")
    return {
        "sources": {s["id"]: s for s in sources},
        "health": {h["id"]: h for h in health},
        "probe": {p["id"]: p for p in probe},
        "candidates": {c["id"]: c for c in cands},
    }


def clean(text: str, limit: int = 110) -> str:
    if not text:
        return ""
    t = re.sub(r"\s+", " ", str(text)).replace("|", "\\|").strip()
    return t[:limit] + ("…" if len(t) > limit else "")


def cell(text: str) -> str:
    """不经截断的单元格（如 URL）也必须转义竖线，否则破坏表格列对齐。"""
    return str(text).replace("|", "\\|")


def stars(tier: str, weight: float, usable: bool, adopted: bool) -> int:
    if tier == "X":
        return 1
    if not usable:
        return 2 if adopted else 1
    if tier == "A":
        return 5 if weight >= 0.7 else 4
    if tier == "B":
        return 4
    return 3  # C：内容有价值但接入通道脆弱


def adopt_state(s: dict) -> str:
    if s.get("tier") == "X":
        return "❌ 失效留证（未采纳）"
    if s.get("enabled"):
        return "✅ 在用"
    return "⏸ 已登记·暂禁用"


def adopt_method(s: dict) -> str:
    kind = s.get("kind", "rss")
    tech = TECH_OVERRIDE.get(s["id"], KIND_TECH.get(kind, kind))
    if s.get("tier") == "X":
        return "—"
    if s.get("method") == "POST":
        return "API 逆向（匿名 POST，无账户）"
    if kind == "git_atom":
        return "Feed（Git 仓库 Atom 直连）"
    if s.get("parser") or s.get("adapter"):
        return f"{tech}（专用解析器/adapter）"
    return f"{tech}（通用解析直连）"


def decide_reason(s: dict, health: dict) -> str:
    note = s.get("note", "")
    bits = []
    if s.get("tier") == "X":
        bits.append("早期调研发现已失效/重定向，保留登记仅防重复踩坑，不再抓取")
    elif not s.get("enabled"):
        bits.append("登记保留但当前禁用（详见 note 中的实测原因与替代源）")
    else:
        w = s.get("weight", 1.0)
        tier_desc = {"A": "Tier A 官方/权威", "B": "Tier B 优质补充",
                     "C": "Tier C 内容佳但通道脆弱（整源降级不阻断日报）"}.get(s.get("tier", "A"), "Tier A")
        if s.get("tier") == "C":
            bits.append(f"{tier_desc}（权重 {w}）")
        elif w >= 0.9:
            bits.append(f"{tier_desc}主源（权重 {w}）")
        elif w >= 0.7:
            bits.append(f"{tier_desc}稳定源（权重 {w}）")
        else:
            bits.append(f"泛消费/低信噪比，降权至 {w}，靠打分自然控噪而非删源（{tier_desc}）")
    if note:
        bits.append(clean(note, 90))
    h = health.get("status")
    if h and health.get("ok") is False and s.get("enabled"):
        bits.append(f"最近体检 {h}（观察名单，未影响采纳）")
    return "；".join(bits)


def usable_and_evidence(sid: str, s: dict, health: dict, probe: dict) -> tuple[str, str]:
    """返回（检测是否可用, 检测证据）。优先用候选探测证据（解析深度更高），否则用登记源体检。"""
    if probe:
        st = probe.get("status", 0)
        ok = probe.get("ok")
        ct = clean(probe.get("content_type") or "", 40)
        if ok:
            ev = (f"{st} / {ct} / 解析 {probe.get('parsed_items', 0)} 条"
                  f"（最新《{clean(probe.get('sample_title'), 46)}》@{probe.get('sample_date') or '?'}）")
            return "可用", ev
        ev = f"{st or '网络失败'} / {clean(probe.get('reason'), 80)}"
        return "不可用", ev
    if health:
        st = health.get("status", 0)
        ok = health.get("ok")
        feed = health.get("looks_like_feed")
        ct = clean(health.get("content_type") or "", 40)
        bts = health.get("bytes_sample")
        # 渲染代理 / Markdown 类源响应体本就不是 XML，looks_like_feed=False 不代表不可用
        non_feed_ok = sid in ("aigc-link",) or ct.startswith("text/plain")
        if ok and (feed or non_feed_ok):
            tag = "响应体确认为 feed/JSON" if feed else "Markdown 渲染代理，按专用解析器出条目"
            return "可用", f"{st} / {ct} / {bts}B / {tag}"
        if ok and not feed:
            return "不稳定", f"{st} / {ct} / {bts}B / 响应体非 feed（疑似反爬挑战页）"
        return "不可用", f"{st or '网络失败'} / {ct}"
    return "未单独检测", "登记于早期调研，未进入本轮批量探测池"


def build_rows(data: dict) -> dict[str, list[dict]]:
    srcs, healths, probes, cands = (data["sources"], data["health"],
                                    data["probe"], data["candidates"])
    rows: dict[str, list[dict]] = {}
    seen = set()

    for sid, s in srcs.items():
        seen.add(sid)
        h = healths.get(sid, {})
        p = probes.get(sid)  # 从候选池晋升的源带上探测证据
        adopted = s.get("tier") != "X" and bool(s.get("enabled"))
        if s.get("kind") == "cli":
            # CLI 型信源（Folo 基线）：可用性=最近一次 fetch 是否成功，与 HTTP 探测语义不同
            usable, ev = usable_and_evidence(sid, s, h, None)
            if h.get("note"):
                usable, ev = "可用", h["note"]
            elif "UNAUTHORIZED" in (h.get("reason") or "") or "登录" in (h.get("reason") or ""):
                usable, ev = "待登录", (h.get("reason") or "等待 FOLO_TOKEN / folocli login")[:100]
            st = 4 if usable == "可用" else 3  # 内容价值高但当前待授权
            cat = "基线信源"
            rows.setdefault(cat, []).append({
                "sort": (0 if usable == "可用" else 1, -st),
                "cells": [
                    cat, s["name"], cell(s["url"]), TECH_OVERRIDE.get(sid, "CLI（Agent 工具链）"),
                    "⭐" * st, "用户 Folo 订阅池：每条经人工订阅，信噪比最高，作为日报基线层",
                    "✅ 在用·待授权" if usable != "可用" else "✅ 在用",
                    "folocli timeline 只读拉取（fetch_folo.py，不标已读/不改订阅）",
                    "2026-11-05 接入：官方 Agent skill（api.folo.is/skill.md）+ 稳定 JSON 信封；"
                    "登录一次即全池可用，无需逐站对接；未登录时软降级不阻断日报",
                    usable, ev,
                ],
            })
            continue
        usable, ev = usable_and_evidence(sid, s, h, p if p and p.get("ok") else None)
        st = stars(s.get("tier", "A"), s.get("weight", 1.0), s.get("tier") != "X", adopted)
        cat = CAT_LABEL.get(s.get("category_hint") or "", s.get("category_hint") or "未分类")
        rows.setdefault(cat, []).append({
            "sort": (0 if s.get("enabled") and s["tier"] != "X" else
                     1 if s["tier"] != "X" else 2, -st),
            "cells": [
                cat, s["name"], cell(s["url"]), TECH_OVERRIDE.get(sid, KIND_TECH.get(s.get("kind"), s.get("kind", ""))),
                "⭐" * st, clean(s.get("note") or f"Tier {s['tier']}，{s.get('kind', 'rss')} 源", 100),
                adopt_state(s), adopt_method(s), decide_reason(s, h), usable, ev,
            ],
        })

    # 候选池里未晋升登记的部分（重复跳过 / 探测失败）
    for cid, c in cands.items():
        if cid in seen:
            continue
        p = probes.get(cid, {})
        usable, ev = usable_and_evidence(cid, c, {}, p)
        cat_key = c.get("cat") or "community"
        cat = CAT_LABEL.get(cat_key, cat_key)
        if p.get("ok"):
            adopted_label = "📋 可用·未采纳（与在用源重复）"
            method = "—（不重复接入）"
            reason = ("三重体检可用，但与既有登记源内容完全重复，显式跳过以免同内容双份采集"
                      f"；来源：{c.get('from', '?')}")
            st = 4
        else:
            adopted_label = "❌ 不可用·未采纳"
            method = "—（无自动化接入通道）"
            reason = (f"探测被拒（{clean(p.get('reason'), 60)}）。"
                      f"来源：{c.get('from', '?')}；有免账户替代的见 docs/14 §4.5")
            st = 1
        rows.setdefault(cat, []).append({
            "sort": (3 if p.get("ok") else 4, -st),
            "cells": [
                cat, c["name"], cell(c["url"]),
                KIND_TECH.get(c.get("kind"), c.get("kind", "")),
                "⭐" * st, clean(c.get("from", ""), 60) and f"候选池来源：{c.get('from', '')}",
                adopted_label, method, reason, usable, ev,
            ],
        })
    return rows


HEADER = """# 数据源全量归档总表

> 本文档汇总本项目**调研过的所有数据源**（在用、已登记暂禁用、检测可用但未采纳、
> 检测不可用/失效留证），一行一源，作为信源决策的完整档案。
> 生成方式：`python scripts/gen_source_archive.py --date {date}`（只读合并
> `config/sources.json` + `config/candidates.json` + 当日探测/体检报告），可重复再生成。

## 图例

- **是否采纳**：`✅ 在用`＝启用抓取并进入日报链路；`⏸ 已登记·暂禁用`＝保留配置与证据、
  当前不抓取（限流/失效/待凭据）；`📋 可用·未采纳`＝三重体检通过但因重复等原因不接；
  `❌ 不可用/失效`＝实测被拒或死链（保留防重复踩坑）。
- **星级**：⭐⭐⭐⭐⭐ Tier A 官方/权威主源；⭐⭐⭐⭐ Tier B / 稳定补充；
  ⭐⭐⭐ Tier C（内容有价值但接入通道脆弱，整源降级不阻断）；⭐⭐ 登记源最近体检异常（观察）；
  ⭐ 失效或被拒。
- **技术类别**：Feed＝RSS/Atom 直连；API＝公开 JSON 接口（含逆向的匿名 POST）；
  Website＝HTML 解析或渲染代理。
- **检测证据**：来自 `reports/candidate-probe-{date}.json`（HTTP 状态 + 内容类型 +
  实际解析条目数 + 样题）或 `reports/source-health-{date}.json`（状态 + 响应体 feed 性校验）。

## 统计

"""

COLS = ("内容类别", "资讯来源名称", "相关URL", "资源来源技术类别", "资讯质量星级", "评价",
        "是否采纳", "采纳方式", "采纳决策原因", "检测是否可用", "检测证据")

CAT_ORDER = ["模型与研究", "Agent 与工程", "开发者工具与版本", "论文与学术", "文档与变更",
             "产业与资本", "市场与投资", "安全与治理", "社区与观点", "深度长文"]


def main() -> int:
    ap = argparse.ArgumentParser(description="生成数据源全量归档表")
    add_date_arg(ap)
    ap.add_argument("--out", default=str(OUT))
    args = ap.parse_args()
    setup_logging(args.verbose)
    data = load_all(args.date)
    rows = build_rows(data)

    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    state_counter = Counter()
    for lst in rows.values():
        for r in lst:
            state_counter[r["cells"][6].split("（")[0]] += 1
    total = sum(len(v) for v in rows.values())

    lines = [HEADER.format(date=args.date)]
    lines.append(f"- 归档总量：**{total} 个数据源**（登记源 {len(data['sources'])} + "
                 f"候选池未晋升 {total - len(data['sources'])}）")
    for k in ("✅ 在用", "⏸ 已登记·暂禁用", "📋 可用·未采纳", "❌ 不可用·未采纳", "❌ 失效留证"):
        if state_counter.get(k):
            lines.append(f"- {k}：{state_counter[k]}")
    lines.append("")

    ordered = [c for c in CAT_ORDER if c in rows] + [c for c in sorted(rows) if c not in CAT_ORDER]
    for cat in ordered:
        lst = sorted(rows[cat], key=lambda r: r["sort"])
        lines.append(f"## {cat}（{len(lst)}）")
        lines.append("")
        lines.append("| " + " | ".join(COLS) + " |")
        lines.append("|" + "---|" * len(COLS))
        for r in lst:
            lines.append("| " + " | ".join(str(x) for x in r["cells"]) + " |")
        lines.append("")

    lines.append("---")
    lines.append(f"*数据来源：config/sources.json（{len(data['sources'])}）、"
                 f"config/candidates.json（{len(data['candidates'])}）、"
                 f"reports/candidate-probe-{args.date}.json、"
                 f"reports/source-health-{args.date}.json；"
                 f"生成脚本 scripts/gen_source_archive.py。*")
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"written {out} rows={total} cats={len(ordered)}")
    print("states:", dict(state_counter))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
