**版本号与金额能逐字复核，日期年份与社区热度不能：今天进门禁的是 1.8.5、$33B 与 1% 这些带单位或口径的读数**

今日能逐字锁定的读数集中在版本号与金额：langchain-core 发布 1.8.5、langchain-anthropic 发布 1.7.13，ElevenLabs 目标估值 $33B 与年度经常性收入 $700M，Netflix 宣布 $380 million 收购；而 Nasdaq 100 当日跌 1%、Bloomberg 标题里的 10% 只剩一个百分比。

2026-11-26 · 入报 8 条 · 信源 181/185

今日主线：
• 版本号能锁，PR 编号不能
• 金额带单位才叫读数
• 百分比要绑定统计窗口
• 同一批市场数据，两种读法
• 规模数字不等于能力证明

重点条目（含关键数字与下一步动作）：
• [1.8.5, 1.8.4] LangChain 发布 langchain-core 1.8.5，复用 provider message id 并澄清 v3 runtime 警告与流式事件 API 说明。
  → 在 2 个环境各跑 1 次流式复现，若 provider message id 复用失败 ≥ 1 次或 1.8.4→1.8.5 后 chunk 结构变化，则判定暂缓升级。
  https://github.com/langchain-ai/langchain/releases/tag/langchain-core%3D%3D1.8.5
• [1.7.13, 1.7.12] LangChain 发布 langchain-anthropic 1.7.13，新增接受自定义 HTTP 与 SDK clients，并刷新 model profile 数据。
  → 注入 1 个自定义 HTTP client 跑 2 次调用，若 1.7.13 与 1.7.12 的超时默认值不一致 ≥ 1 处，则判定需在配置层显式固定。
  https://github.com/langchain-ai/langchain/releases/tag/langchain-anthropic%3D%3D1.7.13
• [60] 智源社区报道北京智源人工智能研究院举办物理AI开放日，汇聚60余家机构并发布 REAL 开放创新平台与 RE 系列成果。
  → 核对开放日材料是否给出 60 家参会清单与评测指标定义；若缺任一项，则判定该规模数字不可复算，仅留事实层。
  https://mp.weixin.qq.com/s?__biz=MzI2MDcxMzQzOA%3D%3D&mid=2247551620&idx=1&sn=eaa4b2b4d19e5c62c304b2ffa6970f75&chksm=eb5467279af72de6d30a7c7e49df62c47010b1d6b7535876dc89f02202cdd44a832868b29fd5&scene=0&xtrack=1
• [$33B, $22B] Techmeme 转述 Bloomberg 消息人士称 ElevenLabs 就新一轮融资初步接洽，目标估值 $33B，高于此前 $22B，年度经常性收入 $700M。
  → 找 2 份一手公告核对 $33B 与 $700M；若一致家数少于 2 或未标轮次状态，则判定金额仅为媒体口径，留线索池。
  https://www.techmeme.com/261125/p30
• [$380 million] Blo