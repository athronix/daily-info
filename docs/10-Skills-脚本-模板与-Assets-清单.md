# 10 · Skills / 脚本 / 模板 / Assets 清单

## 1. 完整文件树（本次交付）

```
personal-daily-info/
├── docs/                                   # 15 份编号方案文档（00 ~ 14）
│   ├── 00-总览与快速开始.md
│   ├── 01-参考仓库深度研究.md
│   ├── 02-总体架构与信息流.md
│   ├── 03-信息来源与采集.md
│   ├── 04-分类聚合与打分.md
│   ├── 05-分析总结机制.md
│   ├── 06-数据存储与产物契约.md
│   ├── 07-展示网站.md
│   ├── 08-订阅与分发服务.md
│   ├── 09-定时任务与-AI-Agent-Prompts.md
│   ├── 10-Skills-脚本-模板与-Assets-清单.md
│   ├── 11-实施路线与验收.md
│   └── 12-内容规范与逆向研究.md         # ★ 语料实测 / 逆向推理 / 七要素采纳清单
├── config/
│   ├── sources.json                        # 45+ 信源注册表（含实测 health / tier / weight）
│   ├── taxonomy.json                       # 10 分类 / 3 组 / 标签 / 聚类阈值 / 质量规则
│   ├── scoring.json                        # 6 维权重 / 阈值 / 配额 / 降级触发 / watchlist
│   ├── subscriptions.json                  # 6 通道 / 5 profile / 幂等 / 留存策略
│   └── content-spec.json                   # ★ 七要素内容规范 / 质量规则 / V8 阈值 / 语料基准
├── scripts/                                # 24 个标准库脚本，零第三方依赖（folo 走 npx CLI 子进程）
│   ├── common.py                           # 共享工具：路径/配置/时间/URL/RSS-Atom 解析/JSON 与字节幂等写/日志/凭据
│   ├── analyze_corpus.py                   # ★ 三仓库语料量化分析 → reports/corpus-analysis.*
│   ├── probe_candidates.py                 # ★ 候选信源三重体检 → reports/candidate-probe-*
│   ├── probe_recover.py                    # ★ 失败源三路链路恢复（gnews site:/RSSHub 镜像/HTML）→ reports/recover-probe-*
│   ├── register_sources.py                 # ★ 幂等登记体检通过的候选 → config/sources.json
│   ├── import_opml.py                      # ★ OPML 清单导入器（实测+按主机去重分流，幂等/--dry-run）
│   ├── gen_source_archive.py               # ★ 数据源全量归档表（只读合并）→ docs/references/data-source.md
│   ├── fetch_folo.py                       # ★ Folo 订阅池基线采集（npx folocli 只读 timeline，软降级）
│   ├── export_library.py                   # ★ P1 资料库沉淀包：items.csv / no-number.csv / 离线快照 / manifest
│   ├── render_email.py                     # ★ P1 邮件正文自动渲染（本地 payload，凭据扫描，不发送）
│   ├── push_daily.py                       # ★ P1 分发编排：核验闸门 + 幂等 + 待授权清单（默认 dry-run）
│   ├── check_release.py                    # ★ P1 站点端到端 18 项（IPv6 ::1 回环实发 HTTP）
│   ├── prepare_pages.py                    # ★ GitHub Pages 部署副本（dry-run / --apply，不联网不 push）
│   ├── check_sources.py                    # 信源体检（只读；kind=cli 读产物探活）→ reports/source-health-*
│   ├── fetch_sources.py                    # 并发采集 → data/raw/<date>/
│   ├── normalize.py                        # 归一 + 规则分类 + SQLite 跨天去重
│   ├── dedupe_cluster.py                   # 并查集聚类 + 6 维打分 + prompt-input
│   ├── make_digest.py                      # AI 白名单合成（v1.1 口径）→ digest.json / digest.md / brief.md
│   ├── build_feeds.py                      # 5 个 Atom profile + JSON Feed + 发布闸门
│   ├── build_site.py                       # 站点 JSON 切片（index/latest/<date>/feeds）
│   ├── verify_digest.py                    # V1~V8 独立核验（含白名单口径三项）→ reports/verify-*
│   ├── pack_week.py                        # 7 日 digest 打包成周复盘输入
│   ├── retention.py                        # 留存报告（默认 dry-run，--apply 需确认）
│   └── run_daily.py                        # 一键编排 9 步（末步 push_daily --dry-run）；--offline-demo smoke
├── assets/
│   ├── prompts/                            # 8 份 prompt
│   │   ├── daily-digest.md                 # ★ 主日报 AI 工作指令
│   │   ├── evidence-audit.md               # ★ 反幻觉证据审计
│   │   ├── theme-adjudicate.md             # 边界簇判定（默认关闭）
│   │   ├── weekly-review.md                # 周复盘
│   │   ├── source-health-triage.md         # 信源体检处置建议
│   │   ├── automation-daily.md             # ★ 可复制的每日定时任务 prompt
│   │   ├── automation-weekly.md            # 可复制的周任务 prompt
│   │   └── automation-maintenance.md       # 信源体检 + 月度归档两个 prompt
│   ├── templates/
│   │   ├── ai-review.schema.json           # ★ AI 结构化输出契约（JSON Schema）
│   │   ├── digest.md.tpl                   # 人读日报模板
│   │   ├── brief.md.tpl                    # 企微短简报模板
│   │   └── email.html                      # 邮件正文模板（内联样式）
│   └── skills/daily-info/                  # 可直接 symlink 部署的 skill 包
│       ├── SKILL.md                        # frontmatter + 工作流 + 安全边界 + 降级 + 汇报格式
│       ├── references/
│       │   ├── architecture.md             # 分层 / 目录 / schema / 打分 / 核验项
│       │   ├── workbuddy-setup.md          # 定时任务 / 站点发布 / 邮件 / 企微 / 资料库 / 三关验证
│       │   ├── research-findings.md        # 四仓库研究结论 + 证据强度分级
│       │   └── pitfalls.md                 # ★ 坑与规避（持续维护）
│       ├── scripts/pipeline.py             # skill 入口：status / run / check / health / week
│       └── templates/ai-review.schema.json # 与主模板哈希一致的副本
├── public/
│   ├── index.html                          # ★ 简约清新单页站点（零依赖）
│   ├── data/                               # 构建产物：index/latest/<date>/feeds.json
│   ├── *.atom                              # 构建产物：5 profile + 默认 feed.atom
│   └── feed.json                           # 构建产物：JSON Feed 1.1
├── data/                                   # 运行时数据（按日期分层）
│   ├── raw/ normalized/ candidate/ digest/ state/
└── reports/                                # 核验 / 体检 / 周报 / 留存报告
```

