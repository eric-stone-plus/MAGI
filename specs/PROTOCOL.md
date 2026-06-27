# MAGI v1.7 — Protocol Specification · Hermes Agent

> **Lightweight heterogeneous pre-verification protocol. hm's self-doubt resolution layer.**
>
> **v1.7 (2026-06-20, aligned 2026-06-28)**: MAGI ecosystem adoption complete: 6-tier error classification across all dispatch paths (magi_dispatch.py v1 unified wrapper for kimi/mimo/rx), JSON sidecard with evidence validation gate (Myrrh), cross-repo consistency check (Fr/mimo). Three doctors dispatchable anytime as standalone pre-verification; inside QUINTE, MAGI is R3 KANSA B only.
>
> *"Where is he that is born King of the Jews? for we have seen his star in the east, and are come to worship him."* — Matthew 2:2

---

## §0 · Naming & Theological Foundation

**MAGI** (マギ / 東方三博士) — the Three Wise Men who followed the star to Bethlehem, bearing Gold, Frankincense, and Myrrh (Matthew 2:1-12).

The three delegates are not merely named after the Gifts — they embody the theological meanings:

- **Gold** — for a King. Incorruptible, the foundation of value. Gold verifies facts: *is this claim true?*
- **Frankincense** — for a Priest. Rising incense, the synthesis that lifts raw data into sacred meaning. Frankincense examines context: *does this hold from another angle?*
- **Myrrh** — for one who would suffer and die. The embalming spice, awareness of mortality. Myrrh audits risk: *what breaks if this is wrong?*

Three persons, one inquiry. Three models, one question. The theological framework is a design narrative — it enriches the protocol's conceptual grammar but generates no testable predictions beyond what the cited ML literature provides.

**Cultural anchor — Evangelion (新世紀エヴァンゲリオン)**: MAGI also references the three biological supercomputers governing Tokyo-3 in Hideaki Anno's *Neon Genesis Evangelion* (1995). Named Melchior, Balthasar, and Casper after the same Wise Men, they vote on every critical decision — majority rule, exactly like MAGI's ≥2/3 convergence gate. Melchior is the scientist (logic), Balthasar the mother (intuition), Casper the woman (pragmatism). When they deadlock, NERV is paralyzed — just as MAGI divergence escalates to QUINTE. The dual anchor — Bethlehem and Tokyo-3 — captures MAGI's essence: three independent minds, one binding vote, and the wisdom that no single perspective sees clearly enough to govern alone.

## §1 · Position in the Ecosystem

MAGI is the antechamber. Three heterogeneous models answer *can this be resolved quickly?*

---

## §2 · Architecture

### 2.1 Trigger

MAGI is **hm-triggered**, not user-triggered. When hm's internal confidence is insufficient, hm dispatches MAGI before answering. The user does not invoke MAGI — hm decides.

Three escalation paths:

| hm's Confidence | Action |
|----------------|--------|
| High | Answer directly |
| Uncertain | MAGI (3 delegates → converge/diverge) |
| Conclusion-grade | Direct QUINTE (bypass MAGI) |

### 2.2 Delegates

Three heterogeneous base models. Not roles on the same model — **different models with different training distributions**.

| Delegate | Cognitive Stance | Function |
|----------|-----------------|----------|
| **Gold** | Factual verification | *is this claim correct?* |
| **Frankincense** | Contextual reasoning | *does this hold from another angle?* |
| **Myrrh** | Adversarial audit | *what breaks if this is wrong?* |

All three delegates dispatched in parallel via independent execution contexts (Hermes `terminal(background=true)` + native CLI, or unified `magi_dispatch.py` wrapper). Each receives the same question. Each answers independently in their own context. No delegate sees another's output.

**Dispatch (v1.7)**: `magi_dispatch.py v1` — unified wrapper for kimi/mimo/rx. Structured JSON error reporting on stderr: `{"status":"ok|error","class":"auth|rate_limit|timeout|interrupted_recoverable|deprecated|unknown","retry":"..."}`.

### 2.3 JSON Sidecar & Evidence Validation (v1.7)

MAGI delegates append a structured JSON block after their markdown answer:

```json
{
  "verdict": "string",
  "confidence": 0.0-1.0,
  "reasoning_chain": ["string"],
  "evidence_citations": ["file:line or command reference"]
}
```

Markdown is the primary output for convergence gate comparison. JSON is consumed by QUINTE Phase 2 auto-diff.

