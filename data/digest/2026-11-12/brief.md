**29,684 次提交换来官方模拟器，United 仍对 agent 关上门：接入层比模型层更卡**

29,684 次提交堆出的 aws-emulator 由官方给出本地服务克隆，United 却禁止 AI agent 代订机票（HN 162 分、150 评论）；同日 Pomerado 以 YC F26 身份把任意网站转成 MCP，Fractile 拿 $720M 挤进专用 AI 芯片赛道。今日张力是：接入层被资本与工具同时加速，却被服务方按下权限闸门。

2026-11-12 · 入报 12 条 · 信源 182/185

今日主线：
• Agent 卡在接入权限，不在模型
• 工具契约要写清失败与授权
• 可复现性被写成硬门槛
• 小版本里藏着要回归的行为
• 算力的钱流向专用与端侧

重点条目（含关键数字与下一步动作）：
• [100美元, 5.5] 谷歌上线 Gemini 4 Carbon 模型 API，向每月 100 美元 Ultra 订阅用户开放，摘要称其对标 Claude Opus 5.5 与 GPT-6 Astra
  → 等官方模型卡或 API 文档，若 100 美元档与 5.5 / 5.2 的对标结论同时被一手来源确认，才写入候选路由表。
  https://mp.weixin.qq.com/s?__biz=MzIzNjc1NzUzMw%3D%3D&mid=2247942861&idx=1&sn=41d0336965ce7b66565918f5d29e0dd8&chksm=e9f26d6615223de84b0445235e0ab28ed341a882ea76a8605119f697ddc73487dd4166ea0227&scene=0&xtrack=1
• [20] LFORLA 的 Capability Retention 基准用 20 个确定性任务、同一套提示词跑每个模型，讨论如何让评测数字可比
  → 固化同一组 20 条提示词跑 3 轮，若三轮得分极差 <2 个百分点，判定该回归集可作为跨版本基线。
  https://dev.to/resk/how-an-llm-benchmark-produces-comparable-numbers-inside-lforlas-llm-evaluation-47o5
• [29,684] AWS 推出官方 aws-emulator，可在本地克隆其多项服务跑测试而无需付费 API key，Rust 代码由 agent 群写出 29,684 次提交
  → 把 1 条现有 AWS 集成用例迁到本地克隆跑 10 次，若 10/10 通过且全程无需 API key，判定可替换云端联调。
  https://simonwillison.net/2026/Nov/11/aws-emulator
• [162, 150] United Airlines 禁止 AI agent 代替旅客订票，HN 条目获 162 分与 150 条评论
  → 在现有 connector 里模拟 403 / 需人工确认 / 限流 3 类拒绝响应，若 3/3 都落到可回滚状态，判定准入分支合格。
  https://www.cbsnews.com/news/united-airlines-bans-ai-agents-booking-flights
• [YOLOv8, Qwen2-VL] 作者用 YOLOv8 与 Qwen2-VL 在 8GB RAM 上搭阿拉伯语优先的盗窃检测，对标每月 $50-200