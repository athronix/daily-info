# 坑与规避（遇到异常先读这里）

> 约定：本文件是**持续维护**的。执行不合规或踩新坑 → 纠正后把根因与规避写进来，
> 再重做交付物，不要只在当次会话里口头说明。

## P01 · 把「子 agent failed 通知」误判为研究失败

**现象**：四份源码分析主报告都已完整交付（含勘误与交叉校验补充），
随后框架又推送 `blogpost-analyst failed` / `investor-analyst failed`，
错误是 `429 usage exceeds frequency limit`。

**根因**：429 发生在 agent 收尾/通知阶段，不是研究阶段；研究成果已经通过消息回传。

**规避**：先核对「是否已有主报告 + 补充」，有则不重跑（重跑会再次撞限流、丢上下文）。
汇报时明确写「报告已交付，failed 为限流收尾失败」。本方案已按此处理。

## P02 · docs-feed 名不副实

**坑**：`docs-feed` / `releases.atom` 听起来像「官方文档变更监控 / GitHub Releases 订阅」，
实际是把作者自己 3 个仓库的 Markdown 聚成全文 Atom；它不调用 Releases API、不解析外部 feed。

**规避**：设计文档里按真实机制写；本方案的「文档变更雷达」是新增能力
（`docs-changelog` 分类 + GitHub Releases Atom 源），不是从 docs-feed 抄来的。

## P03 · 公开 Atom 二次扩散明文密钥

**坑**：上游仓库存在明文 `FINNHUB_API_KEY` 与 GitHub token 的 `credential.helper` 写法，
且不在 docs-feed 的排除清单里；`bleach.clean` 只做标签/属性白名单，**不扫正文**。
`max_entries=100` 恰好把这些旧元文档挤出，属「条件触发的定时炸弹」，当前**尚未实际泄漏**。

**规避**：本方案 `build_feeds.py` / `make_digest.py` / `verify_digest.py` 三处做凭据正则扫描，
命中即整体拒发并保留旧产物；`verify_digest.py` V3 是发布前硬闸门。
另外不要用「黑名单 exclude」做唯一防线，优先用 include 白名单。

## P04 · 上游文件名日期 vs 下游 git 历史日期

**坑**：blogpost 从文件名解析日期（非日期命名文件回退 git log 或写死 `"2026-02"`），
docs-feed 一律用 git 提交时间；同一内容库两套口径。docs-feed 还要求 `fetch-depth: 0` 完整历史。

**规避**：本方案时间口径单一来源 —— `published_at` 统一 UTC ISO8601，
业务 `date` 用 Asia/Shanghai 自然日，`generated_at` 用 UTC；
文件名与文内日期只作展示，**绝不参与排序或去重判定**。

## P05 · 订阅 URL 口径不一致（本项目实测踩过）

**坑**：`config/subscriptions.json` 的 `profiles[].entry` 初版写 `feed.atom` / `feed-high.atom`，
而 `build_feeds.py` 实际生成 `<profile_id>.atom`（`all.atom` / `high-signal.atom` …），
导致站点订阅按钮指向不存在的文件。

**规避**：统一为 `all.atom` 等，并在 `build_site.py` 直接读该字段生成索引；
核验时增加「索引里每个 feed URL 对应文件存在」检查。
**通用原则**：配置文件里的产物路径必须与构建器输出路径同源，不要两处各写一份。

## P06 · 本机网络：TUN 拦截裸 127.0.0.1

**坑**：NekoBox TUN 模式会拦截出站流量，含进程直连 IPv4 `127.0.0.1` 的裸 TCP；
本地静态站 / 前后端联调用 `127.0.0.1` 会返回 401 / Authentication failed。

**规避**：一律用 `localhost`（解析到 IPv6 `::1`）；
node/Python 脚本设 `NO_PROXY=localhost,127.0.0.1`；本地预览用
`python -m http.server 8765 --directory public` + `http://localhost:8765/`。

## P07 · 站点用 file:// 打开时 fetch 被浏览器拦截

**坑**：`public/index.html` 通过 `fetch('data/index.json')` 读数据，双击打开（file://）会因 CORS 失败。

