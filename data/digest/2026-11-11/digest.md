# Gemini 4 Carbon 以 $2/$10 入场、CoreWeave 营收增 168% 仍亏 $709M：能力扩张与单位成本两条曲线正在分叉

> 168% 的同比营收增长伴随 $709M 净亏损，CoreWeave 把 $132.5B 订单积压写进 Q3；同日 llm-gemini 0.36 以 $2/$10 每百万 token 接入 Gemini 4 Carbon，Graphon 拿 $35M 补 Agent 记忆，2,100 tokens/s 的承诺仍待独立复测。今日张力是能力扩张与单位成本的分叉。

> 2026-11-11 · 北京时间 · 生成于 2026-11-10T23:04:57.316406Z

## 📌 今日速览

- **llm-gemini 0.36 发布，Gemini 4 Carbon 从限定人群开放至所有人，输入 $2、输出 $10 每百万 token**（0.36, $2） — 两周前只给 cyber defenders 子集，如今开放且可被命令行调用；可用性的变化比模型评分更影响接入决策。
- **斯坦福 CS 329Z《Agent工程》放出第6讲 Agent 设计模式与脚手架，前几讲依次覆盖 LLM 基础、RAG 与工具调用**（CS 329Z, 第6讲） — 课程把工具调用与任务编排独立成讲，说明 Agent 工程的难点已从模型能力转到与外部系统的交互契约。
- **论文演示 GPT-6 Astra 对神经网络做底层操作，讨论称 Claude Fable 5.2 具备相近的 weight-space-programming 能力**（5.2, 9x9） — 能力比较落在直接改权重而非提示词；若可复现，模型定制的成本结构会从训练数据转向权重编辑。
- **Graphon 以跨 docs、videos、images 建立连接来补 AI agent 记忆短板，获 RRE Ventures 领投的 $35M Series A**（$35M） — 资本把记忆当作独立基础设施层定价而非模型附带能力，说明跨模态索引已是 agent 落地的显性瓶颈。
- **一位 LocalLLaMA 用户用 2 台 Sparks 跑 glm 5.3 flash、以 hermes agent 作 harness，吐槽约 6500 euro 双机投入**（2, 5.3） — 这是少见的把 hermes agent 作为本地编排 harness 的一手配置记录，硬件成本与模型体感被同时量化。
- **Ollama v0.40.17 预发布合入 ChatGPT CLI 恢复与优雅重启、OpenCode thinking metadata 与 Vulkan 集显 mmap 改动**（v0.40.17, #19583） — 三个改动都落在启动与推理路径而非新模型，CLI 优雅重启与集显 mmap 直接决定本地服务能否无人值守常驻。

---

## 🔥 今日主线

### 一、降价入场，成本账却没变简单
$2/$10 的单价让联网推理档第一次可以进成本模型，但 2,100 tokens/s 只有单一实测；CoreWeave 168% 营收增长仍伴 $709M 亏损，说明供给侧的单价下降尚未传导到利润表。（3 条独立条目佐证）

### 二、Agent 的短板在记忆与工具契约
Graphon 用 $35M 做跨 docs、videos、images 的连接，CS 329Z 把工具调用与任务编排独立成讲，本地 2 台 Sparks 加 hermes agent 的 harness 也在算投入产出；三者都指向上下文与契约，而不是模型选型。（3 条独立条目佐证）

### 三、版本号里藏着要回归的调用约定
v0.40.17 改了 CLI 重启与集显 mmap，Blender 5.3 引入 Gaussian Splat，Dependabot 自 December 8, 2026 起按活跃度关闭告警；三处都是行为变更，只盯版本号会漏掉回归点。（3 条独立条目佐证）

### 四、算力需求真实，利润仍在路上
CoreWeave 的 $132.5B 积压与 168% 增速证明需求，OpenAI 向投资人披露 Q3 增 50% 至约 $10B，但 10-year 收益率回到 5% 抬高了长期算力资产的折现率，是同日的反向指标。（3 条独立条目佐证）

