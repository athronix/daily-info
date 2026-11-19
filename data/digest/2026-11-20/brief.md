**版本号、规则条数与融资金额都能逐字回查，型号数字与发布时间年份不算读数；真正决定能否接进门禁的是改动清单，不是漂亮断言**

今日入报里，claude-code 2.1.329 列出 hooks 改动，app-store-compliance 收录 117 条拒收模式，PostgreSQL 19 新增 WAIT FOR LSN；Anthropic 报 $2T 估值与首日 17% 涨幅，Isomorphic Labs 洽谈约 400 亿美元融资。张力在于：编号可逐字回查，金额却分三种口径。

2026-11-20 · 入报 15 条 · 信源 180/185

今日主线：
• 精确标识能进门禁，型号数字不能
• 市值、涨幅与社区热度是三种口径
• 洽谈中、may cost、促销价都要带条件
• 计数必须带分母与范围
• 工具清单的规模是宣称，不是实测

重点条目（含关键数字与下一步动作）：
• [28] 一篇 dev.to 清单文把 n8n 与 Activepieces 并列，宣称覆盖 28 个免费层工具，摘要只截取了 n8n 的开源介绍。
  → 逐个打开清单里 28 个工具的定价页；若可核验免费额度的少于 20 个，则判定该清单不可作为选型依据。
  https://dev.to/rock_boy_c59c5ced86a77a4d/zero-cost-2026-stack-n8n-workflow-automation-vs-activepieces-28-free-tier-tools-2026-11-19-5bbe
• [117, 95] 开源仓库 app-store-compliance 提供合规预提交 guard，收录 117 条拒收模式、跟踪 95 个法律期限，并带一个给 AI coding agents 的 skill。
  → 抽样 10 条拒收模式对照官方条款；若逐条命中的少于 8 条，则判定规则集过期，不接入预提交 guard。
  https://github.com/mjmirza/app-store-compliance
• [19, 0.1] Simon Willison 记录 PostgreSQL 19 因 AI 报告的漏洞潮比往年晚两个月发布，新增 WAIT FOR LSN 让 standby 查询读到主库刚写入的数据。
  → 同一读写用例在 standby 连跑 3 次；若读到旧值次数大于 0，则判定 read-your-writes 未生效，回退主库读。
  https://simonwillison.net/2026/Nov/19/postgresql-19
• [$300] TechCrunch 报道 Meta 新款 AI 可穿戴设备 Muse Charm 定价可能为 $300，Meta 只回应「很快会公布更多」未否认该数字。
  → 核对官方产品页是否给出价格；若 30 天内仍无官方数字，则判定 $300 仅为媒体预估，不写入规格基线。
  https://techcrunch.com/2026/11/19/metas-new-muse-charm-device-may-cost-300
• [2.1.329] claude-code 发布 v2.1.329：新增 hooks 声明位置的信任弹窗、非交互宿主里 managed settings 钩子加载失败告警，并在 /mcp 页面显示远程 HTTP MCP 的 JSON-RPC 报错。
  → 在 2 个非交互宿主各触发 1 次托管 hooks 加