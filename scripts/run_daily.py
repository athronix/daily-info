#!/usr/bin/env python3
"""一键编排：把 7 个确定性步骤串成一条可重放流水线。

  run_daily.py --date 2026-11-04
      1 fetch_sources.py      采集（可 --skip-fetch 复用已有 raw 快照）
      2 normalize.py          归一化 + 规则分类 + 时间窗
      3 dedupe_cluster.py     去重聚类 + 打分 + 生成 prompt-input.json
      ---- AI 边界 ----
      4 (WorkBuddy Agent)     读 prompt-input.json，按 assets/prompts/daily-digest.md
                              写回 data/digest/<date>/ai-review.json
                              脚本不调用 LLM；缺文件时自动走规则降级
      5 make_digest.py        合成唯一事实源 digest.json + digest.md + brief.md
      6 build_feeds.py        Atom / JSON Feed / 5 个订阅 profile
      7 build_site.py         站点 JSON 切片
      8 verify_digest.py      独立核验闸门
      9 push_daily.py --dry-run  分发计划（仅出计划，不写 push-log、不对外发送）

  run_daily.py --offline-demo   不联网、不调 LLM，用内置样例数据完整跑通全链路（用于 smoke）
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ROOT, add_date_arg, day_dir, load_config, read_json, setup_logging, write_json, LOG

SCRIPTS = ROOT / "scripts"
# 离线演示条目：每条都带可核验数字与实体，用于验证七要素白名单（数字必须能在原文找到）
DEMO_ITEMS = [
    ("tldr-ai", "MCP 规范 v2.6 新增结构化工具结果字段，3 个 SDK 需适配", "ai-models", "https://tldr.tech/ai/2026-11-04-mcp-tool-result", 1.0),
    ("hf-blog", "Hugging Face 开源推理吞吐基准覆盖 12 个模型，QPS 提升 37%", "ai-models", "https://huggingface.co/blog/inference-benchmark-2026", 1.1),
    ("hn-algolia", "Show HN：本地优先 Agent 记忆层，815 分 266 评论", "agent-engineering", "https://news.ycombinator.com/item?id=41001", 1.0),
    ("github-blog", "GitHub Actions 并发组语义变更，影响 5 类定时任务", "dev-tools", "https://github.blog/changelog/2026-11-04-concurrency", 0.9),
    ("gh-releases-claude-code", "claude-code v2.1.0 Release 发布 18 项变更", "docs-changelog", "https://github.com/anthropics/claude-code/releases/tag/v2.1.0", 1.2),
    ("arxiv-cs-ai", "arXiv 2611.00001：多智能体长程任务上下文压缩 42%", "research-papers", "https://arxiv.org/abs/2611.00001", 0.8),
    ("interconnects", "Interconnects 长文：开源与闭源成本交叉点测算 2.3 倍差距", "deep-read", "https://www.interconnects.ai/p/cost-crossover", 1.2),
    ("techcrunch-ai", "AI 基础设施公司完成 13 亿美元 D 轮融资，估值 160 亿美元", "industry-capital", "https://techcrunch.com/2026/11/04/ai-infra-funding", 1.0),
    ("cnbc-markets", "美股收盘标普涨 0.36%，VIX 回落至 20.83", "market-invest", "https://www.cnbc.com/2026/11/04/markets-close.html", 0.9),
    ("qbitai", "国内团队开源多模态评测集，含 8 类任务 1200 道题", "ai-models", "https://www.qbitai.com/2026/11/multimodal-eval", 0.8),
    ("solidot", "供应链投毒复盘：恶意依赖包影响 27 个项目", "security-governance", "https://www.solidot.org/story?sid=81001", 0.7),
    ("mit-tr-ai", "MIT Technology Review：Agent 可观测性覆盖 800+ MCP server", "agent-engineering", "https://www.technologyreview.com/2026/11/04/agent-observability", 1.1),
]


def step(name: str, args: list[str]) -> bool:
    cmd = [sys.executable, str(SCRIPTS / name), *args]
    LOG.info("→ %s %s", name, " ".join(args))
    r = subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, encoding="utf-8", errors="replace")
    if r.stdout.strip():
        print(r.stdout.strip())
    if r.returncode != 0:
        LOG.warning("%s 返回 %d（流水线继续，降级标记会被写入产物）\n%s",
                    name, r.returncode, (r.stderr or "")[-800:])
        return False
    return True


def seed_demo(date: str) -> None:
    """造 12 条可重放样例，覆盖多分类、多信源、指标与中英文。"""
    raw = day_dir("raw", date)
    now = datetime.now(timezone.utc)
    by_sid: dict[str, list[dict]] = {}
    cfg = load_config("sources.json")
    meta = {s["id"]: s for s in cfg["sources"]}
    for i, (sid, title, cat, url, w) in enumerate(DEMO_ITEMS):
        sname = meta.get(sid, {}).get("name", sid)
        by_sid.setdefault(sid, []).append({
            "guid": f"demo-{i}", "title": title, "url": url,
            "summary": f"{title}。来源 {sname}。这是用于端到端 smoke 的本地样例内容，不含外部事实主张。",
            "published_raw": (now - timedelta(hours=2 + i)).isoformat().replace("+00:00", "Z"),
            "metrics": {"hn_points": 120 + i * 7, "comments": 30 + i} if sid == "hn-algolia" else {},
        })
    for sid, items in by_sid.items():
        s = meta.get(sid, {})
        write_json(raw / f"{sid}.json", {
            "source_id": sid, "source_name": s.get("name", sid),
            "tier": s.get("tier", "A"), "kind": s.get("kind", "rss"),
            "url": s.get("url", ""), "fetched_at": now.isoformat().replace("+00:00", "Z"),
            "category_hint": s.get("category_hint"), "weight": s.get("weight", 1.0),
            "items": items, "parse_ok": True, "status": 200, "demo": True,
        })
    write_json(raw / "_summary.json", {"date": date, "demo": True, "enabled": len(by_sid),
                                       "ok": len(by_sid), "failed": 0,
                                       "total_items": len(DEMO_ITEMS), "failed_sources": []})


def seed_ai_review(date: str) -> None:
    """模拟 Agent 写回的 v2 ai-review.json：七要素齐全，且数字/实体/URL 均来自原文白名单。"""
    import re
    clusters = read_json(day_dir("candidate", date) / "clusters.json", {})
    cs = clusters.get("clusters", [])
    picked = cs[:10]
    num_re = re.compile(r"\d[\d,.]*%?")

    def numbers_of(member: dict) -> list[str]:
        text = f"{member.get('title', '')} {member.get('summary_raw', '')}"
        seen: set[str] = set()
        vals = []
        for n in num_re.findall(text):
            if n not in seen:
                seen.add(n)
                vals.append(n)
            if len(vals) >= 2:
                break
        return vals or ["1"]

    # 按分类给差异化解读，演示「丰富」而不是同一句模板复读
    copy = {
        "ai-models": ("模型侧的接口或评测口径发生变化，需确认是否影响现有调用链。",
                      "影响 WorkBuddy 的模型接入层：若输出结构变化，归一化与摘要脚本要同步改。",
                      "对照该版本接口的 2 个字段做一次兼容测试，0 报错才判定可接入。"),
        "agent-engineering": ("Agent 记忆与编排出现新的工程约定，值得对照当前实现。",
                              "与 MCP / A2A / skill 编排直接相关：上下文注入方式可能要调整。",
                              "复现该方案并统计上下文 token，若降幅低于 30% 则判定不值得迁移。"),
        "dev-tools": ("工具链的语义变更会直接影响定时任务的并发行为。",
                      "影响 run_daily.py 的并发与幂等假设，需核对并发组配置。",
                      "跑两次 build_site.py，若字节哈希一致（changed=0）才判定幂等未受损。"),
        "docs-changelog": ("Release 变更若被新闻流淹没容易漏读，应单独订阅。",
                           "影响 docs.atom 订阅入口，需把新增字段纳入变更雷达。",
                           "对照 release notes 的 3 个 breaking 项逐条核验后才升级依赖。"),
        "research-papers": ("该研究把长程任务的上下文成本量化，可用于评估本地方案。",
                            "对 WinVM Bridge 的长会话状态管理有参考价值。",
                            "用 1 组真实轨迹复现实验，误差超过 10% 则判定结论不可迁移。"),
        "industry-capital": ("融资规模反映基础设施层的定价权正在转移。",
                             "间接影响自建 vs 托管的成本比较，需更新成本模型。",
                             "把该估值代入成本表，若 12 个月 TCO 差距 > 20% 则重算选型。"),
        "market-invest": ("宏观读数与板块分化同时出现，需要区分反弹与趋势。",
                          "仅作信息聚合，不产生任何仓位或交易判断。",
                          "若广度指标连续 2 日未转正，则在日报中明确标注「未确认」。"),
        "security-governance": ("供应链风险从模型侧转移到工具侧，影响面更贴近日常开发。",
                                "提醒在 skill 与 MCP 工具接入前做依赖扫描。",
                                "对新增依赖跑一次凭据与 CVE 扫描，命中 1 项即拒绝接入。"),
        "community": ("社区讨论给出了可复现的一手实践，而非厂商宣传口径。",
                      "可作为 automation 与 skill 设计的对照样本。",
                      "按帖子步骤复现，若 1 次跑通则收录进参考文件。"),
        "deep-read": ("长文提供了跨周期的成本对照，适合作为周报输入。",
                      "影响下一轮采集权重与分类阈值的设定。",
                      "统计文中 5 个关键数字并与本月日报对照，偏差 > 15% 则标注存疑。"),
    }
    default_copy = ("该条目给出了可核验的具体读数，适合作为当日主线佐证。",
                    "与当前个人信息流水线相关，需评估是否纳入长期跟踪。",
                    "对照原文 2 个字段复核后，再决定是否加入 watchlist。")
    by_cat: dict[str, list[dict]] = {}
    for c in picked:
        m = c["members"][0]
        why, impact, action = copy.get(c["category"], default_copy)
        sname = (m.get("source_name", "") or "本地样例")[:24]
        by_cat.setdefault(c["category"], []).append({
            "id": c["cluster_id"],
            "fact_anchor": m.get("title", "")[:120],
            "numbers": numbers_of(m),
            "entities": [sname],
            "evidence_urls": [m.get("url", "")] if m.get("url", "").startswith("http") else [],
            "why_matters": why,
            "impact": impact,
            "next_action": action,
            "signal_type": "release", "confidence": "fact",
        })
    labels = {c["key"]: c["label"] for c in load_config("taxonomy.json")["categories"]}
    sections = [{"key": k, "label": labels.get(k, k), "items": v} for k, v in by_cat.items()]
    ids = [c["cluster_id"] for c in picked]
    lead_nums = [numbers_of(c["members"][0])[0] for c in picked[:3]] or ["0"]
    theme_specs = [
        ("Agent 工程栈开始收敛到同一套接口", "工具结果、记忆层与可观测性在同一天出现多条独立进展。"),
        ("文档变更不该混在新闻流里", "Release 与平台语义变更需要独立的订阅入口才不会漏读。"),
        ("数字比形容词更能说明进展", "多数条目都给出了可核验的版本、分数或规模读数。"),
        ("安全事件正在从模型转向工具链", "投毒与权限边界成为比模型能力更现实的工程风险。"),
        ("成本曲线决定开源与闭源的位置", "推理成本与本地硬件能力共同决定可落地的方案。"),
        ("个性化视角让日报不是资讯堆砌", "把通用进展落到本职工作的具体判断，才有决策价值。"),
    ]
    themes = [{"title": t, "why": w, "cluster_ids": [ids[i % len(ids)], ids[(i + 1) % len(ids)]]}
              for i, (t, w) in enumerate(theme_specs)]
    editor_note = (
        "本日为离线演示数据，目的是验证「采集 → 归一 → 去重聚类 → AI 研判 → 唯一事实源 → 站点与订阅 → 独立核验」"
        "这条链路在有完整七要素时依然可以端到端跑通，而不是验证新闻内容本身。今天最值得记录的方法论变化是："
        "内容质量第一次变成了可检查的结构，而不是靠模型自觉。每条内容都必须写明事实锚点、可核验数字、关键实体、"
        "原文佐证、为什么值得看、对我意味着什么，以及带判定阈值的下一步动作；数字、实体和链接会被下游逐项拿回原文比对，"
        "对不上的直接丢弃并记入 warnings。这样一来，「具体」不再是一种文风要求，而是一道程序闸门。"
        "对当前手头的 WorkBuddy、MCP、A2A 与 skill 自动化工作来说，最有价值的推论是：把内容契约写进配置与 JSON Schema，"
        "比在提示词里反复强调「不要编造」更可靠；因为前者能被脚本验证，后者只能被祈祷。三份参考语料给出的基准也很清楚，"
        "技术日报约四成行含数字、投资日报接近一半，且所有产物都有加粗判断句和列表条目——这说明高密度信息是可复制的工程习惯，"
        "不是灵感。下一步可验证的动作是：用真实信源跑一次完整日报，比较七要素达标率、引用域名数与降级次数，"
        "若达标率低于八成，应回头检查信源摘要是否过短，而不是放宽校验阈值。最后必须提醒，本站所有外部事实均未独立验证，"
        "核验通过只代表结构、白名单、安全与幂等通过，不代表新闻为真。"
    )
    write_json(day_dir("digest", date) / "ai-review.json", {
        "date": date, "demo": True,
        "headline": "Agent 工程化与文档变更成为今日双主线",
        "lead": f"今日 {len(picked)} 条演示条目出现 {' / '.join(lead_nums)} 等可核验读数，"
                f"说明「具体」可以被程序逐项校验；主线集中在 Agent 接口收敛与文档变更单独订阅两条线。",
        "themes": themes,
        "sections": sections,
        "editor_note": editor_note[:600],
        "brief": "离线演示：Agent 工程化与文档变更为今日两条主线；七要素齐全，数字均来自原文。",
        "watch_signals": [
            {"signal": "七要素达标率", "threshold": "低于 80% 即判定不合格",
             "judgement": "检查信源摘要长度，不放宽校验阈值"},
            {"signal": "真实信源可用率", "threshold": "低于 70% 触发降级出报",
             "judgement": "日报 headline 加 [降级]，不生成编者观察"},
            {"signal": "发布前凭据扫描", "threshold": "命中 1 处即拒发",
             "judgement": "保留旧产物并排查上游明文密钥"},
        ],
    })


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    add_date_arg(ap)
    ap.add_argument("--offline-demo", action="store_true", help="不联网、不调 LLM，造样例跑通全链路")
    ap.add_argument("--skip-fetch", action="store_true", help="复用已有 raw 快照")
    ap.add_argument("--skip-verify", action="store_true")
    ap.add_argument("--base-url", default="https://daily-info.local")
    args = ap.parse_args()
    setup_logging(args.verbose)

    common = ["--date", args.date]
    if args.offline_demo:
        LOG.info("离线演示模式：生成样例 raw / ai-review，跳过联网与 LLM")
        seed_demo(args.date)
    elif not args.skip_fetch:
        step("fetch_sources.py", common)
        # Folo 订阅池基线层（用户人工筛选的信源；未登录时软降级不阻断）
        step("fetch_folo.py", common)

    norm_args = common + (["--demo"] if args.offline_demo else [])
    if not step("normalize.py", norm_args):
        LOG.error("归一化失败，终止")
        return 1
    if not step("dedupe_cluster.py", common):
        LOG.error("聚类失败，终止")
        return 1

    if args.offline_demo:
        seed_ai_review(args.date)
    ai_file = day_dir("digest", args.date) / "ai-review.json"
    digest_args = common if ai_file.exists() else common + ["--fallback"]
    if not ai_file.exists():
        LOG.warning("未发现 ai-review.json → 规则降级出报（请在定时任务里由 Agent 写回该文件）")
    step("make_digest.py", digest_args)
    step("build_feeds.py", common + ["--base-url", args.base_url])
    step("build_site.py", common)
    if not args.skip_verify:
        v = step("verify_digest.py", common)
        if not v:
            LOG.error("核验未通过，请查看 reports/verify-%s.md", args.date)
            return 1
        # P1：核验通过后才出分发计划；默认 dry-run，不生成 payload、不调用外部工具
        step("push_daily.py", common + ["--dry-run"])
    LOG.info("流水线完成 · %s", args.date)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
