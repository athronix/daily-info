# 2026-11-10 站点上线验收报告

- 验收时间：2026-11-10T02:15:13.937106Z
- 公开地址：https://athronix.github.io/daily-info
- 发布方式：定时任务默认授权 → git push `main` → 手动触发 `pages.yml`（workflow_dispatch）
- workflow run：`42741088189`，conclusion = **success**
- 提交：`8d589c4`

## 一、URL 与 MIME

| 路径 | 状态 | Content-Type | 字节 |
|---|---|---|---|
| `/` | 200 | text/html; charset=utf-8 | 26833 |
| `/data/index.json` | 200 | application/json; charset=utf-8 | 7444 |
| `/data/latest.json` | 200 | application/json; charset=utf-8 | 30634 |
| `/data/feeds.json` | 200 | application/json; charset=utf-8 | 1113 |
| `/data/2026-11-10.json` | 200 | application/json; charset=utf-8 | 30634 |
| `/data/2026-11-09.json` | 200 | application/json; charset=utf-8 | 38841 |
| `/data/2026-11-08.json` | 200 | application/json; charset=utf-8 | 42274 |
| `/feed.atom` | 200 | application/atom+xml | 229232 |
| `/feed.json` | 200 | application/json; charset=utf-8 | 215555 |
| `/all.atom` | 200 | application/atom+xml | 229232 |
| `/high-signal.atom` | 200 | application/atom+xml | 229410 |
| `/tech.atom` | 200 | application/atom+xml | 166225 |
| `/invest.atom` | 200 | application/atom+xml | 55069 |
| `/docs.atom` | 200 | application/atom+xml | 19222 |

## 二、契约校验

| 检查项 | 结果 | 明细 |
|---|---|---|
| 14 个 URL 全部 200 | PASS | 14/14 |
| 6 个 .atom = application/atom+xml | PASS | /feed.atom=application/atom+xml /all.atom=application/atom+xml /high-signal.atom=application/atom+xml /tech.atom=application/atom+xml /invest.atom=application/atom+xml /docs.atom=application/atom+xml |
| 2026-11-10.json 与本地等价 | PASS | date=2026-11-10 equal=True |
| index.json 最新为当日 | PASS | 2026-11-10 |
| latest.json 日期为当日 | PASS | 2026-11-10 |
| 占位域名残留 0 | PASS | https://daily-info.local hits=0 |
| 无 localhost/127.0.0.1 占位 | PASS | localhost=0 127=0 |
| feed.atom 稳定 ID 本地/线上集合一致 | PASS | 本地=100 线上=100 交集=100 线上重复=0 |
| 6 个 Atom profile 均可解析且 ID 唯一 | PASS | /feed.atom:100/100 /all.atom:100/100 /high-signal.atom:100/100 /tech.atom:72/72 /invest.atom:25/25 /docs.atom:8/8 |
| 订阅地址指向公开站点 | PASS | feeds.json len=862 |

**合计 10/10，未通过 0 项。**

## 三、口径说明

Atom 稳定 ID 一律用 `xml.etree.ElementTree` 按命名空间解析，
规避 `build_feeds.py` 生成的 `ns0:` 前缀导致裸 `<id>` 正则误判为 0 的历史坑。