**规避**：必须经 HTTP 访问（本地 http.server 或发布为网站后的在线地址）；
页面已在错误提示里写明这一点。

## P08 · AI 越界编造 id / URL / 数字

**坑**：LLM 容易「顺手补一条更完整的新闻」，或把多个来源拼成不存在的链接。

**规避**：`make_digest.py` 对 `ai-review.json` 做白名单过滤 ——
id 必须存在于 `clusters.json`，AI 自带 url 一律忽略，找不到就丢弃并记 `quality.warnings`；
prompt 里把素材定义成 UNTRUSTED DATA 并显式禁止新增事实；V2 核验二次把关。

## P09 · 「格式正确」≠「事实为真」

**坑**：`verify_digest.py` 只验结构、白名单、安全、幂等，不能证明新闻内容真实。
daily-investor 的审计 pilot 自承 `NO_INDEPENDENT_SOURCE_SNAPSHOTS` 就是这个边界。

**规避**：所有产物统一标注「外部事实未独立验证」；
另设只读 `evidence-audit.md` prompt 做逐 claim 台账，状态恒为 `UNVERIFIED`，
**绝不因为核验 0 violations 就宣称内容已核实**。

## P10 · 把订阅地址填成 GitHub 自动生成的 releases.atom

**坑**：docs-feed README 第 7 行专门警告：仓库页的 `/releases.atom` 是 GitHub 自动生成的
Release 订阅，不能用仓库里的同名文件替换。

**规避**：本项目订阅用**静态站点地址**（`<在线域名>/feed.atom`），
发布为网站后填这个；不要填仓库页路径。

## P11 · 时区混用与 cron 误读

**坑**：GitHub Actions cron 用 UTC（`'30 0 * * *'` = 北京 08:30）；
参考仓库同时出现 06:00/06:30/07:00 CST、UTC、美东 ET 三套口径，README 与 footer 还互相矛盾。

**规避**：项目 `timezone: Asia/Shanghai` 单点声明；
所有对外时间戳带 `Z` 或显式时区；定时任务时间写在任务配置里，不写进 prompt。

## P12 · GitHub Actions 长时间无活动会停用 schedule

**坑**：docs-feed README 注明连续 60 天无活动 GitHub 可能停用定时工作流。

**规避**：本方案主调度用 WorkBuddy 定时任务（不依赖 GitHub Actions）；
若额外用 CI 备份，需保证有定期提交或定期手动触发。

## P13 · 安全删除垫片 / 批量删除阈值

**坑**：本机 WorkBuddy 沙箱把 `fs.rm/rmSync` 改成进回收站；回收站不可用会 fail-closed 拒绝删除；
批量删除还有按会话累计 50 次的守卫。

**规避**：本方案**默认不删任何文件**；`retention.py` 默认 `--dry-run`，
`--apply` 需用户明确确认、每批最多 10 个目录、逐批校验、异常即停；
digest / candidate / state / public / config / reports 永不进入清理范围。

## P14 · 信源有效性漂移（2026-11-04 实测）

**坑**：参考仓库 README 里的多个源已失效，但正文长期只标注不处置。
实测：`github-trends-atom.vercel.app/trending` 404、`anthropic.com/rss.xml` 404、
`blog.langchain.dev/rss/` 302 到 HTML、`rsshub.app` 403、`36kr.com/feed` /
`jiqizhixin.com/rss` / `infoq.cn/feed` 返回 text/html、VentureBeat 429。

**规避**：`sources.json` 把这些标为 `tier:"X"` + `enabled:false` 并保留实测证据与替代源；
每周 `check_sources.py` 体检；单源失败整源降级不阻断日报。

## P15 · 抓取得太狠会被限流 / 封禁

**坑**：KDnuggets 429/403、VentureBeat 429、GitHub API 未带 token 时 10 req/min。

**规避**：默认并发 8、超时 20s、重试 2 次指数退避、ETag/Last-Modified 条件请求、
`respect_robots: true`、`min_interval_sec: 1`；B 类 API 单独降权，不把公开实例当生产依赖。

## P16 · 幂等核验会再跑一次构建器

