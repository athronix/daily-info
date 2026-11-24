# 省 37% token 不等于更快，89.1 分不等于可用：今天能进部署门禁的是版本号、组件数与带条件的规格，不是漂亮的百分比

> 今日最硬的两个读数都带条件：Claude Code 的 Code Mode 社区实测大任务省 37% token 却不更快，v2.1.331 才把它落到 Bedrock 与 Foundry 的终端会话；Phonic-1.1 以 89.1 分登顶 Artificial Analysis 语音指数，Everything Claude Code 则打包 67 个 agents、281 个 skills、94 条 commands。

> 2026-11-24 · 北京时间 · 生成于 2026-11-24T01:58:57.872346Z

## 📌 今日速览

- **GitHub 项目 davinci-resolve-mcp 提供 DaVinci Resolve Studio 的 MCP server 集成，摘要列出 Stars 4,313、Forks 493。**（4,313, 493） — 4,313 与 493 是仓库热度，不是功能完成度；MCP server 能否稳定驱动剪辑工程，摘要没有给出任何调用成功率或延迟。
- **dev.to 文章盘点走红的一体化套件 Everything Claude Code，摘要称打包 67 个 agents、281 个 skills、94 条 commands 与扫描器 AgentShield。**（67, 281） — 67/281/94 是可清点的组件数，但文章标题本身在问「该不该全装」；数量多与适配当前 workflow 是两件事。
- **智源社区快讯：旧金山公司 Phonic 发布 Phonic-1.1，称以 89.1 分登顶 Artificial Analysis 语音对语音指数，距 Phonic 1 不到一个月。**（89.1, 1.1） — 89.1 是榜单分数，1.1 是版本号，不到一个月是迭代间隔；分数不带测试集与并发条件，不能直接换算成部署收益。
- **智源社区快讯：Anthropic 在 Claude Code v2.1.323 及以上加入实验性 Code Mode，模型写 JavaScript 编排工具调用，社区实测大任务省 37% token 但不更快。**（37%, 2.1.323） — 37% 是 token 降幅而「不更快」是耗时结论；同一实测给出方向相反的两个判断，正说明成本口径与体验口径不能合并。
- **MacRumors 报道 OpenAI 把 GPT-6.2 Sol 部署到 ChatGPT 的 Chat 标签页，面向 Plus、Pro 等付费档，称策略遵循率达 91–94 percent。**（91, 94） — 91–94 percent 是策略遵循率区间，不是能力总分；报道写明 Free 与 Go 套餐不在本次覆盖内，结论只对付费档成立。
- **claude-code 发布 v2.1.331：终端会话在 Bedrock、Microsoft Foundry 等平台加入 Code Mode 支持，并新增 oidc.groups_jsonpath 网关配置。**（2.1.331, 15） — 2.1.331 是可逐字锁定的版本号，oidc.groups_jsonpath 改变网关取组方式；15 秒无语音自动停录是行为阈值，三者量纲不同。

---

## 🔥 今日主线

### 一、省 token 与提速是两本账
Code Mode 社区实测大任务省 37% token 却不更快，同一天 v2.1.331 把它落到 Bedrock 与 Foundry；Codex 26.11 又改了会话接口。成本口径、体验口径、版本兼容性必须分开记。（3 条独立条目佐证）

### 二、可数清单比形容词可信
ECC 打包 67 agents、281 skills、94 commands，davinci-resolve-mcp 给出 4,313 stars 与 493 forks，Kiteline 3.49.52 是明确版本；能清点的数字才进门禁，走红与否不是依据。（3 条独立条目佐证）

### 三、版本号才进得了门禁
2.1.323 是 Code Mode 起效下限、2.1.331 是本次 release、3.49.52 与 26.11 是两端版本、Phonic-1.1 是迭代号；这些能逐字锁定的编号可写成扫描规则，分数与宣称不行。（4 条独立条目佐证）

### 四、分数和倍数都要带口径
Phonic-1.1 的 89.1 是榜单分数、GPT-6.2 Sol 的 91 与 94 是遵循率区间、英伟达 3.5 倍是产能宣称、Kagi 50GB 是公测规格；四种量纲，缺测试集或状态就不可比。（4 条独立条目佐证）

### 五、规格读数决定部署门槛
50GB 是存储上限、91–94 percent 只在付费档成立、14 年是观测窗口、2 million 是农户基数；读数都要绑定适用范围，越界使用就成了另一件事。（4 条独立条目佐证）

