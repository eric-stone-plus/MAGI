# Archived MAGI x QUINTE PoC (P0)

> Archive notice: this tree preserves the 2026-07-31 same-family smoke-test
> evidence. It is not the active MAGI runtime, contract, policy, or operating
> guide. Use the repository-root `bin/magi`, `specs/PROTOCOL.md`, and
> `docs/runtime.md`. Do not use `poc/scripts/magi-merge` to produce a current
> MAGI product.

三席位容器化原型的第一刀：每席一个独立容器，席内跑一次完整 QUINTE,MAGI 层做确定性
收敛/分歧合并，残差以 MAGI residual trace 形态产出。

## Historical design snapshot (2026-07-31)

- **三席三族**：席 M = MiMo(不限量)、席 D = DeepSeek(不限量)、席 G = gpt5.6-sol
  (OpenAI 族，中转 API,0.52× 计费)。
- 席内完整 QUINTE(R1 五 lane → R2 匿名互审 → R3 双仲裁 → deterministic merge)。
- **仲裁交叉绑**：席 M 仲裁走 DeepSeek、席 D 仲裁走 MiMo、席 G 仲裁走 MiMo——
  零成本的跨族互查。
- 当时的原型用 `scripts/magi-merge` 做确定性聚类。生产 MAGI 已改为 Final
  Adjudicator 产出 `PASS`/`BLOCK`/`ESCALATE`，再由确定性 verifier 验证覆盖、证据、
  closure 与 dissent；旧 merge 结果不是当前 Product Summary。
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
- **P0 的实际产出**：三个同族 MiMo 席，验证当时的容器、凭证、工件、人工 PA 桥和
  聚类脚本。`0.6754` 只是单个 brief、单次三席运行、特定词法 matcher 下的描述性
  pairwise Dice，不是统计相关系数、置信度、上界或可推广的 `ρ̂_w` 估计。
- 该单次观测不能区分任务不确定性、模型相关误差、提示/语言效应或实现方差，也不能
  支撑“降不动即 aleatoric”或停止扩展的因果结论。跨族效果必须另做预注册、多次重复、
  顺序无关且人工核销的评估；它不属于生产运行时判决。

## 目录

```
poc/
  README.md                       本文件
  policies/
    v1-current/seat-m.policy.json 历史 v1 policy 拷贝(三席 P0 共用)
    v2-draft/seat-m.policy.json   废弃草案，不是生产 policy
    v2-draft/seat-d.policy.json   废弃草案，不是生产 policy
    v2-draft/seat-g.policy.json   废弃草案，不是生产 policy
  container/
    Dockerfile                    一体化镜像:quinte 源码构建 + 五个 harness CLI
    compose.yml                   三服务,每席独立 state/artifacts/凭证挂载
    entrypoint.sh                 容器入口:seed 凭证与 state → run → PA handoff 等待
  scripts/
    magi-merge                    确定性合并:三份 result.json → MAGI residual trace
  route-audit.md                  承载矩阵 / 凭证清单 / canary / P2 补丁清单
  trial-manifest.example.json     P0 trial 的 manifest 样例(含污染声明)
```

## Historical reproduction only

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

## Historical criteria (not production gates)

1. **机制**:三席容器端到端完成率 ≥ 2/3,工件齐全(result.json + manifest + hash chain)。
2. **描述量**:`magi-merge` 给出词法匹配后的 pairwise Dice；不得把它称为 Jaccard、
   相关系数、置信度或统计基线。
3. **成本**:记录每席单 run 的 wall time 与 token 用量;席 G(v2 启用后)按月 run 量
   ×0.52 折算预算，超预算则 G 席降 3-lane lean mode。
4. 任何后续跨族比较都需独立评估设计；本 P0 判据不足以证明嵌套收益或任务侧天花板。

## 已知污染(P0 trial_manifest contamination_risks 原文)

- `same_family_all_seats` — P0 三席全是 MiMo 族，只测机制和单次描述量。
- `pa_single_responder` — R3 Primary Arbiter 由宿主同一回答者完成。
- `cc_same_family_as_lanes` — Counterpart Arbiter(claude CLI)后端是 MiMo token plan。
- `shared_evidence_snapshot` — 三席读同一份 brief/snapshot。
- `relay_model_identity_unverified` — (P2 席 G 启用后）中转站模型身份未经 canary
  核验前，席 G 输出一律降级为 advisory。

## Historical follow-up list

- **P1**:MAGI 薄编排器(投送/收集/manifest 自动化)、容器内 PA-bot(仲裁族自动作答)、
  egress 硬隔离(白名单代理)。
- 这些 P1/P2/P3 项保留为历史设计记录，不是当前 roadmap；生产 policy 与 runtime 以
  根目录文档和 QUINTE 当前契约为准。
