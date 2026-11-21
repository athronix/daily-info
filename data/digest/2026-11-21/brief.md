**版本号、百分比与规格能逐字回查并进门禁，型号尾数、发布日期与自写状态码只是声明；可接的是改动清单与可复现阈值，不是漂亮断言**

今日入报里，claude-code v2.1.330 补上自托管 runner 的插件失败 notice，ollama v0.40.17 给出 26B 参数、20GB 内存与 79.2% 的 SWE-Bench 成绩，AWS 分布式 KV 缓存称推理成本最多降 40%、首字延迟最多降 80%；Anthropic IPO 报开盘 111.50 美元、较 83 美元发行价涨 34.3%。

2026-11-21 · 入报 13 条 · 信源 181/185

今日主线：
• 版本号与百分比能进门禁，型号不能
• 上限与预期值都要带条件
• 性能、成本与规格是三种量纲
• 校验要从读日志改成重算回执
• 计数必须带分母与限定词

重点条目（含关键数字与下一步动作）：
• [2.1.330] claude-code v2.1.330 加入企业控制台组织登录、easel 图表与自托管 runner 的 --start-dir，并为插件市场拉取失败、安装失败补上 notice 与 commandFailed 字段。
  → 在 2 个非交互宿主各触发 1 次插件市场拉取失败；若缺 notice 次数 ≥ 1，则判定该路径未覆盖，不纳入部署基线。
  https://github.com/anthropics/claude-code/releases/tag/v2.1.330
• [200] 一篇 dev.to 文章指出 agent 自写的日志行与 200 status 都不算执行校验，主张重算 receipt 而不是读 log。
  → 抽 3 次工具调用，若仅凭 log 与 200 判成功而 receipt 重算不一致次数 ≥ 1，则判定该链路不可用作验收依据。
  https://dev.to/rambozambo/how-do-i-check-an-ai-agents-tool-execution-recompute-the-receipt-not-the-log-2e4e
• [12秒, 0.5秒] 一篇中文报道称 AI 编程助手把调试时的平均等待从约 12 秒缩短到 0.5 秒，结果基于真实编程会话测试，由卡内基梅隆大学于 11 月 12 日公布。
  → 找 2 份独立一手材料核对样本量与测量口径；若一致的少于 2 份，则判定 12 秒与 0.5 秒仅为宣传对比值。
  https://mp.weixin.qq.com/s?__biz=MzI3MTA0MTk1MA%3D%3D&mid=2652744186&idx=2&sn=e971240579573375d9d13105f1750d6f&chksm=f032e663b31b569c7561afe738fbda59b192b86e0fbadb17685fecb2949a2b95442f50ce62bf&scene=0&xtrack=1
• [68%, 204] 一篇 dev.to 文章称在 GPT-5 里斯洛伐克语的 prompt 成本比英语高约 68%，作者 tokenizer 化 204 种语言解释差异。
  → 抽 10 种语言复算同一 prompt 的 token 数；若与 68% 偏差超过 10 个百分点的语言 ≥ 3 种，则判定该值不可外推。
  https://dev.to/ltchurik/slovak-costs-68-more-than-engl