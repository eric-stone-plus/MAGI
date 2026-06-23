# R2 · hm — Kimi Token Efficiency Cross-Review

## hm 对 hm R1 + cw R1 的交叉审查

### 1. 估算叠加关系——关键修正

hm R1 声称 85% 综合节省，但这个数字是简单加总，实际叠加是非线性的。分层计算：

**Layer 1 — 基础层（互斥，选最强）**
- 文本层绕过：90% 文档不触发 kimi。这是最大的单一节省。
- 剩下 10% 必须走 kimi 的扫描件。

**Layer 2 — 单次调用合并（hm 策略 1 = cw 策略 4）**
- 每文档 1 次调用代替 N 次 → 对 10% 扫描件有效
- 3 页 SOF → 从 3 次到 1 次 = 67% 节省（但只能在扫描件上生效）

**Layer 3 — 输出控制（stream-json + thinking 关闭）**
- stream-json 消除 thinking 输出 50% + thinking_enabled=off 消输入 60-70%
- ⚠️ 这两者不同维度：thinking_enabled=off 作用于 **input/computation**，stream-json 作用于 **output/format**
- thinking_enabled=off → 计算端不消耗 thinking token → 节省 ~65% 的 input+compute token
- stream-json → 输出端不返回 thinking 文本 → 节省 ~50% 的 output token  
- **两者叠加**：约 65% × 50% = 约 82% token 节省（乘性，非加性）

**Layer 4 — 模板缓存（hm 策略 3）**
- 对重复 agent 有效。但 60% 节省是在 Layer 2+3 之后的基础上——不是原始 100%
- 实际效果：remaining 18% × 60% = 节省 10.8pp

**Layer 5 — 图像裁剪/跳字段（hm 策略 5+6 = cw 隐含）**
- 30% 输入 savings on 扫描件
- 在 Layer 2+3+4 之后基础上叠加

**实现组合节省**（以 SOF 重复 agent 为例）：
```
Baseline: 100 tokens
→ Layer 1 (文本层绕过): 90% 文档不触发 → 10 tokens (仅扫描件)
→ Layer 2 (单次调用): 1 call vs 3 → 3.3 tokens  
→ Layer 3 (thinking off + stream-json): 3.3 × 0.18 = 0.6 tokens
→ Layer 4 (模板缓存): 0.6 × 0.4 = 0.24 tokens
→ Layer 5 (图像裁剪): 0.24 × 0.7 = 0.17 tokens

综合: 99.83% 节省 ≈ 只剩原消耗的 0.17%
```

但这是扫描件的上界。对新 agent / 首文档，无模板缓存：
```
→ Layer 1-3: 0.6 tokens
→ Layer 5: 0.42 tokens
综合: 99.58% 节省
```

**结论**：hm 的 85% 低估了——正确数字是 99.5-99.8%（含文本层绕过）。cw 的分层更严谨但没做叠加计算。

---

### 2. hm 和 cw 之间的差异

| 维度 | hm | cw | 裁决 |
|------|----|----|------|
| stream-json | 50% 节省 | 提及但未量化 | 一致，hm 更精确 |
| thinking 关闭 | 未提及（外部思考） | 60-70% 节省 | **关键遗漏**——hm 没意识到 Kimi 内部 thinking 是独立消耗 |
| 模板缓存 | 60% 节省 | 类比为 prefix_cache | **互补**——hm 说的是文档结构缓存，cw 说的是 API 前缀缓存。两个都有效，两层缓存可以叠加 |
| 预算上限 | 隐含（SOF 测试触发） | 显式 dispatch 模板 | cw 更工程化 |
| 降级策略 | 未提 | `downgrade_on_warning: deepseek-v3` | cw 有远见但有陷阱——kimi 和 DS 的输入格式不同（kimi 看图片，DS 看文本），降级 ≠ 等价替换 |

---

### 3. 关键遗漏——两个 R1 都没发现

#### 遗漏 1：`KIMI_MODEL_THINKING_MODE=off` 环境变量

kimi-code 支持环境变量覆盖（skill 记载）：
```bash
KIMI_MODEL_THINKING_MODE=off ~/.kimi-code/bin/kimi -p "..." --output-format stream-json
```

这意味着 **不需要修改 config.toml**，不需要 cw 的 whitelist 中间件。MAGI Gold dispatch 加一行 env 即可。cw 的整个 whitelist 调度逻辑在这个场景下 unnecessary complexity。

#### 遗漏 2：output-format 当前配置错误

当前 MAGI skill 的 Gold dispatch 写的是 `--output-format text`。这是 **错的**——text 模式输出 verbose 自我叙述（≈30-50% 额外 token）。stream-json 是 kimi-code 的非交互标准格式，理应作为默认。

#### 遗漏 3：hanging connection 风险

Kimi Code `-p` 模式在 prompt 过大或模型思考过长时可能 120s+ 超时。hm 策略 4（文本层绕过）和策略 1（单次调用）缓解了这个风险——更少的调用 = 更少的机会超时。但 cw 的 dispatch 模板没有超时处理逻辑。

#### 遗漏 4：cw 的 `prefix_cache` 对 kimi 的适用性

cw 建议 prefix_cache 缓存系统 prompt。但 Kimi Code 是 CLI agent，不是 API——它内部处理系统 prompt。`prefix_cache` 是 OpenAI-compatible API 参数，不适用于 kimi-code CLI 调用。这个建议对 MAGI Gold 无效。

#### 遗漏 5：hm 策略 5（图像裁剪）未定义裁剪逻辑

"crop to relevant regions" 很好，但谁来做裁剪？需要sips/ImageMagick 预处理。裁剪坐标从哪来？→ 模板缓存。所以策略 5 是策略 3 的 **子项**，不是独立策略。

---

### 4. 最终排名（修正后）

| 排名 | 策略 | 节省 | 实现成本 | 可靠性 |
|------|------|------|----------|--------|
| 1 | 文本层绕过（已有） | 90% | 0 | ✅ |
| 2 | thinking=off (`KIMI_MODEL_THINKING_MODE=off`) | 65% 输入 | 1 行 env | ✅ |
| 3 | `--output-format stream-json`（已有，需修正） | 50% 输出 | 改 skill | ✅ |
| 4 | 单次调用（已有 pitfall 0a） | 67% 扫描件 | skill 已记载 | ✅ |
| 5 | 模板缓存（新建） | 60% 重复 agent | 新增逻辑 | ⚠️ 需坐标存储 |
| 6 | 预算上限（新建） | 灾备 | 新增逻辑 | ⚠️ 降级路径不清晰 |

策略 1-4 全在 skill 层面改配置即可——不需要新代码。策略 5-6 需要额外工程。

---

### 5. 实施建议（最小可行变更）

**立即（本 session）**：
1. MAGI skill Gold dispatch 从 `--output-format text` → `stream-json`
2. 加 `KIMI_MODEL_THINKING_MODE=off` 环境变量
3. 确认单次调用规则在 skill 中明确

**后续**：
4. 模板缓存：首份同 agent SOF 全量校验 → 存坐标 JSON → 后续只验变化字段
5. 预算上限：监控 kimi API 剩余额度，近 20% 告警
