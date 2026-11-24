**样本量、版本号与金额能逐字复核，型号尾数与社区热度不能：今天进门禁的是 100、160、76 与 544 这些可清点数**

今日能进门禁的四个样本量都带得住复核：有人逐个读了 100 份 MCP server 的工具清单，有人扫描 160 个 npm 包归纳 bug 类别；还有 76 个 DeepSWE 任务与 544 条 prompts 把做对了变成可数判定。张力在于同一批素材里，Firefox 161 的版本号与 $5.3M 的融资额可以逐字锁定，而 YC F26 的批次号、GTA VI 的型号、Section 702 的法条编号只是标识符；

2026-11-25 · 入报 13 条 · 信源 182/185

今日主线：
• 样本量才是门禁的下限
• 版本号与金额能逐字锁定
• 比例读数必须带分母
• MCP 的能力边界写在数字里
• 召回与评测都在量化失败

重点条目（含关键数字与下一步动作）：
• [100, 2 mins] Launch HN 发布 Versine：一个坐在钱包前面的 MCP，让 AI 代用户收发款项，单次最多面向 100 人。
  → 对照官方说明复现 2 次「单次 100 人」与「2 分钟到账」；若任一次未达或缺少 passkey 审批步骤，则判定该 MCP 不进自动化基线。
  https://news.ycombinator.com/item?id=50634426
• [100] dev.to 文章称 AI agent 会盲目信任 MCP server 返回的工具列表，作者逐个读了 100 份工具清单。
  → 抽取 100 份工具清单中的 10 份做调用复现；若描述与实际返回不一致 ≥ 2 份，则判定需加描述校验层再接入。
  https://dev.to/suncly/ai-agents-trust-your-mcp-servers-tool-list-blindly-we-read-100-of-them-45j5
• [544] Google DeepMind 宣布推出 Humanity's First Exam 与 Kaggle hackathon，用 544 prompts 测试 LLM 可靠性。
  → 对照官方题面核对 544 prompts 与评分规则；若题量不符或评分口径未披露，则判定仅作规模记录。
  https://blog.google/innovation-and-ai/models-and-research/google-deepmind/humanitys-first-exam
• [161] The Verge 报道 Mozilla 发布 Firefox 161：可按站点自动开关 VPN，并新增一键清除浏览历史等数据的 Fire 按钮。
  → 在 2 台宿主各配 1 组站点规则并跑 1 次清除；若任一未生效或 profile 字段变更，则判定暂缓升级到 161。
  https://www.theverge.com/tech/1041474/firefox-161-vpn-rules-fire-button
• [45%, 1,864] phys.org 报道九州大学牵头的公民科学研究：调查的神奈川原生植物物种中，近 45% 分布出现下滑，样本共 1,864 种。
  → 核对论文是否给出 1,864 的物种清单与 45% 判定阈值；若缺任一，则判定该比例不可复算，只留线索。
  https://phys.org/news/2026-11-decades-citiz