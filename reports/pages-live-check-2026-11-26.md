# 线上验收 · 2026-11-26

站点 https://athronix.github.io/daily-info · commit `4ab151b` · workflow `45720068507` success

## 14 个 URL

| path | status | content-type | bytes |
| --- | --- | --- | --- |
| / | 200 | text/html; charset=utf-8 | 26833 |
| /data/index.json | 200 | application/json; charset=utf-8 | 23016 |
| /data/latest.json | 200 | application/json; charset=utf-8 | 25723 |
| /data/feeds.json | 200 | application/json; charset=utf-8 | 1115 |
| /data/2026-11-26.json | 200 | application/json; charset=utf-8 | 25723 |
| /data/2026-11-25.json | 200 | application/json; charset=utf-8 | 34567 |
| /data/2026-11-24.json | 200 | application/json; charset=utf-8 | 36060 |
| /feed.json | 200 | application/json; charset=utf-8 | 240607 |
| /feed.atom | 200 | application/atom+xml | 248121 |
| /all.atom | 200 | application/atom+xml | 248121 |
| /high-signal.atom | 200 | application/atom+xml | 248134 |
| /tech.atom | 200 | application/atom+xml | 248199 |
| /invest.atom | 200 | application/atom+xml | 136833 |
| /docs.atom | 200 | application/atom+xml | 62101 |

## 检查项

| 检查项 | 结果 | 说明 |
| --- | --- | --- |
| 14 个 URL 全部 200 | PASS | 14/14 |
| 6 个 .atom = application/atom+xml | PASS | /feed.atom=application/atom+xml /all.atom=application/atom+xml /high-signal.atom=application/atom+xml /tech.atom=application/atom+xml /invest.atom=application/atom+xml /docs.atom=application/atom+xml |
| 2026-11-26.json 与本地等价 | PASS | date=2026-11-26 equal=True |
| index.json 最新为当日 | PASS | 2026-11-26 |
| latest.json 日期为当日 | PASS | 2026-11-26 |
| 占位域名残留 0 | PASS | https://daily-info.local hits=0 |
| 无 localhost/127.0.0.1 占位 | PASS | localhost+127 hits=0 |
| feed.atom 稳定 ID 本地/线上集合一致 | PASS | 本地=100 线上=100 交集=100 线上重复=0 |
| 6 个 Atom profile 均可解析且 ID 唯一 | PASS | /feed.atom:100/100 /all.atom:100/100 /high-signal.atom:100/100 /tech.atom:100/100 /invest.atom:60/60 /docs.atom:26/26 |
| 订阅地址指向公开站点 | PASS | feeds.json len=1073 placeholder=0 |

合计 10/10 通过，violations=0。

备注：首次 workflow run 45720068507 的 Deploy 步骤失败（Upload artifact 成功但 Deploy 查不到 artifact），
诊断 `gh api .../actions/runs/45720068507/artifacts` 返回 total_count=1、artifact ID 15071532390
（585885 bytes / expired=false），确认是 GitHub Actions artifact 元数据最终一致性延迟，不是产物或 commit 问题。
按既定处置保留已落盘 data/ 与已 push 的 commit，未清空重来、未改触发方式；
`gh run rerun 45720068507 --failed` 从失败步骤续跑后 Deploy 成功（15s）。
Atom 计数用 entry 口径，ElementTree 按 local tag 解析（ns0: 前缀无影响）。
