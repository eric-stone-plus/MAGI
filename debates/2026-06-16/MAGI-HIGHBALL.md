# MAGI × HIGHBALL — Does the Constraint Layer Apply?

> 2026-06-14 · Analysis of HIGHBALL's applicability to MAGI

## HIGHBALL Components

HIGHBALL (ハイボール) is the constraint layer:
- **KANSA** (監査) — verdict audit (R3 dual-audit)
- **KENGEN** (権限) — authorization perimeter (push/deploy gate)
- **BANNIN** (番人) — session-level guard (continuous monitoring)
- **KOZO** (小僧) — structural enforcement (format compliance)

## Component-by-Component Analysis

### KANSA (監査) — Verdict Audit

**Applies to MAGI? YES.**

In QUINTE, KANSA is the R3 dual-audit: hm (Consul A) + topic-matched
Auditor B independently draft verdicts. Disagreements are annotated,
not suppressed.

In MAGI, the same pattern applies to Phase 3 (The Manger):
- **Consul A (hm)** evaluates convergence on 3 dimensions
- **Auditor B** independently evaluates the same 3 dimensions
- If scores diverge by >0.2 → flag, don't suppress

The Auditor B mapping:

| MAGI Gift | Auditor B | Rationale |
|-----------|-----------|-----------|
| Gold (verification) | delegate A (if hm holds Myrrh) | Cross-check factual claims |
| Frankincense (synthesis) | delegate B (if hm holds Myrrh) | Cross-check interpretation |
| Myrrh (risk) | hm (if delegates hold Gold+Frankincense) | hm has domain knowledge |

Or: delegate A audits convergence, delegate B audits convergence,
hm merges. Three-way convergence check.

**Implementation**: KANSA for MAGI would be a Phase 3.5 step —
after hm evaluates convergence, a delegate independently evaluates
the same evidence. If scores diverge → annotate, don't force agreement.

### KENGEN (権限) — Authorization Perimeter

**Applies to MAGI? YES, at the boundary.**

MAGI's Phase 4 (Revelation) produces Action Items. If those action
items involve irreversible operations (push, deploy, modify production),
KENGEN's authorization gate applies.

But MAGI is primarily an investigation protocol, not an action protocol.
Most MAGI sessions will produce analysis, not push recommendations.
KENGEN applies only when MAGI's output crosses into action territory.

**Rule**: If MAGI's Action Items include "push", "deploy", "modify",
or "delete" → KENGEN gate activates → user must explicitly authorize.

### BANNIN (番人) — Session-Level Guard

**Applies to MAGI? YES, fully.**

BANNIN monitors the session for:
- hm self-exemption (hm skips Myrrh, goes straight to synthesis)
- Gift confusion (delegate outputs in wrong format)
- Convergence cheating (hm forces ≥0.7 when Gifts clearly disagree)
- Delegate timeout without recovery
- Cross-topic contamination

BANNIN is the continuous monitoring layer. It applies to every phase
of MAGI, just as it applies to every round of QUINTE.

### KOZO (小僧) — Structural Enforcement

**Applies to MAGI? POTENTIALLY.**

KOZO enforces structural compliance. In MAGI's context:
- Each Gift MUST produce its designated output format
- Gold MUST have "## Verified Facts" and "## Confidence Level"
- Frankincense MUST have "## Contextual Synthesis" and "## Narrative"
- Myrrh MUST have "## Risk Map" and "## Fragility Points"

If a Gift's output doesn't match its format → KOZO flags it
as structural drift → automatic retry.

**Implementation**: A post-Phase-1 and post-Phase-2 format check.
If Gold's output lacks "Verified Facts" → kill + retry.

## Summary

| HIGHBALL Component | Applies? | How? |
|-------------------|----------|------|
| KANSA | YES | Phase 3 dual-audit of convergence evaluation |
| KENGEN | YES (at boundary) | Phase 4 action items that cross into push/deploy |
| BANNIN | YES (fully) | Continuous monitoring of all phases |
| KOZO | POTENTIALLY | Post-phase format compliance check |

## Recommendation

HIGHBALL should explicitly reference MAGI as a protocol it constrains.
The current HIGHBALL README references QUINTE — it should also reference
MAGI. The constraint layer is protocol-agnostic: any protocol that
produces conclusions the user might depend on should be guarded by HIGHBALL.
