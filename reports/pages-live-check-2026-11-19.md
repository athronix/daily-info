# 2026-11-19 站点上线验收报告

- 公开地址：https://athronix.github.io/daily-info
- 发布方式：定时任务默认授权 → git push main → 手动触发 pages.yml（workflow_dispatch）
- workflow run：44417343422，conclusion = success（16s，首次触发即成功）
- 提交：af76feb

## 一、URL 与 MIME

| 路径 | 状态 | Content-Type | 字节 |
|---|---|---|---|
| / | 200 | text/html; charset=utf-8 | 26833 |
| /data/index.json | 200 | application/json; charset=utf-8 | 16989 |
| /data/latest.json | 200 | application/json; charset=utf-8 | 31268 |
| /data/feeds.json | 200 | application/json; charset=utf-8 | 1115 |
| /data/2026-11-19.json | 200 | application/json; charset=utf-8 | 31268 |
| /data/2026-11-18.json | 200 | application/json; charset=utf-8 | 28637 |
| /data/2026-11-17.json | 200 | application/json; charset=utf-8 | 37176 |
| /feed.json | 200 | application/json; charset=utf-8 | 232871 |
| /feed.atom | 200 | application/atom+xml | 241777 |
| /all.atom | 200 | application/atom+xml | 241777 |
| /high-signal.atom | 200 | application/atom+xml | 241790 |
| /tech.atom | 200 | application/atom+xml | 244357 |
| /invest.atom | 200 | application/atom+xml | 95188 |
| /docs.atom | 200 | application/atom+xml | 45372 |

## 二、契约校验

| 检查项 | 结果 | 明细 |
| --- | --- | --- |
| 14 个 URL 全部 200 | PASS | 14/14 |
| 6 个 .atom = application/atom+xml | PASS | /feed.atom=application/atom+xml /all.atom=application/atom+xml /high-signal.atom=application/atom+xml /tech.atom=application/atom+xml /invest.atom=application/atom+xml /docs.atom=application/atom+xml |
| 2026-11-19.json 与本地等价 | PASS | date=2026-11-19 equal=True |
| index.json 最新为当日 | PASS | 2026-11-19 |
| latest.json 日期为当日 | PASS | 2026-11-19 |
| 占位域名残留 0 | PASS | https://daily-info.local hits=0 |
| 无 localhost/127.0.0.1 占位 | PASS | localhost+127 hits=0 |
| feed.atom 稳定 ID 本地/线上集合一致 | PASS | 本地=100 线上=100 交集=100 线上重复=0 |
| 6 个 Atom profile 均可解析且 ID 唯一 | PASS | /feed.atom:100/100 /all.atom:100/100 /high-signal.atom:100/100 /tech.atom:100/100 /invest.atom:43/43 /docs.atom:19/19 |
| 订阅地址指向公开站点 | PASS | feeds.json len=1115 placeholder=0 |

**合计 10/10，未通过 0 项。**

## 三、口径说明

Atom 稳定 ID 一律用 xml.etree.ElementTree 按 local tag 解析（只取 entry 下的 id），
规避 build_feeds.py 生成的 ns0: 前缀导致裸 id 正则误判为 0 的历史坑。
