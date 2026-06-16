# MAGI — Protocol Specification

> **M**ulti-agent **A**dversarial **G**rounded **I**nquiry
>
> "Where is he that is born King of the Jews? for we have seen his star
> in the east, and are come to worship him." — Matthew 2:2

---

## §0 · Naming & Theological Foundation

**MAGI** (マギ / 東方三博士) — the Three Wise Men who followed the star
to Bethlehem, bearing Gold, Frankincense, and Myrrh.

The protocol is built on three layers of Christian typology:

### The Three Gifts (三博士の贈り物 · Matthew 2:11)

Each gift carries a meaning that maps to an epistemological stance:

- **Gold** — for a King. The gift of **verified truth**, incorruptible.
  Gold does not tarnish. Facts verified by Gold are the foundation
  upon which all other analysis rests.
- **Frankincense** — for a Priest. The gift of **sacred pattern**, the ability
  to see meaning beyond the material. Frankincense rises — it is the
  synthesis that lifts raw data into understanding.
- **Myrrh** — for one who would suffer and die. The gift of **mortality and
  fragility**, the awareness that all flesh is grass, all structures fragile,
  all conclusions provisional. Myrrh preserves — it is the adversarial
  analysis that keeps truth from decaying into comfortable falsehood.

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

"Go therefore and make disciples of all nations."

