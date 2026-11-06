# WorkBuddy 定时任务 Prompt · 信源体检与月度归档

## A. 信源体检（每周日 21:00）

### 可复制的 prompt

```
你在 D:/Users/towyq/Documents/Projects/personal-daily-info 工作区执行「信源体检」。
全程使用简体中文。

1. 执行 python scripts/check_sources.py（不加 --update，保持只读），
   产出 reports/source-health-<今天>.{json,md}。
2. 读取 assets/prompts/source-health-triage.md 作为完整工作指令，
   结合最近 3 周的 source-health-*.json 判断「连续失败」，
   输出 reports/source-triage-<今天>.md。
   硬约束：只给建议，不改 config/sources.json，不删除信源，不输出破坏性命令；
   每条建议必须引用体检 JSON 的具体字段；覆盖率影响写「估算」；
   最后给出「待用户确认清单」。
3. 汇报：探测总数 / 正常 / 异常 / 需立即处置数 / 观察项数，以及最重要的 3 条建议。
   网络抖动导致的单次失败不要误判为失效源，须与最近 3 周记录比对后再下结论。

禁止：执行 --update、修改任何配置、新建定时任务。
```

| 字段 | 值 |
| --- | --- |
| 重复规则 | 每周日 21:00，`FREQ=WEEKLY;BYDAY=SU;BYHOUR=21;BYMINUTE=0` |
| 权限模式 | Agent（只读为主） |
| 技能 | `@skill:daily-info` |

## B. 月度归档（每月 1 日 09:00）

### 可复制的 prompt

```
你在 D:/Users/towyq/Documents/Projects/personal-daily-info 工作区执行「月度归档」。
全程使用简体中文。

1. 执行 python scripts/retention.py --dry-run，输出按分级列出待清理项
   （raw 快照 > 30 天、normalized > 180 天、public/data 日切片永久保留、digest 永久保留）。
   这只是报告，不要删任何文件。
2. 检查上月缺刊日期：列出 data/digest/ 下缺失的日期，与 reports/verify-*.md 对照，
   输出 reports/monthly-<YYYY-MM>.md，含「日报数 / 缺刊 / 降级次数 / 平均入报条数 /
   各分类分布 / 信源失败 Top5 / 上月改进项」。
3. 把月报沉淀到资料库「我的文档/每日信息/月报/」。
4. 汇报统计结果，并明确说明「本次未执行删除；如需清理请用户确认后单独执行 --apply」。
   瞬时故障保留中间产物，从失败步骤续跑。

禁止：自动删除 data/ 下任何文件、修改历史 digest、绕过核验。
```

| 字段 | 值 |
| --- | --- |
| 重复规则 | 每月 1 日 09:00，`FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=9;BYMINUTE=0` |
| 权限模式 | Agent（只读） |
| 技能 | `@skill:daily-info` |

> `scripts/retention.py` 提供 `--dry-run`（默认）与 `--apply`（需用户明确确认）两档，
> 只处理 `data/raw/` 与 `data/normalized/` 下的过期日期目录，绝不触碰 `digest/` 与 `public/`。
