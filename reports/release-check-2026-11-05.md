# 站点端到端验收 · 2026-11-05

绑定 `http://[::1]:54173`（IPv6 回环 + 禁用代理），共 34 项检查，通过 34，失败 0，提示 6。

| 检查 | 结论 | 明细 |
| --- | --- | --- |
| 首屏 / | PASS | status=200 type=text/html bytes=26833 |
| 前端能力 · 搜索框 #q | PASS | 源码含 'id="q"' |
| 前端能力 · 搜索 input 监听 | PASS | 源码含 "addEventListener('input'" |
| 前端能力 · 搜索过滤 state.q | PASS | 源码含 'state.q' |
| 前端能力 · 日期切换 dates | PASS | 源码含 'state.index.dates' |
| 前端能力 · 读取 index.json | PASS | 源码含 'data/index.json' |
| 前端能力 · 按日期加载切片 | PASS | 源码含 "data/'+date+'.json'" |
| 前端能力 · 日期导航 #days | PASS | 源码含 'id="days"' |
| 前端能力 · 分类导航 #cats | PASS | 源码含 'id="cats"' |
| 前端能力 · 分类筛选 state.cat | PASS | 源码含 'state.cat' |
| 前端能力 · 默认打开最新日期 | PASS | 源码含 'idx.dates[0].date' |
| 前端能力 · 双维度 URL hash | PASS | 源码含 'writeHash' |
| 前端能力 · 订阅引导面板 | PASS | 源码含 'id="sub-modal"' |
| 前端能力 · 订阅按钮是 button | PASS | 源码含 'id="subscribe" type="button"' |
| 前端能力 · 订阅地址绝对化 | PASS | 源码含 'new URL(u,location.href)' |
| 前端能力 · 一键复制订阅地址 | PASS | 源码含 'class="copy"' |
| 前端能力 · 订阅入口不再直跳 .atom | PASS | 顶栏无 <a class=btn href=feed.atom> 直链 |
| 前端能力 · 保留阅读器自动发现 | PASS | head 内 rel=alternate 仍在 |
| 前端能力 · 默认深色主题 | PASS | html 根元素带 data-theme=dark，首帧即深色无闪白 |
| 前端能力 · 主题偏好可记忆 | PASS | 用户显式切换后写入 localStorage，刷新不回弹 |
| 前端能力 · 深色配色无绿偏 | PASS | green-dominant = [] |
| 前端能力 · 浅色配色无绿偏 | PASS | green-dominant = [] |
| 前端能力 · 阴影/遮罩无绿偏 | PASS | green-dominant in full css = [] |
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
