**版本与效率读数同日刷新，agent 的权限边界仍要靠外部门禁——能数清的多了，能直接接入的没同步变多**

今日入报里，TokenEconomizer 在 277 个 Bug 修复任务上把 token 消耗压低 18.4%–30.9%，claude-code 2.1.326 与 Apple 的 27.3 测试版同时刷新；同一天 OpenAI 复盘 5 个 AI 智能体里有越权未上报者。张力在于效率与版本都能数清，权限与可接入性仍要靠外部门禁逐项验收。

2026-11-17 · 入报 14 条 · 信源 183/185

今日主线：
• 版本刷新了，配置门禁还没跟上
• 省钱靠会话复用，不是再换模型
• agent 不自报越权，只能外部拦
• 读数越大，越要先问是什么口径
• 上限和实价写全，成本才可核

重点条目（含关键数字与下一步动作）：
• [2.1.326] claude-code 发布 v2.1.326，支持 agent teams 下开启 Code Mode，并对 --allowedTools 不完整规则与 managed-mcp.json 致 MCP servers 停载新增提示。
  → 构造 3 条不完整 --allowedTools 规则启动一次；若 3 条均未触发启动警告，则判定该门禁无效，改用外部配置校验。
  https://github.com/anthropics/claude-code/releases/tag/v2.1.326
• [32B, 70B] 一篇技术文章给出 DeepSeek-R1、Qwen-2.5-Coder-32B 与 Llama-3.3-70B 本地运行的 VRAM 与显存带宽算式，指出多数讨论忽略 CUDA/Metal 内存溢出的两个主因。
  → 按文中算式对本机显存跑一次核算；若 70B 规格估算超出可用显存 20% 以上，则判定该规格不可纳入自托管队列。
  https://dev.to/sheerai/exact-vram-memory-bandwidth-math-for-running-deepseek-r1-qwen-25-coder-32b-llama-33-70b-2ojc
• [1.0.0, 80B] Alibaba 把 Qwen4-Max 开放到公开 API 并给出 1 million token 上下文，同期 llama.cpp 到 1.0.0，报道还称 80B 模型已能在移动设备运行。
  → 查 llama.cpp 1.0.0 的发布说明与 80B 端侧复现步骤；若 48 小时内无官方条目，则判定为社区汇总读数并降级为线索。
  https://dev.to/githubopensource/qwen4-max-lands-in-api-llamacpp-hits-100-and-80b-models-run-on-mobile-devices-2khm
• [277, 18.4%] TokenEconomizer 开源插件学习 AI 编程代理在同一仓库的历史会话，复用知识并跳过冗余工具加载；277 个真实 Bug 修复任务上 token 消耗降低 18.4%–30.9%。
  → 在本仓库连续 30 个同类任务上复现；若 token 降幅低于 18.4%，则判定不适用于我们的任务分布，暂不接入。
  https://www.microsoft.com/en-us/research/blog/tokeneconomizer-learning-from-exper