**省 37% token 不等于更快，89.1 分不等于可用：今天能进部署门禁的是版本号、组件数与带条件的规格，不是漂亮的百分比**

今日最硬的两个读数都带条件：Claude Code 的 Code Mode 社区实测大任务省 37% token 却不更快，v2.1.331 才把它落到 Bedrock 与 Foundry 的终端会话；Phonic-1.1 以 89.1 分登顶 Artificial Analysis 语音指数，Everything Claude Code 则打包 67 个 agents、281 个 skills、94 条 commands。

2026-11-24 · 入报 13 条 · 信源 182/185

今日主线：
• 省 token 与提速是两本账
• 可数清单比形容词可信
• 版本号才进得了门禁
• 分数和倍数都要带口径
• 规格读数决定部署门槛

重点条目（含关键数字与下一步动作）：
• [4,313, 493] GitHub 项目 davinci-resolve-mcp 提供 DaVinci Resolve Studio 的 MCP server 集成，摘要列出 Stars 4,313、Forks 493。
  → 对照仓库 README 清点 2 次暴露的工具列表；若工具数与文档不一致或 smoke 调用失败 ≥ 1 次，则判定暂不接入 MCP 基线。
  https://github.com/samuelgursky/davinci-resolve-mcp
• [67, 281] dev.to 文章盘点走红的一体化套件 Everything Claude Code，摘要称打包 67 个 agents、281 个 skills、94 条 commands 与扫描器 AgentShield。
  → 清点仓库 2 次核对 281 skills 与 94 commands；若任一数字与清单不符或重复 skill 名 ≥ 3 个，则判定不整体接入。
  https://dev.to/dimsbuild/should-you-install-everything-claude-code-the-all-in-one-kit-gone-viral-2lme
• [91, 94] MacRumors 报道 OpenAI 把 GPT-6.2 Sol 部署到 ChatGPT 的 Chat 标签页，面向 Plus、Pro 等付费档，称策略遵循率达 91–94 percent。
  → 核对 2 份官方安全评测是否给出 91 与 94 的测试集；若两值来自不同测试集，则判定区间不可合并，按测试集分列。
  https://www.macrumors.com/2026/11/23/openai-gpt-6-2-sol-chatgpt
• [2.1.331, 15] claude-code 发布 v2.1.331：终端会话在 Bedrock、Microsoft Foundry 等平台加入 Code Mode 支持，并新增 oidc.groups_jsonpath 网关配置。
  → 在 2 个非交互宿主各跑 1 次 claude doctor；若 API 连通段缺失或 groups 解析失败 ≥ 1 次，则判定暂缓升级到 2.1.331。
  https://github.com/anthropics/claude-code/releases/tag/v2.1.331
• [26.11, 3.49.52] dev.to 文章称 Co