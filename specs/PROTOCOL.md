# MAGI v2.0 — Protocol Specification

> **OCR Verification Protocol · QUINTE's Visual Input Layer**
>
> *"Where is he that is born King of the Jews? for we have seen his star
> in the east, and are come to worship him."* — Matthew 2:2

---

## §0 · Naming & Theological Foundation

**MAGI** (マギ / 東方三博士) — the Three Wise Men who followed the star
to Bethlehem, bearing Gold, Frankincense, and Myrrh.

The protocol is built on three layers of Christian typology. These are not
ornament — they are the structural grammar of the protocol. Each Gift is
an epistemological stance; each phase follows the Magi's journey from the
star to the manger; each delegate is an apostle commissioned with a specific
gift and sent forth.

### The Three Gifts (三博士の贈り物 · Matthew 2:11)

Each gift carries a meaning that maps to an epistemological stance:

- **Gold** — for a King. The gift of **verified truth**, incorruptible.
  Gold does not tarnish. Facts verified by Gold are the foundation
  upon which all other analysis rests. In MAGI v2.0, Gold is the *visual
  verifier* — the only apostle with eyes, comparing image to text.
- **Frankincense** — for a Priest. The gift of **sacred pattern**, the ability
  to see meaning beyond the material. Frankincense rises — it is the
  synthesis that lifts raw data into understanding. In MAGI v2.0,
  Frankincense is the *semantic classifier* — determining whether OCR
  errors change meaning.
- **Myrrh** — for one who would suffer and die. The gift of **mortality and
  fragility**, the awareness that all flesh is grass, all structures fragile,
  all conclusions provisional. Myrrh preserves — it is the adversarial
  analysis that keeps truth from decaying into comfortable falsehood.
  In MAGI v2.0, Myrrh is the *adversarial auditor* — asking "if QUINTE
  reads this uncorrected text, what governance decisions break?"

### The Trinity (三位一体 · One God, Three Persons)

The Three Gifts are not three separate analyses — they are three persons
of one inquiry. Gold, Frankincense, and Myrrh are distinct but
inseparable. You cannot have truth without meaning (Gold needs
Frankincense), meaning without truth (Frankincense needs Gold), or
either without the awareness of fragility (both need Myrrh).

This mirrors the Trinity: three persons, one substance. The protocol
does not produce three competing reports — it produces one converged
verdict that contains three perspectives.

### The Apostolic Commission (使徒の委任 · Matthew 28:19-20)

*"Go therefore and make disciples of all nations."*

The delegates are not mere tools — they are apostles, commissioned
with a specific gift and sent forth. Each carries their gift into the
world of evidence and returns with testimony. The apostolic metaphor
is structural: delegates have authority within their domain (Gold
has authority over visual truth, Frankincense over meaning, Myrrh over risk),
but they report back to the convergence gate.

---

## §1 · Architecture — 3-Phase Gold-Dominant Pipeline

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
    │  Input: image + OCR text + segment map                   │
    │  Output: phase0_star bundle                              │
    │  Tesseract-v2 cross-check baseline generated             │
    └────────────────────────┬────────────────────────────────┘
                             ▼
    ┌─────────────────────────────────────────────────────────┐
    │  PHASE 1 · THE OFFERING (獻禮)                           │
    │  "They opened their treasures" — Matthew 2:11            │
    │                                                         │
    │  GOLD (金) — Visual Verification                         │
    │  Sole visual authority (multimodal delegate)             │
    │  Output: phase1_gold (corrected text + per-segment       │
    │  confidence + error classification)                     │
    └────────────────────────┬────────────────────────────────┘
                             ▼
              ┌──────────────┴──────────────┐
              ▼                             ▼