**说明**：`verify_digest.py` 的 V5 会调用 `build_feeds.py` / `build_site.py` 二次构建并比对字节哈希。
因为所有写入都是「内容不变则不落盘」，这是**无副作用**的；
但它要求核验环境有写权限。只读环境用 `--no-idempotency` 跳过，并在报告里标注 skipped。

## P17 · `.atom` 的 Content-Type 可能被静态托管误判

**现象**：2026-11-04 端到端实测，`python -m http.server` 对 `/feed.atom`、`/all.atom`
返回 `application/octet-stream`（不是 `application/atom+xml`）；文件本身合法且可被解析。

**影响**：多数 RSS 阅读器会按内容与 `<link rel="alternate" type="application/atom+xml">` 容错，
但少数严格的阅读器/代理可能拒收；出现「订阅地址打不开」时先查响应头。

**规避**：发布为网站 / GitHub Pages / 自建托管时，给 `.atom` 配 MIME
`application/atom+xml`；无法配置时，在订阅教程里提示「手动添加 URL」而非依赖自动发现。
本地验证可用 `curl -I http://localhost:8765/feed.atom` 看响应头。

## P18 · 重复跑 offline-demo 污染 seen.db，导致分流 feed 变空

**现象**：v2 首次接入 V8 后核验出现 `FAIL V4 high-signal.atom entries=0`。
`normalize.py` 把演示条目写入真实 `data/state/seen.db`，重复跑时 `repeat_count` 累积、
novelty 分量 `1/(1+repeat-1)` 衰减，分数跌破 `score >= 70`，高信噪 profile 被清空。

**根因**：demo 与真实运行共用同一状态库，破坏了「离线 smoke 可重放」的前提。

**规避**：`normalize.py --demo` 改用内存态 SQLite（`:memory:`），
`run_daily.py --offline-demo` 自动传该参数。真实 `seen.db` 不再被演示数据污染，
重复跑 demo 的分数与订阅 profile 条数保持一致。
另修正 V4：主入口 `all.atom` / `feed.atom` 必须非空，**分流 profile 当日为空是正常视图状态**，
不算 violation，但会在核验报告里注明。

## P19 · 「内容丰富」不能只靠提示词，要有程序闸门

**现象**：早期每条只有「标题 + 一句 why_matters」，AI 容易写出「值得关注的重要进展」这类空话，
也无法验证数字是否真实。

**规避**（v2 七要素，依据 `docs/12` 语料实测）：
- 每条强制七要素；`numbers` / `entities` / `evidence_urls` 由 `make_digest.py` 回原文逐项白名单校验，
  编造即丢弃并记 `quality.warnings`；
- `next_action` 命中「持续关注/后续跟进/保持观察/值得留意/继续跟踪」直接清空；
- `verify_digest.py` V8 检查达标率、导语数字、待验证信号、编者观察字数、主题佐证数；
- 降级日报跳过 V8（只验降级标记），避免把「薄报」误判为「不合格」。

**别反着做**：不要为了让核验通过而放宽阈值或删检查项——先找根因（如 P18）。

## P20 · urllib 对 304 抛 HTTPError，条件请求分支永远走不到

**现象**：真实全量采集时 5 个源报「采集失败 HTTP 304」，但 http-cache 里明明有上次快照。

**根因**：`urllib.request.urlopen` 对 304 **抛 `HTTPError`**（不是返回响应对象），
原代码把 304 处理写在 `with urlopen(...)` 成功分支里，永远不可达；
且快照文件被 retention/清理后 `last_file` 指向不存在的文件时也没有兜底。

**规避**：单独 `except urllib.error.HTTPError`，304 时优先复用上次快照 items；
快照缺失则**去掉条件头强制重抓**而不是记失败。判据：`fetch_sources.py` 的
`_summary.json` 中不应再出现 304 类失败。

## P21 · 白名单能验「值在原文」，验不了「语义匹配」——id 张冠李戴要靠人工/审计兜底

**现象**：真实日报写回时，我把 Boehringer 交易的内容挂到了印度兵役的 cluster id 上；
实体白名单只报出「该 id 原文里没有 Boehringer」，但不会告诉我正确的 id 是哪个。

