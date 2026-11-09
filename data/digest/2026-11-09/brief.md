**先证伪再采信：今天真正有分量的进展，都附了可复测的分母或自己会失败的闸门**

今天最硬的两个读数都带反例：DeepSeek Harness 披露 154 万日活、约 3.5 万第三方插件，公告却在补插件 API 稳定性；XBOW 在 65 个含漏洞应用上实测 GPT-6 Cyber 比 GPT-6.1 Sol 快约 2 倍，却少解出 5 个目标。规模与能力的账，都得先对上分母再采信。

2026-11-09 · 入报 16 条 · 信源 184/185

今日主线：
• 规模声明先看分母，再看口径
• 传闻与反驳同时到达，才值得进报
• Agent 的瓶颈在可回放，不在参数量
• 版本兼容是排查题，不是安装题
• 闸门要能自己失败，才配叫闸门

重点条目（含关键数字与下一步动作）：
• [154 万, 3.5 万] DeepSeek Harness 官方宣布筹建官方插件市场与作者扶持计划，并披露 154 万日活与约 3.5 万第三方插件
  → 逐项跑本仓库已装 skill 的接口声明，若任一 skill 在缺字段时静默降级次数大于 0，即判定契约层需收紧。
  https://arex-research.com/feeds/f054ae8c-c573-4940-bf3e-59bfbe0bb67f
• [2 倍, 5 个] XBOW 创始人 Oege de Moor 公布自建对照测试：在 65 个含漏洞的开源 Web 应用上对比 GPT-6 Cyber 与 GPT-6.1 Sol
  → 在同类任务复跑一次并同时记录耗时与解出数，若解出数仍少 5 个则判定快 2 倍不构成整体优势。
  https://arex-research.com/feeds/884a76f5-674f-43e2-9860-4f8569171d6b
• [12-factor-agents] humanlayer 开源 12-factor-agents，归纳构建可投入生产的 LLM 驱动软件所用原则
  → 把现有插件按 12 条原则逐项打勾，若超过 2 条无对应实现则判定分层需重排。
  https://github.com/humanlayer/12-factor-agents
• [100] SWE-agent 发布 mini-swe-agent，自称用 100 行实现的 AI agent 可解 GitHub issue 或在命令行协助
  → 对照其 100 行骨架复现一次最小 agent 循环，若本仓库 simple 路径代码超过其 3 倍则判定需拆分。
  https://github.com/SWE-agent/mini-swe-agent
• [Qwen2-VL-2B-Instruct, 2B] 开发者转换 Qwen2-VL-2B-Instruct 到 Rockchip 板，发现官方 RKLLM vision demo 在目标 transformers 上跑不起来，用五个版本二分定位
  → 在目标环境复现一次版本二分，若 5 个候选版本中定位不到首个可用版本则判定该依赖组合不可用。
  https://dev.to/anguoyang/the-official-rkllm-vision-demo-doesnt-run-on-the-transformers-it-targets-a-five-version-bisection-4a7i
• [7] 作者对比 7 个 multistream chat 工具，声称表格每个单元格都溯源到各家自己的文档，并开