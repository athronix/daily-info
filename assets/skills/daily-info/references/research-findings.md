# 四个参考仓库研究结论（含证据强度分级）

研究对象（2026-11-04 本地浅克隆 + 源码级通读）：
`kejun/daily-rss`、`kejun/daily-investor`、`kejun/blogpost`、`kejun/docs-feed`。
四个仓库同日仍在更新，是一套真实运行中的个人信息系统。

## 1. 一句话总览：四仓库其实是一条流水线

```
外部 Agent/Cron（采集·写作·行情，代码不在仓库内）
   ↓ git push
[内容层] daily-rss 技术日报 / blogpost 深度文章 / daily-investor 投资观察+AI 创意
         —— 纯 Markdown 产物仓库，按日期组织，Git 即发布载体
   ↓ docs-feed 单向 pull（feed.json 配 source，要求完整 git 历史）
[聚合层] docs-feed：Markdown → 消毒 HTML 全文 → 单一 Atom 1.0 feed（max 100）
   ↓ Raw 静态地址
[订阅层] RSS/Atom 阅读器
```

**重要认知纠正**：`docs-feed` **不是**「追踪官方文档 / changelog 的变更检测器」，
也不调用 GitHub Releases API；它是把作者自己三个仓库的 Markdown 聚合成一个全文 Atom 源。
产物文件名 `releases.atom` 极易误导（README 第 7 行专门澄清）。

## 2. 逐仓库关键事实

### daily-rss（技术日报）
- 257 个被追踪文件**全部是 .md**（256 篇日报 + README），**零代码、零配置、零 workflow**。
- 目录 `2026/MM/YYYY-MM-DD.md`；2026-02-13 ~ 11-04 共 265 天产出 256 篇，缺刊 9 天，覆盖率 **96.6%**。
- README 是一份隐式 prompt 契约：6–8 个核心主题、GitHub Trending Top 8、HN Top 5、
  10–15 条 LLM 动态、3–5 条融资、≥3 篇深度、2–3 篇论文、500–600 字编者观察、
  5000–7000 字、**所有条目必须带原文链接**。
- 信源分层：核心 5 / 深度媒体 6 / 行业研究 9 / Newsletter 5 / 学术 2 = **27 源**；
  最新一期自述 29 信源、原始约 430 条 → 去重后入选 96 条（压缩比约 4.5:1）。
- 调度在外部 OpenClaw Cron，README 说 06:30 CST、footer 实际多为 06:00 CST，口径不一致。
- 生成端无自研反爬/重试：遇 404/429 就「换源 / HTML 直抓 / API 近似 / 正文标注缺失」。
- **订阅是短板**：仓库自身不产 feed、无 HTML、无邮件、无 API；文中给的 RSS 链接是上游 Karpathy 源。

### daily-investor（投资观察 + AI 创意）
- 361 个 .md：`ideas/` 223 篇（每日 07:00 生成）、`observations/` 137 篇（美股收盘日报，08:00 北京）。
- 同样是**零生成代码**：README、依赖清单、写作 prompt 全无；生成在外部 Hermes Agent / cron。
- 唯一可读程序逻辑是手动触发的 `report-evidence-audit` pilot（gh-aw v0.89.21 / Codex
  `gpt-5.1-codex-mini`），**默认未启用付费运行**、staged 只预览不建 issue。
- 最值得抄的是它的**反幻觉 prompt 工程**：全文视为 untrusted data、禁执行/联网/改文件、
  逐行覆盖台账、claim ID + 精确行范围、区分事实/内部算术/标注推断/无依据解读、
  无独立证据一律 `UNVERIFIED`、禁止模型知识补洞、no-findings 也声明外部事实未验证。
- 生成侧「不编造」文化：取不到写「暂无可靠数据」、估算显式标注、单源值弃用、
  多源恒等式交叉核对（SPY×10≈SPX 等）、Firecrawl 402 → RSS + 直连降级、cron 被杀 → 反思会话补录。
- 固定章节模板（0–16 章）当隐式输出 schema；第 16 章「行业/技术趋势独立分析」+
  16.1「数据库/容量规划视角」是**个人化 prompt** 的范例。
- 缺陷：目录格式 4 种并存、同日双份、时间窗口漂移、纯自由文本无结构化字段、
  审计 pilot 自承 `NO_INDEPENDENT_SOURCE_SNAPSHOTS`。

