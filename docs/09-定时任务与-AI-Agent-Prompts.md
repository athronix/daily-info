# 09 · 定时任务与 AI Agent Prompts

> **v2 更新**：`daily-digest.md` 与 `automation-daily.md` 均已升级为七要素版；
> 汇报要求增加「七要素达标率」与「核验含 V8」。内容规范见 `config/content-spec.json`、`docs/12`。
> **v3 更新（2026-11-09）**：定时任务第四步改为「资料库 / 站点 / git push / Pages workflow
> 每日默认执行，邮件单独授权」；完整可复制 prompt 见 `assets/prompts/automation-daily.md`。

> 所有可复制的 prompt 都在 `assets/prompts/`，本文是索引与配置说明。
> **prompt 里不写调度时间 / 工作目录**（这些属于任务配置字段），避免未来改配置时两处冲突。

## 1. 四个定时任务总表

| # | 任务 | 重复规则（RRULE） | 本地时间 | Prompt 文件 | 主要动作 |
| --- | --- | --- | --- | --- | --- |
| 1 | 每日信息 · 主链路 | `FREQ=DAILY;BYHOUR=6;BYMINUTE=45` | 每天 06:45 | `automation-daily.md` | 采集→AI 研判→发布→核验→分发 |
| 2 | 每周复盘 | `FREQ=WEEKLY;BYDAY=MO;BYHOUR=8;BYMINUTE=30` | 周一 08:30 | `automation-weekly.md` | 7 日主线演化、信源健康、下周动作 |
| 3 | 信源体检 | `FREQ=WEEKLY;BYDAY=SU;BYHOUR=21;BYMINUTE=0` | 周日 21:00 | `automation-maintenance.md` §A | 只读取体检 + 处置建议 |
| 4 | 月度归档 | `FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=9;BYMINUTE=0` | 每月 1 日 09:00 | `automation-maintenance.md` §B | 留存报告（不删）、月报 |

> 用「每天 06:45」而非参考仓库的 06:00/08:00：采集窗口 30 小时可覆盖前一日全天；
> daily-rss 约 06:00 CST 出报、daily-investor 08:00 CST 出报，06:45 处于两者之间，信息已较完整。

## 2. 任务配置字段（在 WorkBuddy 定时任务编辑窗口设置）

| 字段 | 值 |
| --- | --- |
| 工作目录 | `D:/Users/towyq/Documents/Projects/personal-daily-info` |
| 权限模式 | Agent（可读写文件 / 执行命令） |
| 技能 | `@skill:daily-info` |
| 连接器 | `agent-mail`、资料库（按需在连接器菜单启用） |
| 模型 | 日常可用模型即可；AI 输入仅 1–3k tokens/天 |
| 消息推送到企业微信 | 按需开启（仅 WebSocket 长连接绑定；绑定后须先给机器人发一条消息） |
| 有效期 | 不设（长期运行） |
| 重复规则 | 见上表 |

**关于执行时长与并发**：定时任务有最大执行时长与并发限制。
本方案把重活放在标准库脚本（通常 < 30 秒），AI 只处理精简后的 `prompt-input.json`，
就是为了避开长时任务被裁断。运行记录可在任务详情里查看。

## 3. Prompt 索引

| 文件 | 类型 | 什么时候用 | 输入 → 输出 |
| --- | --- | --- | --- |
| `daily-digest.md` | **AI 工作指令** | 每日主链路第 2 步 | `prompt-input.json` → `ai-review.json` |
| `automation-daily.md` | 定时任务 prompt | 建「每日信息 · 主链路」 | 编排 7 步 + 分发 + 汇报 |
| `automation-weekly.md` | 定时任务 prompt | 建「每周复盘」 | `pack_week.py` → `reports/weekly-*.md` |
| `automation-maintenance.md` | 定时任务 prompt ×2 | 信源体检 / 月度归档 | 体检 JSON → 建议报告；留存 → 月报 |
| `evidence-audit.md` | AI 工作指令 | 每周 / 存疑期日报道审计 | `digest.md` 分块 → `reports/evidence-audit-*.md` |
| `theme-adjudicate.md` | AI 工作指令（默认关闭） | 开启边界簇判定 | `boundary pairs` → `boundary-review.json` |
| `weekly-review.md` | AI 工作指令 | 周复盘 | `week-<ISO>.json` → 周报 |
| `source-health-triage.md` | AI 工作指令 | 信源体检 | `source-health-*.json` → 处置建议 |

每个 AI 工作指令都包含：安全边界（UNTRUSTED DATA）、输入契约、
输出 schema / 格式、硬约束、缺失处理、成本控制、自检清单。

## 4. 每日主链路 prompt 的五步（摘要）

