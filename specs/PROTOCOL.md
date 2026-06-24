# MAGI v3.5 — Protocol Specification · Hermes Agent

> **Cross-cutting heterogeneous audit layer. hm's self-doubt resolution layer.**
>
> **v3.5 (2026-06-24)**: Synced with QUINTE v3.5. MAGI repositioned as cross-cutting heterogeneous audit layer — always-on alongside QUINTE phases, not a formal debate participant. Three heterogeneous models (Gold, Frankincense, Myrrh — each a different base model with different training distribution) provide the only cross-model signal when all debate agents share the same base model. Internal ≥2/3 convergence produces `[MAGI AUDIT]` annotations; ≤1/3 produces individual annotations. Mode A (standalone pre-verification) and independent anytime deployment remain available.
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

```
RASHOMON (why) → QUINTE (how heavy) → KANSA (監査)
                       │
                MAGI v3.5 audit layer
         (cross-cutting heterogeneous guardrail)
```

MAGI is the antechamber AND the heterogeneity guardrail. Mode A (standalone): three heterogeneous models answer *can this be resolved quickly?* Mode B retired in v3.5 — MAGI no longer sits as an R1 debate participant; it operates as a cross-cutting audit layer alongside every QUINTE phase, providing the only cross-model signal when all 5 debate agents share the same base model.

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

### 2.1a Deployment Modes (v3.5)

MAGI operates as a cross-cutting heterogeneous audit layer during QUINTE v3.5+, plus standalone and anytime deployments (MAGI v3.1+):

- **QUINTE Audit Layer (v3.5 default)**: During QUINTE execution, MAGI's three heterogeneous models dispatch in parallel alongside each phase. Each model audits R1 outputs and R2 cross-examinations; internal ≥2/3 convergence produces a unified `[MAGI AUDIT]` annotation appended to the phase. Findings are advisory — hm weighs them at R3 verdict. This is the only cross-model signal when the 5 formal debate agents share the same base model.
- **Mode A — Standalone Pre-Verification**: hm uncertain → MAGI → ≥2/3 converge (answer) or diverge (escalate to QUINTE).
- **Anytime / Independent (v3.1+)**: MAGI doctors may be dispatched independently or collectively at any QUINTE phase, or outside it, for on-demand analysis, agent fallback, filesystem exploration, or second opinion.

Mode B (R1 participant) retired in v3.5. See [QUINTE v3.5 spec](../../QUINTE/specs/PROTOCOL.md).

### 2.2 Delegates

Three heterogeneous base models. Not roles on the same model — **different models with different training distributions**.

| Delegate | Cognitive Stance | Function |
|----------|-----------------|----------|
| **Gold** | Factual verification | *is this claim correct?* |
| **Frankincense** | Contextual reasoning | *does this hold from another angle?* |
| **Myrrh** | Adversarial audit | *what breaks if this is wrong?* |

All three delegates dispatched in parallel via independent execution contexts (Hermes `terminal(background=true)` + native CLI, or unified `magi_dispatch.py` wrapper). Each receives the same question. Each answers independently in their own context. No delegate sees another's output.

**Dispatch**: Each delegate dispatched via independent execution context. Platform-specific dispatch commands are documented in the private core-rules repository. In QUINTE v3.5+, MAGI also runs as a cross-cutting audit layer alongside R1 and R2, with each delegate receiving the phase outputs for heterogeneity review.

### 2.3 JSON Sidecar & Evidence Validation (v3.4)

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

**Evidence Validation Gate (v3.4 — Myrrh)**: Before QUINTE Phase 2 consumes confidence scores from JSON sidecars, hm MUST verify that all `evidence_citations` resolve to real file:line locations or reproducible command output. Unresolved → `[CITATION_UNVERIFIED]` → claim confidence 0.5× weight. This gate prevents fabricated citations from inflating agent confidence — closing a trust boundary opened by self-reported metadata.

### 2.4 Convergence Gate

In standalone Mode A, hm applies the mechanical binary gate to the three delegate outputs:

