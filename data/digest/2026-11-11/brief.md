**Gemini 4 Carbon 以 $2/$10 入场、CoreWeave 营收增 168% 仍亏 $709M：能力扩张与单位成本两条曲线正在分叉**

168% 的同比营收增长伴随 $709M 净亏损，CoreWeave 把 $132.5B 订单积压写进 Q3；同日 llm-gemini 0.36 以 $2/$10 每百万 token 接入 Gemini 4 Carbon，Graphon 拿 $35M 补 Agent 记忆，2,100 tokens/s 的承诺仍待独立复测。今日张力是能力扩张与单位成本的分叉。

2026-11-11 · 入报 17 条 · 信源 173/185

今日主线：
• 降价入场，成本账却没变简单
• Agent 的短板在记忆与工具契约
• 版本号里藏着要回归的调用约定
• 算力需求真实，利润仍在路上
• 资本给 Agent 胶水层单独定价

重点条目（含关键数字与下一步动作）：
• [0.36, $2] llm-gemini 0.36 发布，Gemini 4 Carbon 从限定人群开放至所有人，输入 $2、输出 $10 每百万 token
  → 用同一 10 条提示词跑 llm-gemini 0.36，若返回完整率 ≥9/10 且单价核算不超预算，才纳入默认路由。
  https://simonwillison.net/2026/Nov/10/llm-gemini
• [CS 329Z, 第6讲] 斯坦福 CS 329Z《Agent工程》放出第6讲 Agent 设计模式与脚手架，前几讲依次覆盖 LLM 基础、RAG 与工具调用
  → 对照第4讲与第5讲清单逐项自查，若工具描述、错误回退、编排幂等三项均覆盖，判定现有契约合格。
  https://mp.weixin.qq.com/s?__biz=MzU4NTQyNjc5Mg%3D%3D&mid=2247499027&idx=1&sn=f2db4105ce173f26380aa00320a4fc51&chksm=fc521d0df4c7db69372ce4e073ca3c75a3079b78cca2e13c063e3f5cf3997a432220ad81f078&scene=0&xtrack=1
• [$35M] Graphon 以跨 docs、videos、images 建立连接来补 AI agent 记忆短板，获 RRE Ventures 领投的 $35M Series A
  → 给现有记忆表加来源与时间戳两项，若跨 3 类素材检索命中率 ≥80%，才判定可替换现有上下文拼接。
  https://www.techmeme.com/261110/p49
• [2, 5.3] 一位 LocalLLaMA 用户用 2 台 Sparks 跑 glm 5.3 flash、以 hermes agent 作 harness，吐槽约 6500 euro 双机投入
  → 在同一 harness 跑 20 次并发任务，若两台 Sparks 负载差 <20% 且无排队超时，判定分发有效。
  https://www.reddit.com/r/LocalLLaMA/comments/1xsytlk/my_ai_is_lazier_than_me
• [v0.40.17, #19583] Ollama v0.40.17 预发布合入 ChatGPT CLI 恢复与优雅重启、OpenCode thinking metadata 与 Vulkan 集显 mmap 改动
  → 升级