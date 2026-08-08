# AGENTS.md — MAGI 项目规则

> 全局规则见 `~/.agents/AGENTS.md`。恢复本项目工作前先读 `~/Documents/Private/agent-design/HANDOFF-LINUX-2026-08-01.md`。旧"重启条件"（codex/claude）已随 2026-07-31 新架构作废。

- 架构（2026-07-31 用户决策重建）：三席三族容器化嵌套——M=MiMo（不限量）、D=DeepSeek（不限量）、G=gpt5.6-sol（OpenAI 族，中转 API 0.52× 计费，canary 探针核身份）；每席独立 docker 容器内跑完整 QUINTE；仲裁交叉绑（M↔D、G←M，零成本跨族互查）。
- **MAGI 主席 = 确定性合并**（非模型，`poc/scripts/magi-merge`，复用 insights 的 CJK bigram + Jaccard 0.12 标定）；三方分歧不裁决、trace 呈人工终裁。外审交叉族走 omp（M←deepseek、D←mimo、G←mimo）；reasonix 仅手动单独使用，不进自动化。
- **用户永久排除 Anthropic**（含"接回真后端"分支全删）；**kimi k3 仅设计态**（kimi code 里定架构），不进运行态。
- 与 QUINTE 分工：MAGI 管生成、QUINTE 管评判；路由 = 新架构合成→MAGI，评审已有方案→QUINTE；QUINTE+MAGI 全局信号量同时最多 1 个 run（防 429）；质量链 MAGI→QUINTE→外审→人工，环节串联必须人工确认、不自动接力。
- PoC 落位 `poc/`：policies（v1 现役逐字节拷贝 + v2 三席草案）、Dockerfile+compose（凭证运行时只读挂载注入）、route-audit.md（承载矩阵/凭证清单/canary/P2 补丁清单）、trial-manifest 样例。运行态 `poc/vol/`（5GB 工件）只留磁盘已 gitignore；`vol/` 下 `input/` 等目录本来就是只读权限（dr-x------），属正常不是损坏。
- 状态：**P0 已收官**（`poc/reports/P0-2026-07-31.md`：三席 3/3 completed，m 12min/d ~13min/g 14min；标定 brief 的 5 个预埋缺陷全进 all-converged；ρ̂_w 基线 = 0.6754 mean pairwise Dice；unique 7/8 是中英文措辞假分歧，P1 修 matcher）。故障链 7 项全修（procps/codewhale 预热+钉 0.8.66/cc 凭证 env 注入/postinstall 分包/QUINTE `24ee25e` null warrant 修复/构建期 CLI 自检门）；另两条为协议设计内行为（kilo 自造字段永久失败、resume 不受理 failed 终态）。
- 待办：P1 = matcher 跨语言 + token 采集 + 容器内 PA-bot + 外审入镜像；P2 = 按 route-audit §P2 打 policy v2（QUINTE v1 校验器写死 roster/arbiter/model，`src/policy.rs:155-235`）后测 ρ̂_b。**判据事先写死：P2 后 ρ̂_b 显著 < ρ̂_w 则嵌套成立；降不动即任务侧 aleatoric、停止加机器。** σ 分解依据：残差 = ρσ²（族相关地板，Knight-Leveson 1986）+ (1−ρ)σ²/n；容器消上下文泄漏但压不掉 ρ，多样性预算必须花在模型族上。
