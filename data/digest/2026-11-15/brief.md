**开源模型往单机挤、Agent 往任务图走，验证门禁与工程实测成了真正的分水岭**

LoopForge 以 694 stars 把 CodeBuddy、Codex、Claude Code 收进带人工审批门的脚本编排；GLM-5.3 在双 DGX 上跑到 607.8 tok/s，145B 参数模型被宣称可在本机运行。张力在于：能力与算力同时上量，2,539 个活密钥却因缺 .gitignore 被推上 GitHub——验证与门禁没跟上开放速度。

2026-11-15 · 入报 16 条 · 信源 183/185

今日主线：
• 参数越大，部署越往单机挤
• 编排权从对话移向可审批的图
• 开放提速，验证与门禁掉队
• 同一场回收，两条独立源互相校准
• 评测读数好看，能力边界仍硬

重点条目（含关键数字与下一步动作）：
• [★0] NBV-AppFactory 发布 transformer-mcp，把 transformer.gg 的 MCP server、CLI 与 agent skills 文档打包开源
  → 克隆仓库逐一核对 server、CLI、skills、docs 四个目录是否齐全，若任一缺失或 ★0 在 7 天后仍为 0 则判定为占位仓库、不纳入选型
  https://github.com/NBV-AppFactory/transformer-mcp
• [694, 114] 腾讯开源自托管 Go 仓库 LoopForge，用脚本编排 CodeBuddy、Codex、Claude Code 并保留人工审批门
  → 读其 workflow 脚本复现一次「提交→审批→执行」链路，若审批门可被脚本绕过或在 694 stars 的 issue 里有未修复绕过记录则判定不可直接借鉴
  https://github.com/Tencent/LoopForge
• [30] 姚期智与 Kimi 创始人杨植麟首次联合署名 arXiv 论文，标题称 30 道数学世界难题无一被 AI 独立攻破
  → 取该 arXiv 预印本核对题目是否确为 30 道并抽查 3 道题的判定规则，若题目数与 30 不符则判定标题口径夸大
  https://mp.weixin.qq.com/s?__biz=MzIzNjc1NzUzMw%3D%3D&mid=2247943908&idx=2&sn=79813e5c6542b53a1ac694e4b426ecf5&chksm=e95bad77f195631f5594129ced0192b85a793ea656b1d06ee8c6004f45f4bbb5686bf6696091&scene=0&xtrack=1
• [145B, 120B] Edge0 AI 开源 Edge0-145B 与 Edge0-120B 两款 latent-MoE 模型及统一推理栈，宣称可在个人电脑本地运行
  → 对照同批 209 tok/s 的本地基线跑一次对比，若 145B 在目标机器上 60 秒内出不来首 token 或需联网拉取未公开权重则判定不可本地部署
  https://dev.to/delimitter/edge0-ai-open-sources-edge0-145b-a-145-billion-parameter-latent-moe-model-that-runs-ai-on-your-own-1i4f
• [15] SpaceX 以「筷子」方式回收 Starship，为 Flight 15 收尾
  → 对照同事