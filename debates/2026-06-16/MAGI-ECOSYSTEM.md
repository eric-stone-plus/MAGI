# MAGI — Ecosystem Positioning

> 2026-06-14 · How MAGI fits into QUINTE/RASHOMON/HIGHBALL

## The Current Ecosystem

```
RASHOMON (羅生門)    why      epistemology     — 多方视角为何有效
QUINTE   (クインテ)  how      methodology      — 怎么辩论
HIGHBALL (ハイボール) guard    constraint       — 裁决审计 + 执行授权
```

Question: Where does MAGI fit?

## Option A: MAGI as Fourth Repo

```
RASHOMON    why       epistemology
QUINTE      how       methodology (5-agent, DeepSeek, heavy)
HIGHBALL    guard     constraint (KANSA + KENGEN + BANNIN)
MAGI        investigate  inquiry (3-agent, mimo, light)
```

MAGI would be a fourth repo answering "how" — but a different "how" than QUINTE.
QUINTE asks "how do we debate?" MAGI asks "how do we investigate?"

**Problem**: This fragments the ecosystem. Four repos for what is essentially
one protocol family.

## Option B: MAGI Inside QUINTE

MAGI as a module within QUINTE — like QUINTE-LITE was, but with its own
architecture rather than being a stripped-down QUINTE.

```
QUINTE/
├── spec/PROTOCOL.md          # Full 5-agent protocol
├── spec/MAGI.md              # 3-agent dialectical spiral
├── lib/magi.py               # MAGI engine
└── ...
```

**Problem**: MAGI has a fundamentally different architecture (spiral vs cross,
Gifts vs undifferentiated agents, confidence topology vs binary verdict).
Putting it inside QUINTE obscures its distinctiveness.

## Option C: MAGI as RASHOMON Application

RASHOMON is the epistemological foundation — the "why" of multi-perspective inquiry.
MAGI is an application of RASHOMON's principles, just as QUINTE is.

```
RASHOMON (epistemology)
  ├── QUINTE (methodology: 5-agent cross-review)
  └── MAGI  (methodology: 3-agent dialectical spiral)
HIGHBALL (constraint layer on top of both)
```

This is the cleanest mapping. RASHOMON provides the theoretical foundation.
QUINTE and MAGI are two different implementations of the same insight:
"single perspective cannot be trusted."

**RASHOMON's existing concepts that apply to MAGI:**

| RASHOMON Concept | MAGI Mapping |
|------------------|--------------|
| Rashomon phenomenon | Three Magi seeing the same star through different eyes |
| Cross-detection asymmetry | Spiral review — each Gift sees what the previous missed |
| Partial Order Consensus | Convergence gate — not all claims are comparable |
| Model Multiplicity | Same model (mimo), but role multiplicity (Gold/Frankincense/Myrrh) |
| Gate system | Single gate (The Manger) vs QUINTE's four gates |

**New RASHOMON concepts MAGI introduces:**

1. **Convergent Offering** (収束の獻禮) — the idea that convergence is not
   about voting but about recognizing the same truth from different angles.
   The Magi didn't vote on whether Jesus was the King — they each
   independently recognized him.

2. **Structural Anti-Drift** (構造的アンチドリフト) — QUINTE fights drift
   through prompt engineering (三层法). MAGI fights drift through role
   differentiation (each Gift has a unique output format). This is a
   fundamentally different anti-drift mechanism that RASHOMON should document.

3. **Confidence Topology** (確信トポロジー) — QUINTE produces a binary verdict.
   MAGI produces a map of confidence levels. This is a richer epistemological
   output that RASHOMON's framework should accommodate.

## Option D: MAGI as HIGHBALL Application

Does HIGHBALL's constraint layer apply to MAGI?

| HIGHBALL Component | Applies to MAGI? | How? |
|-------------------|-----------------|------|
| **KANSA** (監査) | YES | R3 dual-audit — hm's convergence evaluation audited by a second arbiter |
| **KENGEN** (権限) | YES | Phase 4 (Revelation) produces action items — push/modify/deploy still need user authorization |
| **BANNIN** (番人) | YES | Session-level guard — monitors for hm self-exemption, Gift confusion, convergence cheating |
| **KOZO** (小僧) | MAYBE | Structural enforcement — could enforce Gift output format compliance |

HIGHBALL is the constraint layer. It should apply to ANY protocol that
produces conclusions the user might depend on. MAGI is no exception.

## Recommended Architecture

```
RASHOMON (epistemology — why)
  ├── CONCEPTS.md updated with:
  │   ├── Convergent Offering
  │   ├── Structural Anti-Drift
  │   └── Confidence Topology
  │
  ├── QUINTE (methodology — how, heavy)
  │   ├── spec/PROTOCOL.md (5-agent, DeepSeek, cross-review)
  │   └── hermes-skill/ (reference implementation)
  │
  └── MAGI (methodology — how, light)
      ├── spec/PROTOCOL.md (3-agent, mimo, spiral)
      └── lib/magi.py (reference engine)

HIGHBALL (constraint — guard)
  ├── KANSA: applies to both QUINTE and MAGI verdicts
  ├── KENGEN: applies to both QUINTE and MAGI action items
  └── BANNIN: applies to both QUINTE and MAGI sessions
```

## Integration: MAGI → QUINTE Pipeline

The intended workflow:

```
1. User has a question
2. MAGI investigates (3-agent spiral, ~3min, free)
3. MAGI produces Revelation (confidence topology)
4. If high-stakes decision needed:
   → Feed MAGI's Revelation into QUINTE as R1 evidence
   → QUINTE does full 5-agent cross-review
   → QUINTE R3 produces authorized verdict
5. If push/deploy needed:
   → HIGHBALL KENGEN gate checks authorization
```

MAGI is the investigative arm. QUINTE is the judicial arm.
HIGHBALL is the executive guard.

## Decision Pending

- [ ] Does MAGI become a fourth repo, or live inside QUINTE?
- [ ] Should RASHOMON be updated with MAGI's new concepts?
- [ ] Should HIGHBALL explicitly reference MAGI alongside QUINTE?
- [ ] Does MAGI need its own HIGHBALL-style constraint layer?
