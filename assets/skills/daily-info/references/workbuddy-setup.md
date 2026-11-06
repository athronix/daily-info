# WorkBuddy 侧落地配置

> 依据 WorkBuddy 官方文档（定时任务 / 资料库 / 发布为网站）与本会话实测整理。
> 涉及 UI 开关、绑定授权的步骤须由用户在客户端确认，助手不代为授权。

## 1. 定时任务（Automation）

在「定时任务」中新建或编辑任务时，配置字段与本项目对照：

| 字段 | 说明 |
| --- | --- |
| 名称 | 自由命名，建议「每日信息 · 主链路」 |
| 工作目录 | `D:/Users/towyq/Documents/Projects/personal-daily-info`（必须指向本项目，否则脚本路径失效） |
| 权限模式 | Agent（可读写文件 / 执行命令） |
| 模型 / 专家 / 技能 | 技能绑定 `@skill:daily-info`；模型用日常可用模型即可，AI 环节输入很小（prompt-input 约 1–3k tokens） |
| 连接器 | `agent-mail`、资料库（按需在连接器菜单启用） |
| 重复规则 | 见下表 |
| 有效期 | 不设，长期运行 |
| 消息推送到企业微信 | 按需开启（见 §5 约束） |

### 四个任务

| 任务 | 重复规则（RRULE） | 本地时间 | Prompt 文件 |
| --- | --- | --- | --- |
| 每日主链路 | `FREQ=DAILY;BYHOUR=6;BYMINUTE=45` | 每天 06:45 | `assets/prompts/automation-daily.md` |
| 每周复盘 | `FREQ=WEEKLY;BYDAY=MO;BYHOUR=8;BYMINUTE=30` | 周一 08:30 | `assets/prompts/automation-weekly.md` |
| 信源体检 | `FREQ=WEEKLY;BYDAY=SU;BYHOUR=21;BYMINUTE=0` | 周日 21:00 | `assets/prompts/automation-maintenance.md` §A |
| 月度归档 | `FREQ=MONTHLY;BYMONTHDAY=1;BYHOUR=9;BYMINUTE=0` | 每月 1 日 09:00 | `assets/prompts/automation-maintenance.md` §B |

- prompt 里**不要写调度时间 / 工作目录**（这些属于任务配置字段），否则未来改配置会与 prompt 冲突。
- 每日 06:45 的理由：参考仓库 daily-rss 约 06:00 CST 出报、daily-investor 08:00 CST 出报；
  本系统采集窗口 30 小时，06:45 能覆盖前一日全天。
- 定时任务有最大执行时长与并发限制；本流水线把重活放在标准库脚本里（通常 < 30 秒），
  AI 只处理精简后的 `prompt-input.json`，就是为了避开长时任务被裁断。
- 机器离线时定时任务不会补跑；用 `python scripts/run_daily.py --date <缺刊日>` 手动补刊，
  中间产物按日期分目录，互不覆盖。

## 2. Skill 部署

本项目已经把完整 skill 放在 `assets/skills/daily-info/`。
按本机约定**优先用 symlink**（改源即时生效，避免多份拷贝漂移）：

```bash
# Windows（开发者模式/管理员下可用；Git Bash 用 cmd //c mklink /D）
cmd //c mklink /D "C:\Users\towyq\.workbuddy\skills\daily-info" \
  "D:\Users\towyq\Documents\Projects\personal-daily-info\assets\skills\daily-info"
```

或 PowerShell：`New-Item -ItemType SymbolicLink -Path ~/.workbuddy/skills/daily-info -Target <项目路径>`
若需在 macOS / 其它 Agent 环境（kmaster、hermes-agent）复用，同样用 symlink 指向同一目录。

## 3. 展示站发布

`public/` 是纯静态目录（`index.html` + `public/data/*.json` + `*.atom`），**无构建、无后端、无 CDN**。

1. 本地预览：`python -m http.server 8765 --directory public`，
   浏览器打开 `http://localhost:8765/`。
   **Windows 本机使用 `localhost`（IPv6 ::1）而非 `127.0.0.1`**，规避 NekoBox TUN 模式拦截裸 TCP 回环。
2. 在线发布：在 WorkBuddy 里对 `public/` 使用「发布为应用 / 发布为网站」，得到在线链接；
   发布为网站会同时把页面存入资料库，便于跨设备访问。
3. 每次日报生成后 `build_site.py` 幂等写入 `public/data/`；
   内容未变则不重写文件，避免无谓的重新发布。
4. 订阅地址用**站点静态文件地址**（如 `<在线域名>/feed.atom`）填进任意 RSS 阅读器。
   **不要用 GitHub 仓库页自动生成的 `/releases.atom`** —— 那是 Release 订阅，与本项目文件同名但完全不同。

## 4. 邮件分发（agent-mail）

- 连接器：`agent-mail`（当前会话已可用）。
- 正文：`data/digest/<date>/digest.md` 渲染成 `assets/templates/email.html`；
  附件：`public/feed.atom`。
- 主题：`[每日信息] {date} · {headline_short}`。
- 收件人：本账户 Agent Mail 地址（用 `GetMe` 获取，不要硬编码）。
- 幂等：发送前检查 `data/state/push-log.jsonl` 是否已有该日期记录，发送后追加记录，
  避免任务重跑时重复投递。

## 5. 企业微信推送

- 开关位置：定时任务编辑窗口 →「消息推送到企业微信」。
- **仅支持 WebSocket 长连接方式绑定的机器人**，URL 回调方式不支持；
  绑定后须先在企业微信里给该机器人发过一条消息，否则收不到推送。
- 推送内容：`brief.md`（<= 1500 字）+ 站点链接，不要推全文。
- 未开启时不影响其它分发通道，`subscriptions.json` 中 `wecom.enabled=false` 是默认安全值。

## 6. 资料库沉淀

目录约定：`我的文档/每日信息/{YYYY}/{MM}/`，内容分工：

| 文件 | 类型 | 用途 |
| --- | --- | --- |
| `digest.md` | 文档 | 人读叙事、可被知识库检索 |
| `index.html` | 页面 | 呈现与在线分享 |
| `items.csv` | 表格 | 当日条目索引（id / 标题 / 分类 / 分数 / URL），便于后续做时间序列分析 |
| `weekly-*.md` / `monthly-*.md` | 文档 | 周报 / 月报归档 |

原则（来自 blogpost 的实证）：**索引与统计用确定性脚本，内容用生成式模型**；
资料库只放终态产物，不放 `raw/normalized/candidate` 中间层。

## 7. 三关验证（每次改动后必做）

| 关卡 | 命令 | 通过标准 |
| --- | --- | --- |
| 语法 | `python -m py_compile scripts/*.py` | 0 错误 |
| 全链路 smoke | `python scripts/run_daily.py --offline-demo` | 全流程退出码 0 |
| 独立核验 | `python scripts/verify_digest.py --all-dates` | `violations=0`，且报告写明通过项数 |

另需人工确认：`python -m http.server 8765 --directory public` 后浏览器能加载首屏、
日期切换与搜索可用、5 个 Atom 链接可下载。
