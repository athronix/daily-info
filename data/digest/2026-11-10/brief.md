**Fable 5.2 同日进入榜单、CLI 与本地运行时，但 128,000 token 的失败暴露默认档可信度缺口**

Fable 5.2 在 Artificial Analysis 得 65 分，同日 claude-code v2.1.321 设为默认并给出 1M 上下文与 $8/$40 每 Mtok 定价，ollama v0.40.16 把 65B 的 Ripple Preview 收进本地运行时、让 Qwen3.8 少用 27 GiB 内存；但 llm-anthropic 0.31 实测 max 档耗尽 128,000 token 仍返不出图。

2026-11-10 · 入报 12 条 · 信源 184/185

今日主线：
• 模型发布先看工具链是否同日接住
• 最高推理档的失败比分数更值钱
• MCP 的漏洞在凭据重定向而非协议
• 沙箱与运行时开始独立成层
• 本地推理的收益要按 GiB 计量

重点条目（含关键数字与下一步动作）：
• [0.31, 5.2] Simon Willison 发布 llm-anthropic 0.31 适配 Fable 5.2 与 Mythos 5.2，并实测五档推理档生成 SVG 的表现
  → 用同一提示词跑 max 档 10 次，若完整返回 ≥ 9 次且 token 消耗上限可控，判定可启用该推理档。
  https://simonwillison.net/2026/Nov/9/llm-anthropic
• [5.2, 30] Anthropic 发布 Claude Fable 5.2 与 Mythos 5.2，称输出速度最高快 30 percent 且在技术科学基准上超过 Opus 5.5
  → 分别跑 Fable 5.2 与 Mythos 5.2 各 10 次编码任务，若前者护栏拦截率更高且 30 percent 提速可复现，判定按任务分流。
  https://www.macrumors.com/2026/11/09/anthropic-launches-claude-fable-5-2
• [2.1.321, 1M] claude-code v2.1.321 将 Claude Fable 5.2 设为默认模型，给出 1M 上下文定价，并修复 MCP OAuth 重定向泄露凭据等缺陷
  → 构造一次 MCP OAuth 302 重定向并抓包，若非注册主机收到 refresh token 次数为 0，判定 v2.1.321 可纳入 agent 部署基线。
  https://github.com/anthropics/claude-code/releases/tag/v2.1.321
• [27.2.1] Apple 为 iOS、iPadOS 与 macOS 27.2.1 发布安全更新，修复 iMessage 群聊历史越权访问与 AirPlay、Bluetooth 恶意配对缺陷
  → 在 macOS 27.2.1 上跑一次签名脚本回归，若 eMudhra 相关校验失败次数为 0 且自动化任务全通过，判定升级不影响工具链。
  https://www.macrumors.com/2026/11/09/ios-27-2-1-security-fixes
• [0.40.16, 65B] ollama v0.40.16 收录 65B 的 Ripple Preview 编码模型，并让 Qwen3.8 Flash Next 在 Apple silicon 上少用 27 GiB 内存
  