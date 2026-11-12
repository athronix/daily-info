**降价与改契约同日发生：模型把单价压到激活参数，工具把调用改成生成代码，资本却继续抬估值**

70% 的营收增速、2800 亿总参数、$65B 估值同日出现：Cerebras Q3 核心营收 $230.9M，文心5.5 用 2800 亿参数只激活 140 亿、推理超 200 token/秒，Kalshi 数周内把估值从 $40B 抬到 $65B；而 Claude Code v2.1.323 把工具调用改成模型写 JavaScript。张力在于：单价在降，插件契约与 runner 架构却同日收紧。

2026-11-13 · 入报 19 条 · 信源 126/185

今日主线：
• 版本号越小，权限改动越大
• 模型价格战打到激活参数
• 算力账本从营收走到每 token
• 资本抬估值，用户自己造工具
• Agent 比的是交付周期不是模型

重点条目（含关键数字与下一步动作）：
• [2.1.323] Claude Code v2.1.323 新增实验性 Code Mode，让 Claude 写 JavaScript 调用工具，并给 plugin.json 增加引擎版本约束
  → 跑一次隔离环境 smoke：启用 Code Mode 后若插件加载失败数为 0 且 engines 范围校验命中，才判定可接入
  https://github.com/anthropics/claude-code/releases/tag/v2.1.323
• [ARM32, node20] GitHub Actions 托管 runner 将在 8th Dec 2026 前停止 Windows 与 Linux 上的 ARM32 作业，此前已结束 node20 支持
  → 跑一次 workflow 矩阵：若 arm32 与 node20 作业各出现 1 次以上失败，则判定必须迁移 runner 标签
  https://github.blog/changelog/2026-11-12-actions-for-arm32-linux-windows-retirement
• [357, 343] Microsoft 365 服务降级事件在社区讨论中获得 357 分与 343 条评论并汇总多个状态页链接
  → 对照状态页复现一次：若降级持续超过 2 小时且告警未触达，则判定需为外部依赖加超时与本地留痕
  https://status.cloud.microsoft/
• [4, 403] Gemini 4 Hydrogen 发布帖在社区获得 403 分、268 条评论
  → 等第三方基准给出具体分数后，若 Hydrogen 单位 token 成本低于现用模型 20% 以上才进入切换评审
  https://blog.google/innovation-and-ai/models-and-research/gemini-models/introducing-gemini-4-hydrogen
• [20, 71%] 标题以 20 年与 71% 盲区描述深海 AI 大脑，摘要同时披露领渊智能完成千万级种子轮融资
  → 对照原始论文或融资公告核对 71% 的定义与测试集，若找不到出处则判定该读数不可入索引
  https://mp.weixin.qq.com/s?__biz=MzI3MTA0MTk1MA%3D%3D&mid=2652742286&idx=1&sn=7412d40e19e2c81d1c7c921926efb698&chksm=f01a4c444