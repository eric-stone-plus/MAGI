# MAGI Theoretical Foundation

> **Domain**: OCR Verification Protocol — QUINTE's Visual Input Layer  
> **Version**: 1.0 (2026-06-18)  
> **Parent audit**: QUINTE v3.2 theoretical foundation hardening

## Abstract

MAGI is a multi-model OCR verification protocol that serves as QUINTE's visual input layer. It validates text extracted from scanned documents, images, and PDFs through a 3-phase Gold-dominant pipeline: Gold (visual verification by MIMO-v2.5), Frankincense (semantic classification), and Myrrh (adversarial audit). Its design is grounded in Consensus Entropy theory — the finding that correct OCR predictions converge in output space while errors diverge, enabling training-free quality verification through multi-model agreement.

---

## 1. Core Theoretical Pillars

### Pillar 1: Consensus Entropy for Multi-Model OCR Verification

**Source**: Zhang, Liang et al. (2025). *Consensus Entropy: Harnessing Multi-VLM Agreement for Self-Verifying and Self-Improving OCR*. CVPR 2026. arXiv:2504.11101.

**Finding**: Consensus Entropy (CE) is a training-free, model-agnostic metric that estimates OCR output reliability by measuring inter-model agreement entropy. The core insight: **correct predictions converge in output space, while errors diverge.** CE-OCR, built on this principle, improves F1 scores by **42.1%** over VLM-as-Judge baselines. It outperforms self-consistency and single-model baselines at the same cost, requiring no training or supervision.

**MAGI instantiation**:
- **Gold's visual verification** is conceptually inspired by CE's convergence principle: Gold compares OCR text against the source image, flagging divergence (visual comparison, not entropy measurement)
- **Frankincense's semantic classification** extends CE beyond character-level to semantic-level: do OCR errors change meaning?
- **Myrrh's adversarial audit** applies the inverse of CE: when models disagree, what governance decisions break?
- The **3-phase pipeline** (Star → Gift → Convergence Gate) pursues the same goal as CE (multi-model agreement) but through a different mechanism (complementary roles vs. entropy voting)
- **Tesseract + zlib text extraction** provides the baseline OCR that CE-OCR then verifies

**Alignment**: MAGI's core design principle — "three models, three perspectives, one converged verdict" — is conceptually inspired by CE's insight that "correct predictions converge, errors diverge." However, MAGI does not implement CE's entropy-based mathematical framework. Its three models (Gold, Frankincense, Myrrh) perform complementary tasks (visual verification, semantic classification, adversarial audit) rather than voting on the same output. The connection is at the level of design philosophy, not algorithmic mechanism. Benchmarking MAGI against CE-OCR is listed as a P0 evidence requirement.

---

### Pillar 2: Confidence Calibration Through Multi-Agent Interaction

**Source**: *Confidence Calibration through Multi-Agent Interaction in VQA* (2025). arXiv:2511.11169.

**Finding**: Leading VQA models are often miscalibrated — they express high confidence even when wrong. Multi-agent interaction improves confidence calibration by surfacing disagreements that single models miss.

**MAGI instantiation**:
- **Confidence topology** — MAGI's output includes per-segment confidence scores weighted by source quality
- **Convergence Gate** — the phase where Gold, Frankincense, and Myrrh converge on a single verdict with calibrated confidence
- **QUINTE downstream integration** — QUINTE agents weight claims by source segment confidence, preventing miscalibrated OCR from poisoning debate

**Caveat**: The VQA calibration paper addresses visual question answering, not OCR specifically. The transfer to OCR confidence calibration is plausible but not directly tested.

---

### Pillar 3: Multi-Model Ensemble for Vision Tasks

**Source**: Wang et al. (2022). *Self-Consistency Improves Chain of Thought Reasoning*. ICLR 2023. arXiv:2203.11171.

**Finding**: Multiple reasoning paths → marginalize → most consistent answer. Improves GSM8K by 17.9%.

**MAGI instantiation**: Self-consistency's multi-path principle applies to OCR: multiple OCR engines/viewing angles/perspectives on the same image converge on the correct reading. MAGI extends this from single-model multi-path (temperature sampling) to multi-model multi-path (Gold+Frankincense+Myrrh with different models and roles).

**Supporting**: *Effective Confidence Calibration and Ensembles in LLM-Powered Classification* (Amazon Science, 2025). Leveraging calibrated confidence scores, cost-aware cascading LLM ensemble policies achieve improved accuracy while reducing inference cost. This directly supports MAGI's Gold-dominant pipeline where Gold (MIMO) handles the majority of work, with Frankincense and Myrrh as escalation routes.

---

## 2. Model Architecture

### Gold-Dominant Pipeline (Comparative Advantage)

| Gift | Model | Role | Cost Model |
|------|-------|------|------------|
| **Gold** | mimo-v2.5 (主力) → kimi (批量升级) + DS v4-pro (文本层) | Visual verification + bulk upgrade | Lite ¥39/月 |
| **Frankincense** | mimo-v2.5-pro | Semantic classification | Pro tier |
| **Myrrh** | DS v4-pro | Adversarial audit | Pay-per-use |

