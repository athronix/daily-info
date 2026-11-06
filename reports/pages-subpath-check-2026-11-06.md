# GitHub Pages 子路径部署 · 本地端到端验收

> 2026-11-06 · 在 `::1` 起 HTTP 服务，把 `pages-dist/` 挂到 `/pages-dist/` 前缀，
> 模拟 `https://<owner>.github.io/<repo>/` 项目站点；urllib 显式禁用代理。
> 只做本地验证，未访问网络、未推送、未发布。

**结果：14/14 通过**

| # | 检查项 | 结果 | 说明 |
| --- | --- | --- | --- |
| 1 | 子路径首屏 index.html | PASS | HTTP 200 text/html |
| 2 | 子路径 data/index.json | PASS | HTTP 200 |
| 3 | 日期切片 2026-11-05 | PASS | HTTP 200 |
| 4 | 日期切片 2026-11-04 | PASS | HTTP 200 |
| 5 | Atom all.atom | PASS | HTTP 200 application/octet-stream |
| 6 | Atom high-signal.atom | PASS | HTTP 200 application/octet-stream |
| 7 | Atom tech.atom | PASS | HTTP 200 application/octet-stream |
| 8 | Atom invest.atom | PASS | HTTP 200 application/octet-stream |
| 9 | Atom docs.atom | PASS | HTTP 200 application/octet-stream |
| 10 | JSON Feed | PASS | HTTP 200 |
| 11 | .nojekyll 可访问 | PASS | HTTP 200 |
| 12 | feeds.json 公开地址 | PASS | https://athronix.github.io/daily-info |
| 13 | Atom 稳定 ID 未变 | PASS |  |
| 14 | 占位域名零残留 | PASS |  |

## 结论

- 站点前端 `index.html` 与 `data/index.json` 全用相对路径，子路径部署无需改代码。
- 6 个 Atom + JSON Feed 在子路径下均可解析；`.nojekyll` 正常。
- `prepare_pages.py` 已把 self / alternate / feed_url 换成真实公开地址，
  `tag:daily-info.local,...` 稳定 ID 原样保留，不会导致阅读器重复收录。
- 本地 HTTP 的 Content-Type 由 Python http.server 决定；GitHub Pages 的 `.atom`
  MIME 由其自身映射，上线后需再用 curl -I 复核一次。
