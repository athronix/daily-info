**权限的账比参数先到期：会失败的闸门与可下载的数据，正成为 agent 工程的硬指标**

今天的读数分成两端：一端是 Claude Code 的 1,122 个公开 GitHub 文件暴露口令，以及被指控涉 $16B+ 非法资金流的加密交易所；另一端是 Ling-3.2-flash 把上下文拉到 1M token、Claude 把穹窿体提纯从 3 天压到 90 分钟。权限与规模的账，比模型能力更先到期。

2026-11-08 · 入报 18 条 · 信源 183/185

今日主线：
• 权限一旦被记住，代价落到公开仓库
• Agent 卡在编排，不在模型
• 十美元级硬件，卡的是状态不是单价
• 可核验性前移，比参数更值钱
• 先问分母，再信量级

重点条目（含关键数字与下一步动作）：
• [Ling-3.2-flash, 1M] Ant Group 发布 Ling-3.2-flash 多模态模型并支持 1M token 上下文，日刊同时记录 HEELO agents 的任务完成率改进
  → 跑一次长上下文对照：把当日 prompt-input.json 全文塞进单次调用，若关键 id 丢失数不为 0 即判定不可用。
  https://hex2077.dev/docs/2026-11/2026-11-07
• [Track 01] 开发者基于 Switch 搭建 SOC 值守 AI agents，投稿 Flip the Switch 黑客松 Track 01 最佳业务工作流赛道
  → 对照 github.com/manoj1698/soc-shift 仓库复现一次告警处置，若人工接管次数不为 0 就判定不可借鉴。
  https://dev.to/manoj1698/night-shift-without-the-night-ai-agents-that-keep-a-socs-watch-built-on-switch-go
• [6pm] 作者用单个 TOML 文件定义 Six Gates，让发布清单在跳过任一行时以非零码退出
  → 在本流水线补一条退出码断言：删掉任一检查项后若脚本仍返回 0，即判定闸门无效并回滚该改动。
  https://dev.to/rivera123/make-the-checklist-exit-nonzero-six-gates-one-toml-file-no-skipped-rows-568p
• [1,122] Claude Code 的 Don't Ask Again 选项被指与 1,122 个公开 GitHub 文件中的口令暴露相关
  → 在本仓库跑一次全量凭据扫描，若 public/ 与 data/ 中命中数大于 0 则整轮拒发并定位来源。
  https://apiiro.com/blog/coding-agents-leaking-secrets-github-dont-ask-again
• [$10] 作者公开其 $10 USD OpenStick homelab 上实际运行的服务清单
  → 若要在同价位设备部署常驻 agent，先跑 1 轮断网重启恢复测试，状态丢失超过 0 项即判定不可用。
  https://blog.bosscher.ch/posts/openstick
• [14 million] 文章指出地球上至少有 14 million 种昆虫，其维系生态的作用远超出作为食物
  → 对照原文给出的 14 million 与后续修订值，若差异超过 1 个数量级