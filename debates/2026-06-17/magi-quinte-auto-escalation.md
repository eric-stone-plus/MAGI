# MAGI→QUINTE Auto-Escalation Pipeline

## Architecture Decision

**Established**: 2026-06-17, QUINTE 4/4 unanimous + R2 cross-review + R3 dual adjudication

**Serial ordering**: MAGI → QUINTE (investigate before govern, free before paid)

**Multi-model MAGI** (Mac): Gold(kimi, multimodal) + Frankincense(mimo, free) + Myrrh(DeepSeek, risk)

## Pipeline

```
USER INPUT
    │
    ▼
雨門 (Amamon Gate) — ambiguous? → CLARIFY
    │
    ▼
Phase -1 Classifier (~2s, hm-only):
  · Operational (push/deploy/protocol/incident)? → QUINTE-direct
  · Investigative? → MAGI
  · Data-intensive? → MAGI + domain Gift prompts
  · Ambiguous? → CLARIFY
  · Check delegate availability
    │
    ▼
MAGI (~3min, serial dispatch):
  Gold (kimi) → Frankincense (mimo) → Myrrh (hm/DeepSeek)
  Phases 0-4 → Confidence Topology
    │
    ▼
6-Gate Escalation (any trigger → escalate):
  G1: Convergence <0.7 after 2 restarts
  G2: Myrrh CRITICAL + Gold factual verification
  G3: Operational action items in Revelation
  G4: Gold-Fr divergence ≥0.3 per claim
  G5: Delegate failure (2+ timeouts/401)
  G6: User override ("quinte")
    │
    ▼
Cost Gate: "QUINTE ~500K DeepSeek tokens. Continue? [Y/n]"
    │
    ▼
QUINTE (~10min):
  R1: confidence-blind (MAGI claims without scores)
  R2: full topology + cross-review
  R3: dual adjudication (hm + KANSA B)
  HIGHBALL KENGEN if push/deploy

Do NOT auto-trigger on: question length, user identity, token estimates, vibes/heuristics.
```

## Key Risks

| Risk | Severity | Mitigation |
|------|----------|------------|
| Same-model blind spot propagation | CRITICAL | Multi-model MAGI (kimi+mimo+DeepSeek) — three model families |
| Silent cost escalation | HIGH | Cost gate: user confirmation before paid QUINTE |
| MAGI-PASS / QUINTE-BLOCKED divergence | HIGH | Meta-review protocol, recalibration trigger |
| hm-solo degradation chain | MEDIUM | Phase -1 checks delegate availability; no auto-escalation if hm-solo |
| Evidence staleness (13min chain) | MEDIUM | Re-sample time-sensitive evidence before QUINTE R1 |

## Provenance

QUINTE audit session 2026-06-17. Full output at `/tmp/quinte-audit/magi-quinte-ordering/`.