### blogpost（深度文章库）
- 333 篇文章（297 篇 `YYYY-MM-DD-slug.md`，36 篇非日期命名），8.7 个月约 7.9 MB，
  由 OpenClaw Agent「小R」自动生成并经人工审核；仓库本身即发布载体，无构建、无 SSG。
- **核心架构原则**（`docs/translation-fidelity-pilot.md` 明写）：
  「目录工作继续使用确定性脚本」→ 统计/索引/分类/排序绝不让 LLM 参与，保证可复现、零成本、可 diff。
- 文章模板统一：H1 → 数据化导语 blockquote → 中文编号章节（264/297 用 `## 一、`）
  → 表格/架构图 → `## 参考资料` → 生成声明；来源可追溯 + 系列内部互链。
- `scripts/update_readme.py` 用文件名关键词硬编码分类，误分类明显（投资文落「其他」），
  README 分类表 289 ≠ 实际 328，索引需手工跑、易漂移。
- 译文忠实度审计 pilot：96 KiB / 6000 B / 24 块预算、SHA256、`L{n}:` 行号前缀、
  路径穿越/符号链接校验、把输入当不可信数据、超限报 `INCOMPLETE`、staged 只预览。

### docs-feed（聚合为 Atom）
- 10 个文件、3 个依赖（Markdown / bleach / webencodings）、Python 3.11+、GitHub Actions，
  `cron '30 0 * * *'`（UTC）= 北京 08:30，零服务器、零 API Key。
- 变更检测**不做内容 diff**：`git log --format=%x1e%ct --name-only -z --no-renames
  --diff-filter=AMT HEAD` 取每文件首次/末次提交时间作 `published`/`updated`。
  好处是「定时检查本身不改变订阅时间」，代价是**必须 `fetch-depth: 0` 完整克隆**。
- 「增量更新」实为**全量确定性重建 + 幂等写入**：排序带 tie-break、消毒白名单、
  `xml_text` 清控制字符 → 内容不变则字节不变 → `read_bytes()==content` 跳过写入 →
  `.tmp → replace` 原子替换 → `git diff --cached --quiet` 决定不提交。
- 13 个单测覆盖确定性、编辑保留 ID、消毒、失败保留旧产物、push 竞态 3 次重试。
- 实测 `releases.atom` 3.9 MB / 100 条：blogpost 41、daily-investor/ideas 30、daily-rss 29。
- 缺陷：100 条硬截断无归档、无内容级 diff、摘要是纯机械截断 300 字（非摘要）、
  无 LLM、URL 硬编码 `main`、单 feed、无观测告警。

## 3. 可复用要点（本方案逐条落地）

1. **产物即仓库 + 按日期分目录**（daily-rss / daily-investor）→ `data/digest/<date>/`，永久保留、Git 可 diff。
2. **固定板块契约当隐式输出 schema**（daily-rss README / daily-investor 0–16 章）→ `ai-review.schema.json` + 板块 key 枚举。
3. **确定性脚本做索引、生成式模型只做内容**（blogpost）→ AI 边界画在 `prompt-input.json` 之后。
4. **主题聚合而非罗列**（daily-rss）→ 并查集聚类 + 多源互证加分。
5. **全量确定性重建 + 幂等写入 + 原子替换**（docs-feed）→ `write_json` / `write_bytes_idempotent` / V5 核验。
6. **稳定 entry id**（docs-feed）→ `tag:daily-info.local,{date}:{cluster_id}`。
7. **反幻觉 / 证据优先 prompt**（daily-investor）→ `assets/prompts/evidence-audit.md`。
8. **不编造 + 显式缺失标记**（daily-investor）→ `暂无可靠数据`、降级出报。
9. **把 pipeline 健康度写进产物**（daily-rss「今日数据概览」）→ `digest.stats` + `run-log.jsonl`。
10. **个人化视角**（daily-investor 第 16 章）→ `tags.user_focus` + 编者观察锚定用户当前工作。
11. **内容层 / 订阅层解耦**（daily-rss → docs-feed）→ digest.json 唯一事实源，feed 全量投影。
12. **配置驱动多源**（docs-feed feed.json）→ `config/sources.json` 带 tier / weight / health。

## 4. 本方案针对性补齐的缺口

