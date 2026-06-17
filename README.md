<div align="center">

<img src="assets/magi-cover.svg?v=5" alt="MAGI" width="100%">

# MAGI (マギ) Protocol

**OCR verification protocol — QUINTE's visual input layer.**

Single-model OCR hits a confidence ceiling. No amount of prompt engineering fixes modal blindness — a text-only model cannot see the image. MAGI breaks through: three apostles bear distinct epistemological gifts through a Gold-dominant verification pipeline, converging on a confidence topology that QUINTE can trust.

> *"Where is he that is born King of the Jews? for we have seen his star in the east, and are come to worship him."* — Matthew 2:2

---

[![Provider-agnostic](https://img.shields.io/badge/protocol-provider--agnostic-4B6BFB?style=flat)](specs/PROTOCOL.md)
[![Protocol](https://img.shields.io/badge/protocol-v2.0-blue?style=flat)](specs/PROTOCOL.md)
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

<div align="center"><pre>
            ╔═══════════════════════════════════════════════╗
            ║              MAGI Protocol v2.0              ║
            ║       Gold-Dominant OCR Verification         ║
            ║   「われら東にてその星を見たれば」              ║
            ╚═══════════════════════════════════════════════╝

    ┌─────────────────────────────────────────────────────────┐
    │  PHASE 0 · THE STAR (星)                                 │
    │  "We have seen his star in the east" — Matthew 2:2       │
    │                                                         │
    │  Evidence assembly:                                      │
    │  · Original image (PDF page / PNG / JPEG)                │
    │  · Tesseract OCR raw text + word-level confidence        │
    │  · Segment map (text lines, tables, fields)              │
    │  · Tesseract-v2 cross-check baseline                     │
    └────────────────────────┬────────────────────────────────┘
                             ▼
    ┌─────────────────────────────────────────────────────────┐
    │  PHASE 1 · THE OFFERING (獻禮)                           │
    │  "They opened their treasures" — Matthew 2:11            │
    │                                                         │
    │  GOLD (金) — Visual Verification                         │
    │  · Sole visual authority (multimodal delegate)           │
    │  · Per-segment: image vs OCR → corrected text            │
    │  · Error classification: CHAR / LAYOUT / OMISSION /      │
    │    HALLUCINATION                                         │
    │  · Per-segment confidence: 0.0–1.0 with rationale        │
    │  · Tesseract-v2 cross-check on every correction          │
    └────────────────────────┬────────────────────────────────┘
                             ▼
          ┌──────────────────┴──────────────────┐
          ▼                                     ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│ FRANKINCENSE (乳香)      │    │ MYRRH (沒藥)             │
│ Semantic Classification  │    │ Adversarial Audit        │
│                          │    │                          │
│ "Does the error change   │    │ "If QUINTE reads this    │
│  meaning?"               │    │  uncorrected, what       │
│                          │    │  governance decision      │
│ Classifies Gold's        │    │  breaks?"                │
│ errors:                  │    │                          │
│ · COSMETIC               │    │ · Simulates downstream   │
│ · LEXICAL                │    │   QUINTE processing      │
│ · SEMANTIC               │    │ · Identifies blind spots │
│ · STRUCTURAL             │    │ · Ranked impact:         │
│ · QUINTE_CRITICAL        │    │   CRITICAL / MODERATE /  │
│                          │    │   COSMETIC               │
│ (text-only delegate)     │    │ (text-only delegate)     │
└────────────┬─────────────┘    └────────────┬─────────────┘
             └──────────────┬───────────────┘
                            ▼
    ┌─────────────────────────────────────────────────────────┐
    │  PHASE 3 · THE MANGER (馬槽)                             │
    │  "They fell down, and worshipped him" — Matthew 2:11    │
    │                                                         │
    │  « Convergence Gate »                                    │
    │                                                         │
    │  Weighted evaluation:                                    │
    │  · Visual (0.4): Gold confidence + cross-check           │
    │  · Semantic (0.3): Frankincense classification           │
    │  · Risk (0.3): Myrrh CRITICAL risks addressed            │
    │                                                         │
    │  Score ≥0.7 ∧ no unresolved CRITICAL → CONVERGED        │
    │  Score <0.7 ∨ CRITICAL unresolved → HUMAN REVIEW         │
    └────────────────────────┬────────────────────────────────┘
                             ▼
    ┌─────────────────────────────────────────────────────────┐
    │                    → QUINTE ←                           │
    │  Verified text + per-segment confidence topology         │
    │  QUINTE agents weight claims by source confidence        │
    └─────────────────────────────────────────────────────────┘
</pre></div>

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

## Quick Start

```bash
git clone https://github.com/eric-stone-plus/MAGI.git
cd MAGI

# Read the protocol
cat specs/PROTOCOL.md
```

## For Implementors

| Path | What |
|------|------|
| [specs/PROTOCOL.md](specs/PROTOCOL.md) | Canonical v2.0 protocol specification |
| [specs/archive/](specs/archive/) | Historical v1.x specs |
| [concepts/CONCEPTS.md](concepts/CONCEPTS.md) | Theological and philosophical foundations |
| [prompts/](prompts/) | Gift prompt templates (Gold, Frankincense, Myrrh) |

## License

MIT — the protocol and orchestration layer.