| Condition | Outcome | Action |
|-----------|---------|--------|
| ≥2/3 agree | **Converge** | Answer is mechanically adopted. Annotates: `[MAGI 2/3]` or `[MAGI 3/3]`. |
| ≤1/3 agree | **Diverge** | Escalate to QUINTE. Disagreement pattern recorded for KOZO (構造, HIGHBALL attention-quality measurement layer; see [HIGHBALL spec](../../HIGHBALL/README.md#kozo--attention-quality--cross-detection-sensitivity)). |

In QUINTE v3.5+ audit-layer mode, the same ≥2/3 convergence produces a single `[MAGI AUDIT N/3]` annotation appended to the phase output; ≤1/3 produces individual `[MAGI AUDIT 1/3]` annotations. Audit findings are advisory — hm weighs them at R3 verdict.

No weighted voting. No confidence score. Binary gate.

### 2.5 Agent Substitution (v3.4)

When directed by QUINTE v3.5, MAGI doctors serve as fallback for failed core agents:

| Failed Agent | MAGI Substitute | Reason |
|-------------|----------------|--------|
| Debate Agent A | Myrrh | Provider diversity |
| Debate Agent B | Frankincense | Deep file exploration |
| Debate Agent C | Gold | Fast reasoning + external view |
| oc (DS) | Any available | Tool-capable replacement |

Original prompt forwarded directly. 180s deadline. Output annotated `[MAGI: <dr> substituting <agent>]`. Equal voting weight. Substitute failure → degrade, don't block QUINTE.

### 2.6 Cross-Repo Consistency (v3.4)

The `website/` directory within QUINTE is an independent git sub-repo. Before any dispatch script or spec edit, hm MUST grep across both repos. Stale duplicates → sync or annotate `[STALE]`.

---

## §3 · Invariants

1. **hm triggers MAGI.** User does not. MAGI is a tool of hm's judgment, not an external protocol.
2. **Three heterogeneous models.** No two delegates may use the same base model.
3. **Parallel dispatch.** All three run simultaneously. No sequential dependency.
4. **Blind delegates.** No delegate sees another's output before producing its own.
5. **Binary gate.** ≥2/3 → answer. Otherwise → QUINTE. No intermediate states.
6. **Cost cap.** If all three models are unavailable, hm answers directly with `[UNCERTAIN]` annotation.
7. **Error recovery (v3.4).** Any delegate producing 0 bytes → classify error → apply tier-specific recovery (backoff/shrink/resume/skip). Agent interrupted (exit 143) → session resume before substitution.
8. **Evidence verification (v3.4).** JSON sidecar `evidence_citations` MUST be verified as resolvable before QUINTE Phase 2 consumption. Fabricated citations → `[CITATION_UNVERIFIED]` → 0.5× confidence weight.

---

## §4 · Relationship to QUINTE

| Dimension | MAGI | QUINTE |
|-----------|------|--------|
| Agents | 3 (heterogeneous base models) | 5 debate agents (cc/cw/oc/omp/hm) + MAGI audit layer |
| Rounds | 1 in Mode A (parallel → gate); audit layer runs alongside QUINTE R1+R2 | 3 (R1→R2→R3) |
| Decision | Binary gate (2/3) | Dual-consul verdict |
| Failure | Diverge → escalate | Deadlock → human review |
| Cost | Low (3 API calls) | High (15+ API calls) |
| Evidence | Light (answer + reasoning) | Full (claims, evidence, cross-review) |
| Heterogeneity | Only cross-model signal in v3.5 | All debate agents share the same base model without MAGI |

---

## §5 · Theoretical Foundation

See [theoretical-foundation.md](theoretical-foundation.md).

Primary anchors:
- Zhang et al. (2025) — model heterogeneity as "universal antidote" for multi-agent accuracy
- Clinical Mixed-Vendor (2026) — homogeneous teams share correlated blind spots
- CascadeDebate (2026) — cost-aware cascading from lightweight to heavy debate
- Ensemble LLM Survey (Mienye & Swart, 2025) — systematic categorization of multi-model approaches

---

## §7 · Operational Phases

Six-phase pipeline derived from heterogeneous model behavior patterns.

| Phase | Role | Timeout | Rules |
|-------|------|---------|-------|
| 0. Discover | Find files matching pattern, return paths only | 60s | Non-LLM tools only. Do not read contents. |
| 1. Survey | Read specified files, structured summary per file | 120s/file, 600s total | No search. Exact file paths. Size cap 1MB. |
| 2. Diagnose | Synthesize survey → root cause + precise fix | 300s | Structured output required. |
| 3. Verify | Adversarial: find flaws in diagnosis | 180s | Must not see survey output. Similarity check. |
| 4. Attack | Apply verified fix with line-level precision | 60s | Pre-flight snapshot. Diff verification. |
| 5. Post-Verify | Checklist verification of applied fix | 120s | On fail: rollback → loop to phase 2 (max 3). |

### Iron Rules

1. No rabbit holes. Stay on task, don't follow tangents. If a file references history/related topics, ignore them. Read only the specified files/line ranges, answer only the specified question.
2. The survey model must never read files in its own output directory, including any files it has written.
3. Survey model output goes to stdout; hm saves with shell redirect. Survey model must never read files in its own output directory.
4. Phases 0-3 (discover, survey, diagnose, verify) may run concurrently where independent. Phases 4-5 (attack, post-verify) are serial after diagnose.
5. Before killing any process: `process log > archive` first.
6. Every phase has explicit timeout + output size cap.
7. Max 5 invocations per session, max 3 diagnosis→attack loops.
8. Discovery (phase 0) may use non-LLM grep or cheap model — never the survey model.
9. Human gates at post-diagnosis and post-attack for irreversible changes.

### Failure Mode Map

| Symptom | Model | Root Cause | Fix |
|---------|-------|-----------|-----|
| Survey output >100MB, self-referencing | survey | Search tool matched own output | Phase 1 only: read file paths, no search. Discovery done in phase 0. |
| Verify output quotes survey verbatim | verify | Given survey output as reference | Phase 3: adversarial prompt, independence similarity check. |
| Reasoning 29min no output, reading history | reasoning | Rabbit hole: followed tangents instead of staying on task | No rabbit holes: read only specified files, answer only specified question. |
| Survey output file corrupted with null bytes | survey | Survey model read its own output file, triggering recursive write bug | Survey output to stdout; hm saves with shell redirect. Survey must never read its own output directory. |
| Debate agents 0-byte output | debate agents | Authentication or CLI configuration issue | Verify agent authentication before dispatch. |

---

## §8 · Roadmap

### 8.1 BANNIN Code-Level Enforcement (next upgrade)

Current BANNIN is a session-log grep (`lib/bannin.sh`). Next upgrade priorities:

1. **Authorization tokens**: Cryptographic, one-use, time-bound tokens bound to exact commands. Replaces keyword grep.
2. **Command allowlist**: Exact command form matching with flag normalization. No regex bypass.
3. **Protected-file manifest**: Machine-readable list of architecture-critical paths per repo. Pre-write hash verification.
4. **Session isolation**: BANNIN runs outside the guarded agent process. Agent cannot read/write auth tokens or BANNIN configuration.
5. **Structured audit log**: Append-only JSON log outside agent working directory.

### 8.2 hm Auto-Trigger MAGI Dispatch

hm currently decides subjectively when to dispatch MAGI. Next upgrade:

1. **Pre-modification hook**: Before any `patch`/`write_file` to a constitutional file, automatically trigger MAGI dispatch.
2. **Confidence threshold**: If hm's internal confidence score falls below threshold, trigger MAGI without hm needing to decide.
3. **Verifiable trigger trail**: Every MAGI dispatch records trigger reason (pre-modification hook / confidence threshold / manual) in structured log.

---

## §6 · Version History

| Version | Date | Changes |
|---------|------|---------|
| 2.0 | 2026-06-17 | Gold-dominant OCR verification pipeline |
| 3.0 | 2026-06-19 | **Complete redesign**: OCR removed; general-purpose heterogeneous pre-verification; hm-triggered; binary convergence gate; cost-aware escalation to QUINTE |
| 3.1 | 2026-06-20 | **Anytime deployment**: MAGI doctors dispatchable independently or collectively at any QUINTE phase or outside it — on-demand analysis, agent fallback, filesystem exploration, second opinion. Mode A/B remain but non-exhaustive. |
| 3.4 | 2026-06-20 | **QUINTE v3.4 sync**: 6-tier error classification (auth/rate_limit/timeout/interrupted_recoverable/deprecated/unknown); magi_dispatch.py v1 unified wrapper; Grok exit 143 session resume; JSON sidecar evidence validation gate; cross-repo consistency check; agent→MAGI substitution table. Invariant #7 added. Synced with QUINTE v3.4. |
| 3.5 | 2026-06-24 | **QUINTE v3.5 sync + operational refinement**: MAGI repositioned from QUINTE R1 participant to cross-cutting heterogeneous audit layer. Mode B retired. Substitution table updated: rx removed, oc added. Six-phase operational pipeline (discover→survey→diagnose→verify→attack→post-verify) based on empirical failure analysis. Dispatch notes and operational details documented in private core-rules repository. See §7. |

---

*MAGI v3.5 — 2026-06-24*
*sine ira et studio.*
