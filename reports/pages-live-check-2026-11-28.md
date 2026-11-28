# 线上验收 · 2026-11-28

站点 https://athronix.github.io/daily-info · commit `0393050` · workflow `46099271467` success

## 14 个 URL

| path | status | content-type | bytes |
| --- | --- | --- | --- |
| / | 200 | text/html; charset=utf-8 | 26833 |
| /data/index.json | 200 | application/json; charset=utf-8 | 25669 |
| /data/latest.json | 200 | application/json; charset=utf-8 | 32106 |
| /data/feeds.json | 200 | application/json; charset=utf-8 | 1115 |
| /data/2026-11-28.json | 200 | application/json; charset=utf-8 | 32106 |
| /data/2026-11-27.json | 200 | application/json; charset=utf-8 | 25353 |
| /data/2026-11-26.json | 200 | application/json; charset=utf-8 | 25723 |
| /feed.json | 200 | application/json; charset=utf-8 | 242311 |
| /feed.atom | 200 | application/atom+xml | 249551 |
| /all.atom | 200 | application/atom+xml | 249551 |
| /high-signal.atom | 200 | application/atom+xml | 249564 |
| /tech.atom | 200 | application/atom+xml | 249114 |
| /invest.atom | 200 | application/atom+xml | 151680 |
| /docs.atom | 200 | application/atom+xml | 69258 |

## 检查项

| 检查项 | 结果 | 说明 |
| --- | --- | --- |
| 14 个 URL 全部 200 | PASS | 14/14 |
| 6 个 .atom = application/atom+xml | PASS | /feed.atom=application/atom+xml /all.atom=application/atom+xml /high-signal.atom=application/atom+xml /tech.atom=application/atom+xml /invest.atom=application/atom+xml /docs.atom=application/atom+xml |
| 2026-11-28.json 与本地等价 | PASS | date=2026-11-28 equal=True |
| index.json 最新为当日 | PASS | 2026-11-28 |
| latest.json 日期为当日 | PASS | 2026-11-28 |
| 占位域名残留 0 | PASS | https://daily-info.local hits=0 |
| 无 localhost/127.0.0.1 占位 | PASS | localhost+127 hits=0 |
| feed.atom 稳定 ID 本地/线上集合一致 | PASS | 本地=100 线上=100 交集=100 线上重复=0 |
| 6 个 Atom profile 均可解析且 ID 唯一 | PASS | /feed.atom:100/100 /all.atom:100/100 /high-signal.atom:100/100 /tech.atom:100/100 /invest.atom:65/65 /docs.atom:29/29 |
| 订阅地址指向公开站点 | PASS | feeds.json len=1073 placeholder=0 |

合计 10/10 通过，violations=0。

备注：workflow 首次触发即 success（20s），未复现 artifact 元数据最终一致性延迟。
Atom 计数用 entry 口径，ElementTree 按 local tag 解析（ns0: 前缀无影响）。