┌──────────────────────────┐    ┌──────────────────────────┐
│ FRANKINCENSE (乳香)      │    │ MYRRH (沒藥)             │
│ Semantic Classification  │    │ Adversarial Audit        │
│ (text-only delegate)     │    │ (text-only delegate)     │
│                          │    │                          │
│ Output: phase2_fr        │    │ Output: phase2_myrrh     │
│ (semantic impact map)    │    │ (risk topology)          │
└────────────┬─────────────┘    └────────────┬─────────────┘
             └──────────────┬───────────────┘
                            ▼
    ┌─────────────────────────────────────────────────────────┐
    │  PHASE 3 · THE MANGER (馬槽)                             │
    │  "They fell down, and worshipped him" — Matthew 2:11    │
    │                                                         │
    │  « Convergence Gate »                                    │
    │  Weighted: Visual(0.4) + Semantic(0.3) + Risk(0.3)      │
    │                                                         │
    │  Output: confidence topology → verified text             │
    │  ≥0.7 → QUINTE    <0.7 → human review                   │
    └────────────────────────┬────────────────────────────────┘
                             ▼
    ┌─────────────────────────────────────────────────────────┐
    │                    → QUINTE ←                           │
    │  Verified text + per-segment confidence topology         │
    └─────────────────────────────────────────────────────────┘
</pre></div>

**Why Gold-dominant, not spiral?** OCR verification has a fundamental
asymmetry: only the multimodal delegate can see the image. The text-only
delegates operate on text descriptions — they cannot independently verify
visual claims. The old 5-phase spiral assumed symmetric evidence access;
v2.0 acknowledges the modal asymmetry by making Gold the sole visual
authority, with Frankincense and Myrrh running in parallel on Gold's
corrected text rather than chaining through sequential review.

### vs QUINTE

| Dimension | QUINTE | MAGI v2.0 |
|-----------|--------|-----------|
| Agents | 5 (orchestrator + 4 participants) | 3 (Gold + Frankincense + Myrrh) |
| Flow | R1 parallel → R2 cross → R3 dual verdict | P1 Gold → P2 Fr+Myrrh parallel → P3 convergence |
| Roles | Undifferentiated | Differentiated (visual / semantic / adversarial) |
| Convergence | Vote counting (≥3/5) | Weighted gate (≥0.7) |
| Model | Provider-agnostic | Provider-agnostic (ideal: three distinct models) |
| Output | PASS / BLOCKED verdict | Verified text + confidence topology |
| Metaphor | Roman Republic — Senate in the Forum | Bethlehem — Three Magi at the Manger |
| Role | Final governance gate | Pre-processing visual input layer |

---

## §2 · The Three Gifts — Specification

### §2.1 · Gold (金 · Visual Verification)

**"Is this text in the image?"**

Gold is the sole visual authority. It inspects the original image and compares
OCR output against what the image actually shows. Gold does not guess — it
cites pixels. Every correction must trace to a location in the source.

**Capabilities:**
- Image inspection with per-segment visual comparison
- Error classification: CHAR (character-level), LAYOUT (column/table corruption),
  OMISSION (text in image missing from OCR), HALLUCINATION (text in OCR absent from image)
- Confidence assignment: 0.0–1.0 per segment with explicit rationale
- Tesseract-v2 cross-check integration

