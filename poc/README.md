# MAGI × QUINTE 嵌套 PoC(P0)

三席位容器化原型的第一刀：每席一个独立容器，席内跑一次完整 QUINTE,MAGI 层做确定性
收敛/分歧合并，残差以 MAGI residual trace 形态产出。

## 设计定稿(2026-07-31，约束已全部闭环)

- **三席三族**：席 M = MiMo(不限量)、席 D = DeepSeek(不限量)、席 G = gpt5.6-sol
  (OpenAI 族，中转 API,0.52× 计费)。
- 席内完整 QUINTE(R1 五 lane → R2 匿名互审 → R3 双仲裁 → deterministic merge)。
- **仲裁交叉绑**：席 M 仲裁走 DeepSeek、席 D 仲裁走 MiMo、席 G 仲裁走 MiMo——
  零成本的跨族互查。
- **MAGI 主席 = 确定性合并**(scripts/magi-merge),不是模型。三方收敛直出；
  三方分歧不裁决，trace 呈人工终裁。收敛是信号不是证明，分歧必须保留。
- **外审交叉族**:M←DeepSeek、D←MiMo、G←MiMo;`reasonix` 不进自动化，留给单独使用。
- 无 Anthropic 模型（claude CLI 仅以 MiMo 后端身份出现，与现状一致）;
  kimi k3 仅设计态，不进运行态。

## 硬约束：今天能跑什么(诚实栏)

QUINTE v1 的运行期校验把 roster、Counterpart Arbiter、text/multimodal model 全部写死
(`QUINTE/src/policy.rs:155-235`,validate_with_options)。因此:

- `policies/v1-current/seat-m.policy.json` 是**今天唯一过校验**的 policy(现役
  `~/.quinte/policy.json` 的逐字节拷贝，三席容器 P0 阶段共用)。
- `policies/v2-draft/` 三份是**设计草案**,需要 route-audit.md §P2 列出的 QUINTE
  补丁落地后才能加载。
- **P0 的实际产出**：三个同族 MiMo 席，验证容器化、凭证注入、工件收集、PA 桥、
  确定性合并、残差重合度测量这条完整管线，并测出**同族基线 ρ̂_w**(三席同族时
  残差重合的上界)。P0 不产出任何跨族结论。
- P2 补丁落地后换挂 v2 policy，同一套容器/管线直接测 ρ̂_b（族间）。判据事先约定：
  **ρ̂_b 显著 < ρ̂_w 则嵌套成立；降不动则残差是任务侧 aleatoric，停止加机器。**

## 目录

```
poc/
  README.md                       本文件
  policies/
    v1-current/seat-m.policy.json 现役 v1 policy 拷贝(三席 P0 共用)
    v2-draft/seat-m.policy.json   草案:MiMo 席(仲裁→DeepSeek,外审←DeepSeek)
    v2-draft/seat-d.policy.json   草案:DeepSeek 席(仲裁→MiMo,外审←MiMo)
    v2-draft/seat-g.policy.json   草案:GPT 中转席(仲裁→MiMo,canary,外审←MiMo)
  container/
    Dockerfile                    一体化镜像:quinte 源码构建 + 五个 harness CLI
    compose.yml                   三服务,每席独立 state/artifacts/凭证挂载
    entrypoint.sh                 容器入口:seed 凭证与 state → run → PA handoff 等待
  scripts/
    magi-merge                    确定性合并:三份 result.json → MAGI residual trace
  route-audit.md                  承载矩阵 / 凭证清单 / canary / P2 补丁清单
  trial-manifest.example.json     P0 trial 的 manifest 样例(含污染声明)
```

## 快速开始

```bash
cd poc

# 0) 准备 brief(QUINTE brief v1.1 JSON)
cp /path/to/brief.json vol/brief/brief.json

# 1) 构建并启动三席(凭证从宿主只读挂载,见 compose.yml)
docker compose -f container/compose.yml build
docker compose -f container/compose.yml up -d

# 2) 等待 PA handoff:某席 /artifacts 出现 PA_HANDOFF 后,做 PA 桥(每席一次)
#    run manifest 绑定容器内 executable digest,宿主二进制跨平台 submit 会
#    fail-closed —— 协议操作一律在席容器内执行;verdict 经 artifacts 卷共享。
RUN_ID=$(cat vol/artifacts/seat-m/PA_HANDOFF)
docker compose -f container/compose.yml exec seat-m \
  quinte primary-arbiter request "$RUN_ID" --json > vol/artifacts/seat-m/pa-challenge.json
#    …宿主侧(kimi/人工)读 challenge、写 verdict…
docker compose -f container/compose.yml exec seat-m \
  quinte validate --kind verdict /artifacts/verdict.json
docker compose -f container/compose.yml exec seat-m \
  quinte primary-arbiter submit "$RUN_ID" --verdict /artifacts/verdict.json

# 3) 三席 SEAT_DONE 后合并
poc/scripts/magi-merge \
  --label seat-m=vol/state/seat-m/runs/<run-id-m> \
  --label seat-d=vol/state/seat-d/runs/<run-id-d> \
  --label seat-g=vol/state/seat-g/runs/<run-id-g> \
  --risk same_family_all_seats --risk pa_single_responder \
  --out vol/artifacts/magi-trace.json
```

注意:三席各自独立 run,run-id 不同;P0 阶段三席 PA 都由宿主同一回答者完成,
这是已声明污染(pa_single_responder),不是独立意见。

## 判决标准(写死在跑之前)

1. **机制**:三席容器端到端完成率 ≥ 2/3,工件齐全(result.json + manifest + hash chain)。
2. **基线**:magi-merge 给出 pairwise 残差 Jaccard 重合率 = ρ̂_w 的代理量。
3. **成本**:记录每席单 run 的 wall time 与 token 用量;席 G(v2 启用后)按月 run 量
   ×0.52 折算预算，超预算则 G 席降 3-lane lean mode。
4. **P2 复测**:同 brief 重复 run,ρ̂_b(族间)显著低于 ρ̂_w 则继续投 P3;
   否则结论 = 天花板在任务侧，保留 P0 管线但不再加机器。

## 已知污染(P0 trial_manifest contamination_risks 原文)

- `same_family_all_seats` — P0 三席全是 MiMo 族，只测机制与基线。
- `pa_single_responder` — R3 Primary Arbiter 由宿主同一回答者完成。
- `cc_same_family_as_lanes` — Counterpart Arbiter(claude CLI)后端是 MiMo token plan。
- `shared_evidence_snapshot` — 三席读同一份 brief/snapshot。
- `relay_model_identity_unverified` — (P2 席 G 启用后）中转站模型身份未经 canary
  核验前，席 G 输出一律降级为 advisory。

## 后续衔接

- **P1**:MAGI 薄编排器(投送/收集/manifest 自动化)、容器内 PA-bot(仲裁族自动作答)、
  egress 硬隔离(白名单代理)。
- **P2**:QUINTE policy v2 补丁(route-audit.md §P2),换挂 v2-draft policies,测 ρ̂_b。
- **P3**:quinte-insights 按族分解残差，ρ̂ 进 residual KB 成为持续监测量。