```
1. 确定性采集与规则处理
   python scripts/fetch_sources.py
   python scripts/fetch_folo.py
   python scripts/normalize.py
   python scripts/dedupe_cluster.py
   单源失败是预期行为，绝不因某个源 404/429 中断整轮；Folo 未授权软降级。
   dedupe 失败 → 停止 AI 步骤，但仍走 make_digest.py --fallback。

2. AI 研判（唯一需要动脑的环节）
   读 assets/prompts/daily-digest.md 作为完整工作指令，
   读 prompt-input.json 作为唯一事实素材，
   按 assets/templates/ai-review.schema.json 写回 ai-review.json。
   自检：合法 JSON / id 全部可溯源 / 无新增 URL / 无重复 id / 字数达标。

3. 发布与核验
  make_digest.py → build_feeds.py → build_site.py → verify_digest.py
  核验必须 0 violations（含 V8 白名单口径三项）；失败最多修复重跑 3 次，仍失败明确列出未通过项。

4. 分发准备与验收（仅核验通过后）
  check_release.py → push_daily.py --apply
  脚本只做本地 payload：资料库沉淀包（items.csv / no-number.csv / manifest）、
  邮件正文 email.html、push-log.jsonl 幂等记录、pending-dispatch-<date>.json 待授权清单。
  **外部动作由 Agent 按 pending-dispatch 清单执行。2026-11-09 起定时任务默认自动执行
  library / site / atom / jsonfeed（资料库上传、git push、触发 Pages workflow、线上验收，
  顺序不能反）；email 仍需当次单独明确授权，wecom 保持 disabled。核验闸门失败则当日整体停止。
  清单里的 pending_authorization 只是「脚本不自行外发」的边界标记，不是运行时授权闸门。**

5. 汇报
  信源成功/启用 → 原始 → 归一 → 簇 → 入报 → 无实质数字被拒数 → 七要素达标率 →
  实质数字比 → 核验通过数/violations → 降级标记 → 站点端到端结果 →
  各订阅 profile 条目数 → 分发准备结果 / 待授权动作数 → 恢复点。
```

完整可复制文本见 `assets/prompts/automation-daily.md`。

## 5. 瞬时故障（429 / 网络抖动）恢复策略

用户明确要求「重启过程中保持状态不丢失，恢复后继续执行未完成任务」，落地为：

| 原则 | 实现 |
| --- | --- |
| 中间产物按日期落盘 | `data/raw/<date>/`、`normalized/`、`candidate/`、`digest/` 互不覆盖 |
| 失败不清空 | prompt 明令「保留已落盘中间产物，不要清空重来」 |
| 从失败步骤续跑 | `--skip-fetch` 复用 raw；AI 文件缺失自动 `--fallback`；`run_daily.py` 可分步调用 |
| 状态可查 | `data/state/run-log.jsonl` 记录每步事件与统计；`push-log.jsonl` 记录分发 |
| 汇报恢复点 | 汇报格式里必须写「恢复点：无 / 从第 N 步续跑」 |
| AI 不可用不阻断 | 规则降级出报，`ai_status=degraded`，V7 核验把关 |
| 补刊 | 机器离线导致缺刊时，用 `--date <缺刊日>` 手动补，不影响其它日期 |

**实证**：本次会话中四个源码分析子 agent 的收尾阶段曾因 429 失败，
但主报告与补充已通过消息完整交付，判定「不重跑、继续主体任务」——
这条经验已写入 `assets/skills/daily-info/references/pitfalls.md` P01。

## 6. 时区与 cron 约定

| 项 | 口径 |
| --- | --- |
| 项目时区 | `Asia/Shanghai`（`config/*.json` 的 `timezone`） |
| 业务日期 | 北京时间自然日（`today_str()`，UTC+8） |
| 对外时间戳 | UTC ISO8601 `Z` |
| 定时任务时间 | 本地时间，写在任务配置字段，不写进 prompt |
| GitHub Actions（若做 CI 备份） | cron 用 **UTC**，如北京 08:30 = `30 0 * * *` |

对照参考仓库的坑：daily-rss README 06:30 / footer 06:00 / 个别 07:00 或 23:50 抓取；
daily-investor 出现 UTC 00:0x / 08:00 北京 / 14:02 / 04:00 多套口径；
docs-feed 的 `30 0 * * *` 是 UTC，注释与 README 都明确换算成北京 08:30。
本方案单点声明、三处字段分离，避免混用。

## 7. 定时可靠性边界

- 机器离线 / WorkBuddy 未运行时**不会自动补跑**；靠 `--date` 手动补刊 + 周报里的缺刊统计发现。
- 定时任务有最大执行时长；若未来信源大幅增加导致超时，应把采集拆成独立任务或降低并发。
- 若额外用 GitHub Actions 做备份调度，注意「连续 60 天无活动可能停用 schedule」，
  需保证定期提交或定期手动触发。
- 企业微信推送依赖长连接绑定与「先给机器人发过一条消息」，否则静默不达。

## 8. 定时任务创建方式（Automation）

可用 WorkBuddy 的自动化管理能力创建；创建时把这些字段填全：

```
name:        每日信息 · 主链路
scheduleType: recurring
rrule:       FREQ=DAILY;BYHOUR=6;BYMINUTE=45
status:      ACTIVE
cwds:        D:/Users/towyq/Documents/Projects/personal-daily-info
prompt:      <assets/prompts/automation-daily.md 里「可复制的 prompt」全文>
```

另三个任务同理（rrule 见 §1）。若需要企微推送或连接器，先在连接器菜单完成授权，
再把 `connectorIds` 填进任务；**不要依赖当前会话的选择**，未来运行是独立上下文。

> 创建前先检查是否已有同类任务，优先更新而不是重复创建；
> 同一逻辑任务只保留一个，多日期/多时间点用一个 RRULE 表达。

## 9. 汇报模板（要求三关验证结果）

```
信源 26/29 → 原始 430 → 归一 312 → 簇 118 → 入选 40 → 入报 38
七要素达标 38/38 = 100%；待验证信号 5 条；引用独立域名 31
核验 31/31 通过，violations=0（含 V8）；ai_status=ok；降级=否
订阅 profile：all=38 / high-signal=9 / tech=21 / invest=5 / docs=4
分发：企业微信 ✓ · 邮件 ✓ · 资料库 ✓ · 站点 ✓
三关：py_compile 0 错误 · offline smoke 退出码 0 · verify 0 violations
恢复点：无（如发生 429 则注明从第 N 步续跑）
```
