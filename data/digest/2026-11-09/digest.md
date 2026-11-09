# 先证伪再采信：今天真正有分量的进展，都附了可复测的分母或自己会失败的闸门

> 今天最硬的两个读数都带反例：DeepSeek Harness 披露 154 万日活、约 3.5 万第三方插件，公告却在补插件 API 稳定性；XBOW 在 65 个含漏洞应用上实测 GPT-6 Cyber 比 GPT-6.1 Sol 快约 2 倍，却少解出 5 个目标。规模与能力的账，都得先对上分母再采信。

> 2026-11-09 · 北京时间 · 生成于 2026-11-09T01:51:44.934256Z

## 📌 今日速览

- **DeepSeek Harness 官方宣布筹建官方插件市场与作者扶持计划，并披露 154 万日活与约 3.5 万第三方插件**（154 万, 3.5 万） — 规模数字与补接口稳定性、强化插件安全写在同一份公告里，说明生态瓶颈已从数量转到契约。
- **XBOW 创始人 Oege de Moor 公布自建对照测试：在 65 个含漏洞的开源 Web 应用上对比 GPT-6 Cyber 与 GPT-6.1 Sol**（2 倍, 5 个） — 同一组测试给出快约 2 倍与少解出 5 个目标两个反向读数，速度结论无法单独成立。
- **X 账号 Token Gremlin 称 GPT-6.2 Sol 已对部分 ChatGPT 用户灰度现身，约半小时后 Harshith 以截图反驳称实为 GPT-6.1 Sol**（GPT-6.2 Sol, GPT-6.1 Sol） — 首发说法在半小时内被截图级别的复现反驳，说明灰度爆料必须先有可比对证据。
- **日本 AI Robot Association（AIRoA）公开双臂操作基础模型 AIRoA-0，权重放上 Hugging Face、三套代码放上 GitHub，自报十类任务成功率 78%**（78%, AIRoA-0） — 把权重、代码与技术报告一并放出，使 78% 从宣传值变成可被第三方复测的读数。
- **一篇 DIY 指南介绍用 vLLM 在本地构建 D3 Decision Models 多模态 AI 应用**（D3） — 把多模态应用压回本地推理栈，讨论重点从模型选型转向部署与评估方法。
- **humanlayer 开源 12-factor-agents，归纳构建可投入生产的 LLM 驱动软件所用原则**（12-factor-agents） — 把生产可用性拆成可逐条核对的原则清单，比宣称某个框架更好用更可迁移。

---

## 🔥 今日主线

### 一、规模声明先看分母，再看口径
154 万日活与 3.5 万插件是自建生态口径，65 个应用是自建对照集，78% 是自报成功率；三者量级都只在给定分母内成立，跨口径外推即失效。（3 条独立条目佐证）

### 二、传闻与反驳同时到达，才值得进报
GPT-6.2 Sol 灰度说在约半小时后被截图反驳为 GPT-6.1 Sol；AIRoA-0 放出权重与代码让 78% 可被复测；pytest 把争议拆成 28 tests。可核验性来自反例与可下载物。（3 条独立条目佐证）

### 三、Agent 的瓶颈在可回放，不在参数量
12-factor-agents 把生产级原则写成清单，mini-swe-agent 用 100 行收敛复杂度，Week 7 的 LLM 更正了错误测量并合并却仍是 $0；三者都在说状态与交接。（3 条独立条目佐证）

### 四、版本兼容是排查题，不是安装题
RKLLM 官方 vision demo 在目标 transformers 上跑不起来，靠五个版本二分定位；7 个工具对比每格都溯源到自家文档；共同点是把断言换成可复现的定位过程。（3 条独立条目佐证）

### 五、闸门要能自己失败，才配叫闸门
pytest 把 18 claims 落成 28 tests，12-factor-agents 把生产可用性拆成可逐条核对的原则，7 工具对比每格给出处；都要求检查项能独立判失败，而非靠人确认。（3 条独立条目佐证）

### 六、资本读数与工程读数不在同一张表
OpenAI 以 $11B 融资对应 $1.25T 估值，日本拟采购 27,500 颗 Rubin 芯片，DeepSeek Harness 披露 154 万日活；前两者是交易与采购口径，后者是产品使用口径。（3 条独立条目佐证）

### 七、无关条目也要写清为什么无关
H3mm15 与 H3.3 是分子标识，5 项 PlayStation App 功能是清单编号，D3 是模型命名；这类数字可核验但不承载工程判断，如实标注暂无直接影响比硬贴热点更可信。（3 条独立条目佐证）

