# 每日信息 · Daily Info

> **以 `digest.json` 为唯一事实源**的每日信息流水线：确定性脚本负责采集、归一、去重、打分、索引与全部对外产物；
> 生成式模型只负责主题命名、解读与编者观察，且被 id / URL / 数字白名单锁死，不能新增任何事实。

| | |
| --- | --- |
| **在线站点** | **https://athronix.github.io/daily-info/** （默认打开最新日期） |
| 源码仓库 | https://github.com/athronix/daily-info |
| 技术栈 | Python 3 标准库（零第三方依赖）+ 单文件静态 HTML，无构建、无 CDN、无后端 |
| 状态 | 2026-11-06 上线；全归档核验 49/49、站点端到端 34/34、线上 15/15 |

---

## 1. 订阅

站点右上「**订阅 RSS**」会打开引导面板，列出每个频道的**完整订阅地址**并可一键复制。

| 频道 | 地址 | 内容 |
| --- | --- | --- |
| 全量日报 | `https://athronix.github.io/daily-info/feed.atom`（同 `all.atom`） | 全部入报条目 |
| 高信噪 | `.../high-signal.atom` | 高分条目 |
| 只看技术 | `.../tech.atom` | 技术与工程类目 |
| 只看市场 | `.../invest.atom` | 市场与投资类目 |
| 文档变更雷达 | `.../docs.atom` | 文档 / 变更类目 |
| JSON Feed | `.../feed.json` | 供程序消费 |

> ⚠️ **`.atom` 是给 RSS / Atom 阅读器用的源文件，不是网页**：浏览器直接打开会显示 XML 源码，这是正常行为。
> 请复制地址到 Folo / Inoreader / Feedly / NetNewsWire 等阅读器的「添加订阅」，或直接把站点首页交给阅读器
> （页面头部有 `rel="alternate"` 自动发现链接）。站点顶栏与页脚已改为引导面板，不再直接跳到源码页。

## 2. 三条架构原则

1. **确定性脚本做索引，LLM 只做研判**：采集、归一、去重、打分、索引、feed、幂等、核验全部在 `scripts/*.py`；
   AI 只写 `data/digest/<date>/ai-review.json`，不得增删候选条目、URL、数字、日期、实体。
2. **唯一事实源**：`digest.json` 是站点 / Atom / JSON Feed / 邮件 / 资料库 / 离线快照的唯一投影源，
   禁止各通道另写一份内容。`public/` 与 `data/library/` 都是可重建副本。
3. **白名单溯源闸门**：数字、实体、佐证 URL 逐项回原文校验，编造即丢弃并记 warning。
   v1.1 口径下「原文」= `title + summary_raw + metrics`；`published_at` 等采集元数据不算原文，
   原文全文无实质数字的条目直接拒绝入报（每日导出 `no-number-<date>.csv` 待办）。

## 3. 快速开始

```bash
cd D:/Users/towyq/Documents/Projects/personal-daily-info

# 1) 离线全链路 smoke（造样例数据，不需要联网 / API Key）
python scripts/run_daily.py --offline-demo

# 2) 本地预览（用 localhost / ::1，不要用 127.0.0.1，本机 TUN 会拦 IPv4 裸 TCP）
python -m http.server 8765 --directory public
# 打开 http://localhost:8765/

# 3) 独立核验（全归档，必须 0 violations）
python scripts/verify_digest.py --all-dates

# 4) 站点端到端验收 + GitHub Pages 部署副本预演（默认 dry-run，不联网不 push）
python scripts/check_release.py --date 2026-11-05
python scripts/prepare_pages.py --base-url https://athronix.github.io/daily-info
```

真实跑一天：`python scripts/run_daily.py` 会在 AI 环节暂停，由 Agent 按
`assets/prompts/daily-digest.md` 写回 `ai-review.json` 后继续；`assets/skills/daily-info/SKILL.md`
是完整命令表与工作流。凭据只放在 `~/.workbuddy/.env`，经 `common.load_dotenv()` 注入，仓库只留 `${VAR}` 占位。

## 4. 链路与目录

```
fetch_sources → fetch_folo(Folo 基线) → normalize → dedupe_cluster
      → [AI 边界] ai-review.json → make_digest → digest.json（唯一事实源）
      → build_feeds / build_site / export_library / render_email
      → verify_digest（闸门） → push_daily（默认 dry-run，只做本地准备）
```

