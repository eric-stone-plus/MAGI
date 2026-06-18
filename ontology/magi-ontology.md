# MAGI Ontology

> Structural ontology of the MAGI lightweight pre-verification protocol. Conceptual foundation in [RASHOMON ontology](../../RASHOMON/ontology/rashomon-ontology.md).

## Entity Catalog

### Delegate (Three Models)

| ID | Name | Model | Function |
|----|------|-------|----------|
| Au | Gold | mimo-v2.5 | Factual verification |
| Fr | Frankincense | kimi (Andante) | Contextual reasoning |
| My | Myrrh | DeepSeek v4-pro | Adversarial audit |

**Constraint**: No two delegates may use the same base model. Three different training distributions required.

### Gate

| Gate | Condition | Outcome |
|------|-----------|---------|
| Convergence | ≥2/3 agree | Answer adopted with [MAGI N/3] annotation |
| Divergence | ≤1/3 agree | Escalate to QUINTE |

Binary only. No intermediate states. No weighted voting.

### Escalation Path

| hm Confidence | Action |
|---------------|--------|
| High | Answer directly |
| Uncertain | MAGI (3 delegates → converge/diverge) |
| Conclusion-grade | Direct QUINTE |

## Relation Catalog

| Relation | From | To | Cardinality |
|----------|------|----|-------------|
| dispatches | hm | Au, Fr, My | 1:3 parallel |
| evaluates | hm | convergence gate | 1:1 per dispatch |
| escalates | MAGI divergence | QUINTE | 1:1 |
| bypasses | conclusion-grade question | MAGI → QUINTE | 1:1 |

## Invariant Catalog

1. **hm triggers MAGI.** User does not.
2. **Three heterogeneous models.** No two delegates share a base model.
3. **Parallel dispatch.** All three run simultaneously.
4. **Blind delegates.** No delegate sees another's output before producing its own.
5. **Binary gate.** ≥2/3 → answer. Otherwise → QUINTE.
6. **Cost cap.** All three unavailable → hm answers with [UNCERTAIN].

## Cross-References

- [RASHOMON ontology](../../RASHOMON/ontology/rashomon-ontology.md) — Conceptual foundation
- [QUINTE PROTOCOL.md](../QUINTE/specs/PROTOCOL.md) — Full debate protocol
- [../specs/PROTOCOL.md](../specs/PROTOCOL.md) — v3.0 canonical spec
- [../specs/theoretical-foundation.md](../specs/theoretical-foundation.md) — Academic foundations
