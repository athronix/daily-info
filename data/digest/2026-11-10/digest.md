# Fable 5.2 同日进入榜单、CLI 与本地运行时，但 128,000 token 的失败暴露默认档可信度缺口

> Fable 5.2 在 Artificial Analysis 得 65 分，同日 claude-code v2.1.321 设为默认并给出 1M 上下文与 $8/$40 每 Mtok 定价，ollama v0.40.16 把 65B 的 Ripple Preview 收进本地运行时、让 Qwen3.8 少用 27 GiB 内存；但 llm-anthropic 0.31 实测 max 档耗尽 128,000 token 仍返不出图。

> 2026-11-10 · 北京时间 · 生成于 2026-11-10T02:09:37.536152Z

## 📌 今日速览

- **Simon Willison 发布 llm-anthropic 0.31 适配 Fable 5.2 与 Mythos 5.2，并实测五档推理档生成 SVG 的表现**（0.31, 5.2） — 适配速度虽快，但 max 档耗尽 128,000 token 后连图都返回不出，且这是 Fable 系列新出现、Opus 5.5 时代已有的同类故障，说明新模型的极限档不能默认信任。
- **Anthropic 发布 Claude Fable 5.2 与 Mythos 5.2，称输出速度最高快 30 percent 且在技术科学基准上超过 Opus 5.5**（5.2, 30） — 两款模型同架构但 Fable 5.2 多了网络安全与生物护栏，说明差异已落在策略层而非能力层；30 percent 是厂商口径，缺独立复测。
- **claude-code v2.1.321 将 Claude Fable 5.2 设为默认模型，给出 1M 上下文定价，并修复 MCP OAuth 重定向泄露凭据等缺陷**（2.1.321, 1M） — 这次修复集中在信任边界：OAuth 重定向把 refresh token 发往另一主机、只读 Bash 越出沙箱、cp 与 mv 写入绕过 deny 规则，比模型升级更值得先回归。
- **Apple 为 iOS、iPadOS 与 macOS 27.2.1 发布安全更新，修复 iMessage 群聊历史越权访问与 AirPlay、Bluetooth 恶意配对缺陷**（27.2.1） — 更新同时为命令行工具补上 eMudhra 证书防护，影响的不是功能而是本地脚本的信任链，公开细节后未升级设备的利用风险上升。
- **GitHub 项目 virattt/dexter 以 TypeScript 实现面向深度金融研究的自主 agent，仓库标注 27,804 星**（27,804） — 星数只说明关注度，摘要未给任务成功率或 handoff 契约；把它当架构样本前需先确认它返回的是结构化结果还是一段消息。
- **opensandbox-group 开源 OpenSandbox，定位为面向 AI agents 的 Python 沙箱运行时，仓库标注 16,914 星**（16,914） — 把沙箱做成独立运行时而非宿主进程内的权限判断，与同日 claude-code 修复的 Bash 越沙箱问题形成呼应：隔离层正在外移。

---

## 🔥 今日主线

### 一、模型发布先看工具链是否同日接住
Fable 5.2 发布当天，claude-code 设为默认、llm-anthropic 0.31 完成适配、ollama 把 65B 模型收进本地运行时；可用性取决于生态适配速度，而不是榜单上的 65 分。（4 条独立条目佐证）

### 二、最高推理档的失败比分数更值钱
65 分是 Artificial Analysis 的榜单口径，而 llm-anthropic 实测 max 档耗尽 128,000 token 仍无输出；接入前必须用同一提示词复现长任务，不能按分数排序选模型。（3 条独立条目佐证）

### 三、MCP 的漏洞在凭据重定向而非协议
claude-code v2.1.321 修掉 MCP OAuth 重定向把 refresh token 发往另一主机、只读 Bash 越出沙箱、cp 与 mv 绕过 deny 规则；这类边界错误正是 agent 部署最易忽略的面。（3 条独立条目佐证）

### 四、沙箱与运行时开始独立成层
OpenSandbox 把 AI agent 沙箱做成独立 Python 运行时（16,914 星），dexter 以 TypeScript 做自主金融研究 agent（27,804 星）；工程重心正从模型调用转向执行环境隔离。（3 条独立条目佐证）

