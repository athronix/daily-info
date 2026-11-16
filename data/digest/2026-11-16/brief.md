**skill 有了星数也该有评测门槛，权重开放不等于部署路径开放——今日读数密集，可接入项仍需逐项验收**

今日入报里，82 个专用 skill 与 1,308 星的评测框架同时出现，也有 1.6 万亿参数却缺 Nvidia GPU 自托管路径的开源权重；同一天，19 小时宕机与 $887M 罚款把基础设施代价写成了可核验读数。张力在于能数清的越来越多、能直接接入的却没同步变多：版本号密集刷新到 1.2.0，部署清单仍要逐项对照。

2026-11-16 · 入报 18 条 · 信源 182/185

今日主线：
• skill 有了星数，也该有评测门槛
• 版本号密集刷新，工具链在悄悄重排
• 权重开放，不等于部署路径开放
• 基础设施的代价被写成可核验数字
• 资本读数分化，上限与成交要分清

重点条目（含关键数字与下一步动作）：
• [82, 15] elementalsouls 把 82 个专用 skill、15 条 slash command 与 681 条已披露报告模式打包成 Claude-BugHunter 开源 Python skill 集。
  → 拉取仓库逐一核对 skill 目录数与 82 是否一致；若偏差超过 10% 或缺版本锁定文件，则判定不可直接接入，先补 manifest 再评估。
  https://github.com/elementalsouls/Claude-BugHunter
• [1,308, 154] NVIDIA 开源基于 Python 的 SkillEvaluator 框架，用质量闸门与语义重叠检测评估 agent skill，仓库已积累 1,308 星、154 次 fork。
  → 在本地 skill 集上跑一次评测，若语义重叠检出数 >0 且人工确认存在真冲突，则把该检测加进部署前 gate；0 检出则暂不接入以免徒增开销。
  https://github.com/NVIDIA/SkillEvaluator
• [2.5, 1.6 万亿] 美团 LongCat 团队开源 LongCat-2.5 权重，采用 MIT 许可证，总参数 1.6 万亿的 MoE 模型每 token 约激活 480 亿参数，定位长程多步 agent 任务。
  → 查找官方自托管文档，若仍无 Nvidia GPU 路径或最小显存配置，则判定为权重开放、部署路径未开放，暂缓纳入自托管测试队列。
  https://arex-research.com/feeds/a655c45f-f32c-4e74-8be0-e69ed2489277
• [1.2.0, 1.1.6] LangChain 发布 langchain-mistralai 1.2.0，相对 1.1.6 修复推理模型流式行为，并把 ChatMistralAI 改走 LangSmith gateway。
  → 在测试环境把依赖升到 1.2.0 跑一遍流式推理 smoke，若出现调用链中断或流式分片异常，则判定不兼容并锁定 1.1.6。
  https://github.com/langchain-ai/langchain/releases/tag/langchain-mistralai%3D%3D1.2.0
• [1.2.0, 1.1.3] LangChain 发布 langchain-groq 1.2.0，相对 1.1.3 在集成测试中显式指定 reasoning_effort，并把 ChatGroq 改走 LangSmith gateway。
  → 把 