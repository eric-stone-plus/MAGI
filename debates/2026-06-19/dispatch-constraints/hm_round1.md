# HM R1 — 派遣约束协议化

## 5 失败 → 5 约束

| # | 约束 | 位置 |
|---|------|------|
| 1 | R1 文件写后 `chmod 644` | SKILL Pre-R1 已有 |
| 2 | R2 派遣用嵌入内容（≤500 chars），不给文件路径 | SKILL 需新增 |
| 3 | cc 不用 `--output-format stream-json`，用纯文本 `> file 2>&1` | SKILL 需修正 |
| 4 | delegate_task 禁用于 QUINTE/MAGI | SOUL 已有 + SKILL 已有 |
| 5 | 全量 QUINTE 用 terminal CLI，永不用 delegate_task | SOUL 已有 |

## 待写入

**SKILL.md Pre-R1 新增**：
- 约束 2: "R2 cc/cw prompt 用内嵌 R1 摘要（≤500 chars），不给 /tmp/ 文件路径。cw 沙箱无法访问 /tmp/。"
- 约束 3: "cc 输出用纯文本重定向（`> file 2>&1`），不用 `--output-format stream-json`。stream-json 产生不可读的 token 事件流。"

## 置信度

HIGH — 全部 5 个失败模式在本 session 有直接观测。
