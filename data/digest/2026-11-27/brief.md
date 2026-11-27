**带单位的金额与版本号能逐字复核，日期年份、PR 编号与社区热度不能：今天进门禁的是 $1,500、0.40.19 与 13 个内核**

今日能逐字锁定的读数分两类：一类是带单位的量值——Clay 谈 $1,500 覆盖全球公司资格判定、两市融资余额单日减少 156.93亿元、新一代通信网测算约 7万亿元、英国央行下调 60个基点；另一类是版本号与计数——ollama v0.40.19、MLC AI 用 Lean 证明 13 个内核并牵出 3 个同步 bug。两类之外，日期年份、PR 编号、HN 分数与摘要末尾的长度标注都不进门禁。

2026-11-27 · 入报 7 条 · 信源 180/185

今日主线：
• 金额带单位才叫读数
• 版本号与计数能锁，编号不能
• 同一个规模数字，两种读法
• 形式化验证给的是计数不是覆盖率
• 基点与亿元量纲不同，别混排

重点条目（含关键数字与下一步动作）：
• [13, 3] MLC AI 开源 TxVerify，用 Lean 在 PTX 层形式化验证生产 GPU 内核，称证明 13 个 Blackwell GPU 内核并牵出 3 个同步 bug。
  → 拉取开源仓库跑 1 次最小复现，若 13 个内核无法在 2 个环境全部复现、或 3 个同步 bug 与清单定位不一致 ≥ 1 处，则判定暂缓引用其结论。
  https://arex-research.com/feeds/6dfc4fda-0539-45c9-b52d-89785b5a968b
• [$1,500] Clay 的 AI 负责人 Jeff Barg 谈如何用 $1,500 完成全球公司资格判定、客户为何排斥 model selector，以及如何为每个 agent 搭建 go-to-market 基础设施。
  → 搭 1 个 100 家公司的样本集跑 2 轮，若 $1,500 口径下字段缺失率 > 5% 或单轮耗时 > 30 分钟，则判定该成本不可复现、不进选型基线。
  https://latent.space/p/how-clay-builds-gtm-agents-jeff-barg-head-of-ai
• [30 spots, 5-10 minutes] BlueDot Impact 与 AI Safety Founders 联合发起 AI Safety Co-Founding Sprint，开放约 30 个名额、申请表耗时 5-10 minutes，配两周冲刺后向孵化器与资方引荐最强团队。
  → 核对主办方公告的 30 个名额与两周窗口，若 2 份材料缺任一项定义或入选名单，则判定规模仅为活动参数、不进观察表。
  https://www.lesswrong.com/posts/c9wNKhKfkiD2ePpDG/announcing-ai-safety-co-founding-sprint-in-san-francisco
• [0.40.19, 0.40.18] ollama 发布 v0.40.19-rc0，变更含 inkling2 短历史加速与 conv snapshots、mlxrunner 的 Engram 历史缓冲压缩，以及 llama-server 版本提升。
  → 在 2 个环境各跑 1 次会话恢复 smoke，若 0.40.18→0.40.19-rc0 后 conv snapshots 解析失败 ≥ 1 次，则判定暂缓升级并固定旧版。
  https://github.com/ollama/o