**Evidence Validation Gate (v1.7 — Myrrh)**: Before QUINTE Phase 2 consumes confidence scores from JSON sidecars, hm MUST verify that all `evidence_citations` resolve to real file:line locations or reproducible command output. Unresolved → `[CITATION_UNVERIFIED]` → claim confidence 0.5× weight. This gate prevents fabricated citations from inflating agent confidence — closing a trust boundary opened by self-reported metadata.

### 2.4 Convergence Gate

hm reads all three outputs. Binary decision:

| Condition | Outcome | Action |
|-----------|---------|--------|
| ≥2/3 agree | **Converge** | hm adopts answer. Annotates: `[MAGI 2/3]` or `[MAGI 3/3]`. |
| ≤1/3 agree | **Diverge** | Escalate to QUINTE. Disagreement pattern recorded for KOZO. |

No weighted voting. No confidence score. Binary gate.

### 2.5 QUINTE Boundary (v1.7, aligned to QUINTE v3.5)

MAGI does not substitute for QUINTE R1/R2 agents. Current Hermes integration permits MAGI in exactly three contexts:

- standalone pre-verification before hm answers
- R0 implementation support after a QUINTE PASS
- R3 KANSA Auditor B inside QUINTE

If a QUINTE R1/R2 party fails, recovery and fallback are owned by QUINTE and must use another QUINTE party. MAGI output is R3 evidence only, not R1/R2 voting material.

### 2.6 Cross-Repo Consistency (v1.7 — Fr/mimo)

The `website/` directory within QUINTE is an independent git sub-repo. Before any dispatch script or spec edit, hm MUST grep across both repos. Stale duplicates → sync or annotate `[STALE]`.

---

## §3 · Invariants

1. **hm triggers MAGI.** User does not. MAGI is a tool of hm's judgment, not an external protocol.
2. **Three heterogeneous models.** No two delegates may use the same base model.
3. **Parallel dispatch.** All three run simultaneously. No sequential dependency.
4. **Blind delegates.** No delegate sees another's output before producing its own.
5. **Binary gate.** ≥2/3 → answer. Otherwise → QUINTE. No intermediate states.
6. **Cost cap.** If all three models are unavailable, hm answers directly with `[UNCERTAIN]` annotation.
7. **Error recovery (v1.7).** Any delegate producing 0 bytes → classify error → apply tier-specific recovery (backoff/shrink/resume/skip).
8. **Evidence verification (v1.7).** JSON sidecar `evidence_citations` MUST be verified as resolvable before QUINTE Phase 2 consumption. Fabricated citations → `[CITATION_UNVERIFIED]` → 0.5× confidence weight.
9. **QUINTE boundary.** MAGI is never a QUINTE R1/R2 party or substitute. In QUINTE, MAGI may appear only as R3 KANSA B.

---

## §4 · Relationship to QUINTE

| Dimension | MAGI | QUINTE |
|-----------|------|--------|
| Agents | 3 (heterogeneous base models) | 5 (specialized roles) |
| Rounds | 1 (parallel → gate) | 3 (R1→R2→R3) |
| Decision | Binary gate (2/3) | Dual-consul verdict |
| Failure | Diverge → escalate | Deadlock → human review |
| Cost | Low (3 API calls) | High (15+ API calls) |
| Evidence | Light (answer + reasoning) | Full (claims, evidence, cross-review) |

---

## §5 · Theoretical Foundation

See [theoretical-foundation.md](theoretical-foundation.md).

Primary anchors:
- Zhang et al. (2025) — model heterogeneity as "universal antidote" for multi-agent accuracy
- Clinical Mixed-Vendor (2026) — homogeneous teams share correlated blind spots
- CascadeDebate (2026) — cost-aware cascading from lightweight to heavy debate
- Ensemble LLM Survey (Mienye & Swart, 2025) — systematic categorization of multi-model approaches

---

## §6 · Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.7 | 2026-06-20 | **Standalone release**: 6-tier error classification; magi_dispatch.py v1 unified wrapper; JSON sidecard evidence validation gate; cross-repo consistency check. Fully decoupled from QUINTE R1/R2. Doctors: Gold=kimi, Fr=mimo, Myrrh=rx (deepseek-v4-pro). |
| 1.7a | 2026-06-28 | QUINTE v3.5 alignment: removed the old failed-agent fallback semantics; MAGI may appear inside QUINTE only as R3 KANSA B. |

---

*MAGI v1.7 — 2026-06-20*
*sine ira et studio.*
