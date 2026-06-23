179 lines, all 5 questions addressed with verdicts. Structure is clean.

**OMP R1 analysis complete.** Key findings:

1. **grok/kimi/mimo is provably optimal** — the only three-model set with zero architectural overlap with hm (DS v4-pro). Any alternative including DS creates fake heterogeneity.

2. **Fixed mapping is correct** — MAGI is blind parallel pre-verification; dynamic routing adds complexity without benefit for text-only reasoning tasks.

3. **CLI flags are optimal** — Gold max+xhigh is user-mandated; Fr's always_thinking IS its comparative advantage (contextual reasoning); Myrrh default preserves speed.

4. **Four blind spot categories** confirmed: code execution, math without tools, shared internet corpus bias, adversarial deception. All mitigated by QUINTE escalation — not flaws in the model set.

5. **≥2/3 gate is strengthened** by heterogeneity: agreement across different architectures is a stronger signal than v3.0's partially-homogeneous convergence.
onshot AI (CN) | Independent |
| Architecture | Grok (MoE, xAI proprietary) | K2.7 (Moonshot proprietary) | MiMo (proprietary) |
| Training corpus | xAI-curated + X/Twitter data | Chinese + English web | Unknown mix |
| Reasoning style | Broad analytic, philosophical | Contextual, always-thinking | Fast synthesis, structured |

Three distinct vendors, three distinct architectures, three distinct training distributions → **true heterogeneity** as prescribed by Zhang 2025 and Clinical Mixed-Vendor 2026.

### Comparison vs v3.0

v3.0: Gold=mimo, Fr=kimi, Myrrh=DS → Myrrh shares base model with hm → the "adversarial audit" role was structurally compromised. Myrrh was supposed to catch hm's errors, but shared the same architecture's blind spots.

v3.1: Gold=grok, Fr=kimi, Myrrh=mimo → all three are architecturally independent of hm. Myrrh can now genuinely serve as adversarial auditor because it thinks differently from hm.

### Caveat

Mimo-v2.5-pro has rate-limiting issues (documented in magi-v3-integration.md, magi-v3-operations.md: "add 10-15s gap between retries"). If mimo becomes the bottleneck, the fallback is hm-solo, which nullifies MAGI. This is an operational risk, not an architecture flaw — the model set is correct; the dispatch reliability needs monitoring.

---

## Q2: Fixed role mapping vs dynamic routing?

**Verdict: Fixed mapping is correct for MAGI v3.1.**

### Why fixed wins

1. **Blind delegate invariant**: MAGI requires all three delegates to answer the same question independently, without cross-output visibility. Dynamic routing by task type would break this — if routing splits questions across models, they're no longer answering the same thing.

2. **Role consistency**: Fixed mapping creates stable role identities that can be profiled over time:
   - Gold (grok): broad analytical reasoning, philosophical framing
   - Frankincense (kimi): deep contextual reasoning, always_thinking for nuance
   - Myrrh (mimo): adversarial audit, fast synthesis, structured contradiction

3. **No task-type detection overhead**: Dynamic routing requires pre-classification of the question before dispatch. This adds latency, a failure mode (misclassification), and complexity. MAGI's value proposition is "lightweight pre-verification" — adding a routing layer undermines the cost-aware cascade.

4. **MAGI is uniform in function**: Unlike the tiered vision pipeline (magi-v3-integration.md §comparative advantage) where task types genuinely differ (structured forms vs ambiguous regions), MAGI's pre-verification function is text-only reasoning. There's no task-type diversity that would benefit from routing.

### When dynamic routing would be relevant

If MAGI were doing multimodal tasks (vision, structured extraction, code execution), dynamic routing to comparative advantage would be correct. But MAGI v3.1 is text-only pre-verification — the question is always "is this claim correct?" — so fixed mapping is optimal.

---

## Q3: Are the CLI flags optimal?

**Verdict: Yes, with one observation.**

### Gold: --effort max --reasoning-effort xhigh

User-mandated (R1 context: "override benchmark"). Not subject to optimization — this is a design constraint, not a tunable. Gold as the broadest reasoner benefits from max compute regardless.

### Frankincense: default (always_thinking)

Kimi K2.7's always_thinking is described as "unbillable overhead — use for contextual reasoning only" (R1 context). But this IS Frankincense's comparative advantage: contextual reasoning. The thinking overhead is the point, not the waste.

Cost concern: ¥49/月 is the highest fixed cost in the set. But it's a subscription — no per-call marginal cost. And parallel dispatch means Frankincense's thinking latency doesn't add wall-clock time (Gold is slower anyway with max+xhigh).

### Myrrh: default

Mimo-v2.5-pro's default mode is appropriate for fast synthesis. Adding effort flags would slow the fastest model in the set, reducing its value as a rapid adversarial check.

### Observation (not a problem)

The current flag profile creates asymmetric response times: Gold (slowest, max+xhigh) > Fr (medium, always_thinking) > Myrrh (fastest, default). This is actually optimal for parallel dispatch — the slowest model sets the wall clock, so making others faster doesn't help. But if Grok CLI ever adds a timeout parameter, it should be set generously to avoid truncating Gold's max-effort reasoning.

---

## Q4: Blind spots — where do all three share correlated failures?

**Verdict: Four confirmed blind spot categories. Mixed-vendor reduces but doesn't eliminate.**

### Category 1: Code execution / runtime verification

All three are text-generation models. None can execute code, run a debugger, or verify runtime behavior. Tasks requiring "does this code compile/run/crash?" will see all three hallucinate equally. This was pre-empted by the MAGI design: code questions escalate to QUINTE where omp has LSP/DAP debugging and cw has sandbox execution.

### Category 2: Mathematical calculation without tool use

