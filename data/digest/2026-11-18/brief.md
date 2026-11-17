**同日刷新价格、营收与内存上限读数，但融资买的是流程、漏洞卡在版本、治理只剩期次——能数清的多了，能直接复用的仍要逐项验**

今日入报里，GPT‑6.2 Astra 定价降到前代的 80%，输入 $8/MTok、输出 $40/MTok；Nvidia 报出 $115.84 billion 创纪录营收；本地端侧却仍被 14.6 GB 内存与 4 GB GPU VRAM 卡住。张力在于：价格与营收都能数清，端侧可跑通、漏洞已修复、治理已闭环这类结论仍要一手验收，不能由读数直接推出。

2026-11-18 · 入报 10 条 · 信源 180/185

今日主线：
• 降价先落到长会话，端侧仍卡显存
• 两笔融资买的都是流程，不是模型
• 营收创纪录与治理记录是两本账
• 页数和样本量只是尺度，不是成果
• 自托管边界要写成版本与阈值

重点条目（含关键数字与下一步动作）：
• [6.2, 80%] OpenAI 推出 GPT‑6.2 Astra 与 GPT‑6.2 Sol，6.2 Astra 定价为前代 80%，输入 $8/MTok、输出 $40/MTok，缓存价 $0.40/million，LLM 0.38 已支持。
  → 连跑 10 次同类长会话并核对账单；若均价高于 $8/MTok input，则判定摘要价格不适用，改用实付成本重算。
  https://simonwillison.net/2026/Nov/17/gpt62-astra-and-sol
• [1009页, 650页] 赫尔辛基大学逻辑学家扬·冯·普拉托把哥德尔 1009 页手稿转录本输入 Claude，数日内生成 650 页解析，并称挖出数百个此前未被发现的定理。
  → 抽查 650 页解析中的定理；若独立可复核的新定理少于 1 条，则判定「数百个定理」为未证实断言，降级为线索。
  https://mp.weixin.qq.com/s?__biz=MzIzNjc1NzUzMw%3D%3D&mid=2247944324&idx=2&sn=aa3eb0414935136d02e8999ce363f0b1&chksm=e9cd62c0f0bedcc7a7b737f958128563c590e968ced43504cf152529e54ca0f6139cb1b4d474&scene=0&xtrack=1
• [0.9.21] 开发者 Oleksandr 发布自托管 AI bot 团队 kwant 0.9.21，用它控制 Home Assistant，并给出 GitHub 与 MCP docs 链接。
  → 按 MCP docs 跑 1 次最小接入；若 0.9.21 无法在 3 步内连通 Home Assistant，则判定自托管链路尚不可用。
  https://dev.to/ale_ukr/control-home-assistant-with-a-self-hosted-ai-bot-team-kwant-0921-3gha
• [14.6 GB, 4 GB] 工程文章记录 Tauri v2 + Node.js + PyTorch 的本地优先 AI 桌面应用撞上 14.6 GB RAM 与 4 GB GPU VRAM 限制，起因是读 500-page 教材。
  → 在本机 4 GB 显存下复现 500-page 文档处理；若 2 次均因内存溢出中断，则判定该配置不可纳入自托管队列。
  https://dev.to/ayumuml/taming-a-146-gb-ra