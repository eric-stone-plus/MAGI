<div align="center">

<img src="assets/magi-cover.svg?v=5" alt="MAGI" width="100%">

# MAGI (マギ) · Hermes Agent Protocol

**Hermes Agent OCR verification protocol — QUINTE's visual input layer. macOS-only.**

Single-model OCR on macOS (Tesseract) hits a confidence ceiling. On Windows, PaddleOCR is accurate enough that multi-model verification is unnecessary overhead. MAGI exists for the gap: when Tesseract alone isn't enough, three delegates, dispatched by Hermes, bear distinct verification roles through a Gold-dominant pipeline, converging on a confidence topology that QUINTE can trust.

> *"Where is he that is born King of the Jews? for we have seen his star in the east, and are come to worship him."* — Matthew 2:2

---

[![Hermes Agent Protocol](https://img.shields.io/badge/Hermes_Agent-v2.0-blue?style=flat)](specs/PROTOCOL.md)
[![Models](https://img.shields.io/badge/models-mimo%20%7C%20kimi%20%7C%20deepseek-8A2BE2?style=flat)](#deployment)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)

</div>

---

## The Three Gifts

The Magi were three wise men from different lands, following one star, bearing three gifts. They saw the same truth through different eyes and converged on the same manger. This is what MAGI does for OCR.

**Gold** was the gift for a King — incorruptible, the foundation of all value. In MAGI, Gold is the *visual verifier*: the only delegate with eyes to see the original image. Every character it verifies must trace to pixels in the source. Gold does not tarnish; facts verified by Gold are the foundation upon which Frankincense and Myrrh build their analysis.

**Frankincense** was the gift for a Priest — rising incense, the synthesis that lifts raw data into sacred meaning. In MAGI, Frankincense is the *semantic classifier*: determining whether OCR errors change meaning, classifying impact from cosmetic to governance-critical. Frankincense rises — it is the pattern that transforms raw corrections into actionable understanding.

**Myrrh** was the gift for one who would suffer and die — the embalming spice, awareness of mortality and fragility. In MAGI, Myrrh is the *adversarial auditor*: asking the question no one wants to hear — "if QUINTE reads this uncorrected, what governance decision breaks?" Myrrh preserves — it is the conscience that keeps truth from decaying into comfortable falsehood.

*Three persons, one substance. Three gifts, one verified text.*

## Architecture

```
            ╔═══════════════════════════════════════════════╗
            ║              MAGI Protocol v2.0               ║
            ║       Gold-Dominant OCR Verification          ║
            ║          「われら東にてその星を見たれば」             ║
            ╚═══════════════════════════════════════════════╝

    ┌─────────────────────────────────────────────────────────┐
    │  PHASE 0 · THE STAR (星)                                │
    │  "We have seen his star in the east" — Matthew 2:2      │
    │                                                         │
    │  Evidence assembly:                                     │
    │  · Original image (PDF page / PNG / JPEG)               │
    │  · Tesseract OCR raw text + word-level confidence       │
    │  · Segment map (text lines, tables, fields)             │
    │  · Tesseract-v2 cross-check baseline                    │
    └────────────────────────┬────────────────────────────────┘
                             ▼
    ┌─────────────────────────────────────────────────────────┐
    │  PHASE 1 · THE OFFERING (獻禮)                           │
    │  "They opened their treasures" — Matthew 2:11           │
    │                                                         │
    │  GOLD (金) — Visual Verification                        │
    │  · mimo-v2.5 primary, kimi batch fallback               │
    │  · Per-segment: image vs OCR → corrected text           │
    │  · Error classification: CHAR / LAYOUT / OMISSION /     │
    │    HALLUCINATION                                        │
    │  · Per-segment confidence: 0.0–1.0 with rationale       │
    │  · Tesseract-v2 cross-check on every correction         │
    └────────────────────────┬────────────────────────────────┘
                             ▼
              ┌──────────────┴──────────────┐
              ▼                             ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│ FRANKINCENSE (乳香)       │    │ MYRRH (沒藥)              │
│ Semantic Classification  │    │ Adversarial Audit        │
│                          │    │                          │
│ "Does the error change   │    │ "If QUINTE reads this    │
│  meaning?"               │    │  uncorrected, what       │
│                          │    │  governance decision     │
│ Classifies Gold's        │    │  breaks?"                │
│ errors:                  │    │                          │
│ · COSMETIC               │    │ · Simulates downstream   │
│ · LEXICAL                │    │   QUINTE processing      │
│ · SEMANTIC               │    │ · Identifies blind spots │
│ · STRUCTURAL             │    │ · Ranked impact:         │
│ · QUINTE_CRITICAL        │    │   CRITICAL / MODERATE /  │
│                          │    │   COSMETIC               │
│ (mimo-v2.5-pro)          │    │ (DeepSeek v4-pro)        │
└────────────┬─────────────┘    └────────────┬─────────────┘
             └──────────────┬───────────────┘
                            ▼
    ┌─────────────────────────────────────────────────────────┐
    │  PHASE 3 · THE MANGER (馬槽)                             │
    │  "They fell down, and worshipped him" — Matthew 2:11    │
    │                                                         │
    │  « Convergence Gate »                                   │
    │                                                         │
    │  Weighted evaluation:                                   │
    │  · Visual (0.4): Gold confidence + cross-check          │
    │  · Semantic (0.3): Frankincense classification          │
    │  · Risk (0.3): Myrrh CRITICAL risks addressed           │
    │                                                         │
    │  Score ≥0.7 ∧ no unresolved CRITICAL → CONVERGED        │
    │  Score <0.7 ∨ CRITICAL unresolved → HUMAN REVIEW        │
    └────────────────────────┬────────────────────────────────┘
                             ▼
    ┌─────────────────────────────────────────────────────────┐
    │                    → QUINTE ←                           │
    │  Verified text + per-segment confidence topology        │
    │  QUINTE agents weight claims by source confidence       │
    └─────────────────────────────────────────────────────────┘
```

## The Pipeline

**Phase 0 — The Star (星).** Evidence assembly. The original image, Tesseract OCR output, and a segment map dividing the document into verification units — text lines, table cells, header zones. A second Tesseract pass with alternative parameters establishes a mechanical cross-check baseline. Documents with mean Tesseract confidence below 60% are rejected — the Magi do not waste their gifts on illegible scrolls.

**Phase 1 — The Offering (獻禮).** Gold alone approaches the image. The multimodal delegate inspects each segment, comparing OCR output against the original. Every correction carries a confidence score and a rationale. Tesseract-v2 cross-check validates every correction: agreement → auto-accept; conflict → flagged for review. Gold is the sole visual authority — the protocol does not pretend otherwise.

**Phase 2 — Frankincense & Myrrh (parallel).** Two text-only delegates work simultaneously on Gold's corrected text. Frankincense classifies each error by semantic impact — cosmetic, lexical, semantic, structural, governance-critical. Myrrh simulates downstream QUINTE processing, asking "what is the worst plausible misread that could flip a governance decision?" Neither depends on the other; both feed the convergence gate.

**Phase 3 — The Manger (馬槽).** The convergence gate evaluates: have the Magi converged? Weighted scoring across three dimensions determines whether the verified text is ready for QUINTE or requires human review.

## Convergence Gate

| Dimension | Weight | What it measures |
|-----------|--------|------------------|
| Visual | 0.4 | Gold's per-segment confidence; Tesseract cross-check agreement |
| Semantic | 0.3 | Frankincense's classification uncontested |
| Risk | 0.3 | Myrrh's CRITICAL risks addressed or flagged |

Score ≥0.7 with no unresolved CRITICAL → converged → QUINTE.
Below threshold or CRITICAL unresolved → human review or re-scan.

## Relationship to QUINTE

| | QUINTE | MAGI |
|-|--------|------|
| Metaphor | Roman Republic — Senate in the Forum | Bethlehem — Three Magi at the Manger |
| Function | Governance — debate, cross-examine, verdict | Vision — verify, classify, converge |
| Agents | 5 senators of equal standing | 3 apostles with distinct Gifts |
| Flow | R1 parallel → R2 cross → R3 dual verdict | P1 Gold → P2 Fr+Myrrh parallel → P3 convergence |
| Output | PASS/BLOCKED verdict | Verified text + confidence topology |
| Role in pipeline | Final governance gate | Pre-processing visual input layer |

MAGI sees. QUINTE judges. The star leads to the Senate.

## Deployment

Each Gift is assigned the model where it has **comparative advantage** — not the cheapest, not the most powerful, but the *right tool for the task*.

| Gift | Model | Role | Why |
|------|-------|------|-----|
| **Gold** (金) | mimo-v2.5 → kimi fallback | Visual field extraction | mimo: structured forms, no thinking overhead. kimi: ambiguous regions only (handwriting, stamps) |
| **Frankincense** (乳香) | mimo-v2.5-pro | Semantic classification | Text synthesis — strongest text reasoning in the Lite tier |
| **Myrrh** (沒藥) | DeepSeek v4-pro | Adversarial audit | Strongest adversarial reasoning — the only role worth paying per-use |

### Gold Tiered Pipeline

```
Document
  │
  ├─ Text layer? ─── YES → zlib extract → DS v4-pro verify → Fr+Myrrh → QUINTE
  │
  └─ NO (scanned)
       │
       ├─ OCR quality gate (DPI<150 / low contrast / skew>15°)
       │     └─ FAIL → kimi full-doc (thinking=high)
       │
       └─ PASS → Tesseract OCR → mimo-v2.5 Gold
              │
              ├─ confidence ≥ calibrated → accept → Fr+Myrrh
              │
              └─ confidence < calibrated
                   │
                   ├─ text-only field → DS v4-pro (max reasoning)
                   │
                   └─ vision-required → batch composite kimi call (thinking=high)
                        → merge → Fr+Myrrh → QUINTE
```

**Key principle**: kimi's `always_thinking` burns 80% of tokens on internal reasoning. For structured forms (90%+ of fields), this is pure waste — OCR field alignment needs precision, not deliberation. kimi enters only where ambiguity demands reasoning. Every model runs at maximum effort — no cost-driven downgrading.

Circuit breaker: mimo API failure → auto-fallback to all-kimi + alert.

## Quick Start

```bash
git clone https://github.com/eric-stone-plus/MAGI.git
cd MAGI

# Read the protocol
cat specs/PROTOCOL.md
```

## Implementation

MAGI runs on [Hermes Agent](https://github.com/nousresearch/hermes-agent) as QUINTE's pre-processing layer. It depends on Hermes' terminal toolchain for Tesseract/qpdf/zlib execution and delegate_task for multi-model dispatch.

| Path | What |
|------|------|
| [specs/PROTOCOL.md](specs/PROTOCOL.md) | Canonical protocol specification |
| [specs/archive/](specs/archive/) | Historical v1.x specs |
| [concepts/CONCEPTS.md](concepts/CONCEPTS.md) | Theological and philosophical foundations |
| [prompts/](prompts/) | Delegation prompt templates (Gold, Frankincense, Myrrh) |

## License

MIT — the protocol and orchestration layer.

## References

1. Zhang, Liang et al. (2025). Consensus Entropy: Harnessing Multi-VLM Agreement for Self-Verifying and Self-Improving OCR. *CVPR 2026*. arXiv:2504.11101.
2. Confidence Calibration through Multi-Agent Interaction in VQA (2025). arXiv:2511.11169.
3. Wang, X. et al. (2022). Self-Consistency Improves Chain of Thought Reasoning. *ICLR 2023*. arXiv:2203.11171.
4. Effective Confidence Calibration and Ensembles in LLM-Powered Classification (Amazon Science, 2025).
5. Du, Y. et al. (2023). Multiagent Debate. *ICML 2024*. arXiv:2305.14325.
6. Tesseract OCR 5.5.2 (2025). https://github.com/tesseract-ocr/tesseract

Full theoretical foundation: [specs/theoretical-foundation.md](specs/theoretical-foundation.md)