### 五、本地推理的收益要按 GiB 计量
ollama v0.40.16 让 Qwen3.8 Flash Next 在 Apple silicon 上少用 27 GiB 内存并补上 CUDA 13.5 与 Windows on ARM；内存下降比参数规模更能决定本机能否常驻。（2 条独立条目佐证）

### 六、版本号里藏着行为破坏性变更
v0.40.16 改了 /v1/responses 默认截断与 /v1/models 空返回值，v2.1.321 改了 remote-control 的 --settings 会话语义；只盯版本号会漏掉需要回归的调用约定。（3 条独立条目佐证）

### 七、无人值守脚本要设金额与证书双阈值
Solana 买入机器人复盘的 5 个 bug 之一让每笔金额翻倍，Apple 27.2.1 又为命令行工具新增 eMudhra 证书防护；无人值守动作若缺金额上限与证书链校验，一次重定向就足以放大损失。（3 条独立条目佐证）

---

## 🗂 分类聚合

### 模型与研究（2 条）

**Simon Willison 发布 llm-anthropic 0.31 适配 Fable 5.2 与 Mythos 5.2，并实测五档推理档生成 SVG 的表现**
- 关键数字：0.31 / 5.2 / 128,000 / 5.5 · 相关方：llm-anthropic / Anthropic / Fable 5.2 / Mythos 5.2 / Opus 5.5 · 来源：Simon Willison's Weblog · 2026-11-09 23:58 UTC · 78.0 分
- 为什么值得看：适配速度虽快，但 max 档耗尽 128,000 token 后连图都返回不出，且这是 Fable 系列新出现、Opus 5.5 时代已有的同类故障，说明新模型的极限档不能默认信任。
- 对我意味着什么：对 skill 与 automation 的模型调用有直接影响：长任务必须设 token 上限与超时回退，不能把单一推理档当作可靠执行路径。
- 下一步：用同一提示词跑 max 档 10 次，若完整返回 ≥ 9 次且 token 消耗上限可控，判定可启用该推理档。
→ https://simonwillison.net/2026/Nov/9/llm-anthropic

**Anthropic 发布 Claude Fable 5.2 与 Mythos 5.2，称输出速度最高快 30 percent 且在技术科学基准上超过 Opus 5.5**
- 关键数字：5.2 / 30 / 5.5 · 相关方：Anthropic / Claude Fable 5.2 / Mythos 5.2 / Opus 5.5 · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-09 19:38 UTC · 75.16 分
- 为什么值得看：两款模型同架构但 Fable 5.2 多了网络安全与生物护栏，说明差异已落在策略层而非能力层；30 percent 是厂商口径，缺独立复测。
- 对我意味着什么：对 WorkBuddy 模型路由有影响：应按任务类型分流而非按速度单一指标选模型，护栏差异会改变敏感任务的可用集。
- 下一步：分别跑 Fable 5.2 与 Mythos 5.2 各 10 次编码任务，若前者护栏拦截率更高且 30 percent 提速可复现，判定按任务分流。
→ https://www.macrumors.com/2026/11/09/anthropic-launches-claude-fable-5-2

### Agent 与工程（4 条）

**claude-code v2.1.321 将 Claude Fable 5.2 设为默认模型，给出 1M 上下文定价，并修复 MCP OAuth 重定向泄露凭据等缺陷**
- 关键数字：2.1.321 / 1M / $8/$40 / $0.20 / 5.2 · 相关方：Claude Fable 5.2 / MCP OAuth / claude remote-control / Claude Code / SEP-2352 / Bash · 来源：claude-code Releases · 2026-11-09 19:22 UTC · 78.0 分
- 为什么值得看：这次修复集中在信任边界：OAuth 重定向把 refresh token 发往另一主机、只读 Bash 越出沙箱、cp 与 mv 写入绕过 deny 规则，比模型升级更值得先回归。
- 对我意味着什么：与 MCP、agent 部署强相关：三项缺陷要补进双端 setup 的回归断言集，否则 direct MCP-tools 调用链路存在凭据外发风险。
- 下一步：构造一次 MCP OAuth 302 重定向并抓包，若非注册主机收到 refresh token 次数为 0，判定 v2.1.321 可纳入 agent 部署基线。
→ https://github.com/anthropics/claude-code/releases/tag/v2.1.321

