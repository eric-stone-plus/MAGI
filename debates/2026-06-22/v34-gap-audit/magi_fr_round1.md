# MAGI Frankincense — R1 Gap Audit (SOUL.md + SKILL.md vs QUINTE v3.4)

**Scope**: Structural v3.4 features requested for focused comparison: JSON sidecar, Evidence Gate, 6-tier error classification, rx quality gate.
**Method**: Direct read of SOUL.md, SKILL.md, r1_context.md; targeted `grep` for each feature string in both files.
**Status**: All four structural features are **missing** from both constitution files.

---

## 1. JSON sidecar

**Spec expectation** (r1_context.md L3-4): Every MAGI output appends a structured block containing `verdict` / `confidence` / `reasoning_chain` / `evidence_citations`.

| File | Present? | Evidence |
|------|----------|----------|
| SOUL.md | No | Only occurrence of "sidecar" is OCR-related: SOUL.md L164 `-> ocrmypdf --sidecar fallback for scanned documents`. No MAGI output schema defined. |
| SKILL.md | No | No matches for `sidecar`, `JSON`, `verdict`, `confidence`, `reasoning_chain`, or `evidence_citations`. |

**Gap**: Neither file mandates nor describes a machine-readable JSON sidecar appended to MAGI outputs. The concept is absent.

---

## 2. Evidence Validation Gate

**Spec expectation** (r1_context.md L5-6): Myrrh verifies that citations resolve to real `file:line`; fake citations receive a `0.5x` weight penalty.

| File | Present? | Evidence |
|------|----------|----------|
| SOUL.md | No | No matches for `Evidence Validation Gate`, `Myrrh verifies`, `0.5x weight`, or `fake citations`. Kyomon requires evidence anchoring but has no automated Myrrh verification gate. |
| SKILL.md | No | No matches for any Evidence Gate keywords. |

**Gap**: The constitution files contain evidence-anchoring discipline (Kyomon), but not the v3.4 Myrrh-run Evidence Validation Gate with the `0.5x` weight rule.

---

## 3. 6-tier error classification

**Spec expectation** (r1_context.md L8): Errors classified as `auth | rate_limit | timeout | interrupted_recoverable | deprecated | unknown`.

| File | Present? | Evidence |
|------|----------|----------|
| SOUL.md | No | No matches for `error classification`, `interrupted_recoverable`, or the six-class taxonomy. |
| SKILL.md | No | No matches for the taxonomy. SKILL.md L78 mentions `deprecated` only in the phrase "`| tee` deprecated", unrelated to error classification. |

**Gap**: The six-tier error taxonomy is not documented in either file. Agent failure handling exists (MAGI substitution, DEGRADED abolition) but lacks structured error classes.

---

## 4. rx quality gate

**Spec expectation** (r1_context.md L9): If rx output is `<1500 chars` and/or contains `<tool_call>`, dispatch a MAGI doctor substitute.

| File | Present? | Evidence |
|------|----------|----------|
| SOUL.md | No | No matches for `rx quality gate`, `1500 chars`, `<tool_call>`, or `MAGI doctor`. SOUL.md L142 notes that rx run mode cannot read files, but there is no length/tool-call quality gate. |
| SKILL.md | No | SKILL.md L141-142 documents the rx run-mode limitation (`reasonix run` cannot read files), but does not define the `<1500 chars` + `<tool_call>` quality gate or the MAGI doctor substitute rule. |

**Gap**: The rx limitation is noted, but the automated quality gate and substitution trigger are missing.

---

## Summary table

| Structural feature | SOUL.md | SKILL.md |
|--------------------|---------|----------|
| JSON sidecar | Missing | Missing |
| Evidence Validation Gate | Missing | Missing |
| 6-tier error classification | Missing | Missing |
| rx quality gate | Missing | Missing |

**Fr R1 verdict**: All four requested structural v3.4 features are absent from SOUL.md and SKILL.md. The files contain related adjacent concepts (Kyomon evidence anchoring, MAGI substitution, rx run-mode limitation) but not the specific v3.4 mechanisms described in r1_context.md. Recommend minimal additive sections to both files to close these gaps.
