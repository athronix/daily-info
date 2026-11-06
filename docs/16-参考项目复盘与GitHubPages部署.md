# 16 · 参考项目复盘与 GitHub Pages 部署

> 2026-11-06。回答两个问题：**四个参考仓库的东西我们到底抄了哪些、还差哪些**，
> 以及**展示站与订阅源如何安全地上到 `github.io`**。
> 初稿记录本地设计与验收；**2026-11-06 补记**：用户已授权并执行 4 项外部动作，
> 站点已上线，线上实测见 `reports/pages-live-check-2026-11-06.md` 与本文 §6。

## 0. 证据边界（先声明）

- 参考仓库结论来自 `docs/01` 的源码级只读研究与 `docs/12`、`reports/corpus-analysis.md`
  的语料量化研究，四个仓库均为 `--depth 1` 浅克隆，**不能据此推断提交频率与逐日历史**。
- GitHub Pages 的平台限制来自 2026-11-06 核对 `docs.github.com` 官方口径，
  属于外部平台规则，未来可能变化；上线前以仓库 Settings 实际显示为准。
- 下文的 14/14、35/35、18/18 全部是**本地验证**结果，验证的是结构、路径、幂等与安全，
  **不代表线上可达，也不能证明新闻事实为真**。

## 1. 四仓库复盘：借鉴 / 规避 / 待办

| 参考项目 | 它的真实定位 | 我们已经落地 | 刻意规避的缺陷 | 仍然存在的差距 |
| --- | --- | --- | --- | --- |
| `daily-rss` | 技术日报**产物库**（256 篇 .md，仓库内零生成代码） | 固定板块契约、日期目录、健康度写进产物（`digest.stats` / `no-number-<date>.csv`） | 生成逻辑黑盒、模板 9 个月漂移 4 次、无自产订阅、源长期带病无告警 | 尚未积累连续多日产物，无法评估缺刊率与源稳定性 |
| `daily-investor` | 投资 / 创意日报产物库（ideas 223 + observations 137） | 「不编造」上升为程序闸门：数字 / 实体 / 佐证 URL 逐项回原文校验（v1.1 白名单） | 黑盒、目录 4 种路径并存、纯自由文本机器不可读 | 事实核查仍只到「原文有这个数」，不做外部交叉验证 |
| `blogpost` | 深度文章内容库（333 篇），明文原则「确定性脚本做索引」 | 全项目架构原则：采集/归一/去重/打分/索引/feed 全在 `scripts/*.py`，AI 只写 `ai-review.json` | 分类靠文件名硬编码、索引漂移、样本里出现明文 API Key | `evidence-audit` 仍是 `UNVERIFIED`，缺独立来源快照采集器 |
| `docs-feed` | 自有仓库 Markdown → **全文 Atom** 聚合器（唯一含生成代码与 13 单测） | 全量确定性重建、字节幂等写入、稳定 `tag:` ID、`.tmp → replace` | 100 条硬截断、安全闸门缺失、名不副实的 `releases.atom`、依赖完整 git 历史 | 我们的 feed 由 `digest.json` 直接投影，不经 Git 历史取时间，语义与它不同 |

**三条被写进架构、不可动摇的结论**（详见 `MEMORY.md` 与 `docs/00` §2）：

1. 只有成品没有工厂 = 不可复现 → 规则层脚本与配置全部入库，可离线重放；
2. `digest.json` 是唯一事实源 → 站点 / Atom / JSON Feed / 邮件 / 资料库都是它的投影，
   禁止任何通道另写一份内容；
3. 内容质量是程序闸门而不是提示词愿望 → 七要素 + 白名单 + `verify_digest.py` 独立核验，
   编造即丢弃并记 warning。

**对照后的自我判断**：四个仓库里，我们最接近 `docs-feed` 的工程形态，但把「内容层」
换成了结构化 JSON 而非 Markdown，并补上了它缺失的安全闸门与多 profile 订阅。
`daily-rss` 的**每日节奏与固定板块**是产品形态上的参考，不是实现上的参考。

## 2. 为什么选 GitHub Pages，而不是「发布为网站」