The delegates are not mere tools — they are apostles, commissioned
with a specific gift and sent forth. Each carries their gift into the
world of evidence and returns with testimony. The apostolic metaphor
is structural: delegates have authority within their domain (Gold
has authority over facts, Frankincense over meaning, Myrrh over risk),
but they report back to the commission (hm's convergence gate).

---

## §1 · Architecture

```
         ╔═══════════════════════════════════════╗
         ║         MAGI Protocol v1.0            ║
         ║   Dialectical Spiral Architecture     ║
         ╚═══════════════════════════════════════╝

    ┌─────────────────────────────────────────────┐
    │  PHASE 0 · THE STAR (星)                    │
    │  "We have seen his star in the east"        │
    │  hm follows the star — structures the       │
    │  problem, gathers evidence, assigns Gifts   │
    └──────────────────┬──────────────────────────┘
                       ▼
    ┌─────────────────────────────────────────────┐
    │  PHASE 1 · THE OFFERING (獻禮)              │
    │  "They opened their treasures"              │
    │  Gold + Frankincense + Myrrh — PARALLEL     │
    │  Three apostles, three gifts, one manger    │
    └──────────────────┬──────────────────────────┘
                       ▼
    ┌─────────────────────────────────────────────┐
    │  PHASE 2 · THE JOURNEY (旅路)               │
    │  "They departed into their own country      │
    │   another way" — Matthew 2:12               │
    │  Each Gift reviews the previous through     │
    │  its own lens — dialectical spiral          │
    └──────────────────┬──────────────────────────┘
                       ▼
    ┌─────────────────────────────────────────────┐
    │  PHASE 3 · THE MANGER (馬槽)                │
    │  "They saw the young child with Mary        │
    │   his mother, and fell down, and            │
    │   worshipped him" — Matthew 2:11            │
    │  hm evaluates: have the Magi converged?     │
    │  YES → Phase 4 / NO → restart Phase 2      │
    └──────────────────┬──────────────────────────┘
                       ▼
    ┌─────────────────────────────────────────────┐
    │  PHASE 4 · THE REVELATION (啟示)            │
    │  "The truth shall set you free"             │
    │  hm synthesizes final verdict               │
    │  Confidence topology + action items         │
    └─────────────────────────────────────────────┘
```

**vs QUINTE**:

| Dimension | QUINTE | MAGI |
|-----------|--------|------|
| Agents | 5 (hm+cc+cw+omp+rx) | 3 (hm + 2 apostles) |
| Rounds | R1 parallel → R2 cross → R3 verdict | P1 parallel → P2 spiral → P3 convergence → P4 revelation |
| Flow | Flat (parallel then cross) | Helical (each turn builds on the last) |
| Roles | Undifferentiated | Differentiated (Gold/Frankincense/Myrrh) |
| Convergence | Implicit (vote counting) | Explicit (Manger gate with criteria) |
| Model | DeepSeek v4-pro | mimo-v2.5-pro |
| Output | Binary verdict | Confidence topology |
| Metaphor | Roman Republic | Bethlehem · Matthew 2 |
| Gate system | 4 gates (雨門/鏡門/證門/閂門) | 1 gate (The Manger) + Star preparation |
| Anti-drift | Prompt engineering | Structural (Gift role differentiation) |

---

## §2 · The Three Gifts

Each Gift is an epistemological stance — not just a different prompt, but a different
cognitive mode. The apostle assigned to each Gift filters ALL analysis through that lens.

### §2.1 · Gold (金 · Caspar)

**"Is this TRUE? Can I verify it?"**

- Factual accuracy — every claim must trace to evidence
- Numerical precision — no rounding without disclosure
- Source verification — where did this data come from?
- Deductive rigor — if A then B, no handwaving

Gold is the epistemic foundation — without truth, there is nothing to build on.

### §2.2 · Frankincense (乳香 · Melchior)

**"What does this MEAN in context? What patterns emerge?"**

- Contextual analysis — what is the broader picture?
- Pattern recognition — what recurring structures exist?
- Cross-domain synthesis — how does this relate to adjacent fields?
- Narrative coherence — does the story hang together?

Frankincense is the bridge between raw data and actionable understanding.

### §2.3 · Myrrh (沒藥 · Balthasar)

**"Where does this BREAK? What are we not seeing?"**

- Adversarial probing — what could go wrong?
- Fragility mapping — where is the conclusion weakest?
- Blind spot detection — what did the other two miss?
- Anti-fragility — how would the conclusion survive stress testing?

Myrrh is the immune system — it attacks weak conclusions to strengthen the strong ones.

---

## §3 · Phases

### §3.0 · Phase 0 — The Star (星)

*"We have seen his star in the east, and are come to worship him."* — Matthew 2:2

The star was the sign that oriented the Magi's journey. Without it, they would
have wandered. Phase 0 is the same: hm follows the evidence, structures the
problem, and assigns each gift to the apostle best suited to carry it.

hm performs:
1. **Problem decomposition** — break the question into testable sub-claims
2. **Evidence extraction** — gather relevant data (files, documents, code)
3. **Gift assignment** — determine which apostle gets which Gift
4. **Scoping** — define what is in/out of scope

**Star gate** (mandatory): If the problem is ambiguous, hm MUST clarify with
the user before proceeding. The star does not give answers — it gives direction.

### §3.1 · Phase 1 — The Offering (獻禮)

*"And when they had opened their treasures, they presented unto him gifts;
gold, and frankincense, and myrrh."* — Matthew 2:11

Three parallel analyses, each through a distinct lens. The apostles present
their gifts at the same manger — independent perspectives on the same evidence.

Each Gift produces a structured output with:
- Main analysis (verification / synthesis / risk map)
- Key claims with evidence
- Confidence levels (high / medium / low)
- Explicit blind spots
- Guidance for the next Gift in the spiral

### §3.2 · Phase 2 — The Journey (旅路)

*"And being warned of God in a dream that they should not return to Herod,
they departed into their own country another way."* — Matthew 2:12

The Magi's journey was not a straight line. They went first to Jerusalem,
asked at the wrong court (Herod), were sent astray. Only after this detour
did the star reappear and lead them to Bethlehem.

The dialectical spiral mirrors this journey:

```
Gold reviews Myrrh → "Myrrh claims X is a risk. Is this factually grounded?"
Frankincense reviews Gold → "Gold verified facts A, B, C. What pattern emerges?"
Myrrh reviews Frankincense → "Frankincense sees pattern P. Where does it break?"
```

**Spiral depth**: Default 1 full cycle (3 reviews). Max 3 cycles (9 reviews).

### §3.3 · Phase 3 — The Manger (馬槽)

*"They saw the young child with Mary his mother, and fell down, and
worshipped him."* — Matthew 2:11

The Magi arrived at the manger. Have they converged on the same truth?

hm evaluates convergence on three dimensions:

| Dimension | Criterion | Weight |
|-----------|-----------|--------|
| **Factual** | All Gifts agree on verified facts | 0.4 |
| **Interpretive** | Frankincense's synthesis is uncontested | 0.3 |
| **Risk** | Myrrh's risk map has been addressed | 0.3 |

**Convergence score**: weighted sum. ≥0.7 → converged. <0.7 → restart Phase 2.
Max 2 restarts. If still not converged, output with explicit divergence notes.

### §3.4 · Phase 4 — The Revelation (啟示)

*"And ye shall know the truth, and the truth shall make you free."* — John 8:32

The final synthesis. Not a binary verdict, but a **confidence topology** —
a map of what we know, how well we know it, and where the knowledge breaks down.

The Revelation contains:
- **判定 (Verdict)**: Clear, actionable conclusion
- **確信トポロジー (Confidence Topology)**: Every claim rated by confidence
- **既知の未知 (Known Unknowns)**: What we determined we cannot determine
- **行動項目 (Action Items)**: Concrete next steps
- **異議記録 (Dissent Record)**: Unresolved disagreements, preserved not suppressed

---

## §4 · Invocation

All 4 phases. One mode only. Full protocol or nothing.

**Invocation**: "magi [topic]"

MAGI runs on mimo-v2.5-pro exclusively.

---

## §5 · Implementation

### §5.1 · Engine

`lib/magi.py` — the orchestrator. Key functions:

```python
class MagiEngine:
    def follow_star(self, topic: str) -> Problem:
        """Phase 0: Decompose, extract evidence, assign Gifts."""

    def offering(self, problem: Problem) -> ThreeGifts:
        """Phase 1: Parallel analysis through three lenses."""

    def journey(self, gifts: ThreeGifts) -> ThreeGifts:
        """Phase 2: Dialectical spiral."""

    def at_manger(self, gifts: ThreeGifts) -> ConvergenceResult:
        """Phase 3: Evaluate convergence."""

    def revelation(self, gifts: ThreeGifts) -> Verdict:
        """Phase 4: Final synthesis."""

    def run(self, topic: str) -> Verdict:
        """Full protocol execution."""
```

### §5.2 · Apostolic Dispatch

Apostles are dispatched via `delegate_task` with Gift-specific prompts.
Each apostle receives the Gift definition, evidence package, and (in Phase 2)
the previous Gift's output for review.

**Model**: All apostles run mimo-v2.5-pro. No DeepSeek dependency.

### §5.3 · Output Structure

```
/tmp/magi-audit/<topic-slug>/
├── phase0_star.md
├── phase1_gold.md
├── phase1_frankincense.md
├── phase1_myrrh.md
├── phase2_cycle1_{gold,frankincense,myrrh}.md
├── phase3_manger.md
├── phase4_revelation.md
└── manifest.json
```

---

## §6 · Epistemological Commitments

### §6.1 · Testimony (証言)

Every claim must be grounded in evidence. "I believe X" is not a valid Gold
output — "I verified X at [source]" is. Ungrounded assertions are routed
through Myrrh's adversarial filter. This is the epistemological equivalent of
requiring testimony before judgment — no conviction without witnesses.

### §6.2 · Unity in Diversity (多様の中の統一)

Convergence does not require unanimous agreement. The Manger gate measures
alignment on facts, interpretation, and risk — not opinions. Two Gifts can
disagree on interpretation as long as the factual basis is shared and the
disagreement is documented. The Trinity is three persons, one substance —
not three identical copies.

### §6.3 · Revelation (啟示)

The Revelation (Phase 4) explicitly maps what is known, what is uncertain,
and what is unknowable. This tripartite distinction guides resource
allocation: invest where confidence is medium (high ROI), not where it is
already high (diminishing returns) or low (need different evidence).

### §6.4 · Servant Leadership (僕の指導)

hm is always one of the Three Gifts — never pure orchestration. "Whoever
wishes to become great among you shall be your servant" (Mark 10:43).
hm holds a Gift, produces output like any apostle, and submits that output
to the same convergence gate. hm cannot exempt itself from the discipline
it enforces on delegates.

---

## §7 · Constraints

### §7.1 · Token Budget

No artificial limits. MAGI is designed to USE tokens.

### §7.2 · Hard Caps

- Phase 2 spiral: max 3 cycles (9 total reviews)
- Manger gate: max 2 restarts
- Apostle timeout: 300s per apostle per phase
- Total protocol timeout: 1800s (30 min)

### §7.3 · Isolation

Each MAGI topic uses an isolated output directory: `/tmp/magi-audit/<topic-slug>/`.

---

## §8 · Relationship to QUINTE

| | QUINTE | MAGI |
|-|--------|------|
| **Metaphor** | Roman Republic | Bethlehem · Matthew 2 |
| **Use when** | Push authorization, protocol changes | Investigation, analysis, evaluation |
| **Strength** | Multiple independent perspectives | Structured dialectic with confidence maps |
| **Model** | DeepSeek v4-pro | mimo-v2.5-pro |

**Shared DNA**: Evidence-grounded analysis, explicit uncertainty, anti-drift.
**Migration path**: MAGI investigates, QUINTE authorizes.

---

## §9 · Naming Convention

- **MAGI** (マギ) — the protocol
- **Gold** (金) / **Frankincense** (乳香) / **Myrrh** (沒藥) — the Three Gifts
- **The Star** (星) — Phase 0
- **The Offering** (獻禮) — Phase 1
- **The Journey** (旅路) — Phase 2
- **The Manger** (馬槽) — Phase 3
- **The Revelation** (啟示) — Phase 4

English primary + CJK parenthetical.

---

## §10 · Version History

| Date | Version | Change |
|------|---------|--------|
| 2026-06-14 | 1.0 | Initial protocol |
| 2026-06-14 | 1.1 | Christian typology restructure: Trinity, Apostolic Commission, Revelation |

---

*"And when they were come into the house, they saw the young child with
Mary his mother, and fell down, and worshipped him: and when they had
opened their treasures, they presented unto him gifts; gold, and
frankincense, and myrrh."* — Matthew 2:11
