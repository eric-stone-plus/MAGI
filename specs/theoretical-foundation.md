# MAGI Theoretical Foundation

> **Domain**: Lightweight heterogeneous pre-verification — hm's self-doubt resolution layer  
> **Version**: 3.4 (2026-06-20) — QUINTE v3.4 ecosystem sync: 6-tier error classification, magi_dispatch.py v1, JSON sidecar evidence gate, cross-repo consistency check  
> **Parent audit**: QUINTE v3.4 theoretical foundation hardening

## Abstract

MAGI is a lightweight heterogeneous LLM ensemble that serves as hm's pre-QUINTE verification layer. Three heterogeneous base models — each delegated to a different cognitive stance (Gold for factual verification, Frankincense for contextual reasoning, Myrrh for adversarial audit) — answer the same question in parallel, each bringing a different training distribution and inductive bias. Binary convergence gate: ≥2/3 agree → answer adopted; otherwise → escalate to full QUINTE debate. The design draws on model routing cascades, heterogeneous ensemble theory, and the established finding that model diversity — not role diversity — drives multi-agent accuracy gains.

---

## 1. Core Theoretical Pillars

### Pillar 1: Model Heterogeneity as the Critical Factor

**Source**: Zhang, H. et al. (2025). *Stop Overvaluing Multi-Agent Debate*. arXiv:2502.08788 [preprint, not peer-reviewed].

**Finding**: Systematic evaluation of 5 MAD methods across 9 benchmarks shows that model heterogeneity is the "universal antidote" — consistently improving multi-agent performance where homogeneous setups fail to beat single-agent baselines.

**MAGI instantiation**: MAGI's three delegates each use a different base model — not the same model with different prompts — assigned by cognitive stance rather than by model name. This implements heterogeneity at the architecture level. The convergence gate (≥2/3) applies Zhang et al.'s finding: agreement across heterogeneous models carries more weight than agreement across same-model instances.

**Caveat**: Most-cited paper in ecosystem (Zhang 2025) is a preprint [not peer-reviewed].

---

### Pillar 2: Homogeneous Teams Share Correlated Blind Spots

**Source**: *Do Mixed-Vendor Multi-Agent LLMs Improve Clinical Diagnosis?* (2026). EACL 2026 HeaLing Workshop. arXiv:2603.04421.

**Finding**: Single-vendor multi-agent teams produce "correlated failure modes that reinforce shared biases." Mixed-vendor configurations consistently outperform because they "pool complementary inductive biases, surfacing correct diagnoses that homogeneous teams collectively miss."

**MAGI instantiation**: The three-model design directly implements mixed-vendor architecture. When all three agree, the answer has passed through three different training distributions — substantially reducing shared-blind-spot risk compared to same-model self-consistency.

---

### Pillar 3: Cost-Aware Cascading from Light to Heavy Debate

**Source**: *CascadeDebate: Multi-Agent Deliberation for Cost-Aware LLM Cascades* (2026). arXiv:2604.12262 [preprint, not peer-reviewed].

**Finding**: CascadeDebate demonstrates that multi-agent deliberation can route queries cost-effectively — lightweight models handle simple cases, escalating only hard cases to heavier debate. This preserves accuracy while reducing total inference cost.

**MAGI instantiation**: MAGI → QUINTE is a cascade. MAGI's 3-model parallel dispatch is the "lightweight" stage. Its binary convergence gate is the routing decision: converge → answer (cheap), diverge → QUINTE (expensive but thorough). This is the same architectural pattern CascadeDebate validates.

**Caveat**: Core pillar rests on CascadeDebate preprint [not peer-reviewed].

---

### Pillar 4: Ensemble Theory for Language Models

**Source**: Mienye, I.D. & Swart, T.G. (2025). *Ensemble Large Language Models: A Survey*. *Information*, 16(8), 688.

**Finding**: Systematic categorization of LLM ensemble methods across domains. Heterogeneous ensembles (different models) consistently outperform homogeneous ensembles (same model, different prompts) for tasks requiring diverse reasoning paths.

