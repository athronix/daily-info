**运行时延迟与 VM 逃逸同日出现，Agent 工程的瓶颈已从模型转向权限与隔离，资本定价仍在松动**

AegisKernel 把零信任 POSIX 运行时压到 <0.016ms，同一天 Firecracker VM 逃逸被公开；Anthropic 的 IPO 估值口径下修到 $1.3T，Fox 以 $22 billion 完成对 Roku 的收购。张力在于：隔离与权限的读数在收紧，资本定价却在松动——工程侧能复现的数，和交易侧仍在重估的数，构成今天最清楚的对照。

2026-11-07 · 入报 12 条 · 信源 182/185

今日主线：
• 零信任压低延迟，VM 逃逸同期被翻开
• Agent 主动来电，先设静默阈值
• 估值口径下修，交易落地同日出现
• 成本与基准都写成了可复现的数
• 苹果这轮只动交互层，没动算力

重点条目（含关键数字与下一步动作）：
• [3D] SketchAgentBench 把 LLMs 的 3D 空间推理做成可跑的评测基准
  → 取该基准跑一次本地 smoke，若 3D 任务通过率低于 60% 则判定当前 provider 不满足空间推理接入条件
  https://sketchagent.dev/
• [4x] 可求助 Opus 的 Jev 以 4x 更低成本取得 Opus 级准确率
  → 对照 Opus 基线跑 200 条样本，若成本比达到 4 且准确率差小于 2 个百分点才判定可切换路由
  https://hightouch.com/blog/llm-judges-identity-resolution
• [0.016ms] AegisKernel 宣称面向 AI agents 的零信任 POSIX 运行时开销低于 0.016ms
  → 在隔离测试环境跑 100 次冷启动，若 P99 延迟不超过 0.016ms 且 0 violations 才列入沙箱候选
  https://adikshatriyag-crypto.github.io/aegis-kernel
• [2] 一位开发者的后台 AI agent 在 2am 主动来电，且已先定位到 bug
  → 给通知链路设静默窗口，若非工作时段触发 1 次即判定该主动通道应默认关闭并回到人工确认
  https://dev.to/natuworkguy/my-ai-agent-called-me-at-2am-i-picked-up-it-had-already-found-the-bug-bcb
• [$2,899, $3,399] Apple 的 OLED 触控 MacBook Pro 提供 14 与 16 英寸机型，起价分别为 $2,899 与 $3,399
  → 若后续出现 2 个以上独立来源确认触控提升效率，才把它列入开发机换机依据
  https://www.macrumors.com/2026/11/06/oled-macbook-pro-hands-on
• [14, 16] 14 与 16 英寸 MacBook Pro 的发光 Apple logo 需在 Terminal 用命令关闭
  → 把该命令纳入设备配置脚本并跑一次 dry-run，若 0 处副作用才允许在其它机器复用
  https://www.macrumors.com/how-to/turn-glowing-apple-logo-macbook-pro
• [2] PwnEscape 第 2 部分公开 Firecracker VM 逃逸路径
  →