---

## 🗂 分类聚合

### 模型与研究（5 条）

**DeepSeek Harness 官方宣布筹建官方插件市场与作者扶持计划，并披露 154 万日活与约 3.5 万第三方插件**
- 关键数字：154 万 / 3.5 万 · 相关方：DeepSeek Harness / Growing Together with Our Plugin Communi / 插件 API / token · 来源：智源社区 · 最新分享（匿名 API） · 2026-11-08 18:47 UTC · 78.06 分
- 为什么值得看：规模数字与补接口稳定性、强化插件安全写在同一份公告里，说明生态瓶颈已从数量转到契约。
- 对我意味着什么：直接对应 WorkBuddy 的 skill 与 MCP 生态：当第三方插件达到 3.5 万量级，先塌的会是接口契约与权限边界，而不是模型能力。
- 下一步：逐项跑本仓库已装 skill 的接口声明，若任一 skill 在缺字段时静默降级次数大于 0，即判定契约层需收紧。
→ https://arex-research.com/feeds/f054ae8c-c573-4940-bf3e-59bfbe0bb67f

**XBOW 创始人 Oege de Moor 公布自建对照测试：在 65 个含漏洞的开源 Web 应用上对比 GPT-6 Cyber 与 GPT-6.1 Sol**
- 关键数字：2 倍 / 5 个 / 65 个 · 相关方：XBOW / Oege de Moor / GPT-6 Cyber / GPT-6.1 Sol / OpenAI / LinkedIn · 来源：智源社区 · 最新分享（匿名 API） · 2026-11-08 18:44 UTC · 74.83 分
- 为什么值得看：同一组测试给出快约 2 倍与少解出 5 个目标两个反向读数，速度结论无法单独成立。
- 对我意味着什么：对 automation 评估的提醒：agent 或模型的耗时指标必须与完成数一起看，否则会把漏做当成变快。
- 下一步：在同类任务复跑一次并同时记录耗时与解出数，若解出数仍少 5 个则判定快 2 倍不构成整体优势。
→ https://arex-research.com/feeds/884a76f5-674f-43e2-9860-4f8569171d6b

**X 账号 Token Gremlin 称 GPT-6.2 Sol 已对部分 ChatGPT 用户灰度现身，约半小时后 Harshith 以截图反驳称实为 GPT-6.1 Sol**
- 关键数字：GPT-6.2 Sol / GPT-6.1 Sol / 5 秒 / 18:07 · 相关方：Token Gremlin / Harshith / ChatGPT / GPT-6.2 Sol / GPT-6.1 Sol · 来源：智源社区 · 最新分享（匿名 API） · 2026-11-08 18:58 UTC · 78.17 分
- 为什么值得看：首发说法在半小时内被截图级别的复现反驳，说明灰度爆料必须先有可比对证据。
- 对我意味着什么：对数据基建的直接映射：候选集里的单源爆料应有独立佐证字段，否则不该进入 AI 研判的入选簇。
- 下一步：核对该模型是否有官方发布页或版本号记录，若 2 个独立来源都查不到则判定为未证实爆料并降级处理。
- 证据状态：unverified（未独立验证）
→ https://arex-research.com/feeds/a367dcbd-c32f-422a-8a99-1e2d3b063b59

**日本 AI Robot Association（AIRoA）公开双臂操作基础模型 AIRoA-0，权重放上 Hugging Face、三套代码放上 GitHub，自报十类任务成功率 78%**
- 关键数字：78% / AIRoA-0 / arXiv:2611.03815 · 相关方：AIRoA / AI Robot Association / AIRoA-0 / Hugging Face / GitHub / bimanual manipulation · 来源：智源社区 · 最新分享（匿名 API） · 2026-11-08 18:36 UTC · 74.75 分
- 为什么值得看：把权重、代码与技术报告一并放出，使 78% 从宣传值变成可被第三方复测的读数。
- 对我意味着什么：对本项目确定性脚本做索引、AI 只做研判的印证：底层产物可下载，AI 层才不必替上游补洞。
- 下一步：在同类十类任务上复测一次，若成功率与 78% 偏差超过 10 个百分点则判定该值仅为自报口径。
→ https://arex-research.com/feeds/e45443e5-b169-42f0-8229-eec29f656a24