| 路径 | 内容 |
| --- | --- |
| `config/` | 信源、分类体系、打分、订阅、内容规范（v1.1） |
| `scripts/` | 24 个标准库脚本，全链路可离线重放 |
| `data/digest/<date>/` | 每日唯一事实源 + AI 研判 + Markdown / 邮件产物（Git-as-DB，入库） |
| `public/` | 静态站 + 6 个 Atom + JSON Feed + 日期切片（可重建副本） |
| `assets/` | prompts、模板、skill、Pages workflow 模板 |
| `docs/00 ~ 16` | 方案、架构、内容规范、数据源研究、实施验收、Pages 部署复盘 |
| `reports/` | 核验、体检、候选探测、上线验收报告 |

## 5. 站点导航与订阅体验

- **日期维度**：顶部横向日期条，默认打开 `index.json.dates[0]`（最新）；首项带「最新」标记。
- **分类维度**：按当日 `digest.sections` 动态生成分类条（带条数），点击筛选并平滑定位到该板块。
- **搜索**：标题 / 来源 / 摘要 / 研判 / 分类即时过滤，与分类筛选叠加（AND）。
- **可分享**：两个维度写进 URL hash（`#date=2026-11-05&cat=ai-models`），刷新不丢状态，日期切换自动清空分类。
- **订阅**：顶栏按钮与页脚 5 个频道入口都打开引导面板，展示绝对地址 + 一键复制 + 明确的「查看源文件（会显示 XML）」次级链接。
- **主题**：默认深色（中性冷灰 + 石板蓝，不泛绿）；右上角可切浅色并记住选择，隐私模式下回落深色。

## 6. 上线与分发边界

- GitHub Pages：`assets/deploy/github-pages.yml` 是模板，`.github/workflows/pages.yml` 是授权后激活的工作副本，
  **仅 `workflow_dispatch` 手动触发**；`prepare_pages.py` 负责绝对地址替换、`.nojekyll`、稳定 `tag:` ID 保留与发布前校验。
- 主链路定时任务：每天 06:45（`FREQ=DAILY;BYHOUR=6;BYMINUTE=45`）跑全链路，
  **默认不自动对外发送**——不发邮件、不上传资料库、不发布站点、不 git push、不触发 Actions。
- 四支分发脚本（`export_library.py` / `render_email.py` / `push_daily.py` / `check_release.py`）
  只做本地准备；`push_daily.py --apply` 生成 `data/state/pending-dispatch-<date>.json` 待授权清单，
  外部动作一律由 Agent 在**用户单独明确授权**后执行，并用 `push-log.jsonl` 按「日期 + 通道」幂等。
- 核验闸门：报告日期匹配 + `violations=0` + 凭据扫描干净，任一失败整体拒发。

> Free 账户只能从 public 仓库发布 Pages，**站点发布后永久公开**；仓库内 `data/digest/` 历史会一并公开。
> 发布前凭据扫描与占位域名检查见 `docs/16` 与 `reports/pages-live-check-2026-11-06.md`。

## 7. 文档索引

| 编号 | 主题 | 编号 | 主题 |
| --- | --- | --- | --- |
| 00 | 总览与快速开始 | 09 | 定时任务与 Prompts |
| 01 | 参考仓库深度研究 | 10 | Skills / 脚本 / 模板清单 |
| 02 | 总体架构与信息流 | 11 | 实施路线与验收 |
| 03 | 信息来源与采集 | 12 | 内容规范与逆向研究 |
| 04 | 分类聚合与打分 | 13 | 高效数据源扩展研究 |
| 05 | 分析总结机制 | 14 | 数据源扩充与账户源指引 |
| 06 | 数据存储与产物契约 | 15 | 失败源链路恢复研究 |
| 07 | 展示网站 | 16 | 参考项目复盘与 GitHub Pages 部署 |
| 08 | 订阅与分发服务 | | |

## 8. 证据边界

核验脚本验证的是**结构、白名单、幂等与安全**，不证明新闻事实为真；
离线 smoke 的统计来自样例数据，不代表真实信源覆盖率。
信源规模（218 源 / 启用 186）与当日实测数据请以 `reports/` 下最新报告为准。