**根因**：引用 40 个簇时凭列表顺序记忆 id，未逐条回查标题。

**规避**：
1. 写 `ai-review.json` 前，先跑一段「id → title」打印核对（本次就是这么发现错配的）；
2. `warnings` 必须输出**被丢弃的具体值**（已改 `make_digest.py`），空计数无法定位问题；
3. 语义级核验交给 `evidence-audit.md` 的 claim 台账（claim ID + 行范围 + 短引文），
   结构闸门 + 人工/审计双轨，缺一不可。
4. 溯源断言（数字必须逐字在原文）要在**写回前自检**就执行，别等 make_digest 丢数据才发现。

## P22 · 把「首屏 HTML 无内容」当成「无法程序化接入」

**现象**：11-04 把 `hub.baai.ac.cn` 与 `d.aigclink.ai` 判为 Tier C 禁用，理由是
「Nuxt SSR 壳 18KB、零文章数据 / Notion 首屏外链数 0，需无头浏览器」。

**根因**：只探测了首页 HTML 与 `/api/*` 的盲猜路径，没有做三步逆向：
① 看 SSR 内联数据；② 下载 JS chunk 提取 `baseURL` / API 路径；③ 用正确 HTTP 方法试匿名调用。
实际 BAAI 的 `__NUXT__` 里就有 6 条完整 `story_info`，`/_nuxt/ab9f904.js` 里明写
`hub-api.baai.ac.cn` 与 `/v1/story/list`（POST 200、GET 405）；Notion 站的
`requiredRedirectMetadata` 给出 pageId，`/api/v3/loadPageChunk` + `queryCollection` 均匿名 200。

**规避**：判定「不可接入」前必须留三类证据：内联数据搜索结果、JS chunk 中的 API host/path、
GET 与 POST 两种方法的实测响应。别用「无 feed + 首页无内容」直接下结论。
另注意：能拿数据 ≠ 能拿增量（Notion `query.sort` 对匿名请求不生效，只返回最早的行），
此时要么换渲染代理，要么如实登记「结构化路径待解锁」，不许放启用但恒为空的摆设。

## P23 · 200 + application/xml 也可能是未声明 Content-Encoding 的 gzip

**现象**：`deepmind.google/blog/rss.xml` 体检返回 200 + `Content-Type: application/xml`，
但 `parse_feed` 报 `ParseError: syntax error: line 1, column 0`；响应体开头是 `\x1f\x8b`。

**根因**：服务端返回 gzip 压缩体却**没设 `Content-Encoding`**，urllib 不会自动解压；
只看状态码与 Content-Type 的健康检查会把它误判为「正常」。

**规避**：`common.decode_payload` 按 gzip 魔数兜底解压（用 `zlib.decompressobj(16+MAX_WBITS)`，
这样体检只读部分字节也能解出开头，不会因截断流抛 EOFError）；`fetch_sources.py` 与
`check_sources.py` 都调用它。同时把 DeepMind 换到 `blog.google` 官方板块 feed 双保险。

## P24 · 同域多源叠加限流 + 反爬挑战页伪装成 200

**现象**：新增第 3 个 Reddit 子版后，`r/opensource` / `r/artificial` 全量采集持续 429；
`cncf-blog` 体检时是真 feed（10 条），采集时却返回 `text/html` 的 Varnish 挑战页（200 + no-store + Set-Cookie）。

**根因**：Reddit 按来源 IP 给整个域配额，多加源不是「多一份数据」而是「抢同一份配额」；
CNCF 的 Varnish 对高频请求返回挑战页且状态码仍是 200，只看状态码的健康检查识别不了。

**规避**：
1. 同域源控制在 1–2 个，其余禁用并留证据（本轮 Reddit 只保留 `r/LocalLLaMA`）；
2. 体检必须校验**响应体是否为 feed**，不能只看 200；
3. 间歇性反爬源降权 + `note` 写明「整源降级不阻断日报」，靠 Tier C 语义兜底，不要反复重试；
4. 体检报告与日报失败清单分开看：体检通过不等于永久可用。

## P25 · 宿主 `.env` 不会自动进入子进程，`${VAR}` 占位静默回退匿名