## 2. 脚本职责与调用顺序

| 顺序 | 脚本 | 关键参数 | 退出码含义 |
| --- | --- | --- | --- |
| R | `analyze_corpus.py` | `--corpus-root`、`--top` | 只读语料分析，产出 `reports/corpus-analysis.*` |
| R0 | `probe_candidates.py` | `--date`、`--only`、`--concurrency` | 候选三重体检（200 + 真 feed + 能出条目），产出 `reports/candidate-probe-*` |
| R1 | `register_sources.py` | `--date`、`--dry-run` | 幂等登记 `ok=true` 候选；重复运行不重复追加 |
| R2 | `gen_source_archive.py` | `--date`、`--out` | 只读合并注册表+候选池+探测/体检报告，再生成 `docs/references/data-source.md` 全量归档表（含未采纳/不可用源） |
| R3 | `probe_recover.py` | `--date`、`--concurrency` | 失败源三路恢复探测（gnews site:/RSSHub 镜像/HTML 启发式），产出 `reports/recover-probe-*` |
| R4 | `import_opml.py` | `--file`、`--date`、`--dry-run` | OPML 清单导入：三重实测 + 按主机分流（重复/同域/gnews 顶替/复活），产出 `reports/opml-import-*` |
| R5 | `fetch_folo.py` | `--date`、`--max-pages` | Folo 基线采集（npx folocli timeline 只读翻页），产出 `data/raw/<date>/folo-timeline.json`；未登录软降级 exit 0 由 run_daily 容忍 |
| 0 | `check_sources.py` | `--update`（需确认）、`--timeout` | 0 有正常源；1 全部异常 |
| 1 | `fetch_sources.py` | `--only <ids>`、`--save-payload`、`--offline` | 0 至少一源成功；1 全失败 |
| 2 | `normalize.py` | `--window-hours`、`--demo`（内存态 seen.db） | 0 正常 |
| 3 | `dedupe_cluster.py` | `--date` | 0 正常；1 无候选 |
| 4 | **AI 环节（WorkBuddy Agent）** | `daily-digest.md` | 写回 `ai-review.json` |
| 5 | `make_digest.py` | `--fallback` | 0 正常 |
| 6 | `build_feeds.py` | `--base-url` | 0 正常；2 **凭据命中拒发** |
| 7 | `build_site.py` | `--date` | 0 正常；1 无 digest |
| 8 | `verify_digest.py` | `--all-dates`、`--no-idempotency` | 0 `violations=0`（含 V8 内容丰富度）；1 有未通过项 |
| P | `prepare_pages.py` | `--base-url`（必填）、`--dist-dir`、`--apply` | 0 dry-run/落盘通过；1 校验有问题拒发；2 缺 `public/` 或 base_url 非法 |