**Apple 为 iOS、iPadOS 与 macOS 27.2.1 发布安全更新，修复 iMessage 群聊历史越权访问与 AirPlay、Bluetooth 恶意配对缺陷**
- 关键数字：27.2.1 · 相关方：Apple / iOS / iPadOS / macOS / iMessage / eMudhra · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-09 23:07 UTC · 79.0 分
- 为什么值得看：更新同时为命令行工具补上 eMudhra 证书防护，影响的不是功能而是本地脚本的信任链，公开细节后未升级设备的利用风险上升。
- 对我意味着什么：本机 macOS 侧与 WinVM 命令行工具共享证书链，防护变更后需回归自动化脚本的签名校验，避免无人值守任务被静默拦截。
- 下一步：在 macOS 27.2.1 上跑一次签名脚本回归，若 eMudhra 相关校验失败次数为 0 且自动化任务全通过，判定升级不影响工具链。
→ https://www.macrumors.com/2026/11/09/ios-27-2-1-security-fixes

**GitHub 项目 virattt/dexter 以 TypeScript 实现面向深度金融研究的自主 agent，仓库标注 27,804 星**
- 关键数字：27,804 · 相关方：virattt/dexter / TypeScript · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-10 00:03 UTC · 78.06 分
- 为什么值得看：星数只说明关注度，摘要未给任务成功率或 handoff 契约；把它当架构样本前需先确认它返回的是结构化结果还是一段消息。
- 对我意味着什么：A2A 委派路径的参照实现：可作为复杂任务委派的对比样本，但不能凭星数推断其多 agent 交接质量。
- 下一步：给 dexter 派 3 个固定研究任务，若结构化结果返回率 ≥ 2/3，判定其 handoff 契约值得对照 A2A 实现。
→ https://github.com/virattt/dexter

**opensandbox-group 开源 OpenSandbox，定位为面向 AI agents 的 Python 沙箱运行时，仓库标注 16,914 星**
- 关键数字：16,914 · 相关方：OpenSandbox / Python / AI agents · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-10 00:03 UTC · 78.06 分
- 为什么值得看：把沙箱做成独立运行时而非宿主进程内的权限判断，与同日 claude-code 修复的 Bash 越沙箱问题形成呼应：隔离层正在外移。
- 对我意味着什么：直接对应 WinVM Bridge 的沙箱层：独立 Python 运行时可降低 direct MCP-tools 调用越权的风险面。
- 下一步：用 OpenSandbox 跑一次越权写入 smoke，若 0 violations 且隔离进程与宿主无共享句柄，判定可进入 WinVM 沙箱 PoC。
→ https://github.com/opensandbox-group/OpenSandbox

### 文档与变更（1 条）

**ollama v0.40.16 收录 65B 的 Ripple Preview 编码模型，并让 Qwen3.8 Flash Next 在 Apple silicon 上少用 27 GiB 内存**
- 关键数字：0.40.16 / 65B / 27 GiB / 13.5 / 3.8 · 相关方：ollama / Ripple Preview / Ricursive Intelligence / Qwen3.8 / Claude Code / CUDA · 来源：ollama Releases · 2026-11-09 23:45 UTC · 78.34 分
- 为什么值得看：除显存收益外还改了 /v1/responses 默认截断与 /v1/models 空返回值，属调用约定变化；只记版本号会漏掉必须回归的接口行为。
- 对我意味着什么：直接关系 WorkBuddy LLM provider V1 的本地候选：27 GiB 内存下降决定模型能否常驻，长输出处理需按新默认行为回归。
- 下一步：在 Apple silicon 上对比 v0.40.15 与 v0.40.16 峰值内存，若下降 ≥ 27 GiB 且长输出 0 截断，判定可纳入本地常驻候选。
→ https://github.com/ollama/ollama/releases/tag/v0.40.16