| 参考仓库的坑 | 本方案补法 |
| --- | --- |
| 生成逻辑全在外部 Agent，仓库只有产物、不可复现 | 全部规则层脚本入库，配置化，可离线重放 |
| 源长期带病（404/429/空 feed）只在正文标注 | `check_sources.py` 每周体检 + tier X 隔离 + 自动整源降级 + 健康报告 |
| 模板 9 个月漂移 4 次、无 schema | `digest.json` + JSON Schema 强约束，站点只读 JSON |
| 无自产订阅/站点/邮件/API | 5 个 Atom profile + JSON Feed + 静态站 + 邮件 + 企业微信 + 资料库 |
| 纯机械截断摘要、无研判 | AI 主题命名 / why_matters / 编者观察，且白名单约束不编造 |
| 100 条硬截断、无历史留存 | digest 永久保留，feed 只做投影视图 |
| 时间口径三套（文件名 / 文内 / git） | 统一 UTC ISO8601，业务日期单独字段 |
| **公开 Atom 可能二次扩散明文密钥** | 发布前凭据正则扫描，命中整体拒发；HTML 自建标签 + 全量 escape |
| 摘要/事实无独立证据，易把「格式正确」当「事实为真」 | 核验闸门只判结构与安全；另设只读证据审计 prompt，状态恒为 UNVERIFIED |

## 5. 证据强度分级（避免过度推断）

| 级别 | 含义 | 例子 |
| --- | --- | --- |
| **A · 直证** | 仓库内代码 / 配置 / workflow / 产物可复核 | docs-feed `feed.json` 的 sources；`generate_feed.py:72-81` 的 git log；blogpost `update_readme.py`；信源实测 HTTP 状态 |
| **B · 产物自述** | 由生成日报的 AI 写入正文的描述，无源码佐证 | daily-rss 的 27 源清单、去重压缩比、OpenClaw Cron 06:00；daily-investor 的 Firecrawl 402 降级、反思会话补录 |
| **C · 跨仓库推断** | 同作者 / 同署名 / 同节奏的合理推断，**无双向直证** | 「daily-rss → OpenClaw 写作 → blogpost 成文」；外部 Agent 的具体模型与编排 |

**必须标注为 C 的内容**：daily-rss 与 blogpost 之间无直接引用（daily-rss 全库检索
`blogpost|docs-feed|releases.atom` 零命中），只有 blogpost 侧把三仓库并列为配套 + 同署名「小R」+ 同每日节奏。
汇总时写「推断」，**不要写成已验证 pipeline**。

**已确认的单向关系**（A 级）：`docs-feed` 单向消费 `daily-rss` / `blogpost` / `daily-investor`，
配置在 docs-feed 侧；三个上游仓库内均无反向引用——这是解耦设计的应有表现，不是「无关联」。

## 6. 交叉校验修正记录（汇总时以此为准）

1. docs-feed 的真实职责 = 聚合自有仓库 Markdown → Atom，不是官方文档变更监控。
2. blogpost ↔ docs-feed 为 **blogpost → docs-feed 单向**；blogpost 是产量最大的来源（41/100）。
3. `prefix:""` 理论全库收录，但 `max_entries=100` + `updated` 倒序截断，
   使 blogpost 41 条全是 2026-09-30 之后的日期命名文章，旧元文档被挤出。
4. **密钥风险（条件触发，非已泄漏）**：`blogpost/finnhub-integration-complete.md` 明文含
   `FINNHUB_API_KEY` 与 GitHub token 的 `credential.helper` 写法，且不在 docs-feed 的 blogpost
   专属排除清单里；当前 `releases.atom` 全量 grep 相关关键词 **0 命中**。
   一旦这些元文档被编辑刷新 `updated`、调大 `max_entries` 或源文档减少，就会被全文收进公开 Atom。
   `bleach.clean` 只做标签白名单，**不扫正文密钥**。
5. 日期口径差异：blogpost `update_readme.py` 从文件名解析日期（36 篇非日期文件回退 git log 或写死
   `"2026-02"`），docs-feed 一律用 git 提交历史；同一内容库上下游两套口径。
6. 浅克隆冲突：docs-feed 判定 `published/updated` 依赖完整 git 历史（`fetch-depth: 0`）；
   本地研究副本均为 `--depth 1` 单提交快照，不能用来评估真实活跃度，也不能直接喂给聚合层。
7. 抓取策略不可混用：daily-rss 以 **RSS 为主**（27 源，失效则换源/HTML/API 近似）；
   daily-investor 以 **Firecrawl / 行情 API 为主**（RSS 是 402 额度耗尽后的兜底，另有多源交叉核对）。
   daily-rss 的 arXiv 是 HTML 列表页而非 RSS；X/Twitter 在 daily-rss 是正文引用链接（x.com 120 次）
   而非订阅源；Product Hunt / Techmeme 不在 daily-rss 源清单。