**Strategy**: Comparative advantage — deploy the model best suited for each role's specific task, reserving premium models for edge cases where their capabilities are needed.

### Pipeline
```
Document → qpdf decrypt → zlib text layer → DS v4-pro text verification
    │
    └─(scan)─→ Tesseract 5.5.2 → OCR Gate → mimo-v2.5 Gold verification
                    │                              │
                    │                    ┌─────────┴──────────┐
                    │               ≥95% confidence    <95% confidence
                    │                    │                    │
                    │               PASS              ┌──────┴──────┐
                    │                                 │             │
                    │                            kimi batch     Frankincense
                    │                            upgrade        semantic
                    │                                 │             │
                    └─────────────┬───────────────────┴──────┬──────┘
                                  │                          │
                            Myrrh adversarial audit
                                  │
                            QUINTE debate
```

---

## 3. Naming & Theological Framework

MAGI takes its name from the Three Wise Men (東方三博士) of Matthew 2:1-12, who followed the star to Bethlehem bearing Gold, Frankincense, and Myrrh. Each Gift maps to an epistemological stance:

- **Gold** — for a King. Verified, incorruptible truth. The visual verifier.
- **Frankincense** — for a Priest. Sacred pattern, synthesis. The semantic classifier.
- **Myrrh** — for one who would die. Mortality, fragility, adversarial honesty.

**Status**: Design narrative, not architectural constraint. The theological framework enriches the protocol's conceptual grammar but generates no testable predictions beyond what CE theory already provides. Classified as "design narrative" following the QUINTE v3.2 precedent on Polybius.

---

## 4. Counter-Evidence

| Paper | Finding | MAGI Response |
|-------|---------|---------------|
| **Adversarial OCR perturbations** | Small visual perturbations can cause systematic OCR errors across multiple engines | MAGI's confidence topology may fail if all models share vulnerability to the same perturbation class. Cross-engine diversity testing needed. |
| **CE-OCR limitation** (Zhang et al., 2025) | Consensus Entropy requires ≥3 models for reliable agreement measurement | MAGI uses exactly 3 models — at the minimum threshold. Agreement among 2/3 could be insufficient for high-confidence verification. |
| **MIMO rate-limiting** | User-reported: mimo-v2.5 has known rate-limiting issues | Gold's primary model is at risk. Alternative models listed in P3 requirement. |

---

## 5. Current Limitations

1. **Consensus Entropy not directly benchmarked against MAGI.** CE-OCR was tested on standard OCR benchmarks; MAGI's specific 3-model Gold-dominant pipeline has not been compared to CE-OCR.
2. **Kimi batch upgrade is undocumented.** The mechanism by which kimi upgrades Gold's findings for entire document batches lacks formal specification.
3. **Confidence topology is qualitative.** MAGI outputs "≥95% confidence" but the calibration of this threshold has no empirical basis.
4. **MIMO dependency.** Gold's primary model (mimo-v2.5) has known rate-limiting issues. The user has flagged mimo as "deprecated due to rate limiting" — creating a single-model dependency risk.
5. **Myrrh's adversarial scope is underspecified.** "What governance decisions break?" is an open-ended question — the specific failure modes Myrrh tests for are not enumerated.
6. **No comparison against commercial OCR APIs.** Tesseract + zlib vs. Google Cloud Vision / AWS Textract baselines are absent.

---

## 5. Minimum Evidence Requirements

| Priority | Requirement |
|----------|------------|
| P0 | Benchmark MAGI vs. CE-OCR on standard OCR dataset |
| P0 | Calibrate confidence topology threshold (≥95%) from empirical data |
| P1 | Formalize Kimi batch upgrade mechanism |
| P1 | Compare MAGI pipeline vs. commercial OCR API baselines |
| P2 | Enumerate Myrrh adversarial failure modes |
| P2 | Measure end-to-end MAGI→QUINTE accuracy improvement vs. QUINTE with raw OCR |
| P3 | Mitigate MIMO single-model dependency (alternative Gold models) |

---

## References

1. Zhang, Liang et al. (2025). Consensus Entropy. CVPR 2026. arXiv:2504.11101.
2. *Confidence Calibration through Multi-Agent Interaction in VQA* (2025). arXiv:2511.11169.
3. Wang et al. (2022). Self-Consistency. ICLR 2023. arXiv:2203.11171.
4. *Effective Confidence Calibration and Ensembles in LLM-Powered Classification* (Amazon Science, 2025).
5. Du et al. (2023). Multiagent Debate. ICML 2024. arXiv:2305.14325.
6. Zhang et al. (2025). Stop Overvaluing MAD. arXiv:2502.08788.
7. Tesseract OCR 5.5.2 (2025). https://github.com/tesseract-ocr/tesseract

---

*Version 1.0 — 2026-06-18*
