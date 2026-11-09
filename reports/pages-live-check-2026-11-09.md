# 2026-11-09 站点上线验收报告

- 验收时间：2026-11-09T03:22:52Z
- 公开地址：https://athronix.github.io/daily-info
- 发布方式：用户当次授权 → git push `main` → 手动触发 `pages.yml`（workflow_dispatch）
- workflow run：`42555858003`，conclusion = **success**（13s）
- 提交：`999f282`（含 11-08、11-09 两天站点/日报产物，34 文件）

## 一、URL 与 MIME

| 路径 | 状态 | Content-Type | 字节 |
|---|---|---|---|
| `/` | 200 | text/html | 26833 |
| `/data/index.json` | 200 | application/json | 6311 |
| `/data/latest.json` | 200 | application/json | 38841 |
| `/data/feeds.json` | 200 | application/json | 1112 |
| `/data/2026-11-09.json` | 200 | application/json | 38841 |
| `/data/2026-11-08.json` | 200 | application/json | 42274 |
| `/data/2026-11-07.json` | 200 | application/json | 29743 |
| `/feed.atom` | 200 | application/atom+xml | 227689 |
| `/feed.json` | 200 | application/json | 211322 |
| `/all.atom` | 200 | application/atom+xml | 227689 |
| `/high-signal.atom` | 200 | application/atom+xml | 206352 |
| `/tech.atom` | 200 | application/atom+xml | 147439 |
| `/invest.atom` | 200 | application/atom+xml | 52873 |
| `/docs.atom` | 200 | application/atom+xml | 16774 |

## 二、契约校验

| 检查项 | 结果 | 明细 |
|---|---|---|
| 14 个 URL 全部 200 | PASS | 14/14 |
| 6 个 .atom = application/atom+xml | PASS |  |
| 线上 2026-11-09.json 与本地内容等价 | PASS | date=2026-11-09 |
| index.json 以 2026-11-09 为最新 | PASS |  |
| latest.json 日期 = 2026-11-09 | PASS | 2026-11-09 |
| 占位域名残留 0 | PASS | old_base=https://daily-info.local hits=0 |
| 线上无 localhost / 127.0.0.1 占位 | PASS |  |
| feed.atom 稳定 ID 全保留 | PASS | 本地 101 / 线上 101 / 交集 101 |
| 订阅地址指向公开站点 | PASS |  |
| 6 个 Atom profile 均可解析 ID | PASS |  |

**合计 10/10，未通过 0 项。**

## 三、误报说明

首轮脚本用裸 `<id>` 正则统计 Atom 稳定 ID，本地与线上同时得到 0，判定为 FAIL。
根因：`build_feeds.py` 由 `xml.etree.ElementTree` 生成 Atom，标签统一带 `ns0:` 前缀
（`<ns0:id>` / `<ns0:entry>`）。属验收脚本口径错误，**不是站点缺陷**；改用命名空间无关正则后
本地与线上均为 101 个稳定 ID 且集合完全一致，此项 PASS。

## 四、资料库

6 份终态产物已上传（服务端默认目标，未虚构 folder id）：

| 文件 | 类型 | 节点 |
|---|---|---|
| digest-2026-11-09.md | doc | 6Ehz8UqQyOL8BrCb3xU88y |
| brief-2026-11-09.md | doc | cUo49i5r4gMs3cPVg5zamy |
| index-2026-11-09.html | page | p8iFBBwj2yoCISUH8PY430 |
| items-2026-11-09.csv | table | FlMcJaLIMLpKMBFJr4Su1H |
| no-number-2026-11-09.csv | table | jlRqFg8Z0gEoJteajZN1Fy |
| _manifest-2026-11-09.json | drive | gY9IIusppjcNN5aTgpRtBO |

## 五、未执行

- 邮件（未在本次授权范围）、企微（disabled）
- 未改动定时任务默认策略，未新增任何自动化

