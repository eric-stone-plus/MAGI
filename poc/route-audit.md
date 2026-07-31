# Route 审计清单(P0 → P2)

> 归档文件：这是 2026-07-31 的历史承载审计和未决清单，不是当前生产配置。
> `poc/policies/v2-draft/` 不符合当前 QUINTE policy 2.0 契约，不得运行。当前 MAGI
> 要求每席完整 QUINTE 七角色同族、`auto_primary_arbiter=true`，再由 MAGI 做六次
> 跨席 review 和最终 `PASS`/`BLOCK`/`ESCALATE` adjudication。

## §1 承载矩阵:route × 族

| route | 安装来源(已核) | 凭证宿主路径 | MiMo | DeepSeek | OpenAI 中转 |
| --- | --- | --- | --- | --- | --- |
| codewhale | npm `codewhale@0.9.2` | `~/.codewhale/config.toml` | 现役 | ❓自定义 provider 待验证 | ❓同左 |
| opencode | npm `opencode-ai@1.18.10` | `~/.local/share/opencode/auth.json` | 现役 | ✅ 高可行(自定义 provider/base_url) | ✅ 高可行 |
| kilo | npm `@kilocode/cli@7.4.17` | `~/.local/share/kilo/auth.json` | 现役 | ❓待验证 | ❓待验证 |
| mimo | npm `@mimo-ai/cli@0.1.9` | 三候选(见 §2) | 现役(仅 MiMo) | ❌ 不可跨族 | ❌ 不可跨族 |
| omp | npm `@oh-my-pi/pi-coding-agent@17.2.1` | `~/.omp/agent/`(`PI_CODING_AGENT_DIR`) | 现役 | ✅ pi-ai 多 provider | ✅ pi-ai 原生 OpenAI Completions/Responses |
| claude(cc) | npm `@anthropic-ai/claude-code@2.1.220` | `~/.claude/` | 现役(MiMo 后端,非 Anthropic 模型) | ❓ | ❓ |

结论:mimo CLI 只服务 MiMo;跨族席的 Party D lane 一律由 omp 顶替(v2-draft 已如此)。
codewhale/kilo 的跨族能力未验证 → 若不可行同样改 omp,roster 退化为
opencode + 多 omp lane(harness 扰动仍在,族纯度保住)。

## §2 凭证注入清单(compose 挂载 → 容器内路径)

| 宿主 | 容器 /cred | entrypoint 拷至 |
| --- | --- | --- |
| `~/.omp/agent/` | `/cred/omp-agent` | `~/.omp/agent/` |
| `~/.codewhale/config.toml` | `/cred/codewhale-config.toml` | `~/.codewhale/config.toml` |
| `~/.local/share/opencode/auth.json` | `/cred/opencode-auth.json` | 同左对应路径 |
| `~/.local/share/kilo/auth.json` | `/cred/kilo-auth.json` | 同左对应路径 |
| `~/.local/share/mimo/auth.json` | `/cred/mimo-share/` | 三候选之一(adapters.rs:1536-1542 顺序:share/mimo → share/mimocode → config/mimo) |
| `~/.local/share/mimocode/` | `/cred/mimocode/` | 同上 |
| `~/.config/mimo/` | `/cred/mimo-config/` | 同上 |
| `~/.claude/` | `/cred/claude` | `~/.claude/` |
| (Keychain) `xiaomi-mimo-token-plan-api-key` | 环境变量 `ANTHROPIC_API_KEY` | cc 仲裁 lane env |

⚠️ 挂载源不存在时 docker 会创建同名空目录 —— `compose up` 前先逐条核对。