### 五、资本给 Agent 胶水层单独定价
$35M 投跨模态记忆、$27.5 million 投 AI 制药、$25M 投自测试网站，三笔都不是基座模型，而是把检索、仿真、验证闭环做成独立层的中间设施。（3 条独立条目佐证）

### 六、极小的改动也能撬动大模型
零化少于 0.05% 权重即可匹配全量微调，weight-space-programming 在 9x9 围棋网络与 Qwen3-0.6B 上被讨论，SIMCO 用 9 种药物与 2.18 亿白细胞做仿真；成本压缩正从数据侧转向结构侧。（3 条独立条目佐证）

### 七、工具链适配比榜单更决定可用性
llm-gemini 0.36 在开放当天接住新模型，ollama v0.40.17 同步改运行时路径，而 coding agent 若仍按 ~2019 的 JavaScript 生成代码，会把 50 行依赖与焦点管理缺陷批量复制进产品。（3 条独立条目佐证）

---

## 🗂 分类聚合

### 模型与研究（3 条）

**llm-gemini 0.36 发布，Gemini 4 Carbon 从限定人群开放至所有人，输入 $2、输出 $10 每百万 token**
- 关键数字：0.36 / $2 / $10 · 相关方：llm-gemini / Gemini 4 Carbon / Google / GPT-6.1 · 来源：Simon Willison's Weblog · 2026-11-10 20:09 UTC · 77.52 分
- 为什么值得看：两周前只给 cyber defenders 子集，如今开放且可被命令行调用；可用性的变化比模型评分更影响接入决策。
- 对我意味着什么：对 WorkBuddy 模型路由与 skill 调用有直接影响：可把联网推理档纳入候选，但需按 $2/$10 单价核算长任务预算。
- 下一步：用同一 10 条提示词跑 llm-gemini 0.36，若返回完整率 ≥9/10 且单价核算不超预算，才纳入默认路由。
→ https://simonwillison.net/2026/Nov/10/llm-gemini

**斯坦福 CS 329Z《Agent工程》放出第6讲 Agent 设计模式与脚手架，前几讲依次覆盖 LLM 基础、RAG 与工具调用**
- 关键数字：CS 329Z / 第6讲 / 第2讲 / 第3讲 · 相关方：斯坦福 / Agent工程 / RAG / LLM · 来源：智源社区 · 最新分享（匿名 API） · 2026-11-10 12:10 UTC · 77.55 分
- 为什么值得看：课程把工具调用与任务编排独立成讲，说明 Agent 工程的难点已从模型能力转到与外部系统的交互契约。
- 对我意味着什么：对 MCP / A2A 与 skill 设计有直接参考价值：第4讲的工具调用边界可对照当前 connector 契约逐条核对。
- 下一步：对照第4讲与第5讲清单逐项自查，若工具描述、错误回退、编排幂等三项均覆盖，判定现有契约合格。
→ https://mp.weixin.qq.com/s?__biz=MzU4NTQyNjc5Mg%3D%3D&mid=2247499027&idx=1&sn=f2db4105ce173f26380aa00320a4fc51&chksm=fc521d0df4c7db69372ce4e073ca3c75a3079b78cca2e13c063e3f5cf3997a432220ad81f078&scene=0&xtrack=1

**论文演示 GPT-6 Astra 对神经网络做底层操作，讨论称 Claude Fable 5.2 具备相近的 weight-space-programming 能力**
- 关键数字：5.2 / 9x9 / 0.6B · 相关方：Claude Fable 5.2 / GPT-6 Astra / Qwen3-0.6B / weight-space-programming · 来源：LessWrong · 2026-11-10 18:06 UTC · 72.82 分
- 为什么值得看：能力比较落在直接改权重而非提示词；若可复现，模型定制的成本结构会从训练数据转向权重编辑。
- 对我意味着什么：对 skill 与 agent 部署暂无直接影响：权重级改动需要可复现的评测集，当前只有单篇讨论，不构成接入依据。
- 下一步：在同一数学基准复跑 3 组权重编辑，若 Qwen3-0.6B 提升可重复且无回归，才判定该路径值得评估。
- 证据状态：unverified（未独立验证）
→ https://www.lesswrong.com/posts/wg3K6xFFTdM6RmRgn/claude-fable-5-2-can-do-weight-space-programming-about-as