**一篇 DIY 指南介绍用 vLLM 在本地构建 D3 Decision Models 多模态 AI 应用**
- 关键数字：D3 · 相关方：D3 Decision Models / vLLM / AI infrastructure · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-08 11:00 UTC · 74.08 分
- 为什么值得看：把多模态应用压回本地推理栈，讨论重点从模型选型转向部署与评估方法。
- 对我意味着什么：对数据基建的参照：本地 vLLM 路线可评估离线快照节点的推理可行性，但摘要未给出吞吐读数。
- 下一步：在同一台机器上跑一次本地推理基准，若单请求延迟高于云端基线 2 倍则判定不适合承载常驻任务。
→ https://dev.to/sharathjapa/diy-guide-d3-decision-models-build-fast-multimodal-ai-applications-locally-with-vllm-2822

### Agent 与工程（3 条）

**humanlayer 开源 12-factor-agents，归纳构建可投入生产的 LLM 驱动软件所用原则**
- 关键数字：12-factor-agents · 相关方：humanlayer / 12-factor-agents / LLM · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-09 00:03 UTC · 79.92 分
- 为什么值得看：把生产可用性拆成可逐条核对的原则清单，比宣称某个框架更好用更可迁移。
- 对我意味着什么：可直接对照 WorkBuddy 的 skill、MCP 与 A2A 分层，检查工具注册、状态与权限是否各自有明确归属。
- 下一步：把现有插件按 12 条原则逐项打勾，若超过 2 条无对应实现则判定分层需重排。
→ https://github.com/humanlayer/12-factor-agents

**SWE-agent 发布 mini-swe-agent，自称用 100 行实现的 AI agent 可解 GitHub issue 或在命令行协助**
- 关键数字：100 · 相关方：SWE-agent / mini-swe-agent / GitHub · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-09 00:03 UTC · 78.32 分
- 为什么值得看：用 100 行把 agent 骨架收敛到可读规模，暴露的是编排逻辑而非框架体积。
- 对我意味着什么：对 WinVM Bridge 的直接参照：直接 MCP 工具调用这条简单路径应能收敛成一个可读的最小实现。
- 下一步：对照其 100 行骨架复现一次最小 agent 循环，若本仓库 simple 路径代码超过其 3 倍则判定需拆分。
→ https://github.com/SWE-agent/mini-swe-agent

**一个由 LLM agent（Claude Code）运营的账户自述第 7 周更正了一处错误测量并被合并，收入仍为 $0**
- 关键数字：Week 7 / $0 · 相关方：Claude Code / Vellum Labs / LLM agent / API · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-08 23:02 UTC · 79.2 分
- 为什么值得看：把错误测量公开更正并合并进流程，比宣称自主赚钱更接近可复盘的 agent 运行记录。
- 对我意味着什么：对 automation 的直接提醒：无人值守任务的价值是可回放的状态与更正记录，而非单轮结果。
- 下一步：在本流水线补一条更正留痕字段，若 1 条被更正读数无法追溯到原条目则判定回放链不完整。
- 证据状态：unverified（未独立验证）
→ https://dev.to/vellumkasane/week-7-of-an-llm-trying-to-earn-money-on-its-own-i-posted-a-wrong-measurement-corrected-it-and-558j

### 开发者工具与版本（2 条）

**开发者转换 Qwen2-VL-2B-Instruct 到 Rockchip 板，发现官方 RKLLM vision demo 在目标 transformers 上跑不起来，用五个版本二分定位**
- 关键数字：Qwen2-VL-2B-Instruct / 2B · 相关方：Qwen2-VL-2B-Instruct / Rockchip / rknn-llm / transformers / RKLLM · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-08 22:11 UTC · 78.61 分
- 为什么值得看：官方 demo 与目标版本不兼容这件事靠逐版本回退定位，比换更大模型更贴近真实工程成本。
- 对我意味着什么：对 WinVM 与桌面端插件的启示：宿主依赖版本变更后应跑一次最小复现，而不是只看安装是否成功。
- 下一步：在目标环境复现一次版本二分，若 5 个候选版本中定位不到首个可用版本则判定该依赖组合不可用。
→ https://dev.to/anguoyang/the-official-rkllm-vision-demo-doesnt-run-on-the-transformers-it-targets-a-five-version-bisection-4a7i

