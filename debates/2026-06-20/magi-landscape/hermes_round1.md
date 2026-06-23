# Hermes R1 — MAGI Landscape Analysis Verification

## Task
Verify the completeness and accuracy of magi-landscape-analysis.md: Are all relevant GitHub MAGI projects captured? Are the classifications and comparisons accurate? Any blind spots?

## 1. 搜集完整性

### 已覆盖项目（15个）

**学术论文级**：
1. co-evolve-lab/magis — NeurIPS 2024, GitHub Issue resolution, 4 agents
2. Skytliang/Multi-Agents-Debate (MAD) — 2023, first LLM debate framework
3. MAGI-CORE / MAgICoRe — EMNLP 2025, coarse-to-fine reasoning, 7 datasets
4. MAGI psychiatric — ACL 2025 Findings, MINI interview

**工程产品级**：
5. fshiori/magi — pip package, ICE protocol, MMLU benchmark
6. gumbel-ai/agent-debate — code review debates, file:line evidence
7. magi-core — Rust crate v0.3.0, crates.io

**EVA fan projects**：
8. CosmoJelly/MAGI-PROTOCOL — FastAPI+Next.js+Redis+WebSocket, full-stack
9. hirakujira/MAGI-System — Next.js, 3 API, Critical Matter rule
10. TomaszRewak/MAGI — Python Dash, GPT-3.5, earliest
11. lordpba/AI_Magi — CrewAI+Gradio, v2.0
12. 07JP27/MagiSystem — C# .NET 8, Azure OpenAI

**其他**：
13. just-every/magi — TypeScript, auto-orchestrator (not 3-vote)
14. albinjal/multi-agent-debate-mcp — MCP server
15. achntj/multi-agent-reasoning — TypeScript debate system

### 可能遗漏
- Reddit MAGI Claude Code plugin (jbolivarg) — 搜索到但未找到独立 repo
- botablenz-prog/MAGI-v2 — LinkedIn 提及但 web_extract blocked
- 可能还有其他 Evangelion 衍生项目

## 2. 分类准确性

分类逻辑：按 peer-review 发表 → 工程成熟度 → demo/fan project 分层，合理。

**需验证**：
- fshiori/magi 的 83% MMLU 数据来自仅 5+2=7 题（abstract_algebra 5题 + professional_law 2题），非标准 MMLU 全量。分析中正确指出了"25题PoC"。
- gumbel-ai 的项目定位为"代码审查专用"准确——有 watch mode、file:line 引用、parking lot 机制。
- just-every/magi 确实不同于其他 MAGI 项目——是单 orchestrator 而非三方投票。

## 3. 与 QUINTE 对比准确性

| 维度 | 自评 |
|------|------|
| agent 数量对比 | 准确：QUINTE R1=5方 vs fshiori=3方 |
| 模型异构 | 准确：QUINTE 有 4 模型源 vs fshiori 通过单一 litellm |
| ICE vs R2 | ICE 类似 R2 但缺 R1 独立盲审和 R3 终裁 |
| 收敛门 | QUINTE 多层级（MAGI ≥2/3 + R2 ≥3/5 + R3 双人），fshiori 仅 Jaccard |
| 监督者 | QUINTE 独有——这是关键差异 |
| 门机制 | QUINTE 独有——雨門/鏡門/證門/閂門 |
| benchmark | fshiori 有实证但样本小（7题"Hell Mode"），QUINTE 有理论框架但缺实证 |

## 4. 潜在盲区

1. **fshiori/magi 作者是 Eric Chen** — pyproject.toml 显示。未在分析中标注。
2. **magi-core Rust crate v0.3.0 已被 yanked** — crates.io 显示 status: Yanked。未在分析中标注。
3. **CosmoJelly/MAGI-PROTOCOL 使用 Python 3.14 + Node 26** — 版本非常新，说明积极开发。
4. **TomaszRewak/MAGI 使用 ChatGPT-3.5** — 极其老旧，历史意义大于实用。
5. **fshiori/magi benchmark 中 Sonnet 版本是 4.6** — 可能笔误（Claude Sonnet 最新是 4 或 4.5？需验证）。

## 5. 结论自评

分析基本完整、分类合理、对比准确。三个待修正点：
- fshiori 作者标注
- magi-core yanked 状态
- Sonnet 版本号验证