`run_daily.py` 把 1→8 串起来（AI 环节检查 `ai-review.json` 是否存在，缺失自动降级）。

## 3. Skill 部署

本机约定**优先 symlink**（改源即时生效，避免多份拷贝漂移）：

```bash
# Windows / Git Bash
cmd //c mklink /D "C:\Users\towyq\.workbuddy\skills\daily-info" \
  "D:\Users\towyq\Documents\Projects\personal-daily-info\assets\skills\daily-info"

# PowerShell 等价
# New-Item -ItemType SymbolicLink -Path ~/.workbuddy/skills/daily-info -Target <项目路径>
```

在 macOS / kmaster / hermes-agent 环境复用时，同样用 symlink 指向同一目录。
`SKILL.md` 的 frontmatter 符合本机规范（`name` / `description` / `license` / `metadata`），
`description` 写清触发条件（跑日报 / 补刊 / 检查信源 / 重建订阅 / 核验 / 周复盘 / 配定时任务）。

### skill 入口命令

```bash
python assets/skills/daily-info/scripts/pipeline.py status        # 只读状态
python assets/skills/daily-info/scripts/pipeline.py run --offline-demo
python assets/skills/daily-info/scripts/pipeline.py run
python assets/skills/daily-info/scripts/pipeline.py check --all
python assets/skills/daily-info/scripts/pipeline.py health
python assets/skills/daily-info/scripts/pipeline.py week
```

`pipeline.py` 只是薄封装，所有逻辑仍在项目 `scripts/` 下，避免 skill 与项目出现两套实现。

## 4. 模板与 assets 使用位置

| 资产 | 被谁使用 | 备注 |
| --- | --- | --- |
| `config/content-spec.json` | `make_digest.py` 白名单校验、`verify_digest.py` V8、`daily-digest.md` prompt | 七要素与阈值的唯一权威，改这里即可调整内容质量线 |
| `ai-review.schema.json` | AI Agent 写回前自检；skill references 引用 | **v2 七要素版**；主模板与 skill 副本哈希一致，需同步维护 |
| `digest.md.tpl` | 资料库沉淀 / 邮件正文素材的版式参考 | 实际 `digest.md` 由 `make_digest.py` 确定性渲染 |
| `brief.md.tpl` | 企微推送文案版式参考 | 实际 `brief.md` 由脚本生成，≤1500 字 |
| `email.html` | agent-mail 正文 | 占位符：`{date} {headline} {item_count} {themes_html} {sections_html} ...` |
| `public/index.html` | 静态站 | 只读 `public/data/*.json` |
| `assets/prompts/*` | 定时任务 / AI 环节 | 见 `09` 索引 |

## 5. 三关验证（每次改动后必做）

```bash
cd D:/Users/towyq/Documents/Projects/personal-daily-info

# 关卡 1：语法
python -m py_compile scripts/*.py assets/skills/daily-info/scripts/*.py

# 关卡 2：全链路 smoke（离线样例）
python scripts/run_daily.py --offline-demo

# 关卡 3：独立核验
python scripts/verify_digest.py --all-dates
```

| 关卡 | 通过标准 |
| --- | --- |
| 语法 | 0 编译错误 |
| smoke | 全流程退出码 0，7 个步骤均有输出 |
| 核验 | `violations=0`，且报告写明通过项数 |

