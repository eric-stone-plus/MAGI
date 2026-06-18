<div align="center">

<img src="assets/magi-cover.svg?v=5" alt="MAGI" width="100%">

# MAGI (マギ) · Hermes Agent Protocol

**Lightweight heterogeneous pre-verification — hm's uncertainty resolver.**

When hm is uncertain, MAGI dispatches three base models in parallel. Each brings a different cognitive stance. Converge → answer. Diverge → escalate to QUINTE.

> *"Where is he that is born King of the Jews? for we have seen his star in the east, and are come to worship him."* — Matthew 2:2

---

[![Hermes Agent Protocol](https://img.shields.io/badge/Hermes_Agent-v3.0-blue?style=flat)](specs/PROTOCOL.md)
[![License](https://img.shields.io/badge/license-MIT-green?style=flat)](LICENSE)

</div>

---

## What is MAGI?

MAGI is hm's self-doubt mechanism. Not a user-facing tool — an internal escalation pathway.

```
User asks hm
  │
  ├─ hm is confident → answer directly
  ├─ hm is uncertain → MAGI dispatches 3 delegates
  │     ├─ converge → answer (with confidence annotation)
  │     └─ diverge → escalate to QUINTE (5-agent full debate)
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

## Convergence Gate

| Outcome | Condition | Action |
|---------|-----------|--------|
| **Converge** | ≥2/3 agree | Answer adopted. Confidence annotated (2/3 = moderate, 3/3 = high). |
| **Diverge** | ≤1/3 agree | Escalate to QUINTE. Disagreement pattern recorded. |

No weighting, no scoring, no "convergence score." Binary gate: enough agreement to proceed, or not enough.

## Relationship to QUINTE

| | QUINTE | MAGI |
|-|--------|------|
| Trigger | User requests, or hm's 證門 gate | hm's internal uncertainty |
| Agents | 5 (specialized roles) | 3 (heterogeneous base models) |
| Rounds | 3 (R1→R2→R3) | 1 (parallel → converge/diverge) |
| Cost | High | Low (3 API calls) |
| Output | Verdict with evidence | Answer with confidence level |
| Failure | Deadlock → human review | Diverge → escalate to QUINTE |

QUINTE is the Senate. MAGI is the antechamber — three wise men asking *is this worth the Senate's time?*

## Model Routing

Operational details (which model serves which delegate) live in the Hermes profile. The protocol is model-agnostic — any three heterogeneous base models satisfy the architecture.

## Implementation

MAGI runs on [Hermes Agent](https://github.com/nousresearch/hermes-agent). Three delegates dispatched via `delegate_task` in parallel. hm adjudicates convergence.

| Path | What |
|------|------|
| [specs/PROTOCOL.md](specs/PROTOCOL.md) | Canonical v3.0 protocol specification |
| [specs/theoretical-foundation.md](specs/theoretical-foundation.md) | Academic foundations |
| [ontology/](ontology/) | Protocol ontology |

## License

MIT — the protocol and orchestration layer.

## References

1. Zhang, H. et al. (2025). Stop Overvaluing Multi-Agent Debate. arXiv:2502.08788.
2. Clinical Mixed-Vendor (2026). Do Mixed-Vendor Multi-Agent LLMs Improve Clinical Diagnosis? *EACL 2026 HeaLing Workshop*. arXiv:2603.04421.
3. Du, Y. et al. (2023). Multiagent Debate. *ICML 2024*. arXiv:2305.14325.
4. CascadeDebate: Multi-Agent Deliberation for Cost-Aware LLM Cascades (2026). arXiv:2604.12262.
5. Mienye, I.D. & Swart, T.G. (2025). Ensemble Large Language Models: A Survey. *Information*, 16(8), 688.
6. Wang, X. et al. (2022). Self-Consistency Improves Chain of Thought Reasoning. *ICLR 2023*. arXiv:2203.11171.
