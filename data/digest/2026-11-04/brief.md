**Agent 技能进入包管理时代，harness 与信任成本同日升温**

今日 40 个候选簇中，skill 治理（Dependabot APM + 2 篇 arXiv）、harness 之争（agent-desktop 12,669 星拆解、优化 harness 论文）、信任三案（Gemini 训练 / Muse 许可证 / RTX 固件降至 35%）与选举日市场四线联动构成四条主线。

2026-11-04 · 入报 35 条 · 信源 67/68

今日主线：
• Agent 技能开始像依赖包一样被治理
• harness 之争取代模型之争
• 同意机制跟不上能力扩散
• 选举日重塑资产预期
• 职能型 AI 继续吸金

重点条目（含关键数字与下一步动作）：
• [2026-11-03] GitHub Dependabot 版本更新支持 Agent Package Manager，可自动更新 agent skills、prompts 与 instructions
  → 在测试仓库注册 1 个 skill 包，若 Dependabot 能自动开 PR 更新则判定可迁移到 skills 发布流程
  https://github.blog/changelog/2026-11-03-dependabot-version-updates-support-agent-package-manager
• [2026-11-03] Google DeepMind 发布 Antigravity 驱动的 agentic cheminformatics，用 Cheminformatics Skills 加速药物发现
  → 对照其 Skills 结构与 canonical AgentRole schema，若字段覆盖率不低于 80% 则考虑对齐
  https://deepmind.google/blog/agentic-cheminformatics-with-google-antigravity
• [35] HN 热帖：Nvidia RTX Spark 加密固件使第三方推理速度降至官方的 35%
  → 若后续实测降幅收窄到 15% 以内则解除对 RTX 系本地推理的选型顾虑
  https://www.mindstudio.ai/blog/linux-nvidia-rtx-spark-laptop
• [2026-11-04] SpecPilot 论文帖：并行投机解码离理论加速上限仍有差距，识别出三项系统挑战
  → 在我们的负载上复测 draft 接受率，低于其报告值 20% 则判定收益不成立
  https://www.reddit.com/r/LocalLLaMA/comments/1xnjrgj/paper_specpilot_autonomous_algorithm_discovery
• [0.50] Kitty 终端发布 0.50 版本
  → 在测试机升级后跑 tmux/kitty 脚本集，全部通过才升级主力机
  https://sw.kovidgoyal.net/kitty/changelog
• [2026-11-04] GitHub Copilot 用量 API 新增 BYOK 与企业自定义模型用量拆分
  → 对照其 API 字段，若能覆盖我们 5 类 provider 中至少 4 类则接入成本看板
  https://github.blog/changelog/2026-11-03-byok-and-enterpris