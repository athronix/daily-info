# 线上验收 · 2026-11-24

站点 https://athronix.github.io/daily-info · commit `7fcbb4a` · workflow `45309407390` success

## 14 个 URL

| path | status | content-type | bytes |
| --- | --- | --- | --- |
| / | 200 | text/html; charset=utf-8 | 26833 |
| /data/index.json | 200 | application/json; charset=utf-8 | 20580 |
| /data/latest.json | 200 | application/json; charset=utf-8 | 36060 |
| /data/feeds.json | 200 | application/json; charset=utf-8 | 1115 |
| /data/2026-11-24.json | 200 | application/json; charset=utf-8 | 36060 |
| /data/2026-11-21.json | 200 | application/json; charset=utf-8 | 36970 |
| /data/2026-11-20.json | 200 | application/json; charset=utf-8 | 38510 |
| /feed.json | 200 | application/json; charset=utf-8 | 240182 |
| /feed.atom | 200 | application/atom+xml | 247342 |
| /all.atom | 200 | application/atom+xml | 247342 |
| /high-signal.atom | 200 | application/atom+xml | 247355 |
| /tech.atom | 200 | application/atom+xml | 249394 |
| /invest.atom | 200 | application/atom+xml | 114842 |
| /docs.atom | 200 | application/atom+xml | 57087 |

## 检查项

| 检查项 | 结果 | 说明 |
| --- | --- | --- |
| 14 个 URL 全部 200 | PASS | 14/14 |
| 6 个 .atom = application/atom+xml | PASS | /feed.atom=application/atom+xml /all.atom=application/atom+xml /high-signal.atom=application/atom+xml /tech.atom=application/atom+xml /invest.atom=application/atom+xml /docs.atom=application/atom+xml |
| 2026-11-24.json 与本地等价 | PASS | date=2026-11-24 equal=True |
| index.json 最新为当日 | PASS | 2026-11-24 |
| latest.json 日期为当日 | PASS | 2026-11-24 |
| 占位域名残留 0 | PASS | https://daily-info.local hits=0 |
| 无 localhost/127.0.0.1 占位 | PASS | localhost+127 hits=0 |
| feed.atom 稳定 ID 本地/线上集合一致 | PASS | 本地=100 线上=100 交集=100 线上重复=0 |
| 6 个 Atom profile 均可解析且 ID 唯一 | PASS | /feed.atom:100/100 /all.atom:100/100 /high-signal.atom:100/100 /tech.atom:100/100 /invest.atom:51/51 /docs.atom:24/24 |
| 订阅地址指向公开站点 | PASS | feeds.json len=1073 placeholder=0 |

合计 10/10 通过，violations=0。

备注：run 45309305618 与 45309407390 首次执行均为 GitHub Actions artifact 服务瞬时不一致，
Deploy 查不到刚上传的 artifact（Upload 步骤 success，API 可查到 ID 14881564850）。
按既定处置保留已落盘 data/ 与已 push 的 commit，未清空重来、未改触发方式；
`gh run rerun 45309407390 --failed` 从失败步骤续跑后 success（20s）。
Atom 计数用 entry 口径，ElementTree 按 local tag 解析（ns0: 前缀无影响）。