### 六、钱与指数是事实不是判断
Supertake 的 $20M 是融资额、马来西亚 17 年是距上次调整的年数、3.5 倍是厂商宣称；都只陈述公开数据与来源状态，不推资金流向，也不构成投资建议。（3 条独立条目佐证）

### 七、数字白名单挡住虚高统计
本期 40 簇主动剔除 27 簇：型号尾数、日期年份、listicle 计数、commit hash、HN 热度都不算原文读数；v1.1 把 published_at 排除后，留下的 13 条才经得起逐字复核。（4 条独立条目佐证）

---

## 🗂 分类聚合

### Agent 与工程（4 条）

**GitHub 项目 davinci-resolve-mcp 提供 DaVinci Resolve Studio 的 MCP server 集成，摘要列出 Stars 4,313、Forks 493。**
- 关键数字：4,313 / 493 · 相关方：davinci-resolve-mcp / MCP / DaVinci Resolve Studio / Python · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-24 00:03 UTC · 81.26 分
- 为什么值得看：4,313 与 493 是仓库热度，不是功能完成度；MCP server 能否稳定驱动剪辑工程，摘要没有给出任何调用成功率或延迟。
- 对我意味着什么：与 MCP 关注面直接相关：接入前要按工具清单逐个验证，Stars 只能当线索，不能当 WinVM 侧部署门禁的通过依据。
- 下一步：对照仓库 README 清点 2 次暴露的工具列表；若工具数与文档不一致或 smoke 调用失败 ≥ 1 次，则判定暂不接入 MCP 基线。
→ https://github.com/samuelgursky/davinci-resolve-mcp

**dev.to 文章盘点走红的一体化套件 Everything Claude Code，摘要称打包 67 个 agents、281 个 skills、94 条 commands 与扫描器 AgentShield。**
- 关键数字：67 / 281 / 94 · 相关方：Everything Claude Code / ECC / AgentShield / Claude Code · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-23 23:45 UTC · 81.05 分
- 为什么值得看：67/281/94 是可清点的组件数，但文章标题本身在问「该不该全装」；数量多与适配当前 workflow 是两件事。
- 对我意味着什么：对 skill 与 agent 部署最相关：这类 all-in-one kit 若整体装入，会与现有 namespace skills 冲突，应逐项比对再决定取用。
- 下一步：清点仓库 2 次核对 281 skills 与 94 commands；若任一数字与清单不符或重复 skill 名 ≥ 3 个，则判定不整体接入。
→ https://dev.to/dimsbuild/should-you-install-everything-claude-code-the-all-in-one-kit-gone-viral-2lme

**智源社区快讯：旧金山公司 Phonic 发布 Phonic-1.1，称以 89.1 分登顶 Artificial Analysis 语音对语音指数，距 Phonic 1 不到一个月。**
- 关键数字：89.1 / 1.1 · 相关方：Phonic / Phonic-1.1 / Artificial Analysis / speech-to-speech / agentic · 来源：智源社区 · 最新分享（匿名 API） · 2026-11-23 19:36 UTC · 76.9 分
- 为什么值得看：89.1 是榜单分数，1.1 是版本号，不到一个月是迭代间隔；分数不带测试集与并发条件，不能直接换算成部署收益。
- 对我意味着什么：对 agent 部署的语音链路是选型线索：面向 agentic 任务的 speech-to-speech 模型要按榜单口径、延迟、并发分列评估，先入线索池不进基线。
- 下一步：对照 Artificial Analysis 榜单 2 个版本核对 89.1；若测试集或评分版本未披露，则判定该分数仅作位次，不进选型矩阵。
- 证据状态：unverified（未独立验证）
→ https://arex-research.com/feeds/94fd0677-b44b-4434-80be-6d0d5fc6bc32