**现象**（2026-11-05）：用户已在 `C:/Users/towyq/.workbuddy/.env` 配好 `GITHUB_TOKEN / USER / EMAIL`，
但采集脚本里 `os.environ` 三个变量全 MISSING——GitHub 仍 10 req/min、SEC 源仍回退匿名，
占位机制「看起来配了」实际从未生效，且**没有任何报错**（静默回退是设计特性，也掩盖了配置断链）。

**根因**：WorkBuddy 不解析宿主 `.env` 注入子进程；`resolve_credentials` 的「未设置即丢弃 header」
策略让缺失凭据表现为正常匿名。

**规避**：
1. `common.load_dotenv()`：按 `PERSONAL_DAILY_INFO_DOTENV` → `~/.workbuddy/.env` → `ROOT/.env`
   读第一个存在的文件注入 `os.environ`（不覆盖已有值、不打印值、只返回注入键数）；
   fetch/check 入口调用。
2. 验证凭据真生效用**行为证据**而非配置读取：GitHub `/rate_limit` 实发对照 10 → 30、SEC 200、
   OpenAlex 200；单测 `redact_credentials` 用真实值往返必须还原为 `${VAR}`。
3. 全仓明文凭据扫描必须包含当日 `data/raw`（mailto 在 URL 查询串里，最易泄漏面）。

## P26 · 外部清单自称「100% 可用」仍需全量实测，且要按域名做重复度分流

**现象**（2026-11-05）：用户 OPML 清单标称 60 个"100% 纯正可用"feed，实测仅 38/60 通过
（WSJ/PitchBook/Gizmodo 等 403、Pedaily/kr-asia/科学网 xml 端点 404、2 个 feed 本体畸形）。
若直接全量导入，一半是死源；若只导新域，又会漏掉两类惊喜——**同站不同路径的复活**
（InfoQ `/feed` 旧判 text/html 系并发误伤、Space.com `/feeds/all` 顶替 404 的 `/feeds/all.xml`、
Reddit 标准 `.rss` 路径顶替持续 429 的 `hot.rss`）和**官方版顶替转载版**（space/cell/linuxfoundation
的原生 feed 出原文直链，比 gnews 转载对溯源白名单更友好）。

**规避**：`scripts/import_opml.py` 固化「解析 → 三重实测 → 按主机分流」：URL 规范化重复跳过；
同主机已有启用源跳过（防同域配额双花）；官方原生 feed 自动禁用同域 gnews 转载版；
仅 Tier X/禁用或全新主机才登记。幂等 + `--dry-run`，任何清单来了走同一条链。

## P27 · Windows 下 subprocess 直接 exec `npx` 报 WinError 2

**现象**：`fetch_folo.py` 用 `subprocess.run(["npx", "--yes", …])` 报
`FileNotFoundError: [WinError 2] 系统找不到指定的文件`——但同一命令在 bash 里正常。

**根因**：npm 在 Windows 装的是 `npx.cmd` 垫片，CreateProcess 不解析 .cmd 后缀，
且 shell=False 时不走 PATHEXT。

**规避**：Windows 分支把命令首元素替换为 `npx.cmd`（比 `shell=True` 安全，避免参数注入面）；
所有经 subprocess 调 npm/npx/pnpm 垫片的脚本都要注意同一坑。

## P28 · 把 `published_at` 算进「原文」白名单，数字条目比会形式通过

**现象**（2026-11-05）：`make_digest.py` 把 `title + summary_raw + metrics + published_at`
拼成原文用于数字/实体白名单。当天 32 条入报里有 **9 条**只靠时间戳里的 `2026`
通过「可核验数字」校验——实测这 9 条的 `title+summary+metrics` **一个数字都没有**，
V8 却报「含数字条目比 100%」，属于统计虚高。

**根因**：发布时间是采集侧元数据，不是新闻内容里的读数；把它算进原文，
等于给所有条目发了一张免检通行证。兜底逻辑 `NUMBER_RE.findall(original)` 又会
从同一时间戳里捞出年份，形成「白名单 + 兜底」双重放水。