**作者对比 7 个 multistream chat 工具，声称表格每个单元格都溯源到各家自己的文档，并开源了配套工具 CrossChat**
- 关键数字：7 · 相关方：CrossChat / OBS / multistream chat tools · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-08 17:17 UTC · 74.0 分
- 为什么值得看：把每个比较单元格都挂回一手文档，是对照表能否被复核的分界线。
- 对我意味着什么：直接呼应本项目数字白名单闸门：结论只有能逐项回原文才准进报，跨源拼凑的值一律丢弃。
- 下一步：抽查表中任意 7 个单元格的出处链接，若有 1 个打不到对应文档则判定该对比不可引用。
→ https://dev.to/randynorthrup/7-multistream-chat-tools-compared-every-cell-sourced-to-their-own-docs-239c

### 安全与治理（1 条）

**开发者用 pytest 审计两个物理预印本，把 18 claims 落成 28 tests，强调不做人身攻击**
- 关键数字：18 / 28 · 相关方：pytest / physics preprints / claims / tests · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-08 22:42 UTC · 78.96 分
- 为什么值得看：把争议主张转成会红会绿的测试用例，让分歧落在可复现的断言上而非立场。
- 对我意味着什么：对 verify_digest 的直接参照：检查项应能自己失败，本项目仍缺删项后退出码的反面测试。
- 下一步：给发布闸门补一条删除检查项后的退出码断言，若删掉 1 项脚本仍返回 0 即判定闸门无效。
→ https://dev.to/magopredator/auditing-a-fringe-physics-theory-with-pytest-18-claims-28-tests-no-ad-hominem-45b5

### 深度长文（1 条）

**Latent Space 访谈 Mihail Eric 与 Monaco 团队，讲斯坦福 CS146S 如何教 AI-Native 工程**
- 关键数字：CS146S · 相关方：Stanford / CS146S / Mihail Eric / Monaco · 来源：Latent Space · 2026-11-08 21:41 UTC · 73.48 分
- 为什么值得看：当学生能一次做完去年的作业，课程要教的就从写法转到验收与系统判断。
- 对我意味着什么：对 skill 与 automation 设计的参照：把可一键生成的部分交给 agent，工程重心移到可验证的验收条件。
- 下一步：挑 1 个本仓库可自动生成的产物补上验收断言，若断言缺失数大于 0 则判定该产物不可直接采信。
→ https://latent.space/p/cs146s

### 产业与资本（1 条）

**一份备忘录全文提到 Nvidia CEO Jensen Huang 致员工说明，同篇提到日本计划采购 27,500 颗下一代 Rubin 芯片**
- 关键数字：27,500 · 相关方：Jensen Huang / Nvidia / Rubin · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-08 22:54 UTC · 74.31 分
- 为什么值得看：备忘录全文与采购数字同框，提醒公司治理事件与产能读数应分开核对，不能互相背书。
- 对我意味着什么：暂无直接影响：属公司治理与芯片采购公开信息，与 agent 部署及数据基建无工程交集，仅作量级读数核验样本。
- 下一步：核对 27,500 是否有第二处公开来源，若仅此 1 处则判定该采购量级不可直接引用。
→ https://www.theverge.com/ai-artificial-intelligence/1029595/full-text-jensen-huang-affair-memo-nvidia

### 市场与投资（1 条）

**一条 Folo 基线目标题称 OpenAI 以 $11B 融资对应 $1.25T 估值，摘要仅剩 Comments 无进一步细节**
- 关键数字：$11B / $1.25T · 相关方：OpenAI · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-08 14:49 UTC · 74.29 分
- 为什么值得看：标题给出融资额与估值两个量级，但摘要缺失使口径无法核对，属于典型的可读不可引条目。
- 对我意味着什么：对数据基建的提醒：候选集应把标题数字与可核验摘要分开标记，缺摘要时不得当作完整事实入报。
- 下一步：补一手来源核对 $11B 与 $1.25T 是否分别对应融资额与估值，若 2 个数字口径混淆则判定该条不可引用。
- 证据状态：unverified（未独立验证）
→ https://247wallst.com/investing/2026/11/07/openai-just-raised-11-billion-at-a-1-25-trillion-valuation-below-the-1-4-trillion-it-first-sought

### 论文与学术（1 条）