**智源社区快讯：Anthropic 在 Claude Code v2.1.323 及以上加入实验性 Code Mode，模型写 JavaScript 编排工具调用，社区实测大任务省 37% token 但不更快。**
- 关键数字：37% / 2.1.323 · 相关方：Anthropic / Claude Code / Code Mode / JavaScript / Bash · 来源：智源社区 · 最新分享（匿名 API） · 2026-11-23 19:26 UTC · 76.8 分
- 为什么值得看：37% 是 token 降幅而「不更快」是耗时结论；同一实测给出方向相反的两个判断，正说明成本口径与体验口径不能合并。
- 对我意味着什么：对 MCP 与 agent 部署最关键：工具编排方式直接影响子 agent 的上下文用量，但功能默认关闭、需设环境变量，接入前必须跑 smoke 对照。
- 下一步：同一批大任务在 2 个宿主各跑 3 次；若 token 降幅达 37% 而墙钟耗时未下降的次数 ≥ 2，则判定只算省成本、不写提速结论。
→ https://arex-research.com/feeds/d9ff3c57-fe11-446f-bc28-9af3ff4a5351

### 模型与研究（1 条）

**MacRumors 报道 OpenAI 把 GPT-6.2 Sol 部署到 ChatGPT 的 Chat 标签页，面向 Plus、Pro 等付费档，称策略遵循率达 91–94 percent。**
- 关键数字：91 / 94 · 相关方：OpenAI / GPT-6.2 Sol / ChatGPT / Codex / Plus · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-23 23:52 UTC · 78.13 分
- 为什么值得看：91–94 percent 是策略遵循率区间，不是能力总分；报道写明 Free 与 Go 套餐不在本次覆盖内，结论只对付费档成立。
- 对我意味着什么：对 agent 部署是分层提醒：模型可用范围与订阅档位绑定，选型表要标「可用档位」字段，不能把付费档读数当成全局基线。
- 下一步：核对 2 份官方安全评测是否给出 91 与 94 的测试集；若两值来自不同测试集，则判定区间不可合并，按测试集分列。
→ https://www.macrumors.com/2026/11/23/openai-gpt-6-2-sol-chatgpt

### 开发者工具与版本（2 条）

**claude-code 发布 v2.1.331：终端会话在 Bedrock、Microsoft Foundry 等平台加入 Code Mode 支持，并新增 oidc.groups_jsonpath 网关配置。**
- 关键数字：2.1.331 / 15 · 相关方：Code Mode / Amazon Bedrock / Microsoft Foundry / oidc.groups_jsonpath / claude doctor · 来源：claude-code Releases · 2026-11-23 21:34 UTC · 79.76 分
- 为什么值得看：2.1.331 是可逐字锁定的版本号，oidc.groups_jsonpath 改变网关取组方式；15 秒无语音自动停录是行为阈值，三者量纲不同。
- 对我意味着什么：对 automation 与 MCP 网关最相关：升级前要核对 oidc.groups_jsonpath 的 JSONPath 子集是否覆盖现有 group 字段，否则定时任务权限会错配。
- 下一步：在 2 个非交互宿主各跑 1 次 claude doctor；若 API 连通段缺失或 groups 解析失败 ≥ 1 次，则判定暂缓升级到 2.1.331。
→ https://github.com/anthropics/claude-code/releases/tag/v2.1.331

**dev.to 文章称 Codex desktop 26.11 停止向其它应用暴露会话控制，跟随该接口的第三方工具掉线，作者评估 Kiteline 3.49.52 的手机回复能力。**
- 关键数字：26.11 / 3.49.52 · 相关方：Codex desktop / Kiteline / Codex · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-24 00:10 UTC · 76.75 分
- 为什么值得看：26.11 与 3.49.52 是两端版本号；接口一变第三方就掉线，说明跨应用会话控制是未承诺的私有面，不是稳定契约。
- 对我意味着什么：对 agent 部署与 WinVM 桥接是同构风险：依赖宿主私有接口的自动化要有降级路径，不能把「能连上」当成长期保证。
- 下一步：在 2 台宿主各验证 1 次手机回复；若任一因 26.11 接口变更失败且无降级通道，则判定该链路不进自动化基线。
→ https://dev.to/hon6/replying-to-codex-desktop-2611-sessions-from-your-phone-what-kiteline-34952-can-and-cant-do-2ja7

### 产业与资本（2 条）

**TechCrunch 报道初创公司 Supertake 融资 $20M，产品让 AI agents 把用户的市场判断转成股票组合，用户无需自己挑个股。**
- 关键数字：$20M · 相关方：Supertake / AI agents / stock portfolios · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-23 22:02 UTC · 76.86 分
- 为什么值得看：$20M 是融资额，不是管理规模或收益；「把预测转成组合」是产品描述，原文没有给出任何回测或合规口径。
- 对我意味着什么：对 automation 是边界提醒：涉及持仓与组合生成的能力不纳入本任务评估范围，只记录融资金额这一公开事实，不构成任何投资建议。
- 下一步：核对 2 份一手融资公告是否确认 $20M；若仅媒体单方报道且无轮次信息，则判定金额标 unverified，只留线索池。
→ https://techcrunch.com/2026/11/23/supertake-raises-20m-to-let-ai-agents-turn-your-market-predictions-into-stock-portfolios

