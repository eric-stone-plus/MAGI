# MAGI vs QUINTE — Historical Session Substitution Analysis

> 2026-06-14 · 基于历史 session 使用模式的替代分析

## 核心洞察

QUINTE 要用两个底座模型（DeepSeek v4-pro + mimo/claude）才能发挥最大价值——
跨模型多样性是 QUINTE 的核心卖点。但很多场景根本不需要跨模型，
单模型就够。这些场景 MAGI 可以完全替代 QUINTE/QUINTE-LITE。

## 历史 Session 分类

### 已用 QUINTE-LITE 的场景（全部可被 MAGI 替代）

| Session | 场景 | 用的什么 | 能用 MAGI? | 原因 |
|---------|------|---------|-----------|------|
| 20260613_235845 | 滞期费全量审计 (54报告) | QUINTE-LITE hm+cc+mc | ✅ 完全替代 | 纯调查分析，不涉及 push |
| 20260614_115505 | 内地房价监测系统 | QUINTE-LITE hm+cc+mc | ✅ 完全替代 | 系统设计，不涉及授权 |
| 20260614_000529 | quinte-website 代码审查 | QUINTE-LITE hm+cc+mc | ✅ 完全替代 | 代码审查 = MAGI Gold 的核心功能 |
| 20260614_004338 | 四套领域系统设计 | QUINTE-LITE hm+cc+mc | ✅ 完全替代 | 架构设计，KAIKEI/HANREI/SENPAI/YOSOKU 原本就按 MAGI 结构设计 |
| 20260614_124337 | Crypto 交易模型 | MAGI (已用) | ✅ 已经在用 | Phase 0-4 完整闭环，3,686 行代码 |

### 需要完整 QUINTE 的场景（MAGI 不能替代）

| 场景 | 为什么 MAGI 不够 |
|------|-----------------|
| git push 授权 | 需要 HIGHBALL KENGEN gate + QUINTE R3 双人裁决 |
| 协议变更 | 需要 5 agent 全员投票，MAGI 只有 3 |
| 跨模型验证 | QUINTE 的核心价值——DeepSeek + mimo 交叉检测共享盲区 |
| 争议性法律分析 | 需要 rx 的纯推理交叉裁判（MAGI 没有 rx） |
| meta-QUINTE（自审） | 审计 QUINTE 自身需要 QUINTE 全量框架 |

### MAGI 专属场景（QUINTE 做不好的）

| 场景 | MAGI 优势 |
|------|----------|
| 快速迭代（<3min） | MAGI ~3min vs QUINTE ~10min |
| Token 经济（mimo 免费） | MAGI 全 mimo vs QUINTE DeepSeek 自费 |
| Confidence topology | MAGI 输出置信度地图，QUINTE 只有 PASS/FAIL |
| 领域特化 | MAGI 可加载 KAIKEI/HANREI/SENPAI/YOSOKU 专用 Gift prompt |
| 同模型深度推理 | 螺旋辩证 O(n) vs 交叉审查 O(n²)，更深入而非更广 |

## 替代决策树

```
用户有问题/任务
  │
  ├─ 涉及 push/deploy/commit？
  │   └─ YES → 完整 QUINTE + HIGHBALL KENGEN
  │
  ├─ 涉及协议/规则变更？
  │   └─ YES → 完整 QUINTE（5 agent 全员投票）
  │
  ├─ 需要跨模型验证？
  │   └─ YES → 完整 QUINTE（DeepSeek + mimo 交叉）
  │
  ├─ 纯调查/分析/设计/审查？
  │   └─ YES → MAGI（3 agent 单模型，~3min）
  │
  ├─ 数据密集型（滞期费/台账/勾稽）？
  │   └─ YES → MAGI + 领域特化 Gift prompt
  │
  └─ 不确定？
      └─ MAGI（更快、更便宜、出错代价更低）
```

## Token 成本对比

| 维度 | QUINTE (5-agent) | MAGI (3-agent) | 节省 |
|------|-----------------|---------------|------|
| Agent 数 | 5 (hm+cc+cw+omp+rx) | 3 (hm+delegate×2) | 40% |
| 模型 | DeepSeek v4-pro (自费) | mimo-v2.5-pro (免费) | 100% |
| 轮次 | R1+R2+R3 = 3轮 | P1+P2+P3+P4 = 4阶段但更轻 | ~50% |
| 单次耗时 | ~10min | ~3min | 70% |
| 单次 token | ~500K | ~150K | 70% |

## 迁移路径

现有 QUINTE-LITE 使用者（hm+cc+mc 模式）：

1. **今天**：把 QUINTE-LITE 调用替换为 MAGI 调用
   - QUINTE-LITE: `delegate_task` 给 cc 和 mc，hm 交叉对比
   - MAGI: `delegate_task` 给 Gold 和 Frankincense，hm 做 Myrrh + 收敛评估

2. **本周**：为常用场景创建领域特化 Gift prompt
   - 滞期费审计 → SENPAI Gift prompt
   - 合同条款 → HANREI Gift prompt
   - 财务勾稽 → KAIKEI Gift prompt
   - 价格预测 → YOSOKU Gift prompt

3. **本月**：MAGI → QUINTE 管道自动化
   - MAGI 产出 Revelation → 自动作为 QUINTE R1 证据
   - 仅在需要 push 时才启动完整 QUINTE

## 总结

**80% 的历史 QUINTE-LITE 使用场景可以用 MAGI 替代。**

理由：
- 这些场景都是调查/分析/设计，不涉及 push 授权
- 单模型（mimo）在这些场景中已经足够——跨模型多样性是锦上添花，不是必需
- MAGI 更快（3min vs 10min）、更便宜（免费 vs 自费）、输出更丰富（confidence topology vs binary）
- MAGI 的螺旋辩证比 QUINTE-LITE 的简单交叉对比更深入

**剩下 20%（push/协议变更/跨模型验证/争议性分析）仍需完整 QUINTE。**