| 维度 | `workbuddy_sites_deploy`（原 P1 待授权清单） | GitHub Pages（本轮新增方案） |
| --- | --- | --- |
| 交付形态 | 平台分配的在线链接，随时可下线 | `https://<owner>.github.io/<repo>/`，与仓库同生命周期 |
| 订阅地址稳定性 | 链接可能随重新发布变化 | 域名固定，适合写进 RSS 阅读器与 Atom `self` |
| 与 Git-as-DB 的关系 | 独立产物，与仓库无耦合 | 产物从仓库 workflow 生成，`data/digest` 与站点同源 |
| 更新方式 | 每次手工发布 | 手动触发 workflow（模板默认 `workflow_dispatch`），可授权后加 `push` 自动 |
| 代价 | 无 | 需创建 **public** 仓库；站点**永久公开**，撤回只能删站点/改私有 |
| 凭据面 | 平台托管 | 凭据全部留在本机，CI 只跑 `prepare_pages.py`，不碰采集、Folo、LLM |

结论：**订阅源优先走 GitHub Pages**（地址稳定），「发布为网站」保留为快速预览的可选通道。
两者都用同一份 `public/` 投影，不存在两份事实源。

## 3. 子路径部署的五个技术要点

项目站点挂在 `/<repo>/` 子路径下，直接推 `public/` 会踩以下坑：

1. **前端相对路径**：`index.html` 与 `data/index.json` 全部用相对链接，天然适配子路径，
   `validate()` 用正则拒绝任何根绝对路径 `href="/..."`，避免 404。
2. **绝对地址替换**：`build_feeds.py --base-url` 把 Atom 的 `self` / `alternate`、
   JSON Feed 的 `home_page_url` / `feed_url`、`data/feeds.json` 的 profile URL 写成绝对地址；
   本地是占位域名 `https://daily-info.local`，上线前必须换成真实站点地址，否则全是死链。
3. **稳定 ID 不能动**：`tag:daily-info.local,<date>:<id>` 与部署域名无关，
   一旦改写，所有订阅阅读器会把历史条目当新条目重收。`validate()` 逐个 Atom 校验 ID 前缀。
4. **`.nojekyll`**：阻止 Jekyll 构建介入静态目录（尤其 `data/` 下.json 与 `_` 前缀文件）。
5. **feed 级 link 与 entry 级 alternate 要分开**：entry 的 `alternate` 指向外部原文，
   绝不能替换成本站域名；校验只取 `root.findall(ATOM_NS + "link")`（feed 级），
   早期用 `root.iter()` 会把 entry 链接误算进来，产出 6 项误报（见 `pitfalls.md` P31）。

`prepare_pages.py` 的职责严格限定为**本地准备**：

```bash
# 默认 dry-run：只在内存构造 + 校验，不落盘、不联网、不 push
python scripts/prepare_pages.py --base-url https://<owner>.github.io/<repo>

# --apply 才写 pages-dist/（.gitignore 已排除，可随时重建）
python scripts/prepare_pages.py --base-url https://<owner>.github.io/<repo> --apply
```

校验项：必备文件、旧域名零残留、根绝对路径、index 指向的日期切片与 feed 文件存在、
Atom 可解析且稳定 ID 未变、feed 级 self/alternate 指向新域名、JSON Feed 与 profile URL、
全部 JSON 可解析、凭据特征扫描。任一失败整体拒绝生成；写入按字节幂等，
二次执行 `changed=0`。`manifest.json` 记录每个文件的 sha256 便于独立复核。

## 4. 发布工作流与授权边界

`assets/deploy/github-pages.yml` 是**模板，默认不激活**，刻意放在 `assets/deploy/`
而不是 `.github/workflows/`——后者会在 push 时自动部署，等于绕过用户授权。

- 触发方式只保留 `workflow_dispatch`（手动）；每次 push 自动发布需要用户授权后自行加。
- 步骤：checkout → setup-python → 计算公开地址 → `prepare_pages.py --apply`
  → configure-pages → upload-pages-artifact → deploy-pages。
- `permissions`: `contents: read` / `pages: write` / `id-token: write`，environment `github-pages`。
- CI **不跑采集、不调 Folo、不调 LLM**：`GITHUB_TOKEN` / `FOLO_TOKEN` 等凭据只留在
  `~/.workbuddy/.env`，经 `common.load_dotenv()` 注入本机脚本；仓库只留 `${VAR}` 占位。

平台口径（2026-11-06 核对）：