**智源社区快讯：英伟达宣布与 Amkor、Foxconn、Kinsus、TSMC 等扩大多年供应链承诺，标题称 Kinsus 桃园 ABF 载板产能将提高逾 3.5 倍。**
- 关键数字：3.5 · 相关方：英伟达 / Kinsus / ABF 载板 / Vera Rubin NVL72 / Amkor Technology / TSMC · 来源：智源社区 · 最新分享（匿名 API） · 2026-11-23 19:32 UTC · 75.26 分
- 为什么值得看：3.5 倍是产能提升宣称、NVL72 是产品型号、三季度是时间标记；三者量纲不同，合起来读会高估已落地产能。
- 对我意味着什么：对数据基建的算力供给是上游线索：产能承诺属多年框架，不等于当期出货；规格与协议状态要分列，不进落地清单。
- 下一步：找 2 份供应链一手公告核对 3.5 倍；若一致家数少于 2 或无交付节点，则判定仅为厂商口径，标 unverified 留线索池。
- 证据状态：unverified（未独立验证）
→ https://arex-research.com/feeds/5e6fb281-553a-4746-ac24-ac8d6da28f2d

### 市场与投资（1 条）

**Bloomberg 报道马来西亚将对股票基准指数做 17 年来首次重大调整，可能把更多资金引向科技与能源公司。**
- 关键数字：17 · 相关方：Malaysia / equity benchmark / AI trade · 来源：Bloomberg Markets · 2026-11-24 01:12 UTC · 78.01 分
- 为什么值得看：17 是「距上次大改的年数」，不是调整幅度；报道只说 may channel，属可能性表述，不能读成资金流入结论。
- 对我意味着什么：对数据基建是状态标注样本：指数调整这类公开事实只进事实层并标来源，机构观点与资金流向推测另列，不构成投资判断。
- 下一步：核对 2 份一手公告是否给出调整清单与生效日；若均无，则判定 17 年仅为背景描述，不进当期事件表。
→ https://www.bloomberg.com/news/articles/2026-11-24/malaysia-index-rejig-puts-tech-power-stocks-in-focus-for-2027

### 安全与治理（1 条）

**The Verge 报道 Kagi 推出 Kagi Mail 公测：无广告、走开放标准，提供 50GB 存储、内置日历与不限量别名，默认 @kagimail.com 地址。**
- 关键数字：50GB · 相关方：Kagi / Kagi Mail / Gmail / @kagimail.com · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-24 00:02 UTC · 76.66 分
- 为什么值得看：50GB 是公测规格，contacts 与原生 App 分别排在 2027 年初与三季度；把规划功能当成已上线会高估当前完成度。
- 对我意味着什么：对数据基建与邮件通道是规格样本：容量、别名数、路线图要分列并标状态；本任务邮件仍走既有 agent-mail 通道，不据此切换。
- 下一步：核对公测页 50GB 与 2027 路线状态；若 contacts 未在 early 2027 上线，则判定路线图需带状态列，规格与计划分存。
→ https://www.theverge.com/tech/1041000/kagi-mail-email-google-gmail-alternative

### 论文与学术（2 条）

**phys.org 报道 Southwest Research Institute 主导的研究首次绘出日球尾瓣在 14 年周期里的运动路径，数据来自 NASA 航天器。**
- 关键数字：14 · 相关方：NASA / Southwest Research Institute / heliotail · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-23 23:20 UTC · 76.15 分
- 为什么值得看：14 是观测窗口长度而非变化幅度；「首次绘出」说明结论受限于该窗口内的航天器覆盖，不能外推到更长周期。
- 对我意味着什么：暂无直接影响：属空间物理科研，与 WorkBuddy / agent 部署 / 数据基建无交集；仅作「观测窗口需显式标注」的字段样本。
- 下一步：核对论文是否给出 14 年窗口的起止与数据 gaps；若缺口超过 1 年未标注，则判定该窗口不可复算，只留作线索。
→ https://phys.org/news/2026-11-nasa-spacecraft-reveal-solar-tail.html