### 开发者工具与版本（1 条）

**一篇技术拆解以 Geometry Survivor Mod APK v1.0 为例，讨论稳定性、包签名完整性与运行时行为**
- 关键数字：1.0 · 相关方：Geometry Survivor / APK / Android · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-09 21:50 UTC · 78.14 分
- 为什么值得看：把包签名完整性当作判定第三方修改版可信度的首要字段，比「安全镜像」这类名号更可核验，可作为准入清单的反例教材。
- 对我意味着什么：对 agent 部署有间接参照：第三方 APK 的验签逻辑同样适用于 WinVM 侧安装包准入判定的字段设计。
- 下一步：抽取该 APK 两个镜像验签，若签名哈希一致率 100% 且运行时无额外联网，判定可作为 WinVM 安装包准入样本。
→ https://dev.to/tanvir1704/technical-teardown-geometry-survivor-mod-apk-v10-architecture-safe-mirrors-2ce2

### 安全与治理（1 条）

**作者复盘自售的 Solana 买入机器人，称一次审计发现 5 个 bug，其中之一把每笔买入金额翻倍**
- 关键数字：5 · 相关方：Solana / buy bot · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-09 21:48 UTC · 78.11 分
- 为什么值得看：金额翻倍属状态累积型缺陷，单次执行看起来正常、重跑才放大；这类复盘比功能发布更能暴露自动化管线的验收盲区。
- 对我意味着什么：对 automation 幂等设计是直接警示：prepared/dispatched 双状态去重同理，金额与数量类动作必须有单次上限断言。
- 下一步：在测试网重放买入脚本 20 次，若单笔金额与配置值偏差为 0 且重跑不产生重复订单，判定幂等断言通过。
→ https://dev.to/opsnode_dev/my-solana-buy-bot-doubled-every-buy-amount-heres-the-post-mortem-2dea

### 深度长文（1 条）

**Artificial Analysis 给出 Claude Fable 5.2 得分 65，标题称其为迄今最高，摘要区无正文内容**
- 关键数字：5.2 / 65 · 相关方：Claude Fable 5.2 / Artificial Analysis · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-09 20:04 UTC · 77.02 分
- 为什么值得看：65 是第三方评测口径且摘要为空，无法独立核对测试集；同日已有 max 档失败的实测，榜单分不足以支撑默认模型切换。
- 对我意味着什么：对 LLM provider V1 的选型口径有影响：默认模型切换须先跑固定提示词对照，不能只用榜单分排序。
- 下一步：用固定提示词对照 65 分榜单口径复跑，若长任务完整返回率 ≥ 90%，判定可把 Fable 5.2 提为默认候选。
- 证据状态：unverified（未独立验证）
→ https://artificialanalysis.ai/models/claude-fable-5-2

### 市场与投资（1 条）

**Bournemouth University 与 Museum of London 的研究者重新分析一条沟渠中出土的 8,000 块古蛙骨**
- 关键数字：8,000 · 相关方：Bournemouth University / Museum of London · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-10 00:10 UTC · 76.54 分
- 为什么值得看：十年前的材料靠新方法重新得出结论，说明保留可重算的原始样本比保存当时的结论更有价值，这是资料沉淀的通用教训。
- 对我意味着什么：暂无直接影响：考古样本研究不涉及 WorkBuddy、MCP、agent 部署任何环节；8,000 仅作为本期实质读数样本供白名单复算。
- 下一步：核对报告中 8,000 块骨骼的计数口径，若与发掘清单一致率 100%，判定该数字可作为白名单正样本。
→ https://phys.org/news/2026-11-case-roman-frog-graveyard.html

### 社区与观点（1 条）

