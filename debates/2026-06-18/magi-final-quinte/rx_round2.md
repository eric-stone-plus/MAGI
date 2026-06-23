# R2 rx cross-review: MAGI final

## Role: rx — Logic / Analysis Perspective

Cross-review of all R1 findings (hm, cc, omp) against current state of four canonical sources (SOUL.md, MEMORY.md, SKILL.md, README.md). Fixes applied between R1 and R2 are verified against live file contents.

---

## 1. Fix Verification

### ✅ FIXED — C1 / C1: Gold dispatch stale memory

| Before (MEMORY.md L23) | After |
|---|---|
| `Gold→kimi(-p one-shot batch)` | `Gold→mimo-v2.5主力→kimi batch fallback+DS text tier` |

MEMORY.md L23 now matches L25-27 and all other sources. Grep for `Gold→kimi` returns 0 results. **Fix confirmed.**

### ✅ FIXED — C1.2: per-field vs batch kimi escalation

SKILL.md L71: `kimi batch escalation per-document`
SKILL.md L133: `Clarity gate — batch escalation per-document:`
SKILL.md L475: `batch escalation per-document when mimo confidence < calibrated_threshold`

Grep for `per-field escalation` returns 0 results. All references now say per-document batch. **Fix confirmed.**

### ✅ FIXED — C2 / C2: Version numbers unified

| Source | Before | After |
|---|---|---|
| MEMORY.md L23 | v2.1 | v2.0 |
| SOUL.md L120 | v2.0 (already correct) | v2.0 |
| README.md badge | protocol-v2.0 (already correct) | protocol-v2.0 |

**Residual**: SKILL.md header L4 still says `version: "2.1"` while the description L3 and all body references say `v2.0`. This is a cosmetic inconsistency — SKILL.md is internally split between v2.1 in the YAML header and v2.0 everywhere else. Low severity, but hm_round2's claim of "Unified to v2.0" is not fully accurate for SKILL.md.

### ⚠️ BY DESIGN — calibrated_threshold TBD

All three reviewers (hm, cc, omp) agree this is a deployment prerequisite, not a contradiction. The architecture correctly documents this as a blocking condition requiring calibration data. **hm is correct**: this is by design, not a specification gap.

---

## 2. Cross-Reviewer Contradictions

### 2.1 hm_round1 "No Contradictions" vs cc/omp findings

**hm_round1 verdict**: "PASS. No contradictions." — This was provably wrong. cc found 4 contradictions (2 HIGH), omp found 5 (2 HIGH). hm's R1 reading was surface-level; it missed:

- MEMORY.md L23 Gold dispatch contradiction (existed in 2 of 4 sources hm claimed to audit)
- Per-field vs batch contradiction within SKILL.md
- Version number inconsistency across all 4 sources
- Text-layer path divergence (SOUL vs SKILL)

**Logical assessment**: hm's R1 sampling was biased toward consensus confirmation. The hm agent read SOUL.md, MEMORY.md, SKILL.md, README.md but did not cross-compare them at the line level. This is a coverage failure, not a logical error — the contradictions were present in the text but hm's audit methodology missed them.

### 2.2 hm_round2 "/tmp BY DESIGN" vs omp G7/D7

hm_round2 claims: "SKILL.md uses /tmp for intermediate artifacts. MEMORY.md禁止/tmp for deliverables. Separate concerns."

**rx finding**: This reasoning is **incorrect**. SKILL.md L195 specifies `/tmp/magi-audit/<topic-slug>/` as the **output directory** for Phase 0-3 artifacts — including the convergence gate output that feeds into QUINTE. This IS a deliverable path for the MAGI pipeline. MEMORY.md L19 is unambiguous: "NEVER write output files, reports, code, or any artifacts to /tmp or /private/tmp." The `/tmp/magi-audit/` path appears 18+ times across SKILL.md and its references.

The only mention of a persistent path for MAGI output appears in `references/philosophy-debate-workflow.md` L60: "during work" → `/tmp/magi-audit/`, "for archival" → `~/Downloads/DEVELOPMENT/MAGI/`. This is in a legacy reference file, not in the main SKILL.md output structure section.

**Verdict**: omp G7/D7 is correct. hm_round2's dismissal is wrong. `/tmp` usage violates MEMORY.md and creates an audit trail reliability risk. **This is a genuine contradiction between SKILL.md and MEMORY.md that persists after all fixes.**

### 2.3 hm_round2 "No remaining logical contradictions" — premature