LLM arithmetic weakness is architecture-independent. Complex calculations, especially those requiring multi-step derivation, will produce correlated errors across grok/kimi/mimo. GSM8K benchmark (benchmark-methodology.md) confirmed this: all agents converged on the same wrong answer (1620 vs ground truth 540) for an ambiguous question.

### Category 3: Shared internet-scale corpus bias

All three models are trained on internet-scale text. They share the same corpus-level biases: overrepresented Western perspectives, English-language bias, recency cutoff effects, and systematic errors in web-scraped "facts." Mixed-vendor reduces vendor-specific biases (e.g., Moonshot's Chinese-centric training vs xAI's X/Twitter data) but doesn't eliminate the common denominator of internet text.

### Category 4: Adversarial deception

Prompt injection, trick questions with deliberate misdirection, and adversarial framing exploit LLM attention mechanisms — which are universal across architectures. All three will fail similarly on well-crafted adversarial inputs.

### Mitigation

These blind spots are exactly what QUINTE escalation covers. MAGI's design philosophy (magi-v3-redesign.md) explicitly states: "MAGI is lightweight pre-verification." When 2/3 converge on wrong answer due to shared blind spot → QUINTE catches it in R2 cross-review (different architecture, different perspective, tool-augmented verification).

The v3.1 model set is *better* than v3.0 at resisting Category 3 (DS+grok+kimi would have shared Chinese-centric bias; grok+kimi+mimo diversifies training data origins) and Category 4 (different RLHF/alignment pipelines create different susceptibility profiles).

---

## Q5: Is convergence gate ≥2/3 correct for this model set?

**Verdict: Yes. ≥2/3 is the only meaningful gate for three models. Heterogeneity strengthens the signal.**

### Mathematical necessity

With exactly 3 models, the only possible gates are:
- ≥3/3 (unanimity): too strict → most questions escalate to QUINTE, defeating MAGI's cost-saving purpose
- ≥2/3 (majority): correct balance of confidence and efficiency
- ≥1/3 (any agreement): non-informative — single-model agreement is not a gate

≥2/3 is the only gate that provides meaningful pre-verification while keeping the cost cascade functional.

### Heterogeneity strengthens the signal

The key insight from Zhang 2025 and the Clinical Mixed-Vendor study: agreement across heterogeneous models carries MORE weight than agreement across homogeneous models. When grok (xAI MoE) and kimi (Moonshot K2.7) independently converge on the same answer, that's a stronger signal than two instances of the same model agreeing — they overcame different training distributions to reach the same conclusion.

### Risk: 2/3 on wrong answer

The benchmark methodology (benchmark-methodology.md) documented this: GSM8K Q4 saw all agents converge on 1620 (wrong). With ≥2/3, this would produce `[MAGI 3/3]` on a wrong answer. But this is an acceptable risk for lightweight pre-verification — MAGI's purpose is to catch OBVIOUS disagreements, not guarantee correctness. The full QUINTE debate exists for correctness.

### Gate behavior under v3.1 vs v3.0

v3.0: Myrrh=DS → often agreed with hm's implicit bias (same architecture) → inflated convergence rate. The gate was less informative because one model wasn't truly independent.

v3.1: All three models architecturally independent → lower convergence rate (good: fewer false positives) → more informative gate. Lower convergence means more QUINTE escalations, but each escalation is more justified.

---

## Synthesis

### Summary verdict on v3.1

| Dimension | Assessment | Confidence |
|-----------|-----------|------------|
| Q1: Model set optimality | ✅ Optimal — zero hm overlap, true heterogeneity | High |
| Q2: Fixed vs dynamic | ✅ Fixed — correct for blind parallel pre-verification | High |
| Q3: CLI flags | ✅ Optimal — Gold user-mandated, Fr/Myrrh appropriate | High |
| Q4: Blind spots | ⚠️ Four categories — acceptable, mitigated by QUINTE | Confirmed |
| Q5: Convergence gate | ✅ Correct — strengthened by heterogeneity | High |

### One design tension

The v3.1 change moves from "one subscription model (mimo ¥39/月) + one subscription (kimi ¥49/月) + one pay-per-use (DS)" to "one API (grok) + one subscription (kimi ¥49/月) + one subscription (mimo ¥39/月)." The cost profile shifts toward fixed costs. If grok API costs spike, the cost cascade (MAGI cheap → QUINTE expensive) could invert. Monitor grok API pricing.

### v3.0 → v3.1 delta: genuine improvement

The primary change — replacing DS with grok — addresses the single biggest architectural flaw in v3.0: Myrrh sharing architecture with hm. This was not merely "suboptimal"; it was a structural violation of MAGI's core premise (heterogeneous ensemble). v3.1 fixes this completely.

The role mapping shift (Gold: mimo→grok, Myrrh: DS→mimo) is a secondary but beneficial change: Gold as grok (broadest reasoner, max+xhigh) plays to grok's philosophical/analytical strength, while Myrrh as mimo (fast synthesis, default) recovers the speed that v3.0's Myrrh=DS brought but from an independent architecture.

### References consulted

- magi-v3-integration.md (architecture, pitfalls, cost ordering)
- magi-v3-operations.md (invariants, dispatch, gate rules)
- magi-v3-redesign.md (theoretical anchors, repo relationship)
- model-dispatch-comparative-advantage.md (tiered routing, anti-use cases)
- benchmark-methodology.md (GSM8K shared blind spot confirmation)
- rashomon-math-foundations.md (Partial Order Consensus, uncertainty decomposition)
- theory-hardening.md (venue verification, mapping discipline)
- POSTMORTEM.md (MAGI original design overwrite, MiMo artifact detection)
- anti-drift-layered-defense.md (three-layer defense, drift detection)
