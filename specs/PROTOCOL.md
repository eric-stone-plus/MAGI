1|# MAGI v3.1 — Protocol Specification · Hermes Agent
2|
3|> **Lightweight heterogeneous pre-verification protocol. hm's self-doubt resolution layer.**
4|>
5|> **v3.1 (2026-06-20)**: Expanded deployment model. MAGI is no longer restricted to QUINTE R1 pre-verification. Three doctors (Gold/Fr/Myrrh) can be dispatched independently or collectively at ANY phase of QUINTE or outside it — as on-demand analysis, agent fallback, filesystem exploration, or quick second opinion. Mode A (pre-verification) and Mode B (R1 participant) remain, but neither is exhaustive. Usage: anytime, anywhere, any question.
6|>
7|> *"Where is he that is born King of the Jews? for we have seen his star in the east, and are come to worship him."* — Matthew 2:2
8|
9|---
10|
11|## §0 · Naming & Theological Foundation
12|
13|**MAGI** (マギ / 東方三博士) — the Three Wise Men who followed the star to Bethlehem, bearing Gold, Frankincense, and Myrrh (Matthew 2:1-12).
14|
15|The three delegates are not merely named after the Gifts — they embody the theological meanings:
16|
17|- **Gold** — for a King. Incorruptible, the foundation of value. Gold verifies facts: *is this claim true?*
18|- **Frankincense** — for a Priest. Rising incense, the synthesis that lifts raw data into sacred meaning. Frankincense examines context: *does this hold from another angle?*
19|- **Myrrh** — for one who would suffer and die. The embalming spice, awareness of mortality. Myrrh audits risk: *what breaks if this is wrong?*
20|
21|Three persons, one inquiry. Three models, one question. The theological framework is a design narrative — it enriches the protocol's conceptual grammar but generates no testable predictions beyond what the cited ML literature provides.

**Cultural anchor — Evangelion (新世紀エヴァンゲリオン)**: MAGI also references the three biological supercomputers governing Tokyo-3 in Hideaki Anno's *Neon Genesis Evangelion* (1995). Named Melchior, Balthasar, and Casper after the same Wise Men, they vote on every critical decision — majority rule, exactly like MAGI's ≥2/3 convergence gate. Melchior is the scientist (logic), Balthasar the mother (intuition), Casper the woman (pragmatism). When they deadlock, NERV is paralyzed — just as MAGI divergence escalates to QUINTE. The dual anchor — Bethlehem and Tokyo-3 — captures MAGI's essence: three independent minds, one binding vote, and the wisdom that no single perspective sees clearly enough to govern alone.
22|
23|## §1 · Position in the Ecosystem
24|
25|```
26|RASHOMON (why) → QUINTE (how heavy) → KANSA (監査)
                       │
                 ┌─────┴─────┐
           MAGI (Mode A)   MAGI (Mode B)
           antechamber     R1 5th element
```

MAGI is both the antechamber AND a senator. Mode A: three heterogeneous models answer *can this be resolved quickly?* Mode B (v3.3+): MAGI enters QUINTE R1 as an embedded collective element, internal convergence gate ACTIVE, one vote.
32|
33|---
34|
35|## §2 · Architecture
36|
37|### 2.1 Trigger
38|
39|MAGI is **hm-triggered**, not user-triggered. When hm's internal confidence is insufficient, hm dispatches MAGI before answering. The user does not invoke MAGI — hm decides.
40|
41|Three escalation paths:
42|
43|| hm's Confidence | Action |
44||----------------|--------|
45|| High | Answer directly |
46|| Uncertain | MAGI (3 delegates → converge/diverge) |
47|| Conclusion-grade | Direct QUINTE (bypass MAGI) |

### 2.1a Dual-Mode Operation (v3.3+)

MAGI operates in two mutually exclusive modes:

- **Mode A — Standalone Pre-Verification**: hm uncertain → MAGI → ≥2/3 converge (answer) or diverge (escalate to QUINTE).
- **Mode B — QUINTE R1 Participant**: During QUINTE v3.3+ execution, MAGI enters R1 as one collective element. Internal convergence gate is ACTIVE — three delegates converge (≥2/3) into one output with one vote. Delegates do not participate in R2. Mode A and Mode B cannot both be active in the same session. See [QUINTE v3.3 spec](https://github.com/eric-stone-plus/QUINTE/blob/master/specs/PROTOCOL.md).
48|
49|### 2.2 Delegates
50|
51|Three heterogeneous base models. Not roles on the same model — **different models with different training distributions**.
52|
| Delegate | Cognitive Stance | Function |
|----------|-----------------|----------|
| **Gold** | Factual verification | *is this claim correct?* |
| **Frankincense** | Contextual reasoning | *does this hold from another angle?* |
| **Myrrh** | Adversarial audit | *what breaks if this is wrong?*

Three heterogeneous base models. Not roles on the same model — **different models with different training distributions**. Specific model-to-delegate assignments are operational details that live in the Hermes profile, not the protocol spec.
60|
61|All three delegates dispatched in parallel via independent execution contexts (e.g., Hermes `terminal(background=true)` + native CLI). Each receives the same question. Each answers independently in their own context. No delegate sees another's output. The dispatch mechanism is operational — model-to-delegate assignments and CLI specifics live in the Hermes profile, not the protocol spec.
62|
63|### 2.4 Convergence Gate
64|
65|hm reads all three outputs. Binary decision:
66|
67|| Condition | Outcome | Action |
68||-----------|---------|--------|
69|| ≥2/3 agree | **Converge** | hm adopts answer. Annotates: `[MAGI 2/3]` or `[MAGI 3/3]`. |
70|| ≤1/3 agree | **Diverge** | Escalate to QUINTE. Disagreement pattern recorded for KOZO. |
71|
72|No weighted voting. No confidence score. Binary gate.
73|
74|---
75|
76|## §3 · Invariants
77|
78|1. **hm triggers MAGI.** User does not. MAGI is a tool of hm's judgment, not an external protocol.
79|2. **Three heterogeneous models.** No two delegates may use the same base model.
80|3. **Parallel dispatch.** All three run simultaneously. No sequential dependency.
81|4. **Blind delegates.** No delegate sees another's output before producing its own.
82|5. **Binary gate.** ≥2/3 → answer. Otherwise → QUINTE. No intermediate states.
83|6. **Cost cap.** If all three models are unavailable, hm answers directly with `[UNCERTAIN]` annotation.
84|
85|---
86|
87|## §4 · Relationship to QUINTE
88|
89|| Dimension | MAGI | QUINTE |
90||-----------|------|--------|
91|| Agents | 3 (heterogeneous base models) | 5 (specialized roles) |
92|| Rounds | 1 (parallel → gate) | 3 (R1→R2→R3) |
93|| Decision | Binary gate (2/3) | Dual-consul verdict |
94|| Failure | Diverge → escalate | Deadlock → human review |
95|| Cost | Low (3 API calls) | High (15+ API calls) |
96|| Evidence | Light (answer + reasoning) | Full (claims, evidence, cross-review) |
97|
98|---
99|
100|## §5 · Theoretical Foundation
101|
102|See [theoretical-foundation.md](theoretical-foundation.md).
103|
104|Primary anchors:
105|- Zhang et al. (2025) — model heterogeneity as "universal antidote" for multi-agent accuracy
106|- Clinical Mixed-Vendor (2026) — homogeneous teams share correlated blind spots
107|- CascadeDebate (2026) — cost-aware cascading from lightweight to heavy debate
108|- Ensemble LLM Survey (Mienye & Swart, 2025) — systematic categorization of multi-model approaches
109|
110|---
111|
112|## §6 · Version History
113|
114|| Version | Date | Changes |
115||---------|------|---------|
116|| 2.0 | 2026-06-17 | Gold-dominant OCR verification pipeline |
117|| 3.0 | 2026-06-19 | **Complete redesign**: OCR removed; general-purpose heterogeneous pre-verification; hm-triggered; binary convergence gate; cost-aware escalation to QUINTE |
| 3.1 | 2026-06-20 | **Anytime deployment**: MAGI doctors dispatchable independently or collectively at any QUINTE phase or outside it — on-demand analysis, agent fallback, filesystem exploration, second opinion. Mode A/B remain but non-exhaustive. |
118|
119|---
120|
121|*MAGI v3.1 — 2026-06-20*
122|*sine ira et studio.*
123|