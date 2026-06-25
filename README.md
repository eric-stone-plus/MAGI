<div align="center">

<img src="assets/magi-cover.svg?v=5" alt="MAGI" width="100%">

# MAGI (マギ) · Hermes Agent Protocol

**Cross-cutting heterogeneous audit layer + standalone pre-verification — hm's uncertainty resolver.**

When hm is uncertain, MAGI dispatches three base models in parallel. Each brings a different cognitive stance. Converge → answer. Diverge → escalate to QUINTE.

> *"Where is he that is born King of the Jews? for we have seen his star in the east, and are come to worship him."* — Matthew 2:2

---

[![Protocol](https://img.shields.io/badge/protocol-v1.6-blue?style=flat)](specs/PROTOCOL.md)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)

</div>

---

## What is MAGI?

MAGI is hm's self-doubt mechanism and an inseparable part of QUINTE v1.6. Not merely a user-facing tool — both an internal escalation pathway (Mode A) and a cross-cutting audit layer.

```
User asks hm
  │
  ├─ hm is confident → answer directly
  ├─ hm is uncertain → MAGI dispatches 3 delegates
  │     ├─ converge → answer (with confidence annotation)
  │     └─ diverge → escalate to QUINTE (5-element full debate)
  └─ conclusion-grade question → direct QUINTE
```

MAGI answers: *before I burn 5 agents on a full debate, can 3 heterogeneous models resolve this quickly?*

## The Three Delegates

Not three roles — three base models. Each brings a different training distribution, architecture, and inductive bias. Zhang et al. (2025) showed that model heterogeneity is the critical factor in multi-agent accuracy gains. MAGI implements this at the lowest level.

| Delegate | Cognitive Stance | Function |
|----------|-----------------|----------|
| **Gold** | Factual verification | *is this claim correct?* |
| **Frankincense** | Contextual reasoning | *does this hold from another angle?* |
| **Myrrh** | Adversarial audit | *what breaks if this is wrong?* |

MAGI v1.6: Gold=codex/gpt-5.4, Fr=kimi, Myrrh=mimo

## Convergence Gate

| Outcome | Condition | Action |
|---------|-----------|--------|
| **Converge** | ≥2/3 agree | Answer adopted. Confidence annotated (2/3 = moderate, 3/3 = high). |
| **Diverge** | ≤1/3 agree | Escalate to QUINTE. Disagreement pattern recorded. |

No weighting, no scoring, no "convergence score." Binary gate: enough agreement to proceed, or not enough.

## Relationship to QUINTE

MAGI is an inseparable part of QUINTE v1.6. Not an external filter — a senator with dual citizenship.

| | QUINTE | MAGI |
|-|--------|------|
| Trigger | User or Shōmon gate (evidence gate) | hm's internal uncertainty |
| Audit layer | Cross-cutting heterogeneous audit alongside all phases | 3 delegates (Gold+Fr+Myrrh) converge internally → advisory annotation |
| Rounds | 3 (R1→R2→R3) | 1 (parallel → converge/diverge) |
| Cost | High | Low (3 API calls) |
| Failure | Deadlock → human review | Diverge → escalate to QUINTE R2+ |

**Dual citizenship:** Mode A — MAGI is the antechamber, filtering questions before the Senate convenes. Cross-cutting audit layer (v1.6+) — MAGI operates alongside every QUINTE phase as a heterogeneous audit layer, providing advisory annotations. Bethlehem does not observe Rome from outside.

## Delegate Routing

The protocol is model-agnostic — any three heterogeneous base models satisfy the architecture. Platform-specific dispatch details are documented in the private core-rules profiles.

## Implementation

MAGI runs on a model-agnostic agent runtime. Three delegates dispatched in parallel via independent execution contexts. hm adjudicates convergence.

| Path | What |
|------|------|
| [specs/PROTOCOL.md](specs/PROTOCOL.md) | Canonical v1.6 protocol specification |
| [specs/theoretical-foundation.md](specs/theoretical-foundation.md) | Academic foundations |
| [ontology/](ontology/) | Protocol ontology |

## License

MIT — the protocol and orchestration layer.

## Cultural Anchors

- **Matthew 2:1-12** — Three wise men follow the star to Bethlehem, bearing gold, frankincense, and myrrh. Three gifts, three perspectives, one truth sought from different directions.
- **Hideaki Anno**, *Neon Genesis Evangelion* (1995) — The MAGI supercomputer system governing Tokyo-3: Melchior (scientist/logic), Balthasar (mother/intuition), Casper (woman/pragmatism). Three biological computers vote on every critical decision — majority rule, exactly like MAGI's ≥2/3 convergence gate. When they deadlock, NERV is paralyzed.

## References

1. Zhang, H. et al. (2025). Stop Overvaluing Multi-Agent Debate. arXiv:2502.08788.
2. Clinical Mixed-Vendor (2026). Do Mixed-Vendor Multi-Agent LLMs Improve Clinical Diagnosis? *EACL 2026 HeaLing Workshop*. arXiv:2603.04421.
3. Du, Y. et al. (2023). Multiagent Debate. *ICML 2024*. arXiv:2305.14325.
4. CascadeDebate: Multi-Agent Deliberation for Cost-Aware LLM Cascades (2026). arXiv:2604.12262.
5. Mienye, I.D. & Swart, T.G. (2025). Ensemble Large Language Models: A Survey. *Information*, 16(8), 688.
6. Wang, X. et al. (2022). Self-Consistency Improves Chain of Thought Reasoning. *ICLR 2023*. arXiv:2203.11171.