**九州大学研究者发现组蛋白 H3.3 亚型 H3mm15 参与小鼠精子发育的正常调控**
- 关键数字：H3mm15 / H3.3 · 相关方：Kyushu University / H3mm15 / H3.3 / histone · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-09 00:10 UTC · 78.4 分
- 为什么值得看：用具体亚型编号而非笼统的组蛋白修饰来定位机制，结论才能被后续实验逐项复核。
- 对我意味着什么：暂无直接影响：属表观遗传学研究，与 WorkBuddy、MCP 及 agent 部署无工程交集，仅作可核验标识符样例。
- 下一步：核对 H3mm15 与 H3.3 是否在同篇报告中被明确区分，若 2 个编号指向同一对象则判定表述冗余。
→ https://phys.org/news/2026-11-small-histone-differences-gene-sperm.html

### 文档与变更（1 条）

**一篇清单文章列出 5 个被低估的 PlayStation App 功能，称可让用户使用更省事**
- 关键数字：5 · 相关方：PlayStation App · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-08 19:00 UTC · 73.39 分
- 为什么值得看：用固定条数组织功能清单，读者可逐项核对是否真的被低估，而非接受一个整体评价。
- 对我意味着什么：暂无直接影响：属消费应用功能清单，与 agent 部署及数据基建无工程交集，仅作清单式条目样本。
- 下一步：逐项核对 5 个功能在当前客户端是否仍存在，若缺失超过 1 项则判定该清单已过期。
→ https://www.engadget.com/2309256/underrated-playstation-app-features

---

## 📊 今日数据概览

| 指标 | 数值 |
| --- | ---: |
| 信源可用 | 184 / 185 |
| 原始条目 | 1177 |
| 聚合簇 | 1095 |
| 入选簇 | 40 |
| 实际入报 | 16 |
| 七要素达标 | 16 / 16（100.0%） |
| 引用域名数 | 8 |

高频来源：dev.to(5)、arex-research.com(4)、github.com(2)、latent.space(1)、theverge.com(1)、247wallst.com(1)、phys.org(1)、engadget.com(1)

---

## 🔭 待验证信号（可证伪）

| 信号 | 判定阈值 | 达到后判定 |
| --- | --- | --- |
| 已装 skill 接口契约缺字段时是否静默降级 | 逐项跑接口声明，静默降级次数大于 0 | 判定契约层需收紧，先补显式报错再谈扩规模 |
| 发布闸门删项后是否真的失败 | 人为删掉 1 个检查项后脚本退出码不等于 0 | 判定闸门有效，否则视为人工确认的伪装 |
| AIRoA-0 自报成功率能否被独立复测 | 十类任务复测结果与 78% 偏差超过 10 个百分点 | 判定 78% 属自报口径，不可直接引用为通用指标 |
| 速度优势是否以解出数为代价 | 在 65 个含漏洞应用上复跑，解出目标数仍少 5 个 | 判定快 2 倍不等于整体能力更强，需按解出数加权 |
| 同日同通道分发幂等记录 | push-log.jsonl 中同日同通道重复计数大于 0 | 判定幂等失效，暂停该通道分发并核对待授权清单 |

---

## 💡 编者观察

分母比量级重要。40 个入选簇只有 16 条带得住实质读数，其余按 v1.1 拒绝入报：22 条原文无数字，3 条的数字只是日期年份或用户名尾数。本期数据覆盖不足，未放宽阈值，被剔除条目进 no-number 待补清单。

对 WorkBuddy，最直接的是 DeepSeek Harness：154 万日活、约 3.5 万第三方插件，公告重心却在插件 API 稳定性与安全。这和 skill 与 MCP 生态是同一道题：规模到量级后先塌的是接口契约。可证伪动作：逐项跑已装 skill 的接口声明，若任一缺字段时静默降级不报错，就判定契约层需收紧。

闸门要能自己失败。pytest 把 18 claims 落成 28 tests，XBOW 在 65 个应用上给出快 2 倍却少解出 5 个目标的反向读数。本流水线已有零 violations 核验，缺的是反面测试：删掉 1 个检查项后若脚本仍返回 0，闸门就是伪装。

A2A 与 agent 部署侧盯可回放。12-factor-agents 的原则清单、mini-swe-agent 的 100 行收敛、更正了错误测量却仍是 $0 的自主 agent，都指向状态可恢复与交接可判定。WinVM Bridge 的 streaming 进度同理，先定谁在何时接管。市场与资本只陈述公开数字，不构成任何建议。

---

*本日报由规则层采集/去重/打分 + AI 研判生成；每条附原文链接，关键数字须能在原文中找到。*
*外部事实未独立验证，内容仅供参考，不构成投资建议；取不到可靠数据处标注「暂无可靠数据」。*
