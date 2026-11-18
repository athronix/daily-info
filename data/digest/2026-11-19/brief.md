**同一天里，版本号与 CVE 编号能直接写进门禁，融资额与并购额只是绝对值，真正决定能不能接的是复现率与改动清单**

今日入报里，107 条 AI 设计抗体仅不足 30% 通过实验验证，1,200 项任务 RL 把 Terminal-Bench 4.1 从 5.6% 提到 12%；HomeView 27.2.1 与 vLLM 0.34.0 给出可匹配版本号，CVE-2026-99312 给出可扫描编号；Lilly 并购越过 $32B、Payhawk 融资 $280M。张力在于：编号、版本、复现率能逐字回查，金额与型号却推不出可用性。

2026-11-19 · 入报 11 条 · 信源 181/185

今日主线：
• 同一个 27.2.1，两种信息量
• 能写进规则的是编号与版本
• 复现率比 SOTA 更能定能不能接
• 计数口径不同，并成一句就失真
• 金额是绝对值，推不出闭环

重点条目（含关键数字与下一步动作）：
• [27.2.1] Apple 为 HomeView 设备发布 27.2.1 版软件更新，是上市后首次更新，摘要称未公布具体改动或安全修复细节、也未列出 CVE 条目。
  → 核对官方 release notes 是否列出改动项；若可逐条核对的修复项少于 2 条，则判定该版本缺可复现依据，不写入变更基线。
  https://www.macrumors.com/2026/11/18/homeview-27-2-1-software
• [99, 7] 一项研究确认玻利维亚 Madidi 国家公园有 100 个蝙蝠分类单元，其中 99 个已确认物种、7 个为该国新记录。
  → 核对原文是否列出 100 个分类单元明细；若无法逐项对应 99 与 7，则判定口径混用，只保留可复核的物种计数。
  https://phys.org/news/2026-11-bolivia-madidi-national-species-country.html
• [0.34.0] vLLM 0.34.0 改动默认 GPU 内存配置与 block size 以优化高负载吞吐，这份周报同时提到 Mistral Vibe Desktop 与对新模型的早期批评。
  → 同一高负载用例在旧版与 0.34.0 各跑 3 次；若新版吞吐低于旧版达到 2 次，则判定新默认配置不适用，回退为显式配置。
  https://dev.to/githubopensource/vllm-0340-mistral-vibe-desktop-and-early-critiques-of-gpt-62-astra-kh1
• [19, 18] 一篇 benchmark 复盘记录了 18 次运行里出现第 19 次提交：agent 被判定否决后又提交一次，Vow 与 TypeScript 最终打平。
  → 回放该 benchmark 的 18 次运行日志；若重跑后提交次数与运行次数仍不相等，则判定判定器状态未隔离，不接入自动评测。
  https://dev.to/jakeburwick/submission-19-of-18-runs-the-benchmark-where-vow-and-typescript-tied-27ef
• [27.2.1, 27.3] Apple 发布 HomeView 27.2.1，摘要列出恢复与 iOS 27.3 beta 配对时的 Siri 功能、修正 Siri 支持下载、避免新增 hub 时被移出家庭网络。
  → 逐条核对 3 