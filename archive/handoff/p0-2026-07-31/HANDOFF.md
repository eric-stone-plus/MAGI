# MAGI × QUINTE P0 — codex 审查交接单

交接日期:2026-07-31 · 交接人:kimi(k3) · 审查人:codex

## 一句话

MAGI 三席容器化嵌套 QUINTE 的 P0 原型已端到端跑通(3/3 completed),同族基线
ρ̂_w=0.6754 已测出;途中抓到并修复一个 QUINTE 真实 bug(0.1.8 字段 serde 重序列化
null 污染,已修)和一个 audit 耦合(quinte-audit 已参数化)。请审查下列 commit 与产物。

## 审查对象(两个 GitHub 仓库,均已推送)

**`eric-stone-plus/QUINTE` main(本地 `~/Public/QUINTE`)**

- `24ee25e` — fix:optional claim 字段在 serde round-trip 后保持 schema 干净
  (model.rs 的 skip_serializing_if + adapters.rs 的 intake 归一化 + 2 个回归测试)。
  **重点审**:修复面是否完备(还有没有其他 Option 字段有同类风险)、归一化是否会
  误吞合法内容、与 0.1.9 故障分类学的一致性。
- `21677ff` — feat:quinte-audit 参数化 --auditor reasonix|omp(默认行为不变)。
  **重点审**:omp 调用参数是否与 src/adapters.rs 的 lane 调用一致、env 默认链
  (flag > QUINTE_AUDITOR > reasonix)是否破坏现有自动化。

**`eric-stone-plus/MAGI` main(本地 `~/Public/MAGI`)** — 全部新工作在 `poc/`:

- `poc/README.md` — P0 设计定稿与诚实栏(今天能跑什么、不能跑什么)
- `poc/container/{Dockerfile,compose.yml,entrypoint.sh}` — 镜像与编排
  **重点审**:凭证注入面(只读挂载+env)、构建期 CLI 自检门、entrypoint 的
  envelope 解析与 PA 等待环
- `poc/policies/` — v1 现役拷贝 + v2 三席草案(交叉仲裁/外审绑定、canary)
  **重点审**:v2 草案的族绑定逻辑,与 route-audit.md §P2 补丁清单的对应
- `poc/scripts/magi-merge` — 确定性合并器(无模型主席)
  **重点审**:聚类阈值(0.12)与语言敏感性(P0 报告显示 unique 7/8 是中英文
  措辞假分歧)
- `poc/route-audit.md` — §P2 的 QUINTE policy v2 补丁清单(下一步最大决策点)

## 运行证据

- P0 报告:`P0-2026-07-31.md`(判据-结论链、故障链 7 项、成本缺口)
- MAGI trace:`P0-2026-07-31-magi-trace.json`(25 簇,all=9/pair=8/unique=8)
- 三席 run 工件(哈希链完整)在 `~/Public/MAGI/poc/vol/state/<seat>/runs/`(未入 git)
- 三席 completed run id:m=`019fb6a1…` d=`019fb6f3…` g=`019fb6e1…`

## 关键判断(请重点挑战)

1. **P0 只证明机制,不证明跨族收益**——三席同族 MiMo,ρ̂_w=0.6754 只是基线;
   抬天花板要看 P2(QUINTE policy v2,族拆分)后 ρ̂_b 是否显著低于它。判据事先写死
   在报告 §判决标准,请审这个判据本身是否成立。
2. **"确定性合并代替模型主席"**——MAGI 协议原本就不是 aggregator,我们把 chair 也
   做成了无模型 diff/聚类。请审这是否过度解读了"chair 合成"。
3. **kilo R2 两次 schema 漂移**(null warrant、自造字段)——一次靠补丁,一次靠协议
   内永久失败+整轮重跑。请审"normalize vs fail-closed"的边界划得对不对。
4. **cc 凭证 env 注入**(ANTHROPIC_API_KEY 经 .env 进容器)——P0 权宜,请审是否
   必须在 P1 换 apiKeyHelper 形态。

## 不要审的

- `~/Public/QUINTE` 工作树里的 `skills/SKILL.md` 未提交改动 —— 用户的既有本地改动,
  与本次工作无关,交接时不要动它。