**一份预测称 2026 年全球化石燃料碳排放将下降 0.4%，归因于太阳能与风电扩张及伊朗冲突**
- 关键数字：0.4% · 相关方：fossil fuels / solar / wind power / Iran / CO₂ · 来源：Folo 订阅池基线（人工筛选信源） · 2026-11-10 01:00 UTC · 75.54 分
- 为什么值得看：0.4% 的降幅小于常见统计波动，且属预测而非实测；把它当趋势拐点会误读，需与后续实测年值分开存放。
- 对我意味着什么：对数据基建有轻量用途：带单位的百分比读数是 feed 数字白名单的好样本，可验证提取器不把百分号或年份误当计数。
- 下一步：用 0.4% 跑一次数字白名单单测，若百分号被正确保留且 2026 未被误判为读数，判定提取器通过。
- 证据状态：unverified（未独立验证）
→ https://phys.org/news/2026-11-fossil-emissions-decrease-energy-growth.html

---

## 📊 今日数据概览

| 指标 | 数值 |
| --- | ---: |
| 信源可用 | 184 / 185 |
| 原始条目 | 2456 |
| 聚合簇 | 2359 |
| 入选簇 | 40 |
| 实际入报 | 12 |
| 七要素达标 | 12 / 12（100.0%） |
| 引用域名数 | 6 |

高频来源：github.com(4)、macrumors.com(2)、dev.to(2)、phys.org(2)、simonwillison.net(1)、artificialanalysis.ai(1)

---

## 🔭 待验证信号（可证伪）

| 信号 | 判定阈值 | 达到后判定 |
| --- | --- | --- |
| Fable 5.2 默认档长任务可用性 | 同一提示词连跑 10 次，max 档完整返回 ≥ 9 次且 token 消耗低于 128,000 | 判定可进入 WorkBuddy LLM provider V1 默认候选，否则只做备选模型 |
| MCP OAuth 重定向凭据泄露 | 构造 302 重定向后抓包，非注册主机收到 refresh token 次数为 0 | 判定 claude-code v2.1.321 满足 agent 部署基线，可升级 |
| ollama 本地内存收益 | Apple silicon 上 Qwen3.8 峰值内存下降 ≥ 27 GiB 且 smoke 0 violations | 判定本地常驻推理可行，纳入 WinVM 侧候选 |
| 只读 Bash 越沙箱 | 沙箱内执行只读命令 20 次，越权提示缺失次数为 0 | 判定权限边界修复有效，可放开 direct MCP-tools 调用 |
| 本期无实质读数簇占比 | no-number CSV 待补摘要条目数较前一日下降 ≥ 5 条 | 判定供数摘要质量改善，否则继续换一手来源而不放宽阈值 |

---

## 💡 编者观察

别急着追新模型，先把 claude-code v2.1.321 的三条修复翻成自己的回归用例：MCP OAuth 重定向把 refresh token 发给另一台主机、只读 Bash 越出沙箱、cp 与 mv 绕过 deny 规则，正是 WinVM Bridge 里 direct MCP-tools 与 A2A 委派的信任边界。双端 one-click setup 加一组断言：构造 302 重定向，凭据不出现在非注册主机；跑只读 Bash，0 次越沙箱；目录写入按目标文件而非源路径判权。三项全绿才纳入 agent 部署基线，否则沿用旧版标记 blocked。模型选型同样要收紧：Fable 5.2 拿到 65 分，但 llm-anthropic 0.31 实测 max 档耗尽 128,000 token 仍返回不出图；ollama v0.40.16 让 Qwen3.8 少用 27 GiB 内存。WorkBuddy 的 LLM provider V1 应按长任务是否完整返回验收默认模型，本地常驻候选按峰值内存筛选，27 GiB 的下降比 65B 规模更值得复测。数据基建侧，本期 40 个入选簇仅 12 条带实质读数，其余多为 Comments 空摘要，按 v1.1 口径全部不入报，no-number CSV 留作补摘要待办；宁可少一条，才保得住可复算性。

---

*本日报由规则层采集/去重/打分 + AI 研判生成；每条附原文链接，关键数字须能在原文中找到。*
*外部事实未独立验证，内容仅供参考，不构成投资建议；取不到可靠数据处标注「暂无可靠数据」。*
