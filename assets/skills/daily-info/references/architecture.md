# 架构与数据契约

## 1. 分层（借鉴四仓库实证，补上它们的缺口）

```
[信源层]  config/sources.json  ·  Tier A 稳定 feed / B 结构化 API / C HTML / X 已失效
   ↓ fetch_sources.py（并发 8、超时 20s、重试 2、指数退避、ETag/Last-Modified 条件请求）
[原始层]  data/raw/<date>/<source-id>.json + _summary.json   · 可重放快照，保留 30 天
   ↓ normalize.py（时间窗 30h、canonical_url 去追踪参数、规则分类、seen.db 跨天去重）
[归一层]  data/normalized/<date>/items.jsonl + data/state/seen.db(SQLite)
   ↓ dedupe_cluster.py（并查集 + token Jaccard、6 维打分、配额选择）
[候选层]  data/candidate/<date>/clusters.json + prompt-input.json（唯一喂给 AI 的输入）
   ↓ ===== AI 边界 =====  WorkBuddy Agent 写回 ai-review.json
[事实源]  data/digest/<date>/digest.json（唯一事实源）+ digest.md + brief.md   · 永久保留
   ↓ make_digest.py / build_feeds.py / build_site.py（全部确定性、幂等写入）
[服务层]  public/index.html + public/data/*.json + public/*.atom + public/feed.json
   ↓ verify_digest.py（只读核验闸门）
[分发层]  站点 / Atom / JSON Feed / agent-mail / 企业微信 / 资料库
```

**关键解耦**：内容层（digest.json）与订阅层（feed）分离，订阅层全量确定性重建。
这来自 daily-rss → docs-feed 的「纯 Markdown 产物仓库 → 聚合为 Atom」两层结构，
但补上了 docs-feed 缺失的历史留存、多 feed、发布前安全闸门。

## 2. 目录契约

| 路径 | 内容 | 留存 |
| --- | --- | --- |
| `config/*.json` | 信源、分类、打分、订阅配置 | 永久（Git） |
| `data/raw/<date>/` | 每源一份抓取快照 + `_summary.json` | 30 天 |
| `data/normalized/<date>/items.jsonl` | 统一 Item schema | 180 天 |
| `data/candidate/<date>/` | `clusters.json`、`prompt-input.json` | 180 天 |
| `data/digest/<date>/` | `ai-review.json`、`digest.json`、`digest.md`、`brief.md` | **永久** |
| `data/digest/week-<ISO>.json` | 周复盘打包输入 | 永久 |
| `data/state/seen.db` | canonical_url → first_seen / repeat_count（SQLite） | 永久 |
| `data/state/http-cache.json` | ETag / Last-Modified | 永久 |
| `data/state/run-log.jsonl` | 每步事件（fetch/normalize/cluster/digest/feeds/site） | 永久 |
| `data/state/push-log.jsonl` | 分发幂等记录 | 永久 |
| `public/data/` | `index.json`、`latest.json`、`<date>.json`、`feeds.json` | 永久 |
| `public/*.atom` / `feed.json` | 5 个 profile + 默认入口 | 每次重建 |
| `reports/` | 信源体检、核验、周报、留存报告 | 永久 |

## 3. Item schema（`data/normalized/<date>/items.jsonl`）

```json
{
  "id": "sha1(canonical_url)[:16]",
  "source_id": "tldr-ai", "source_name": "TLDR AI", "source_tier": "A",
  "source_weight": 1.0,
  "title": "...", "url": "...", "canonical_url": "...", "guid": "...",
  "author": null, "published_at": "2026-11-04T02:10:00Z", "fetched_at": "...",
  "lang": "en", "summary_raw": "...",
  "category": "ai-models", "category_hint": "ai-models",
  "tags": ["user_focus","release"], "matched_rules": ["ai-models:3"],
  "metrics": {"hn_points": 512, "comments": 233},
  "repeat_count": 1, "tokens": ["..."],
  "cluster_id": null, "score": null, "ai": null
}
```

**时间口径单一来源**：所有 `published_at` 统一为 UTC ISO8601（Z）；
业务日期 `date` 用 Asia/Shanghai 自然日；`generated_at` 用 UTC。
绝不用「文件名日期」「文内日期」当权威时间（参见 `pitfalls.md` 的上下游日期口径坑）。

## 4. 打分（`config/scoring.json`）

`score = 100 × Σ(weight_i × component_i)`，分量裁剪到 [0,1]：

| 分量 | 权重 | 计算 |
| --- | --- | --- |
| source_quality | 0.25 | `min(1, source.weight / 1.2)` |
| freshness | 0.20 | `exp(-ln2 × age_hours / 18)`；无时间取 0.45 |
| engagement | 0.15 | `log1p(hn_points)/log1p(500)` 等取最大；无指标用 `source_quality × 0.5` |
| relevance | 0.20 | `0.35 + keyword_hits×0.08 + user_focus_bonus(0.15)` |
| novelty | 0.12 | `1/(1+repeat_count-1)`，seen.db 跨天去重 |
| coverage | 0.08 | 簇内独立信源数（簇级加分 `0.04/源`，上限 0.2） |

选择：`daily_total=40`，按 `taxonomy.categories[].quota_per_day` 配额，
`min_score=45`，`must_include_top_n=5`（前 5 名无视分数/配额强制入选）。