**Limitations:**
- Single visual authority — no second pair of eyes unless a second multimodal delegate is deployed
- Cannot semantically interpret the corrected text (that is Frankincense's domain)
- Legibility ceiling: heavily degraded images may produce low-confidence output

**Per-segment operations:**
1. Read the image segment
2. Compare Tesseract OCR against visual ground truth
3. Classify any discrepancy
4. Produce corrected text
5. Assign confidence with rationale
6. Cross-check against Tesseract-v2

**Output:** `{segment_id, raw_ocr, corrected_text, error_type, confidence, cross_check_status, rationale}`

### §2.2 · Frankincense (乳香 · Semantic Classification)

**"Does the error change meaning?"**

Frankincense receives Gold's corrected text and classifies each error by its
semantic impact. It is the bridge between raw corrections and actionable
understanding — determining not just *what* was fixed, but *whether it matters*.

**Capabilities:**
- Semantic impact classification: COSMETIC, LEXICAL, SEMANTIC, STRUCTURAL, QUINTE_CRITICAL
- Cross-segment pattern recognition — errors concentrated in specific document regions?
- Domain-aware classification — shipping, legal, financial terminology

**Limitations:**
- Cannot verify visual claims — operates on Gold's output, not the original image
- Classification is only as good as the corrected text it receives
- May misclassify domain-specific terms without adequate context

**Per-flagged-segment operations:**
1. Receive Gold's error-flagged segments
2. Classify each by semantic impact
3. Identify cross-segment error patterns
4. Flag QUINTE-critical segments with impact rationale

**Output:** `{segment_id, semantic_class, impact_summary, cross_segment_pattern, quinte_critical_reason}`

### §2.3 · Myrrh (沒藥 · Adversarial Audit)

**"If QUINTE reads this uncorrected, what governance decision breaks?"**

Myrrh is the adversarial conscience. It does not verify Gold's visual claims
(it cannot — it has no eyes). Instead, it asks the question no one wants to
hear: what if we're wrong about being right? Myrrh simulates QUINTE's downstream
processing to identify residual risks in the corrected text.

**Capabilities:**
- QUINTE impact simulation — worst-case plausible misread per segment
- Blind-spot identification — error types Gold is structurally unlikely to catch
- Impact severity ranking: CRITICAL, MODERATE, COSMETIC
- Correction priority ordering — which errors demand immediate attention

**Limitations:**
- Cannot verify visual claims — adversarial analysis is speculative, not confirmed
- Incentivized to find risks — may produce false positives (mitigated by Frankincense plausibility review)
- Dependent on Gold's accuracy — audits corrected text, not original image

**Operations:**
1. Receive Gold's corrected text + confidence topology
2. Simulate downstream QUINTE processing on uncorrected text
3. Identify blind-spot categories (dense numeric tables, low-contrast stamps)
4. Rank impact severity per segment
5. Produce correction priority ranking

**Output:** `{segment_id, worst_case_misread, quinte_impact, blind_spot_category, severity, priority_rank}`

---

## §3 · Convergence Gate (The Manger)

The convergence gate evaluates whether the three Gifts have converged on a
single verified text.

| Dimension | Weight | Criterion |
|-----------|--------|-----------|
| Visual | 0.4 | Gold's per-segment confidence; Tesseract-v2 cross-check agreement |
| Semantic | 0.3 | Frankincense's classification uncontested |
| Risk | 0.3 | Myrrh's CRITICAL risks addressed or flagged |

**Convergence rules:**
- Gold confidence ≥0.9 AND no CROSS_CHECK_CONFLICT → auto-accept
- Gold confidence 0.7–0.9 → accept with flag (QUINTE receives confidence metadata)
- Gold confidence <0.7 OR CROSS_CHECK_CONFLICT OR Frankincense flags QUINTE_CRITICAL
  with Gold confidence <0.95 → route to human review

**Overall threshold:**
- Score ≥0.7 with no unresolved CRITICAL → converged → handoff to QUINTE
- Score <0.7 or CRITICAL unresolved → human review or re-scan

---

## §4 · MAGI→QUINTE Handoff

<div align="center"><pre>
Tesseract OCR → MAGI verification → Confidence Topology → QUINTE governance debate
</pre></div>

MAGI outputs verified text with per-segment confidence topology. QUINTE agents
weight claims by source segment confidence — it is metadata, never a binary
"verified / unverified" flag. A 95% confidence segment is not ground truth;
a 60% confidence segment is not discarded — it enters QUINTE with its
uncertainty intact.

---

## §5 · Pre-filter & Quality Gates

Documents must meet minimum quality thresholds before the Three Gifts are
dispatched:

| Condition | Action |
|-----------|--------|
| Text-layer PDF (zlib extraction successful) | Skip MAGI → route directly to QUINTE |
| Tesseract mean word confidence <60% | Reject → re-scan (illegible document) |
| Tesseract mean word confidence ≥60% | Proceed → dispatch Gold |
| Handwritten or mixed-script document | Flag → route to specialized OCR service |

---

## §6 · Legacy Mode

MAGI v1.x (5-phase dialectical spiral for general investigation) is accessible
via explicit `MAGI/general` mode. The Apostolic Commission continues — v1.x
delegates are not recalled, only redeployed.

---

## §7 · Implementation Notes

**Provider-agnostic.** This protocol does not mandate specific models.
Implementors select delegates based on capability requirements:
- Gold requires a multimodal delegate with visual inspection capability
- Frankincense requires a text-only delegate with strong semantic classification
- Myrrh requires a text-only delegate with strong adversarial reasoning

**Model diversity.** Using different model families for different Gifts
maximizes viewpoint diversity — the three Magi came from different lands.
The protocol is most robust with three distinct models but functions with
fewer. Model routing is a deployment concern, not a protocol requirement.

---

*MAGI v2.0 — QUINTE R1-R3 ratified 2026-06-17.*
