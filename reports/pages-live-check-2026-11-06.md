# GitHub Pages 上线验收 · 2026-11-06

> 用户 2026-11-06 明确授权 4 项外部动作后执行。本报告只记录**线上实测**，
> 与 `reports/pages-subpath-check-2026-11-06.md`（本地模拟 14/14）互为补充。
> 核验方式：`curl -I` 等价的 `curl -sS -o /dev/null -w "%{http_code} %{content_type}"`
> + GitHub REST API 只读查询。

**站点**：https://athronix.github.io/daily-info/
**仓库**：https://github.com/athronix/daily-info （public，3 个提交）
**部署**：workflow run `42159781336`，`status=completed / conclusion=success`；
Pages `build_type=workflow`，仅 `workflow_dispatch` 手动触发，未配置 push 自动部署。

## 1. 线上 URL 全量复核：15/15 返回 200

| # | 路径 | HTTP | Content-Type |
| --- | --- | --- | --- |
| 1 | `/` | 200 | text/html; charset=utf-8 |
| 2 | `/.nojekyll` | 200 | application/octet-stream |
| 3 | `/index.html` | 200 | text/html; charset=utf-8 |
| 4 | `/all.atom` | 200 | **application/atom+xml** |
| 5 | `/feed.atom` | 200 | **application/atom+xml** |
| 6 | `/high-signal.atom` | 200 | application/atom+xml |
| 7 | `/tech.atom` | 200 | application/atom+xml |
| 8 | `/invest.atom` | 200 | application/atom+xml |
| 9 | `/docs.atom` | 200 | application/atom+xml |
| 10 | `/feed.json` | 200 | application/json; charset=utf-8 |
| 11 | `/data/index.json` | 200 | application/json; charset=utf-8 |
| 12 | `/data/latest.json` | 200 | application/json; charset=utf-8 |
| 13 | `/data/feeds.json` | 200 | application/json; charset=utf-8 |
| 14 | `/data/2026-11-05.json` | 200 | application/json; charset=utf-8 |
| 15 | `/data/2026-11-04.json` | 200 | application/json; charset=utf-8 |

**P17 风险解除**：6 个 `.atom` 在 GitHub Pages 上全部返回 `application/atom+xml`，
本地 `http.server` 的 `application/octet-stream` 确属本地服务映射差异，不是产物问题。

## 2. 内容与链接复核

| 检查项 | 结果 |
| --- | --- |
| `https://daily-info.local` 占位 URL 残留（5 个关键文件逐个扫） | **0 命中** |
| `tag:daily-info.local,...` 稳定 ID（feed.atom） | **59 个原样保留**，阅读器不会重复收录 |
| `index.html` 根绝对路径 `href="/" / src="/"` | **0 命中**，子路径部署无 404 |
| feed 级 `self` / `alternate` | 均指向 `https://athronix.github.io/daily-info/...` |
| JSON Feed `home_page_url` / `feed_url` | 指向真实站点域名 |

> 注意：`grep -c "daily-info.local"` 会命中 59 次，那是**稳定 ID**，不是占位 URL；
> 精确判定必须用 `https://daily-info.local`（带协议前缀），结果为 0。

## 3. 其余三项授权动作

| 动作 | 结果 | 证据 |
| --- | --- | --- |
| 主链路定时任务 | ✅ ACTIVE | id `e3ced83a-e776-4247-a9d0-fb5ad78de870`，`FREQ=DAILY;BYHOUR=6;BYMINUTE=45`，工作目录已绑定 |
| 邮件日报 | ✅ queued | 收件人 `athronix@agent.qq.com`（GetMe 动态取），3 个附件，日配额 48→47 |
| 资料库沉淀包 | ✅ 6/6 | `digest/brief/index.html/items.csv/no-number.csv/_manifest` 均返回 node_id |

执行凭证与幂等回写：`data/state/dispatch-receipt-2026-11-06.json`、
`data/state/push-log.jsonl`（追加 5 条 `dispatched`，共 10 行）。

## 4. 偏离项与风险（如实记录）

1. **邮件正文形态**：邮件 API 要求正文以字符串内联传入，无法直接引用本地
   `data/digest/2026-11-05/email.html`（18387 字）。本次正文改为摘要版 HTML
   （今日概览 + 线上订阅地址），并把**完整 18387 字 HTML 日报作为第 3 个附件**随信发送，
   另有 `digest.md` 与 `feed.atom`。内容零丢失，但「正文即全文」未按原 payload 实现；
   若要求正文全文，需由支持文件引用的发送通道或后续接口能力补齐。
2. **资料库落点**：上传工具只接受 `parent_id` 且禁止虚构目录 id，本次使用服务端默认目标，
   **未落到** `我的文档/每日信息/2026/11/`。需在资料库界面移动，或提供真实 folder id 后重投。
3. **定时任务不自动外发**：任务 prompt 明确写死「默认不发送邮件 / 不上传资料库 /
   不发布站点 / 不 git push / 不触发 Actions」，仅做本地准备；需要每日自动分发时另行授权。
4. **站点永久公开**：Free 账户只能从 public 仓库发 Pages，仓库内 `data/digest/`
   历史与信源清单已公开。发布前凭据扫描 0 命中（唯一 `USER` 命中是公开域名 owner，误报）。
5. **未执行**：企微推送（配置 `disabled`）、push 自动部署（workflow 仍为手动触发）。
6. 本报告验证的是**可达性、MIME、链接与结构**，不证明新闻事实为真，也不代表抓取覆盖率。