- GitHub Free 账户**只能从 public 仓库发布 Pages**；
- **发布后的站点永远公开**，即使之后把源仓库改为私有，站点仍可访问；
- `CNAME` 文件不会自动配置自定义域名，需在 Settings → Pages 里设置；
- `.atom` 的 MIME 由 Pages 自身映射决定，本地 `http.server` 返回
  `application/octet-stream` 属正常，**上线后必须再 `curl -I` 复核一次**。

## 5. 本地验收结果（未联网、未发布）

| 项目 | 结果 | 证据 |
| --- | --- | --- |
| `prepare_pages.py` dry-run | 0 问题，14 文件 / 782,368 B | 本报告 §3；`manifest.json` 记录 sha256 |
| `--apply` + 二次执行 | `changed=0`，字节幂等 | 本地日志 |
| 子路径端到端（IPv6 `::1` HTTP） | **14/14 PASS** | `reports/pages-subpath-check-2026-11-06.md` |
| 日报核验 | **35/35，violations=0** | `reports/verify-2026-11-05.md` |
| 站点端到端 | **18/18 PASS** | `reports/release-check-2026-11-05.md` |
| 全脚本 `py_compile` | 0 错误 | 三关验证第 1 关 |
| 凭据明文扫描 | 0 命中 | 发布前扫描；`.env` 未入库 |

> 本地联调一律用 IPv6 `::1` / `localhost` 并显式 `ProxyHandler({})`，
> 规避本机 NekoBox TUN 对 IPv4 `127.0.0.1` 裸 TCP 的拦截。

**上线后复核清单**（发布动作执行后逐条验证，不在本文预先宣称通过）：

1. `curl -I https://<owner>.github.io/<repo>/` → 200；
2. `curl -I .../feed.atom` → `Content-Type` 是否为 `application/atom+xml`（P17）；
3. `curl -s .../feed.atom | head` → `self` / `alternate` 为真实域名，无 `daily-info.local`；
4. `data/index.json`、`data/2026-11-05.json` 子路径 200，前端日期切换与搜索正常；
5. `tag:daily-info.local,...` ID 与本地一致（阅读器不重复收录）；
6. 站点公开可见性符合预期——**此步不可逆，删除前想清楚**。

## 6. 待授权动作（助手不擅自执行）

| # | 动作 | 性质 | 状态（2026-11-06 更新） |
| --- | --- | --- | --- |
| 1 | 创建 public 仓库 `daily-info`、设置 remote、push 全部提交 | 外部可见 / 不可逆公开 | ✅ 已执行：3 提交，`athronix/daily-info` public |
| 2 | 激活 `.github/workflows/pages.yml` 并触发部署 | 站点上线 | ✅ 已执行：run `42159781336` success，线上 15/15 200 |
| 3 | 创建「每日信息 · 主链路」定时任务（每天 06:45） | 自动调度 | ✅ 已执行：ACTIVE，默认不自动外发 |
| 4 | 实发邮件日报 / 上传资料库 / 企微推送 | 对外发送 | ✅ 邮件与资料库已执行；企微仍 `disabled` |

四项由用户逐项勾选授权后执行。执行凭证：
`data/state/dispatch-receipt-2026-11-06.json`（含 node_id / file_id / run id / automation id）
与 `data/state/push-log.jsonl`（追加 5 条 `dispatched`，共 10 行）。
线上复核、偏离项与风险见 `reports/pages-live-check-2026-11-06.md`。

**两项如实记录的偏离**：
1. 邮件正文改为摘要版 HTML，完整 18387 字 `email.html` 作为第 3 个附件随信发送
   （邮件 API 要求正文内联，无法引用本地文件）；
2. 资料库上传使用服务端默认目标，未落到 `我的文档/每日信息/2026/11/`
   （工具禁止虚构 folder id，需在界面移动或提供真实 id）。

## 7. 误报风险声明

- 14/14 是本地 `http.server` 挂载 `/pages-dist/` 前缀的**模拟**子路径，
  与 GitHub Pages 的 CDN、缓存、MIME 映射、重定向行为不等价；
- `violations=0` 只说明结构、白名单、幂等与安全闸门通过，**不证明新闻事实为真**；
- 公开仓库会暴露 `data/digest/` 的全部历史内容与信源清单，
  凭据虽已扫描排除，仍建议上线前再人工过一遍 `git ls-files`；
- `docs/01` 对跨仓库协作关系的推断标注为 C 级证据，复盘时不可写成事实。
