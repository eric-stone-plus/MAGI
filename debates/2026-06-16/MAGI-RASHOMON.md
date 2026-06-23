# MAGI × RASHOMON — Should MAGI's Concepts Live in RASHOMON?

> 2026-06-14 · Analysis of MAGI's contribution to RASHOMON's epistemology

## RASHOMON's Current Concept Set

RASHOMON (羅生門) is the epistemological foundation of the ecosystem.
It answers "why" — why multi-perspective inquiry works.

Current concepts in RASHOMON/CONCEPTS.md:
- Rashomon phenomenon (羅生門現象)
- Cross-detection asymmetry (交叉検出の非対称性)
- Partial Order Consensus (JMLR 2023)
- Model Multiplicity (Breiman 2001)
- Rashomon Ratio
- Gate system (四道門)

## Three Concepts MAGI Introduces

### 1. Convergent Offering (収束の獻禮)

**What it is**: Convergence is not voting. It's recognition.
The Magi didn't vote on whether Jesus was the King — they each
independently recognized him. MAGI's convergence gate measures
whether three independent perspectives arrive at the same truth,
not whether a majority agrees.

**Why it belongs in RASHOMON**: This is a fundamentally different
convergence mechanism than QUINTE's vote counting (≥3/5).
RASHOMON should document both:
- QUINTE: convergent by majority (投票的収束)
- MAGI: convergent by recognition (認識的収束)

**RASHOMON mapping**: Extends Partial Order Consensus — some claims
are not orderable (different Gifts see different aspects), but
convergence means all Gifts recognize the same truth despite
seeing it through different lenses.

### 2. Structural Anti-Drift (構造的アンチドリフト)

**What it is**: QUINTE fights agent drift through prompt engineering
(task-first, semantic isolation, mandatory restatement — 三层法).
MAGI fights drift through structural role differentiation:
each Gift has a unique output format. If Gold produces a risk map
instead of verification tables, the structural mismatch immediately
flags drift — no content-level detection needed.

**Why it belongs in RASHOMON**: This is a new anti-drift mechanism
that RASHOMON's framework should document alongside prompt-level
anti-drift. It's more robust because it's architectural, not textual.

**RASHOMON mapping**: New concept. No existing RASHOMON concept covers
structural (format-based) drift detection.

### 3. Confidence Topology (確信トポロジー)

**What it is**: QUINTE produces a binary verdict (PASS/FAIL).
MAGI produces a topology — a map of confidence levels across all claims.
High confidence (verified, uncontested), Medium (supporting evidence
but gaps), Low (weak source, contested). Plus known unknowns.

**Why it belongs in RASHOMON**: The epistemological output of the
protocol is richer. RASHOMON should accommodate both:
- QUINTE: binary verdict (二元判定)
- MAGI: confidence topology (確信トポロジー)

**RASHOMON mapping**: Extends the concept of "convergence" —
convergence is not binary (converged/not converged) but a spectrum.
The confidence topology IS the convergence spectrum.

## Recommendation

YES — all three concepts should be added to RASHOMON/CONCEPTS.md.
They are genuine epistemological contributions, not just implementation
details. RASHOMON is the right home because:

1. They describe WHY multi-perspective inquiry works (not just HOW)
2. They apply to both QUINTE and MAGI (not protocol-specific)
3. They extend RASHOMON's existing mathematical foundations

## What RASHOMON Should NOT Contain

MAGI's implementation details (delegate dispatch, prompt templates,
convergence weights, timeout values) belong in MAGI's own spec,
not in RASHOMON. RASHOMON is theory, not implementation.