**phys.org 文章提示南非超过 2 million 小农户在超级 El Niño 来临前需要遮阴、供水与饲料支持，并给出可操作设置建议。**
- 关键数字：2 million · 相关方：South Africa / smallholder households / super El Niño · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-23 22:30 UTC · 75.57 分
- 为什么值得看：2 million 是受影响前的农户基数，不是已受助户数；标题里的 need help 是建议，原文没有给出覆盖率或损失估计。
- 对我意味着什么：暂无直接影响：属农业气候适应建议，与自动化 / MCP / 数据基建无交集；仅作「基数与覆盖数分列」的口径样本。
- 下一步：核对 2 份官方统计是否都给出 2 million 口径；若统计年份或农户定义不一致，则判定该基数不可比，不进汇总表。
→ https://phys.org/news/2026-11-south-africa-small-cattle-farmers.html

---

## 📊 今日数据概览

| 指标 | 数值 |
| --- | ---: |
| 信源可用 | 182 / 185 |
| 原始条目 | 2575 |
| 聚合簇 | 2542 |
| 入选簇 | 40 |
| 实际入报 | 13 |
| 七要素达标 | 13 / 13（100.0%） |
| 引用域名数 | 8 |

高频来源：arex-research.com(3)、github.com(2)、dev.to(2)、phys.org(2)、macrumors.com(1)、techcrunch.com(1)、bloomberg.com(1)、theverge.com(1)

---

## 🔭 待验证信号（可证伪）

| 信号 | 判定阈值 | 达到后判定 |
| --- | --- | --- |
| Code Mode 的 37% token 节省是否换来提速 | 同一批大任务跑 3 次，若耗时未下降而 token 降幅达 37% 的次数 ≥ 2 | 判定省 token 属成本口径而非性能收益，不写进提速结论 |
| ECC 组件清单是否与仓库一致 | 清点仓库 2 次，若 281 skills 或 94 commands 任一不一致 | 判定组件数为宣传口径，不进 skill 基线 |
| Phonic-1.1 的 89.1 分口径 | 对照 Artificial Analysis 榜单 2 个版本，若 89.1 分对应测试集未披露 | 判定该分数仅作榜单位次，不进模型选型矩阵 |
| GPT-6.2 Sol 的 91 与 94 遵循率 | 核对 2 份官方安全评测，若 91 与 94 来自不同测试集 | 判定区间不可合并，按测试集分列并标档位 |
| Kagi Mail 50GB 与 2027 路线状态 | 核对公测页 50GB 与路线图，若 contacts 晚于 early 2027 上线 | 判定路线图需带状态列，规格与计划分存 |
| 英伟达 3.5 倍产能宣称的一手佐证 | 找 2 份供应链公告核对 3.5 倍，若一致家数少于 2 | 判定该倍数仅为厂商口径，标 unverified 留线索池 |

---

## 💡 编者观察

本期最该带走的判断是：能进部署门禁的读数，必须是可逐字锁定且带齐条件的那一个，而不是标题里最醒目的数字。Claude Code 的 Code Mode 用一段 JavaScript 编排工具调用，社区实测大任务省 37% token 却并不更快；同一天的 v2.1.331 把 Code Mode 落到终端会话的 Bedrock、Foundry 等平台，两个版本号 2.1.323 与 2.1.331 才是能写进兼容性矩阵的硬读数。对 automation 与 agent 部署的含义很直接：省 token 属于成本口径，耗时属于体验口径，两者要分列评估，不能因为一个百分比就把实验功能默认打开，原文写明它默认关闭、需设环境变量。第二条是可数的清单比形容词更可信。Everything Claude Code 把 67 个 agents、281 个 skills、94 条 commands 和 AgentShield 打包成一个 kit，davinci-resolve-mcp 则给出 Stars 4,313、Forks 493 的仓库热度。对 skill 与 WinVM 侧基线来说，组件数量、版本号、仓库指标都能逐字复核，可直接做成门禁规则；但大而全不等于适配，接入前应先跑一次清点，核对 281 skills 与 94 commands 是否与仓库清单一致。

---

*本日报由规则层采集/去重/打分 + AI 研判生成；每条附原文链接，关键数字须能在原文中找到。*
*外部事实未独立验证，内容仅供参考，不构成投资建议；取不到可靠数据处标注「暂无可靠数据」。*
