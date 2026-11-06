# 站点端到端验收 · 2026-11-05

绑定 `http://[::1]:51354`（IPv6 回环 + 禁用代理），共 18 项检查，通过 18，失败 0，提示 6。

| 检查 | 结论 | 明细 |
| --- | --- | --- |
| 首屏 / | PASS | status=200 type=text/html bytes=16490 |
| 前端能力 · 搜索框 #q | PASS | 源码含 'id="q"' |
| 前端能力 · 搜索 input 监听 | PASS | 源码含 "addEventListener('input'" |
| 前端能力 · 搜索过滤 state.q | PASS | 源码含 'state.q' |
| 前端能力 · 日期切换 dates | PASS | 源码含 'state.index.dates' |
| 前端能力 · 读取 index.json | PASS | 源码含 'data/index.json' |
| 前端能力 · 按日期加载切片 | PASS | 源码含 "data/'+date+'.json'" |
| /data/index.json | PASS | status=200 dates=2 feeds=5 |
| 索引含当日 | PASS | dates=['2026-11-05', '2026-11-04'] |
| /data/latest.json | PASS | status=200 date=2026-11-05 |
| /data/2026-11-05.json | PASS | status=200 date=2026-11-05 sections=9 |
| /feed.atom | PASS | status=200 entries=58 unique=58 type=application/octet-stream |
| /all.atom | PASS | status=200 entries=58 unique=58 type=application/octet-stream |
| /high-signal.atom | PASS | status=200 entries=44 unique=44 type=application/octet-stream |
| /tech.atom | PASS | status=200 entries=34 unique=34 type=application/octet-stream |
| /invest.atom | PASS | status=200 entries=16 unique=16 type=application/octet-stream |
| /docs.atom | PASS | status=200 entries=1 unique=1 type=application/octet-stream |
| /feed.json | PASS | status=200 items=58 version=https://jsonfeed.org/version/1.1 |

## 已知事项（不判失败）

- /feed.atom MIME（P17 已知事项）：本地 http.server 返回 application/octet-stream；上线时需配 application/atom+xml
- /all.atom MIME（P17 已知事项）：本地 http.server 返回 application/octet-stream；上线时需配 application/atom+xml
- /high-signal.atom MIME（P17 已知事项）：本地 http.server 返回 application/octet-stream；上线时需配 application/atom+xml
- /tech.atom MIME（P17 已知事项）：本地 http.server 返回 application/octet-stream；上线时需配 application/atom+xml
- /invest.atom MIME（P17 已知事项）：本地 http.server 返回 application/octet-stream；上线时需配 application/atom+xml
- /docs.atom MIME（P17 已知事项）：本地 http.server 返回 application/octet-stream；上线时需配 application/atom+xml

> 本检查只验证本地静态站可访问与数据切片自洽，不代表站点已上线、也不代表外部事实已核实。上线动作需用户授权后执行。