**规避**（方案 ①，不放宽阈值）：
1. 抽出唯一口径函数 `original_text(member)`，只取 `title + summary_raw + metrics`；
2. 兜底仍只从该函数取，找不到就 `warnings.append("rejected_no_substantive_number:<id>")`
   并 `continue` —— **直接拒绝入报**，不靠空数字凑七要素；
3. 主题佐证只从 `published_ids` 过滤，禁止引用被拒簇；
4. `content-spec.json` 升 v1.1 写明口径 + 排除字段 + `effective_from`，
   V8 增三项闸门（排除元数据 / 实质数字比自洽 / 拒绝留痕），历史归档按日期豁免；
5. AI 侧由 `daily-digest.md` 明令「无数字条目不要写进 sections」，而非等下游兜底。

**实测效果**：演练态 9 条被拒、18 条 warning、主题佐证掉到 1（V8 会 FAIL）；
按新口径重做研判后 23 条入报、七要素 100%、实质数字比 100%、warnings=0、35/35 核验通过。
`no-number-<date>.csv` 每日导出入选簇中 13 条无数字条目，供「补上游摘要」而非调阈值。

## P29 · 邮件正文长度阈值是 P0 拍脑袋值，实测会截掉 5 个板块

**现象**：`subscriptions.json` 的 `max_body_chars=12000` 在 P1 首次自动渲染时，
23 条完整七要素正文需要 **18387 字符**，`render_email.py` 的保底截断逻辑连删 5 个板块
才压到 11781 字，违反「六个通道从唯一事实源全量投影」原则。

**根因**：P0 只写了模板没写渲染器，阈值没有实测依据；Inline style 重复使
每条 HTML 约 450–600 字符，23 条轻松破万。

**规避**：按实测上调到 `24000` 并在配置里写 `max_body_chars_note` 记录依据；
`render_email.py` 保留 `--max-chars` 便于容量复测，且**一旦发生板块省略就打 WARNING**，
不允许静默丢内容。站点未上线时（`daily-info.local`）不输出占位死链，改提示「正文自包含」。

## P30 · 分发脚本必须止步于「准备到只差授权」，不得自行发送

**现象**：P0 只在 `subscriptions.json` 写了 6 个通道配置与 `email.html` 模板，
分发动作全靠定时任务 Agent 临场发挥，既无核验闸门复核、也无 `push-log.jsonl` 幂等，
更没有「哪些动作待授权」的可核对清单。

**规避**：`push_daily.py` 把边界写死——
1. 闸门：核验报告日期必须匹配、`violations=0`、凭据扫描干净，任一失败整体拒发；
2. 默认 `--dry-run` 只出计划；`--apply` 才调 `export_library.py` / `render_email.py`
   生成**本地** payload，并写 `push-log.jsonl`（日期+通道去重）；
3. 输出 `pending-dispatch-<date>.json`，逐条列出 channel / tool / payload / status，
   但脚本**不调用** agent-mail、企微、资料库、站点发布中的任何一个；
4. 外部动作由 Agent 在用户明确授权后读取该清单执行。

**实证**：`--apply` 连跑两次，第二次 `changed=0`、`push-log` 新增 0 条，幂等成立；
`pending-dispatch` 里 3 条 `pending_authorization`、2 条 `requires_site_publish`、
1 条 `disabled`，动作边界一目了然。

## P31 · 校验 Atom 的 self/alternate 时，root.iter 会把 entry 链接算进来

**现象**：`prepare_pages.py` 初版用 `root.iter(ATOM_NS + "link")` 收集 link，
随后按 `rel` 建字典；entry 级 `rel=alternate` 指向**外部原文**，会覆盖 feed 级
`rel=alternate`，导致 6 个 Atom 全部误报「alternate 未指向新域名」，dry-run 直接拒发。

**根因**：Atom 文档里 feed 级与每个 entry 级都有 `<link>`，二者语义完全不同；
`iter()` 是全树遍历，`findall()` 才是只看直接子节点（feed 级）。

**规避**：校验 feed 级地址只用 `root.findall(ATOM_NS + "link")`；
entry 级 alternate 必须保持外部原文地址，绝不能替换成本站域名。
另在 `docs/16` §3 明确写出「稳定 `tag:` ID、entry alternate 均不随部署域名变化」。