hm_round2 claims the architecture has "No remaining logical contradictions." This overstates the resolution. The following logical tensions persist (not all are contradictions, but hm's blanket claim is inaccurate):

| Issue | Reviewer | Status |
|---|---|---|
| Model count: 3 or 4? | omp C3 | UNRESOLVED — semantic but operationally significant |
| Text-layer path: Fr+Myrrh or not? | omp C4 | UNRESOLVED — SOUL.md is ambiguous |
| Gold as 1, 2, or 3 models? | cc 3.2 | UNRESOLVED — SOUL implies 3-model composite |
| Model names in public README vs design principle | cc 1.4 | UNRESOLVED — SKILL.md L32 still says "provider-agnostic" |
| /tmp output vs MEMORY.md prohibition | omp G7/D7 | UNRESOLVED — hm_round2's dismissal is incorrect |

---

## 3. Persistent Issues After Fixes

### 3.1 🔴 CRITICAL — Input format unresolved (QUINTE 0a-iii #5)

SKILL.md L735 still lists: "(5) Resolve whether mimo receives raw image + OCR text or text-only."

This is a QUINTE 4/4-agent blocking condition. It is **not addressed in hm_round2 at all**. The input format determines:

- Whether Gold's "visual verification" stance is epistemologically valid
- Prompt token cost (raw image inline vs text-only)
- Whether mimo-v2.5's multimodal capability is utilized or wasted
- Whether Tesseract OCR text is provided as context or the model must re-derive all text

**This is the single most critical open item.** Until resolved, the pipeline cannot be deployed for any document. hm_round2's silence on this is a significant coverage gap.

### 3.2 🟡 HIGH — SKILL.md header version "2.1" vs body "v2.0"

SKILL.md header L4: `version: "2.1"`. Description L3: `"MAGI v2.0"`. Architecture section L36: `"Architecture (v2.0)"`. This is a residual version mismatch within a single file. The header was not updated when the body was unified to v2.0. **Low impact on deployability but violates the version unification claim.**

### 3.3 🟡 HIGH — Model count: 3 vs 4 (omp C3, persists)

SKILL.md L115: "Three Gifts = three models: mimo-v2.5 + mimo-v2.5-pro + DS v4-pro. kimi is surgical fallback only."

MEMORY.md L27: "MAGI Gold 三模型全火力不降级: mimo-v2.5主力 + kimi + DS v4-pro"

Two conflicting enumerations:
- SKILL.md: 3 base models (mimo-v2.5, mimo-v2.5-pro, DS) + kimi as 4th fallback
- MEMORY.md: 3 models total, kimi is one of them

At runtime, 4 distinct model endpoints are provisioned. The "3 vs 4" framing affects capacity planning and cost modeling. If kimi is "just a fallback," why is it counted in "全火力"? If kimi is "全火力" core, why does SKILL.md exclude it from the Three Gifts?

**Recommendation**: Standardize on "4 models, 3 base + 1 escalation" or "3 models with kimi as the surgical tier."

### 3.4 🟡 HIGH — Gold composition: 2-model or 3-model? (cc 3.2, persists)

SOUL.md L7 (per evidence.md): `Gold: mimo-v2.5+kimi+DS v4-pro` — implies 3-model Gold composite.

MEMORY.md L23: `Gold→mimo-v2.5主力→kimi batch fallback+DS text tier` — Gold is bimodal (mimo+kimi); DS is separate text tier.

SKILL.md L105-109: Gold = mimo → kimi fallback; DS text tier is separate routing.

The SOUL.md formulation makes Gold sound like a three-model ensemble. MEMORY.md and SKILL.md clearly have Gold as bimodal with DS as parallel text-only routing. This ambiguity could cause dispatch errors if someone builds from SOUL.md alone.

### 3.5 🟡 HIGH — Text-layer path: Fr+Myrrh coverage (omp C4, persists)

SOUL.md L120 describes: "扫描件或无文本层 PDF：Tesseract → MAGI (Gold/kimi 看原图校验 → Fr+Myrrh 语义+对抗)" — this covers the scanned path but the text-layer path is described separately in L116 (zlib extract → DS verify). SOUL.md doesn't explicitly state whether text-layer documents receive Fr+Myrrh review.

SKILL.md L41 pipeline diagram shows Fr+Myrrh on both paths. An operator building from SOUL.md alone might skip semantic+adversarial review for text-layer documents.

### 3.6 🟡 MEDIUM — Model names in public repo vs SKILL.md design principle (cc 1.4, persists)

SKILL.md L32: "The public repo (README, PROTOCOL.md) is abstract and provider-agnostic. Model names belong in this skill only."

README.md: Contains `mimo-v2.5-pro`, `DeepSeek v4-pro`, `mimo-v2.5` in architecture diagrams and deployment tables.

hm_round2 claims: "User decision: MAGI is 量身定制 for mimo/kimi/DS. Provider-agnostic badge removed." But the badge removal doesn't resolve the SKILL.md L32 instruction — SKILL.md still tells developers the public repo should be abstract. Either SKILL.md L32 must be updated, or README.md must be made provider-agnostic. Currently they contradict.

### 3.7 🟡 MEDIUM — Volume gate underspecified (cc 2.3, omp G3)

The `<8 docs/week → all-kimi` rule remains a QUINTE blocking condition (0a-iii #6) with no operational definition:
- Measurement window undefined
- Hysteresis undefined
- Interaction with Frankincense undefined (does Frankincense also become kimi?)
- Cost justification unvalidated (at 8 docs/week, is kimi actually cheaper?)

### 3.8 🟡 MEDIUM — Circuit breaker underspecified (cc 2.4, omp G4)

Detection criteria, recovery procedure, state persistence, and interaction with Frankincense all undefined. hm_round2 dismisses this as "implementation scope" but circuit breaker behavior directly affects architecture correctness — if it trips mid-document, what guarantees consistency?

### 3.9 🟡 MEDIUM — Cost model absent (cc 2.5)

Claims of "13%→1%" quota reduction and "~1/10 token cost" are unvalidated. No per-document cost formula, no break-even analysis, no kimi quota baseline. The architecture asserts cost improvement as a design goal but provides no verification framework.

### 3.10 🟠 LOW — "三模型全火力不降级" vs routing optimization (cc 3.1)

MEMORY.md says "全火力不降级" (full firepower, no downgrade) while simultaneously routing 90%+ fields to the cheapest model and reserving expensive models for edge cases. This is a philosophical tension: is the system designed for maximum accuracy or cost-optimized accuracy? The language and the routing contradict.

---

## 4. Cross-Reviewer Coverage Analysis

### Issues FOUND by all three reviewers

| Issue | hm | cc | omp |
|---|---|---|---|
| calibrated_threshold TBD | ⚠️ minor gap | 🔴 CRITICAL gap | 🔴 CRITICAL deployability |
| Calibration not executed | — | 🔴 blocking | 🔴 blocking |

### Issues FOUND by two reviewers, MISSED by one

| Issue | hm | cc | omp |
|---|---|---|---|
| Gold dispatch contradiction | ❌ MISSED | 🔴 | 🔴 |
| Per-field vs batch contradiction | ❌ MISSED | 🔴 | — |
| Version numbers | ❌ MISSED | 🟡 | 🟡 |
| Volume gate underspecified | — | 🟡 | 🟡 |
| Circuit breaker underspecified | — | 🟡 | 🟡 |
| Tesseract-v2 undefined | — | 🟢 | 🟢 |
| Input format unresolved | ❌ MISSED | 🔴 | — |

### Issues found by ONLY ONE reviewer (unique coverage)

| Issue | Reviewer | Missed by | Severity |
|---|---|---|---|
| Model names in public repo vs design | cc 1.4 | hm, omp | MEDIUM |
| Cost model missing | cc 2.5 | hm, omp | MEDIUM |
| Myrrh/hm dual role in QUINTE | cc 2.7 | hm, omp | LOW |
| "三模型全火力" vs cost | cc 3.1 | hm, omp | LOW |
| Gold as 1/2/3 models | cc 3.2 | hm, omp | MEDIUM |
| SKILL.md legacy scope | cc 3.3 | hm, omp | LOW |
| kimi thinking mode ambiguity | cc 3.4 | hm, omp | LOW |
| Output path /tmp violation | omp G7/D7 | hm, cc | MEDIUM |
| Model count 3 vs 4 | omp C3 | hm, cc | MEDIUM |
| Text-layer path Fr+Myrrh | omp C4 | hm, cc | MEDIUM |
| HIGHBALL applicability | omp C5 | hm, cc | LOW |
| Confidence score semantics | omp G8 | hm, cc | MEDIUM |
| Batch kimi format unspecified | omp G5 | hm, cc | MEDIUM |
| No monitoring/telemetry | omp G6 | hm, cc | MEDIUM |
| Credential systems (3 separate) | omp D5 | hm, cc | LOW |
| No dry-run/test mode | omp D6 | hm, cc | LOW |
| Dependency health check missing | omp G10/D8 | hm, cc | LOW |
| Convergence gate composite | omp A3 | hm, cc | LOW |
| Merge consistency gate | omp A4 | hm, cc | LOW |
| Text-layer detection method | omp A7 | hm, cc | LOW |
| PDF-to-image pipeline | omp A8 | hm, cc | LOW |
| README prose sync | hm #1 | cc, omp | LOW |

**Pattern**: hm found minimal issues (just prose sync). cc focused on cost/logic/design consistency. omp found the most issues with a heavy operations orientation. No single reviewer caught everything — the three-way cross-review is working as designed.

---

## 5. Deployability Assessment (rx logic perspective)

### Currently BLOCKED (2 items)

1. **QUINTE 0a-iii #5: Input format** — mimo receives raw image + OCR text OR text-only? Unresolved. Pipeline cannot be constructed without this decision.

2. **QUINTE 0a-iii #1: Calibration** — mimo-v2.5 must be calibrated on 50-200 labeled docs, ≥95% precision. Not executed. Without calibration, `calibrated_threshold` cannot be set and the entire routing logic is inoperable.

### Deployment prerequisites (non-blocking but required before go-live)

3. Set `calibrated_threshold` from calibration results
4. Operationalize volume gate (window, hysteresis, Frankincense interaction)
5. Define circuit breaker detection, trigger, and recovery
6. Resolve mimo input format (pick text-only or raw+OCR)
7. Move output path from `/tmp` to persistent storage
8. Define batch kimi call format (region packaging, prompt template, output schema)
9. Define confidence score extraction mechanism for mimo-v2.5

### Architecture concerns (resolve before deploy but not strictly blocking)

10. Standardize model count: 3 or 4?
11. Clarify Gold composition (2-model or 3-model?)
12. Resolve SKILL.md header version "2.1" → "2.0"
13. Align public README with SKILL.md design principle (or update SKILL.md)
14. Add cost monitoring instrumentation
15. Define text-layer path Fr+Myrrh coverage explicitly in SOUL.md
16. Add dependency health check / pre-flight validation

---

## 6. Verdict

### On hm_round2

hm_round2 claims "Architecture is logically complete and internally consistent" and "No remaining logical contradictions." **This verdict is too optimistic.** While the 7 fixes did resolve the most critical contradictions (Gold dispatch, per-field/batch, version numbers), several logical tensions persist:

- SKILL.md header v2.1 vs body v2.0 (internal inconsistency)
- Model count 3 vs 4 (semantic contradiction between SKILL.md and MEMORY.md)
- Gold as 2-model vs 3-model (SOUL.md vs other sources)
- Text-layer path coverage (SOUL.md ambiguous)
- /tmp output path violation (SKILL.md vs MEMORY.md)
- Input format unresolved (critical blocking condition unaddressed by hm_round2)

hm_round2's dismissal of omp G7 (/tmp) as "BY DESIGN" is incorrect on the facts. Its silence on QUINTE 0a-iii #5 (input format) is a coverage gap.

### On cc_round1

cc's analysis is the most balanced of the three R1 reviews. It correctly identifies the two critical blocking conditions, maps contradictions to specific lines, and flags cost model gaps. Its categorization of calibrated_threshold as "CRITICAL — deployability blocker" is correct even though the TBD status is by design.

### On omp_round1

omp's review is the most thorough with 32 issues across 5 contradictions, 10 gaps, 8 ambiguities, and 9 deployability concerns. omp correctly identifies the /tmp output path violation (which cc missed and hm dismissed) and surfaces operations-critical gaps (credential systems, monitoring, dry-run mode) that the other reviewers overlooked.

### Overall Architecture Verdict

The MAGI architecture is **logically sound in its core routing design** (田忌赛马: mimio→kimi→DS tiered pipeline). The three-model cost optimization is well-motivated and internally consistent. The QUINTE handoff (confidence topology) is correctly specified.

However, the architecture has **two genuine deployment blockers** (input format unresolved, calibration not executed) and **one persistent contradiction** (/tmp output path violating MEMORY.md). These prevent deployment but do not invalidate the architecture.

**Final rx verdict: CONDITIONAL PASS**
- Core architecture: LOGICALLY SOUND ✅
- Deployment: BLOCKED on 2 QUINTE conditions (0a-iii #1, #5) 🔴
- Cross-source consistency: 3 residual logical tensions remain 🟡
- Operational readiness: Insufficient (monitoring, circuit breaker, volume gate) 🟡

**Recommended R3 actions before KANSA final:**
1. Resolve QUINTE 0a-iii #5: decide mimo input format (raw image + OCR text vs text-only)
2. Execute mimo-v2.5 calibration on labeled shipping docs
3. Fix SKILL.md header version "2.1" → "2.0"
4. Move MAGI output path from `/tmp` to persistent storage
5. Update SKILL.md L32 to reflect that public README may contain model names
6. Clarify model count (3 vs 4) and Gold composition (2-model vs 3-model) across all sources