⚠️ **cc 仲裁凭证特殊**:宿主走 macOS Keychain(service `xiaomi-mimo-token-plan-api-key`,
QUINTE `credential.rs` probe 顺序:protected store → `~/.claude/settings.json` env 块 →
`ANTHROPIC_API_KEY` env)。容器是 Linux,无 Keychain;宿主 settings.json 也无 env 块,
故**唯一路径是 env 注入**:`ANTHROPIC_API_KEY=$(security find-generic-password -s
"xiaomi-mimo-token-plan-api-key" -w) docker compose … up -d`(值只进进程环境,
不落盘、不进镜像;`docker inspect` 可见,P0 可接受,P1 换 apiKeyHelper 方案)。

## §3 席 G 中转(relay)

- 注入:`SEAT_G_RELAY_BASE_URL` / `SEAT_G_RELAY_API_KEY` 环境变量(compose 注释位),
  进 omp provider 配置;key 不进镜像、不进 git。
- **canary**(v2-draft/seat-g.policy.json `canary` 段):run 前发 3 个指纹探针——
  算术确定性题(验基本能力)、自报家门题(验声称身份)、可复现格式题(验指令遵循)。
  任一失配 → 该 run 标记 `family_unverified`,输出降级 advisory,不进收敛统计。
- 顺带验证:中转站常只兼容 OpenAI **Completions**;pi-ai 同时支持 Responses,
  canary 需确认实际命中的协议并固定之。
- 隐私:过中转 = 第三方经手 brief。含敏感 quant 数据的 brief 要么脱敏,要么
  该 trial 只用 M+D 两席,并在 trial_manifest 记录。

## §4 审计承载(quinte-audit 解耦后)

- `quinte-audit --auditor reasonix|omp`,默认取 env `QUINTE_AUDITOR`,再默认 reasonix
  (现状不变;reasonix 仅手动单独使用,不进任何自动化)。
- omp auditor 复用 QUINTE adapter 的已验证调用形态(`-p --mode text --thinking xhigh
  --no-session --no-skills …`,output TextJson),`--model` 透传,omit 时用 omp 默认模型。
- 交叉绑定:M←omp/deepseek-v4-pro、D←omp/mimo(MiMo provider 需先在 omp 配好,
  **验证项**)、G←omp/mimo。
- `--effort max`(reasonix)与 `--thinking xhigh`(omp)均为写死不降档,与现行纪律一致。

## §5 PA(Primary Arbiter)后端

- P0:宿主人工/kimi 经 `quinte primary-arbiter request/submit --home vol/state/<seat>`
  桥接,三席同一回答者 = 已声明污染 `pa_single_responder`。
- P1:容器内 PA-bot —— 用本席交叉绑族的模型自动回答 challenge
  (request → `quinte validate --kind verdict` → submit,失败重试一次再转人工)。

## §6 P2 QUINTE 补丁清单(Rust,另案评审)

1. `policy.rs`:接受 `policy_version: "2.0"`;roster/arbiter 允许 per-route
   `family`/`model` 字段与 omp/mimo 承载替换;`audit_binding`、`relay`、`canary`
   三个可选段;v1 文件行为逐字节不变。
2. run manifest 与 verdict 记录 `seat.family`/`seat.id`。
3. `cli.rs:489` 自动外审从 policy `audit_binding` 取 `--auditor/--model`(现状写死
   `quinte-audit <run-id>`,脚本默认 reasonix)。
4. `specs/PROTOCOL.md`/`CLI.md`:固定路由表改写为"族 + 席位"表述;v1
   "no substituting a route, changing the model" 段限定为 v1 scope;补 family 定义。
5. 测试:v1 兼容回归 + v2 新绑定校验 + canary 失配降级路径。
6. `quinte-insights`:残差按 family 分解,ρ̂_w/ρ̂_b 进 stats(P3 正式化)。

## §7 未决问题

- omp 的 DeepSeek/MiMo provider 名与配置方式(读 omp 文档定)。
- codewhale/kilo 自定义 base_url 能力。
- 中转站对 `gpt5.6-sol` 的实际路由模型与协议(Completions vs Responses)。
- 席 G 单 run token 成本实测(P0 数据)与月预算折算。
