# MAGI — Definition & Positioning

> 2026-06-14 · Initial design

## What MAGI Is

MAGI is a **three-agent dialectical spiral protocol** for grounded inquiry.
Named for the Three Magi who followed the star to Bethlehem (Matthew 2:1-12).

It is NOT:
- A lite version of QUINTE
- A replacement for QUINTE
- A subset of QUINTE with fewer agents

It IS:
- A standalone epistemological protocol with its own architecture
- A complementary tool to QUINTE (MAGI investigates, QUINTE authorizes)
- A structurally different approach to the same problem (multi-perspective truth)

## Core Problem

Single-model AI hits a confidence ceiling. Both QUINTE and MAGI solve this
through multi-agent adversarial analysis. But they solve it differently:

| | QUINTE | MAGI |
|-|--------|------|
| **Approach** | Parallel then cross (flat) | Parallel then spiral (directed) |
| **Diversity** | 5 agents, cross-model (DeepSeek) | 3 agents, same-model (mimo) |
| **Output** | Binary verdict (PASS/FAIL) | Confidence topology (map) |
| **Cost** | Heavy (~10min, expensive) | Light (~3min, free tier) |
| **When** | High-stakes decisions | Investigation, analysis, iteration |

## The Three Gifts (三博士の贈り物)

Each agent carries a **Gift** — an epistemological stance, not just a different prompt:

| Gift | Agent | Cognitive Mode | Core Question |
|------|-------|---------------|---------------|
| **Gold** (金) | delegate A | Verification | "Is this TRUE?" |
| **Frankincense** (乳香) | delegate B | Synthesis | "What does this MEAN?" |
| **Myrrh** (沒藥) | hm | Adversarial | "Where does this BREAK?" |

**Structural anti-drift**: Each Gift has a unique output format.
Gold produces verification tables. Frankincense produces narratives.
Myrrh produces risk maps. If Gold outputs a risk map, the structural
mismatch flags drift — no content-level detection needed.

## Five Phases

```
Phase 0 · The Star (星)         hm structures problem, assigns Gifts
Phase 1 · The Offering (獻禮)   Three parallel analyses
Phase 2 · The Journey (旅路)    Dialectical spiral (each reviews previous)
Phase 3 · The Manger (馬槽)     Convergence gate (≥0.7 = pass)
Phase 4 · The Revelation (啟示) Final verdict with confidence topology
```

## Convergence Gate (The Manger)

Three dimensions, weighted:

| Dimension | Weight | Criterion |
|-----------|--------|-----------|
| Factual | 0.4 | All Gifts agree on verified facts |
| Interpretive | 0.3 | Frankincense's synthesis uncontested |
| Risk | 0.3 | Myrrh's risks addressed |

Score ≥0.7 → converged → Revelation.
Score <0.7 → restart Phase 2 on weakest dimension.
Max 2 restarts (3 total Phase 2 executions).

## Output: Confidence Topology (確信トポロジー)

Not a binary verdict. A map:

| Claim | Confidence | Evidence | Dissent |
|-------|-----------|----------|---------|
| X | High | Gold verified at file:line | None |
| Y | Medium | Frankincense pattern match | Myrrh notes fragility |
| Z | Low | Single source | Myrrh: breaks under [condition] |

Plus: Known Unknowns (既知の未知) + Action Items (行動項目) + Dissent Record (異議記録)

## Christian Typology

Three layers:
1. **The Three Gifts** (Matthew 2:11) — Gold, Frankincense, Myrrh
2. **The Trinity** (三位一体) — three persons, one substance → three perspectives, one verdict
3. **The Apostolic Commission** (Matthew 28:19) — delegates as apostles, commissioned not commanded

Each phase maps to a moment in the Magi's journey:
Star → Offering → Journey → Manger → Revelation (John 8:32)
