# WorkBuddy 定时任务 Prompt · 周度复盘

## 可复制的 prompt

```
你在 D:/Users/towyq/Documents/Projects/personal-daily-info 工作区执行「每周信息复盘」。
全程使用简体中文。

1. 用确定性脚本打包最近 7 天的日报（不要手写聚合逻辑）：
   python scripts/pack_week.py
   若脚本不存在或失败，改为读取 data/digest/ 下最近 7 个日期目录里的 digest.json，
   并按 assets/prompts/weekly-review.md 的输入约定自行组装，同时在报告里注明「打包脚本降级」。

2. 读取 assets/prompts/weekly-review.md 作为完整工作指令，产出
   reports/weekly-<ISO 周编号>.md。
   硬约束：只依据 7 天日报与 run-log.jsonl 中已有内容；不联网检索；
   不新增原文之外的 URL/数字；缺刊写「暂无可靠数据」，不推测补齐；
   外部事实标注「未独立验证」；不产生投资建议。

3. 运行 python scripts/verify_digest.py --all-dates --no-idempotency 做一次全归档核验，
   把「通过数 / violations」写进周报第 3 节。若有 violations，逐条列出但不自动修复。

4. 通过 agent-mail 把周报发到本账户 Agent Mail 地址，主题「[每周信息复盘] <ISO 周编号>」；
   并把周报沉淀到资料库「我的文档/每日信息/周报/」。

5. 汇报：覆盖日期范围、日报数、缺刊日期、降级次数、核验结果、3 条最重要的主线演化。
   瞬时故障时保留已生成文件，从失败步骤续跑，不清空重来。

禁止：修改历史 digest、删除 data/ 目录、新增定时任务、绕过核验。
```

## 配套配置字段

| 字段 | 值 |
| --- | --- |
| 重复规则 | 每周一 08:30，`FREQ=WEEKLY;BYDAY=MO;BYHOUR=8;BYMINUTE=30` |
| 权限模式 | Agent |
| 技能 | `@skill:daily-info` |
| 连接器 | `agent-mail`、资料库 |

> `scripts/pack_week.py` 是可选辅助脚本（把 7 天 digest 压成单个只读输入文件）。
> 未实现时按 prompt 第 1 条的降级分支执行，不影响主链路。