### Agent 与工程（2 条）

**Graphon 以跨 docs、videos、images 建立连接来补 AI agent 记忆短板，获 RRE Ventures 领投的 $35M Series A**
- 关键数字：$35M · 相关方：Graphon / RRE Ventures / Business Insider · 来源：Techmeme · 2026-11-10 20:25 UTC · 72.29 分
- 为什么值得看：资本把记忆当作独立基础设施层定价而非模型附带能力，说明跨模态索引已是 agent 落地的显性瓶颈。
- 对我意味着什么：对 agent 部署与数据基建有直接影响：多模态记忆需要可回溯引用链，现有 skill 上下文管理应补来源字段。
- 下一步：给现有记忆表加来源与时间戳两项，若跨 3 类素材检索命中率 ≥80%，才判定可替换现有上下文拼接。
→ https://www.techmeme.com/261110/p49

**一位 LocalLLaMA 用户用 2 台 Sparks 跑 glm 5.3 flash、以 hermes agent 作 harness，吐槽约 6500 euro 双机投入**
- 关键数字：2 / 5.3 / 6500 · 相关方：glm 5.3 flash / hermes agent / MacBook Air / Sparks · 来源：r/LocalLLaMA · 2026-11-10 21:11 UTC · 71.52 分
- 为什么值得看：这是少见的把 hermes agent 作为本地编排 harness 的一手配置记录，硬件成本与模型体感被同时量化。
- 对我意味着什么：对 hermes-agent 部署有直接参考：多机加 MacBook 的编排需验证任务分发是否真的落到两台机器。
- 下一步：在同一 harness 跑 20 次并发任务，若两台 Sparks 负载差 <20% 且无排队超时，判定分发有效。
- 证据状态：unverified（未独立验证）
→ https://www.reddit.com/r/LocalLLaMA/comments/1xsytlk/my_ai_is_lazier_than_me

### 开发者工具与版本（3 条）

**Ollama v0.40.17 预发布合入 ChatGPT CLI 恢复与优雅重启、OpenCode thinking metadata 与 Vulkan 集显 mmap 改动**
- 关键数字：v0.40.17 / #19583 / #19409 / #19640 · 相关方：ChatGPT CLI / OpenCode / Vulkan / Ollama · 来源：ollama Releases · 2026-11-10 22:25 UTC · 79.65 分
- 为什么值得看：三个改动都落在启动与推理路径而非新模型，CLI 优雅重启与集显 mmap 直接决定本地服务能否无人值守常驻。
- 对我意味着什么：对 automation 与本地 agent 运行时有直接影响：常驻推理服务升级前需回归 CLI 重启与 GPU 内存映射路径。
- 下一步：升级后跑 10 次 CLI 中断重启，若 ≥9 次恢复会话且集显显存占用不升，判定可替换现有版本。
→ https://github.com/ollama/ollama/releases/tag/v0.40.17-rc0

**Blender 5.3 发布并加入 Gaussian Splat 支持，HN 条目获 385 分**
- 关键数字：5.3 / 385 · 相关方：Blender / Gaussian Splat · 来源：HN Algolia front_page (points/comments) · 2026-11-10 16:15 UTC · 76.11 分
- 为什么值得看：Gaussian Splat 进入主流 DCC 工具，意味着 3D 资产管线从网格扩展到辐射场表示，导出与版本管理都要跟着改。
- 对我意味着什么：对 3D 资产生成链路有直接影响：需确认生成的 Splat 数据能否在 5.3 里直接导入并转存。
- 下一步：导入 1 个 Splat 场景做往返测试，若 5.3 能无损导出且渲染无报错，判定可纳入资产流程。
→ https://www.blender.org/download/releases/5-3

