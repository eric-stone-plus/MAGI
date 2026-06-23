# Gold Verdict — Dispatch Failure → Protocol Constraints

## SOUL Constraints (3) — 永久协议，不可绕过

| # | 失败 | 约束 | 理由 |
|---|------|------|------|
| 2 | 沙箱 /tmp/ 不可达 | **SOUL-AGENT-SCOPE**: 子 agent 工作目录必须在项目根下；禁止依赖宿主机临时路径。 | 沙箱隔离是运行时不可变事实，属于 agent 架构级约束。 |
| 4 | delegate_task 假异构 | **SOUL-DELEGATE-INHERIT**: delegate_task 子 agent 继承父 provider；真异构必须用 terminal CLI 调独立进程。 | provider 继承是框架级行为，无法在 SKILL 层修正。 |
| 5 | 用户消息中断子 agent | **SOUL-INTERRUPT-ISOLATION**: delegate_task 无中断隔离；长任务必须用 run_in_background 或独立 CLI 进程。 | 并发消息路由是协议级限制，非战术可修。 |

## SKILL Constraints (2) — 可由 SKILL 指令层修复

| # | 失败 | 约束 | 理由 |
|---|------|------|------|
| 1 | chmod 600 权限 | **SKILL-PRE-R1-CHMOD**: write_file 产出后必须 `chmod 644`；已嵌入 Pre-R1 checklist。 | 文件权限是可执行步骤，已在 SKILL 层验证生效。 |
| 3 | stream-json 噪音 | **SKILL-CLI-FORMAT**: cc/cw 调用禁止 `--output-format stream-json`；使用 `text` 或嵌入内容。 | CLI flag 选择是调用约定，属 SKILL 指令范围。 |

## 裁决摘要

五项派遣失败中，沙箱边界、provider 继承、中断隔离三项属 SOUL 级协议约束——它们对应运行时不可变的架构事实，必须永久写入协议层；文件权限和 CLI 输出格式两项属 SKILL 级约束——它们通过可执行的 checklist 和调用约定即可修复，已在今日验证中生效。分类依据是约束的可绕过性：SOUL 层约束无论何种 SKILL 策略均无法突破，SKILL 层约束可通过正确指令序列规避。置信度 **HIGH**——五项失败均有至少一次完整复现验证，修复已通过实际派遣确认。

## Confidence: HIGH

依据：5/5 失败均有实际复现记录，3/3 修复已在今日派遣中验证生效。