聚类：`similarity_threshold=0.62`（token Jaccard 并查集），`ai_boundary_low=0.45`
（边界对只记录、默认不调模型），`max_cluster_size=8`。

## 5. digest.json schema（唯一事实源）

```json
{
  "date": "YYYY-MM-DD", "headline": "...", "headline_short": "...",
  "generated_at": "...Z",
  "themes": [{"title":"...","why":"...","cluster_ids":["..."],"verified_by":2}],
  "sections": [{"key":"ai-models","label":"模型与研究","items":[{
     "id":"...","title":"...","url":"...","source":"...","published_at":"...",
     "score":78.2,"category":"...","cluster_id":"...","summary":"...","why_matters":"..."}]}],
  "editor_note": "...", "brief": "...",
  "stats": {"sources_ok":26,"sources_total":29,"total_items":430,
            "clusters":118,"selected":40,"published_items":38},
  "quality": {"ai_status":"ok|degraded","missing_data_marker":"暂无可靠数据",
              "warnings":[],"id_whitelist":true,"url_whitelist":true,
              "credential_scan":"clean"},
  "demo": false
}
```

**不可变约束**：`sections[].items[].id` 与 `url` 必须能在 `clusters.json` 中找到；
`make_digest.py` 对 AI 产出做白名单过滤，命中不了的整条丢弃并记 `quality.warnings`。

### 5.1 v2 七要素（依据 `config/content-spec.json` 与 `docs/12`）

每条 `sections[].items[]` 除上述字段外必须含：

| 字段 | 校验 |
| --- | --- |
| `fact_anchor` | 谁+做了什么，≤120 字，去 URL |
| `numbers[]` | **每个值必须出现在该条目原文 `title + summary_raw + metrics` 值中**（v1.1 口径，`published_at` 等采集元数据不算原文），否则丢弃；为空时仍只从该原文兜底取一个真实数字；原文全文无数字则**拒绝该条目入报**并记 `rejected_no_substantive_number` |
| `entities[]` | 必须出现在原文中，否则丢弃并记 warning |
| `evidence_urls[]` | 只允许同簇成员 URL；AI 自带新 URL 一律忽略；空则填该条目 url |
| `impact` | 锚定 user_focus，说明对我工作的具体影响 |
| `next_action` | 必须含判定阈值；命中「持续关注/后续跟进/…」空话直接清空并记 warning |

顶层新增：`lead`（数据化导语，含可核验数字）、`watch_signals[]`（signal + threshold + judgement）、
`reference_summary[]`（引用域名统计）、`stats.seven_element_ratio`。
`quality` 增加 `number_whitelist` / `entity_whitelist` / `content_spec_version`。
完整契约见 `assets/templates/ai-review.schema.json`（v2，`additionalProperties:false`）。

## 6. 订阅契约（`config/subscriptions.json`）

| profile | 过滤 | 产物 |
| --- | --- | --- |
| all | `score >= 45` | `all.atom`（同时 `feed.atom`） |
| high-signal | `score >= 70` | `high-signal.atom` |
| tech | `category in taxonomy.groups.tech` | `tech.atom` |
| invest | `category in [market-invest, industry-capital]` | `invest.atom` |
| docs | `category == docs-changelog` | `docs.atom` |

- Atom 1.0 全文（`content type=html`），`entry id = tag:daily-info.local,{date}:{cluster_id}` **稳定不变**；
- `feed.json` 用 JSON Feed 1.1，额外 `_daily_info` 扩展字段带 score / source / cluster_id / ai_status；
- 全量确定性重建 + 字节比较幂等写入（内容不变不重写、不触发发布）；
- 发布前凭据扫描命中 → 整体拒发并保留旧文件；
- HTML 自建固定标签 + 全量 `html.escape`，不允许 script / onerror / javascript: / iframe。

## 7. 核验项（`verify_digest.py`）

| ID | 检查 | 通过标准 |
| --- | --- | --- |
| V1 | 结构完整性、ai_status 合法、stats 自洽 | 必填字段齐全，计数一致 |
| V2 | id / url 白名单、无重复条目 | violations = 0 |
| V3 | 凭据正则 + 危险 HTML | violations = 0 |
| V4 | Atom XML 可解析、entry id 唯一 | 每个 feed ≥ 1 条且唯一 |
| V5 | 二次构建字节幂等 | changed files = 0 |
| V6 | 站点 index / latest / 日切片 | 日期一致、文件存在 |
| V7 | 降级标记 | degraded 时 headline 带 `[降级]` 且无 editor_note；V8 对降级日报跳过 |
| **V8** | **内容丰富度** | 七要素达标率 ≥80%、含数字条目比 ≥70%、lead 含数字、watch_signals ≥3、next_action 无空话、editor_note 400-600 字、themes 6-8 且各 ≥2 佐证、白名单标记全为 true |

报告写入 `reports/verify-<date>.{json,md}`，退出码 0 才允许分发。

## 8. 站点契约

`public/index.html` 是**零依赖单页**：只读 `public/data/index.json`、`latest.json`、`<date>.json`。
无任何构建步骤、无 CDN、无后端。改数据不改代码。
需通过 HTTP 访问（`file://` 下 fetch 会被浏览器拦截）：
`python -m http.server 8765 --directory public`（Windows 下用 `localhost` 而非 `127.0.0.1`，规避本机 TUN 代理拦截）。