**GitHub 宣布自 December 8, 2026 起对过去一年无活动的大多数仓库关闭 Dependabot 告警，既有告警归档不删除**
- 关键数字：December 8, 2026 · 相关方：Dependabot / GitHub · 来源：GitHub Changelog · 2026-11-10 14:20 UTC · 72.3 分
- 为什么值得看：告警从持续在线变成按活跃度开关，归档仓库的安全债会被静默隐藏而不是被修复。
- 对我意味着什么：对 automation 与仓库数据基建有直接影响：无人值守的依赖巡检不能把 Dependabot 告警当唯一信号。
- 下一步：在 December 8, 2026 前导出归档仓库清单，若无活动但仍在部署的仓库 ≥1 个，则补独立扫描任务。
→ https://github.blog/changelog/2026-11-10-dependabot-alerts-will-pause-on-inactive-repositories

### 论文与学术（2 条）

**arXiv 论文《The Surprising Effectiveness of Deleting Weights in LLM Post-Training》称零化少于 0.05% 权重即可匹配全量微调**
- 关键数字：0.05% · 相关方：LLM / FFT · 来源：r/LocalLLaMA · 2026-11-10 19:44 UTC · 67.51 分
- 为什么值得看：若结论可复现，后训练的资源门槛会从全量微调降到极小权重子集，改变模型定制的成本模型。
- 对我意味着什么：对 skill 与 agent 部署暂无直接影响：结论只在三类后训练场景给出，未覆盖工具调用类任务。
- 下一步：在自有评测集复现 3 次 0.05% 权重零化，若与 FFT 差距 <2 个百分点，才判定可用于轻量定制。
→ https://www.reddit.com/r/LocalLLaMA/comments/1xswmb7/the_surprising_effectiveness_of_deleting_weights
→ https://arxiv.org/abs/2611.10866

**斯坦福医学院发布单细胞级数字孪生系统 SIMCO，基于 9 种药物与 2.18 亿白细胞重建母体免疫微环境**
- 关键数字：9种药物 / 2.18亿 / 37周 · 相关方：SIMCO / 斯坦福医学院 / 数字孪生 · 来源：智源社区 · 最新分享（匿名 API） · 2026-11-10 12:20 UTC · 72.83 分
- 为什么值得看：数字孪生把药物筛选从真实试验前移到仿真层，2.18 亿白细胞是少数给出明确样本量级的公开读数。
- 对我意味着什么：对数据基建有间接影响：单细胞级仿真说明高基数结构化数据的版本与溯源设计仍是瓶颈。
- 下一步：核对样本量与评测口径是否公开，若 9 种药物的仿真排序与实验一致 ≥7 种，判定结果可引用。
→ https://mp.weixin.qq.com/s?__biz=MzU3NTQ2NDIyOQ%3D%3D&mid=2247531296&idx=1&sn=93d9fcad3fd222953256c04854baec9a&chksm=fc42a1c45186425bbb8868ba7b72482d197ec949756406624b8ff7c93fd77bd8598ea0a7fb4a&scene=0&xtrack=1

### 深度长文（1 条）

**Latent Space 实测 NaiveAI，检验其 2,100 Tokens per Second 的速度承诺在编码任务上是否守住质量**
- 关键数字：2,100 · 相关方：NaiveAI / Artificial Analysis / DeepSeek · 来源：Latent Space · 2026-11-10 18:56 UTC · 76.69 分
- 为什么值得看：速度与编码质量被分开测：厂商只给吞吐承诺，独立测试才回答长任务里是否仍旧可用。
- 对我意味着什么：对 automation 的模型选型有直接影响：高吞吐只有在长提示词下不降质才值得替换现有执行档。
- 下一步：用 10 个长提示词跑编码回归，若吞吐 ≥2,000 tokens/s 且通过率不低于现有档，判定可切换。
→ https://latent.space/p/naiveai

### 产业与资本（3 条）

