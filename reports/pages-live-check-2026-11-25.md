# 线上验收 · 2026-11-25

站点 https://athronix.github.io/daily-info · commit `a947f22` · workflow `45505278765` success

## 14 个 URL

| path | status | content-type | bytes |
| --- | --- | --- | --- |
| / | 200 | text/html; charset=utf-8 | 26833 |
| /data/index.json | 200 | application/json; charset=utf-8 | 21863 |
| /data/latest.json | 200 | application/json; charset=utf-8 | 34567 |
| /data/feeds.json | 200 | application/json; charset=utf-8 | 1115 |
| /data/2026-11-25.json | 200 | application/json; charset=utf-8 | 34567 |
| /data/2026-11-24.json | 200 | application/json; charset=utf-8 | 36060 |
| /data/2026-11-21.json | 200 | application/json; charset=utf-8 | 36970 |
| /feed.json | 200 | application/json; charset=utf-8 | 239276 |
| /feed.atom | 200 | application/atom+xml | 245810 |
| /all.atom | 200 | application/atom+xml | 245810 |
| /high-signal.atom | 200 | application/atom+xml | 245823 |
| /tech.atom | 200 | application/atom+xml | 248324 |
| /invest.atom | 200 | application/atom+xml | 124316 |
| /docs.atom | 200 | application/atom+xml | 59647 |

## 检查项

| 检查项 | 结果 | 说明 |
| --- | --- | --- |
| 14 个 URL 全部 200 | PASS | 14/14 |
| 6 个 .atom = application/atom+xml | PASS | /feed.atom=application/atom+xml /all.atom=application/atom+xml /high-signal.atom=application/atom+xml /tech.atom=application/atom+xml /invest.atom=application/atom+xml /docs.atom=application/atom+xml |
| 2026-11-25.json 与本地等价 | PASS | date=2026-11-25 equal=True |
| index.json 最新为当日 | PASS | 2026-11-25 |
| latest.json 日期为当日 | PASS | 2026-11-25 |
| 占位域名残留 0 | PASS | https://daily-info.local hits=0 |
| 无 localhost/127.0.0.1 占位 | PASS | localhost+127 hits=0 |
| feed.atom 稳定 ID 本地/线上集合一致 | PASS | 本地=100 线上=100 交集=100 线上重复=0 |
| 6 个 Atom profile 均可解析且 ID 唯一 | PASS | /feed.atom:100/100 /all.atom:100/100 /high-signal.atom:100/100 /tech.atom:100/100 /invest.atom:55/55 /docs.atom:25/25 |
| 订阅地址指向公开站点 | PASS | feeds.json len=1073 placeholder=0 |

合计 10/10 通过，violations=0。

备注：首次 workflow run 45505278765 的 Deploy 步骤失败（Upload artifact 成功但 Deploy 查不到 artifact），
诊断 `gh api .../actions/runs/45505278765/artifacts` 返回 total_count=1、artifact ID 14972823146，
确认是 GitHub Actions artifact 元数据最终一致性延迟，不是产物或 commit 问题。
按既定处置保留已落盘 data/ 与已 push 的 commit，未清空重来、未改触发方式；
`gh run rerun 45505278765 --failed` 从失败步骤续跑后 Deploy 成功（13s）。
Atom 计数用 entry 口径，ElementTree 按 local tag 解析（ns0: 前缀无影响）。
