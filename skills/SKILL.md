---
name: magi
description: "MAGI v1.7 - three-delegate heterogeneous audit for standalone checks, post-QUINTE R0 implementation, and QUINTE R3 KANSA B. Never participates in QUINTE R1/R2."
spec: "https://github.com/eric-stone-plus/MAGI/blob/master/specs/PROTOCOL.md"
version: "1.7"
triggers:
  - "magi"
  - "kansa-b"
---

# MAGI v1.7

## Boundary

MAGI is a separate heterogeneous audit protocol from QUINTE.

MAGI may run in exactly three contexts:

| Context | Role |
|---------|------|
| Standalone | pre-verification when hm is uncertain |
| R0 after QUINTE | implementation support after a QUINTE PASS |
| R3 inside QUINTE | KANSA B for the dual-consul verdict |

MAGI never participates in QUINTE R1/R2 and never substitutes for failed QUINTE debate parties.

## Three Delegates

The public protocol defines roles, not provider bindings. Concrete model and CLI mappings live in the platform core-rules profiles. A valid MAGI deployment preserves three-way heterogeneity: no two delegates should collapse onto the same base model unless the verdict is explicitly degraded.

| Delegate | Function | Operational stance |
|----------|----------|--------------------|
| Gold | factual verification | establish what is true and design the fix when edits are needed |
| Frankincense | contextual reasoning | inspect surrounding files, assumptions, and stragglers |
| Myrrh | adversarial audit | verify runtime behavior and identify what breaks if the answer is wrong |

## Pipeline

MAGI can be used as a compact three-delegate vote or as an operational audit pipeline. Platform profiles may implement more detailed dispatch mechanics, but the role boundary stays the same.

| Phase | Actor | Purpose |
|-------|-------|---------|
| 0. Discover | non-LLM search | find relevant files and scope |
| 1. Survey | Gold / Frankincense | read bounded inputs and summarize facts |
| 2. Diagnose | Gold | root cause and fix specification |
| 3. Verify | Myrrh | adversarial check of the diagnosis |
| 4. Attack | Gold | apply the verified fix when file edits are required |
| 5. Post-Verify | Frankincense / Myrrh | confirm the edit landed cleanly and no stragglers remain |

Read-only tasks may stop after convergence. File modifications require attack plus post-verify.

## Dispatch Rules

- Dispatch all three delegates independently; do not route them through a parent model.
- Use real CLI processes in separate execution contexts.
- Use file-based prompts for long tasks or prompts containing code, paths, or shell-sensitive characters.
- Capture output with `> file 2>&1`; do not use `tee` as the primary capture path.
- Do not use `delegate_task` for MAGI dispatch because it destroys model heterogeneity.
- Do not let any delegate read another delegate's output before producing its own first answer.

## Gate

| Result | Action |
|--------|--------|
| 3/3 agree | accept as `[MAGI 3/3]` |
| 2/3 agree | accept as `[MAGI 2/3]` with dissent noted |
| 1/3 or 0/3 agree | escalate to QUINTE or human review |

All three delegates are expected. If a delegate fails, classify the failure and retry or substitute within the MAGI profile. If fewer than two valid delegate outputs remain after recovery, do not silently produce an hm-solo verdict.

## QUINTE Boundary

When invoked by QUINTE, MAGI is R3 KANSA B only. It reviews R1/R2 evidence and draft verdict context, then votes internally through the MAGI gate.

MAGI output from a prior standalone audit must not become a self-referential veto in R3. R3 input should be the QUINTE R1/R2 record plus the draft verdict context.

MAGI has no R1/R2 authority:

- no R1/R2 debate-party status
- no R1/R2 fallback status
- no R1/R2 audit veto
- no replacement for QUINTE's five-party dispatch

## File Modification Gate

For code, system configuration, agent constitution, deployment, or other high-impact file edits, hm should route implementation through MAGI rather than patching solo. The minimum acceptable edit flow is:

```text
Discover -> Diagnose -> Attack -> Post-Verify
```

## Public / Platform Boundary

This public skill is the protocol contract. It intentionally does not hardcode private paths, API keys, provider names, pricing assumptions, or per-machine command flags. Platform repos define those dispatch details and must preserve the boundary above.