**附带教训**：域名替换是纯文本 `str.replace(old_base, new_base)`，只命中真实占位域名，
不会误伤 `tag:daily-info.local,...` 这类不带斜杠与 `https://` 前缀的稳定 ID。

## P32 · 订阅按钮别直链 `.atom`：浏览器打开就是 XML 源码

**现象**：顶栏「订阅 RSS」写成 `<a href="feed.atom">`，页脚 5 个 profile 也是
`<a href="*.atom">`。用户点击后浏览器把 `application/atom+xml` 渲染成 XML 源码树，
体验极差，且容易被误认为「订阅页坏了」。

**根因**：Atom / RSS 是给**阅读器**消费的机器可读源文件，不是给人看的网页；
配对了 MIME 反而会让浏览器老老实实显示源码，这不是 bug，是入口设计错了。

**规避**：
1. 顶栏与页脚入口一律改为 `<button>`，打开订阅引导 modal：解释源文件用途、
   用 `new URL(f.url, location.href).href` 生成**绝对地址**展示并提供一键复制
   （`navigator.clipboard` + `execCommand('copy')` 兜底，兼容 `file://`）；
2. 只保留一个明确标注「查看源文件（会显示 XML）」的次级链接给高级用户；
3. `<head>` 里的 `rel="alternate"` 自动发现链接**必须保留**，阅读器输入站点首页即可识别；
4. 不要靠给 Atom 加 XSL 样式表来「美化源码页」：会改动 feed 生成契约，
   且 GitHub Pages 对 `.xsl` 的 MIME 不可控，跨浏览器风险高于收益。

**验收**：`check_release.py` 增加静态检查「订阅入口不再直跳 .atom」「保留阅读器自动发现」；
Chrome headless `--dump-dom` 双场景断言 16/16（`reports/site-ui-check-2026-11-06.md`）。
**断言写法注意**：DOM 里含 `<script>` 源码，JS 模板字面量里的 `<button class="feed"` 会被
正则误计数；Chrome 还会把布尔属性序列化成 `readonly=""`。断言前先剔除 `<script>`，
并用 `<input[^>]*value="...">` 而非固定属性顺序，否则会产生 3 项纯误报。

## P33 · 主题配色别让「点缀绿」蔓延到中性色；默认主题要写在 `<html>` 上

**现象**：深色页面整体泛绿，用户一眼觉得「怎么有点绿」；同时站点默认浅色，
想看深色得手动点一次，刷新还回弹。

**根因**：`--bg:#151a17`、`--surface:#1d241f`、`--ink:#eef2ee` 这些被当成「中性色」的值
其实都是 G 通道最大的墨绿；连 `--shadow:rgba(30,45,35,…)` 与遮罩
`rgba(15,22,18,.55)` 也是绿的。整页大面积铺墨绿，不是某个点缀色的问题。
另外默认主题靠 `:root` 兜底、切换靠 body 末尾 JS 后置改属性，既会首帧闪白，也不记选择。

**规避**：
1. 中性色统一中性冷灰，硬约束 `G <= max(R,B)`；点缀色也换成同色系石板蓝
   （浅 `#3b6d9e` / 深 `#8fb9e0`），避免深浅切换时色相跳变；
2. 把约束写进 `check_release.py`：正则抽 `:root` 与 `html[data-theme="dark"]` 块里的
   `#rrggbb` / `rgba()`，逐个算通道，绿通道主导即 FAIL；
3. 默认主题直接写 `<html data-theme="dark">`，并在 `<head>` 的 `<style>` **之前**
   用内联脚本读 `localStorage`，只覆盖用户显式选过的浅色；`try/catch` 兜底，
   隐私模式 / `file://` 下静默回落深色；
4. 切换按钮文案与 `aria-label` 由 `syncThemeBtn()` 统一派生，别把初始文案写死成
   「深色」——默认改深之后它应该写「浅色」。

**验收**：Chrome headless `getComputedStyle` 双场景 **13/13**
（`reports/site-theme-check-2026-11-06.md`），含同一 `--user-data-dir` 二次访问验证
`localStorage` 记忆；`check_release.py` **34/34**。