**本次实测（2026-11-04，v2 最终核验）**：
`py_compile` 0 错误；5 份 config + 2 份 schema JSON 均可解析；
两份 `ai-review.schema.json` sha256 一致；`docs/` 13 份齐全；站点 JS `node --check` 通过。
`12 → 12 → 12 簇 → 入报 10 条 / 9 板块`，**七要素达标 10/10 = 100%**；
订阅 `all=10 / high-signal=6 / tech=6 / invest=2 / docs=2`；
核验 **31/31 通过，violations=0**（含 V5 `files=11 changed=0`、V6 五个订阅地址存在性、
V8 内容丰富度 9 个子项全通过），报告 `reports/verify-2026-11-04.md`。
语料研究 `reports/corpus-analysis.{json,md}` 由 `analyze_corpus.py` 可复现生成。
⚠️ 这是**离线演示数据**，仅证明链路可运行，不代表真实信源覆盖率或 AI 质量。

另需人工验证：`python -m http.server 8765 --directory public` 后浏览器首屏、
日期切换、搜索、深浅主题、5 个 Atom 链接均正常。

## 6. 一致性维护约定

| 约定 | 检查方式 |
| --- | --- |
| `subscriptions.json` 的 `profiles[].entry` 必须与 `build_feeds.py` 输出文件名一致 | 检查 `public/data/index.json` 的 feeds URL 对应文件存在 |
| `ai-review.schema.json` 主模板与 skill 副本必须哈希一致 | `sha256sum` 两文件比对 |
| `docs/` 里的命令与实际脚本参数一致 | 按 `00` §3 逐条执行 |
| `taxonomy.categories[].key` 与 schema 的 `sections[].key` 枚举一致 | 人工核对 + smoke |
| 新增脚本必须同步更新 `SKILL.md` 命令表与 `10` 本文 | 文档 review |

## 7. 未实现 / 有意留白（诚实清单）

| 项 | 状态 | 说明 |
| --- | --- | --- |
| `dedupe_cluster.py --apply-boundary` | **未实现**（P3） | prompt 与规则已写好，默认不启用；开启前需补这段确定性合并逻辑 |
| `common.parse_html_items` 的 `html_sec_edgar` | **未实现** | 该源默认 `enabled:false`，不影响主链路 |
| 独立来源快照采集器 | **未实现**（P3） | 因此 `evidence-audit` 状态恒为 `UNVERIFIED`，这是有意的知识边界 |
| `items.csv` 资料库索引导出 | ✅ **已实现**（P1） | `export_library.py` 输出 12 列 UTF-8 BOM 表，2026-11-05 实测 23 行 |
| 无实质数字条目诊断清单 | ✅ **已实现**（P1） | `no-number-<date>.csv`，实测 13 行，用于补上游摘要而非放宽阈值 |
| 资料库离线快照 + manifest | ✅ **已实现**（P1） | 自包含 HTML（不依赖站点相对路径）+ sha256 清单 |
| 邮件正文自动渲染 `email.html` | ✅ **已实现**（P1） | `render_email.py` 渲染全部 9 板块 23 条，18387 字，凭据扫描 clean |
| 分发闸门 / 幂等 / 待授权清单 | ✅ **已实现**（P1） | `push_daily.py` 默认 dry-run，`--apply` 只准备本地 payload |
| 站点端到端验收 | ✅ **已实现**（P1） | `check_release.py` IPv6 ::1 实发 HTTP，18/18 通过 |
| GitHub Pages 子路径部署副本 | ✅ **已上线** | `prepare_pages.py` dry-run 0 问题 / `--apply` 幂等 / 子路径 14/14 / 线上 15/15（见 `docs/16`） |
| 日期 + 分类双维导航 / 订阅引导面板 | ✅ **已实现**（v3） | `public/index.html`；`check_release.py` 静态检查 14 项 + Chrome headless 双场景 DOM 断言 **16/16**（`reports/site-ui-check-2026-11-06.md`） |
| 真实联网跑一次完整日报 | ✅ **已执行** | 2026-11-05：184/185 源、11288 条原始、AI 研判、35/35 核验 |
| `agent-mail` / 企微 / 资料库的实际发送 | ⏳ **待用户授权** | 脚本已把 payload 与动作清单备齐（`pending-dispatch-<date>.json`），外部工具未调用 |
| 站点发布为在线链接 | ⏳ **待用户授权** | `public/` 已可本地访问，上线涉及对外可见性 |
| 「每日信息 · 主链路」定时任务 | ⏳ **待用户授权** | prompt（v1.1）与 rrule 已就绪；创建会每天自动调度并可能推送，故不擅自创建 |

> 已实现项均有当日实证；待授权项**不谎称已完成**。详见 `08` §10 与 `11` §1 P1。
