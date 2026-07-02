---
name: magi
description: "MAGI Hermes Agent Protocol - triadic independent inquiry; model/tool bindings unassigned."
spec: "https://github.com/eric-stone-plus/MAGI/blob/main/specs/PROTOCOL.md"
triggers:
  - "magi"
---

# MAGI

## Boundary

MAGI is a Hermes Agent Protocol for triadic independent inquiry. This skill
explains the structure only. It does not select models, select tools, run
agents, assign standing roles, aggregate answers, or authorize edits.

## Frame

Use MAGI as a protocol shape when a conclusion benefits from three
independent perspectives:

- Perspective A states its claim, evidence, and uncertainty.
- Perspective B does the same independently.
- Perspective C does the same independently.
- The synthesis adopts only material convergence and preserves material dissent.
- Action-relevant output preserves a residual trace with source, evidence,
  disposition, closure state, and scope.

The perspectives are placeholders. They are not fixed tools, providers, models,
or people.

## Convergence

Material agreement means a shared claim may be used only with evidence
attached.

Material disagreement means dissent must remain visible.

Missing evidence means the claim remains unresolved.

No weighted voting. No confidence arithmetic. Agreement is a review signal, not
proof.

## Residual Trace

MAGI does not authorize action. For action-relevant findings, emit residuals
with ids, severity, source perspective, evidence, disposition, closure state,
closure evidence, and scope. Leave unresolved high-risk items open or escalated
unless direct evidence or a scoped human waiver exists.
The trace must be compatible with RASHOMON
`schemas/residual-trace.schema.json`.
For action-relevant traces, include a trial manifest with perspective artifacts,
prompt hashes, perturbation axes, independence controls, contamination risks,
and cost.
Include enough evidence, uncertainty, closure state, closure evidence, and
scope for host-side residual quality metrics. Do not self-certify the trace as
high quality.
Treat earlier MAGI outputs as adoption evidence only; do not
rewrite old outputs solely to improve residual-trace metrics.

## Non-Goals

- Do not dispatch tools from this skill.
- Do not infer a current runtime route from historical MAGI implementations.
- Do not treat any third-party position as fixed until an implementation repo or
  host runtime explicitly binds it.
- Do not decide that MAGI is sufficient near an action boundary; HIGHBALL
  residual routing owns that decision.
- If HIGHBALL builds an Action Packet, MAGI supplies only the trace component.
  HIGHBALL owns route decision, validation, quality measurement, and boundary
  decision.
- If later evidence confirms or contradicts the MAGI trace, record that in a
  HIGHBALL outcome ledger. Do not rewrite the trace or self-certify downstream
  success.