**The Information 引述消息称 OpenAI 向投资人披露 Q3 营收增 50% 至约 $10B，Q2 增速为 17%**
- 关键数字：50% / $10B / 17% / Q3 · 相关方：OpenAI / The Information · 来源：Techmeme · 2026-11-10 21:22 UTC · 71.36 分
- 为什么值得看：增速从 17% 跳到 50% 是向投资人披露的口径而非经审计财报，数字用途应限定在趋势而非估值。
- 对我意味着什么：对 WorkBuddy 侧模型采购预算暂无直接影响；仅作为 API 供给方产能扩张的间接信号。
- 下一步：等一手财报或官方披露，若 50% 与 $10B 两项均被正式确认，才把它写入成本模型。
- 证据状态：unverified（未独立验证）
→ https://www.techmeme.com/261110/p51

**前 SignalFire 投资人 Sahir Raoof 为 Proximal Ventures 募得 $27.5 million 首期基金，投向 AI 制药**
- 关键数字：$27.5 · 相关方：Proximal Ventures / SignalFire / Sahir Raoof · 来源：TechCrunch Venture · 2026-11-10 20:47 UTC · 73.65 分
- 为什么值得看：首期基金规模不大但方向专一，说明 AI 制药仍靠专项资本而非平台级预算推动。
- 对我意味着什么：对数据基建暂无直接影响；可对照 SIMCO 一类仿真工作看资本是否流向可验证的样本量级。
- 下一步：核对该基金前 3 笔投资是否披露评测口径，若 ≥2 笔给出可复现数据，判定方向成立。
→ https://techcrunch.com/2026/11/10/proximal-ventures-raises-debut-fund-to-back-startups-bringing-ai-to-drug-development

**Coframe 用 AI 生成可自测与按访客个性化的网站，获 $25M Series A，累计融资 $35M**
- 关键数字：$25M / $35M · 相关方：Coframe / Business Insider / Vinod Khosla · 来源：Techmeme · 2026-11-10 22:45 UTC · 72.39 分
- 为什么值得看：把 A/B 测试与个性化交给网站自身执行，等于把改动与验证的闭环做成产品而非运营流程。
- 对我意味着什么：对 automation 有方法论参考：可验证闭环应内置阈值与回滚，而不是靠人工巡检判定效果。
- 下一步：若其公开案例给出 ≥2 个可复现的转化率阈值与回滚条件，才判定该闭环值得借鉴。
→ https://www.techmeme.com/261110/p55

### 市场与投资（2 条）

**CNBC 报道 CoreWeave Q3 营收同比增 168% 至 $3.66B（预期 $3.55B），净亏损 $709M，订单积压 $132.5B**
- 关键数字：168% / $3.66B / $3.55B / $709M / $132.5B · 相关方：CoreWeave / CNBC / Jordan Novet · 来源：Techmeme · 2026-11-10 21:40 UTC · 73.18 分
- 为什么值得看：营收超预期与净亏损同时扩大，$132.5B 积压说明算力需求真实，但转化为利润仍需资本开支周期。
- 对我意味着什么：对数据基建与成本核算有间接影响：算力供给紧俏时，无人值守任务的预算阈值要按峰值单价重算。
- 下一步：对照下一季财报，若净亏损收窄至 $500M 以下且积压仍 ≥$100B，判定规模效应开始兑现。
→ https://www.techmeme.com/261110/p53

**10-year Treasury 收益率回到 5%，CPI 高于预期与 Waller 表态推升加息预期**
- 关键数字：10-year / 5% · 相关方：Treasury / CPI / Waller · 来源：CNBC Markets · 2026-11-10 21:06 UTC · 71.66 分
- 为什么值得看：无风险利率抬升会抬高长期算力资产的折现率，是解释同日算力资本开支叙事的反向指标。
- 对我意味着什么：对数据基建预算暂无直接影响，但可作为评估长期算力合约成本时的外部宏观变量。
- 下一步：若 10-year 连续 5 个交易日站稳 5% 以上，判定高利率情景需纳入明年预算假设。
→ https://www.cnbc.com/2026/11/10/us-bonds-treasurys-yields.html

### 社区与观点（1 条）