**MAGI instantiation**: MAGI is a heterogeneous ensemble with a binary voting gate. The survey validates this architecture as a well-established pattern in the literature, distinct from both single-model self-consistency and full multi-agent debate.

---

## 2. Supporting Literature

### Self-Consistency
Wang, X. et al. (2022). *Self-Consistency Improves Chain of Thought Reasoning*. ICLR 2023. arXiv:2203.11171. Multiple reasoning paths from same model → marginalize → most consistent answer. MAGI extends this from within-model to across-model diversity.

### Multi-Agent Debate
Du, Y. et al. (2023). *Multiagent Debate*. ICML 2024. arXiv:2305.14325. Foundational MAD paper. MAGI's parallel dispatch + convergence gate is a lightweight form of the debate pattern.

---

## 3. Counter-Evidence

| Paper | Finding | MAGI Response |
|-------|---------|---------------|
| **Zhang et al. 2025** (primary finding) | MAD frequently fails to outperform single-agent CoT baselines | MAGI uses heterogeneous models — the factor Zhang identifies as the "universal antidote" |
| **Cemri et al. 2025** (MAST) | 14 failure modes in multi-agent systems | MAGI's binary gate and 3-model limit reduce attack surface compared to 5-agent QUINTE |
| **Model availability risk** | If 2 of 3 models are unavailable, MAGI degrades to single-model | Invariant#6: hm answers directly with [UNCERTAIN] annotation |

---

## 4. Current Limitations

1. **No direct empirical validation.** MAGI's 3-model ensemble has not been benchmarked against single-model baselines or against direct QUINTE on the same questions.
2. **Binary gate is crude.** ≥2/3 agreement discards nuance. A 1-point disagreement between essentially compatible answers triggers unnecessary QUINTE escalation.
3. **Model availability is fragile.** Three-model dependency means two unavailable models → MAGI cannot operate. This is a real risk for a system that runs on cloud APIs.
4. **Cost ordering is aspirational.** The "cheap → expensive" cascade depends on MAGI catching most questions. If divergence rate is high, MAGI + QUINTE is more expensive than QUINTE alone.
5. **hm trigger logic is undefined.** The protocol says "hm decides when uncertain" but provides no operational definition of "uncertain."

---

## 5. Minimum Evidence Requirements

| Priority | Requirement |
|----------|------------|
| P0 | Benchmark MAGI vs. single-model CoT on ≥1 QA benchmark |
| P0 | Measure MAGI convergence rate in production (what % of hm's uncertainties converge?) |
| P1 | Compare MAGI→QUINTE cascade cost vs. direct QUINTE |
| P1 | Define operational hm uncertainty trigger criteria |
| P2 | Test binary gate vs. weighted voting on calibration dataset |
| P3 | Benchmark against CascadeDebate's reported results |

---

## Cross-Repository References

- [QUINTE (escalation target)](../../QUINTE/specs/theoretical-foundation.md)
- [RASHOMON (heterogeneity theory)](../../RASHOMON/specs/theoretical-foundation.md)

---

## References

1. Zhang, H. et al. (2025). Stop Overvaluing Multi-Agent Debate. arXiv:2502.08788 [preprint, not peer-reviewed].
2. Clinical Mixed-Vendor (2026). EACL 2026 HeaLing Workshop (workshop). arXiv:2603.04421.
3. CascadeDebate: Multi-Agent Deliberation for Cost-Aware LLM Cascades (2026). arXiv:2604.12262 [preprint, not peer-reviewed].
4. Mienye, I.D. & Swart, T.G. (2025). Ensemble Large Language Models: A Survey. *Information*, 16(8), 688.
5. Wang, X. et al. (2022). Self-Consistency Improves Chain of Thought Reasoning. *ICLR 2023* (CORE A*). arXiv:2203.11171.
6. Du, Y. et al. (2023). Multiagent Debate. *ICML 2024* (CORE A*). arXiv:2305.14325.
7. Cemri, M. et al. (2025). Why Do Multi-Agent LLM Systems Fail? arXiv:2503.13657 [preprint, not peer-reviewed].

---

*Version 3.4 — 2026-06-20 — QUINTE v3.4 ecosystem sync: general-purpose heterogeneous pre-verification*
