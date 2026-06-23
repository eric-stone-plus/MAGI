# Hermes R1 — MAGI Borrowings Absorption Analysis

## Question
QUINTE 应从 MAGI 生态吸收哪些改进？优先级？代码约束？

## 7 项候选改进

### A. 结构化输出 (jason-chao/MAGI)
**方案**: agent 产出附 `{verdict, confidence, reasoning_chain, evidence_citations}` JSON
**影响**: R1/R2 agent prompt 模板需改，parse 逻辑需改
**阻力**: cc/cw/omp 产出自有格式，强加 JSON Schema 可能降质
**h评估**: 可行但需测试。建议先对 MAGI 三博士试点，再推广到 R1。

### B. R2 匿名审议 (jason-chao/MAGI)
**方案**: R2 用 "Agent A/B/C/D" 替代真实 agent 名
**影响**: prompt 改一行
**h评估**: 零代码阻力，但 QUINTE agent 身份本身就包含信息（cc 在 MiMo，cw 在 DS）——模型即身份。匿名化可能反而损失信息。

### C. Mind-change tracking (fshiori/magi ICE)
**方案**: R2 explicit 追踪 "从立场X转为Y，原因是Z"
**影响**: R2 prompt 加一行
**h评估**: 低阻力。但已有 R2 交叉审隐含此功能。

### D. 错误分级 (jason-chao/MAGI)
**方案**: deprecated/auth/rate_limit/timeout/unknown 五级，不同恢复策略
**影响**: dispatch 代码重写
**h评估**: 高价值，但改动大。优先做 rate_limit vs timeout 二分类（最高 ROI）。

### E. Rapporteur 加权 (jason-chao/MAGI)
**方案**: R1 置信度最高 agent 在 R3 有额外权重
**影响**: R3 裁决规则需改
**h评估**: 与现有 "R3 双人裁决" 冲突——hm 垄断终裁权。需讨论。

### F. 强制 file:line (gumbel-ai/agent-debate)
**方案**: R1 prompt 追加 "每条声明附 file:line，否则不计入投票"
**影响**: prompt 改一行
**h评估**: 低阻力，高价值。已有鏡門但只约束 hm。

### G. Adaptive 预检 (fshiori/magi)
**方案**: R1 ≥80% 一致→R2 轻量确认性审计
**影响**: QUINTE 核心规则变更——当前 "R2 永不跳过"
**h评估**: 与 SOUL.md "不自判简化" 直接冲突。这是禁止项。

## h初步排序

| 优先级 | 改进 | 阻力 | 价值 |
|--------|------|------|------|
| P0 | F. 强制 file:line | 低 | 高 |
| P1 | D. 错误分级 (rate_limit/timeout 二分类) | 中 | 高 |
| P1 | C. Mind-change tracking | 低 | 中 |
| P2 | A. 结构化输出 (MAGI 试点) | 中 | 中 |
| P2 | B. 匿名审议 | 低 | 低（模型即身份） |
| P3 | E. Rapporteur 加权 | 高（协议冲突） | 待议 |
| ⛔ | G. Adaptive 预检 | 违反铁律 | — |

## 待 MAGI 裁决
- kimi: 代码约束——breaker changes、向后兼容
- grok: 代码约束——implementation 成本
- Myrrh: 整体可行性 + 遗漏