**HN 项目主张让 coding agent 用浏览器原生原语替代 ~2019 年那套 JavaScript，举例 50 行 JS 可被原生能力替代**
- 关键数字：~2019 / 50 / 205 · 相关方：JavaScript / CSS.highlights / showModal() / field-sizing · 来源：HN Algolia front_page (points/comments) · 2026-11-10 18:01 UTC · 77.28 分
- 为什么值得看：agent 生成的代码若停留在旧范式，会把依赖与焦点管理缺陷批量复制进产品；这是生成质量的输入侧问题。
- 对我意味着什么：对 skill 与前端 automation 有直接影响：应把现代原语清单写进代码生成约束，减少无谓依赖。
- 下一步：在生成模板中替换 3 处旧写法，若依赖数下降且焦点回归用例 10/10 通过，判定清单有效。
→ https://github.com/GoogleChrome/modern-web-guidance

---

## 📊 今日数据概览

| 指标 | 数值 |
| --- | ---: |
| 信源可用 | 173 / 185 |
| 原始条目 | 3240 |
| 聚合簇 | 3180 |
| 入选簇 | 40 |
| 实际入报 | 17 |
| 七要素达标 | 17 / 17（100.0%） |
| 引用域名数 | 12 |

高频来源：techmeme.com(4)、mp.weixin.qq.com(2)、reddit.com(2)、github.com(2)、simonwillison.net(1)、lesswrong.com(1)、blender.org(1)、github.blog(1)

---

## 🔭 待验证信号（可证伪）

| 信号 | 判定阈值 | 达到后判定 |
| --- | --- | --- |
| Gemini 4 Carbon 的 $2/$10 定价是否带来长任务成本下降 | 同一 10 条长提示词下总费用下降 ≥20% 且完整返回 ≥9 次 | 判定可把联网推理档纳入默认模型路由，否则只保留为可选档 |
| CoreWeave 净亏损与订单积压的剪刀差 | 下一季净亏损 <$500M 且积压仍 ≥$100B | 判定规模效应开始兑现；否则上调无人值守任务的算力单价假设 |
| 0.05% 权重零化可否复现匹配全量微调 | 3 次复跑与 FFT 差距均 <2 个百分点且无回归 | 判定轻量后训练路径值得评估，否则仅作为研究线索记录 |
| Dependabot 告警关闭对归档仓库的暴露面 | December 8, 2026 前导出清单，无活动但仍在部署的仓库 ≥1 个 | 判定必须补一条独立依赖扫描任务，不能只靠平台告警 |
| coding agent 生成代码的依赖膨胀是否可控 | 替换 3 处旧写法后依赖数下降且焦点回归用例 10/10 通过 | 判定现代浏览器原语清单可写进代码生成约束 |

---

## 💡 编者观察

本期 173 个信源收进 10600 条、聚成 3180 簇，Folo 基线降级为 0 条，社区侧覆盖偏薄；按 v1.1 口径把无实质读数的簇挡在 sections 外，最终 17 条入报。三条判断落到工程动作。一是模型侧变的是可得性：llm-gemini 0.36 把 Gemini 4 Carbon 接进命令行，$2/$10 让联网推理档能进成本模型，但 2,100 tokens/s 只有单一实测，须跑同一组 10 条长提示词、通过率不低于现有档才切换。二是 Agent 瓶颈在记忆与工具契约：Graphon 用 $35M 做跨模态连接，CS 329Z 把工具调用与编排独立成讲；skill 与 MCP/A2A 的上下文要补齐来源、时间戳与幂等字段，跨 3 类素材命中率过 80% 再替换拼接逻辑。三是防静默降级：GitHub 自 December 8, 2026 起对无活动仓库关闭 Dependabot 告警且只归档不删除，ollama v0.40.17 改了 CLI 重启与集显 mmap；把 10 次中断重启 ≥9 次恢复、归档清单仍有部署中仓库 ≥1 个就补独立扫描写成断言。

---

*本日报由规则层采集/去重/打分 + AI 研判生成；每条附原文链接，关键数字须能在原文中找到。*
*外部事实未独立验证，内容仅供参考，不构成投资建议；取不到可靠数据处标注「暂无可靠数据」。*
