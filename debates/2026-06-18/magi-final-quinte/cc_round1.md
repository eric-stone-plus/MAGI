TASK: MAGI final audit. Contradictions, gaps, ambiguity, deployability.

# CC Round 1 — MAGI Final Architecture Audit (Cost/Dev Perspective)

## Sources Audited
- **SOUL.md**: `/Users/ericstone/.hermes/profiles/technical/SOUL.md` (lines 7–9, 120–122)
- **MEMORY.md**: `/Users/ericstone/.hermes/profiles/technical/memories/MEMORY.md` (lines 14–17, 23–27)
- **MAGI SKILL.md**: `/Users/ericstone/.hermes/profiles/technical/skills/multi-agent-debate/magi/SKILL.md` (full 858 lines, v2.1)
- **MAGI README.md**: `/Users/ericstone/Public/MAGI/README.md` (full 204 lines, public repo)

---

## 1. CONTRADICTIONS 🔴

### 1.1 Gold dispatch: kimi-primary (MEMORY v2.1) vs mimo-primary (SKILL v2.1/README/SOUL)

| Source | Line | Gold Model | Role |
|--------|------|------------|------|
| **MEMORY.md** | L23 | `Gold→kimi(-p one-shot batch)` | kimi primary |
| **MEMORY.md** | L27 | `mimo-v2.5主力(Lite ¥39/月)+kimi(Andante ¥49/月,thinking=high)` | mimo primary, kimi fallback |
| **SOUL.md** | L7 | `Gold: mimo-v2.5+kimi+DS v4-pro` | Three-model composite |
| **README.md** | L62, L151 | `mimo-v2.5 primary, kimi batch fallback` | mimo primary |
| **SKILL.md** | L105, L463-471 | `Gold primary: mimo-v2.5 → kimi fallback` | mimo primary |

MEMORY.md L23 states `Gold→kimi(-p one-shot batch)` — kimi is the primary dispatch. MEMORY.md L27 (further down in the same file) states mimo-v2.5 is 主力 (main force). These are directly contradictory within the same file. L23 appears to be a stale v2.1 snapshot that was not updated when the 田忌赛马 revision (2026-06-18) demoted kimi from primary to surgical fallback. **Severity: HIGH** — operational dispatch depends on which line someone reads.

### 1.2 Per-field vs batch-per-document kimi escalation

| Source | Line | Semantics |
|--------|------|-----------|
| **SKILL.md** | L475 | `per-field escalation when mimo confidence < calibrated_threshold AND vision required` |
| **SKILL.md** | L63, L735 (0a-iii #2) | `Batch kimi escalations per-document, not per-field` |
| **README.md** | L62 | `kimi batch fallback` |

SKILL.md contradicts itself within the same file: L475 says per-field, L63 and L735 (QUINTE blocking condition #2) say per-document batch. Per-field escalation costs N × always_thinking preamble (~40K tokens/field). Per-document batch costs 1 × preamble. The cost difference is substantial. **Severity: HIGH** — this directly impacts kimi quota consumption.

### 1.3 Version numbering: v2.0 vs v2.1

| Source | Location | Version |
|--------|----------|---------|
| **README.md** | Badge | `protocol-v2.0` |
| **SOUL.md** | L7 | `MAGI v2.0` |
| **SOUL.md** | L120 | `MAGI v2.0 (2026-06-17)` |
| **MEMORY.md** | L23 | `MAGI v2.1 (Mac)` |
| **SKILL.md** | Header | `version: 2.1` |
| **SKILL.md** | L337 | `MAGI v2.0 = OCR verification only` |

No single version number is universally agreed. README, SOUL, and parts of SKILL say v2.0. MEMORY and SKILL header say v2.1. If v2.1 is the Gold dispatch revision (mimo primary), then SOUL and README are out of date. If v2.1 is something else, what changed? **Severity: MEDIUM** — causes confusion about which spec is authoritative.

### 1.4 Model names in public repo vs protocol design principle

| Source | Statement |
|--------|-----------|
| **README.md** L62, L85-86, L151-153 | Explicit model names: `mimo-v2.5`, `mimo-v2.5-pro`, `DeepSeek v4-pro` |
| **SKILL.md** L32 | `Model names belong in this skill only` |
| **SKILL.md** L86-87 | Public repo: `model-agnostic, agent-agnostic... "multimodal delegate", "text-only delegate"... not "kimi/DeepSeek/hm"` |

README.md (public repo) contains provider-specific model names in the architecture diagram, Mac Deployment table, and tiered pipeline diagram. This directly violates SKILL.md's stated design principle that the public repo should be abstract and provider-agnostic. **Severity: MEDIUM** — design principle vs actual content mismatch.

---

## 2. GAPS 🟡

### 2.1 Calibrated confidence threshold undefined (BLOCKING)

SKILL.md L735 (0a-iii #1): *"Calibrate mimo-v2.5 on 50-200 labeled shipping docs before deploy. Must achieve ≥95% precision at chosen threshold."* But the threshold value itself is explicitly **TBD**: SKILL.md L731 says *"calibrated_threshold (TBD from benchmark, NOT 0.7)"*.

The entire tiered pipeline — mimo→kimi escalation, DS text tier routing — depends on this threshold. Without it:
- No field can be routed correctly
- kimi escalation is either never triggered or always triggered
- Cost model cannot be validated

**Severity: CRITICAL — deployability blocker.**

### 2.2 Raw image + OCR input format unresolved (BLOCKING)

SKILL.md L735 (0a-iii #5): *"Resolve whether mimo receives raw image + OCR text or text-only."*

This is a fundamental input format question. If mimo receives text-only, the multimodal advantage is wasted and Gold's epistemological stance ("visual verification") collapses. If raw image + OCR text, the prompt format and token cost change dramatically. This is listed as a QUINTE blocking condition and is explicitly **unresolved**. **Severity: CRITICAL — deployability blocker.**

### 2.3 Volume gate operational definition missing

SKILL.md L735 (0a-iii #6): *"Volume gate: <8 docs/week → all-kimi (¥39/mo not justified)."*

Gaps:
- What window? Sliding 7-day? Calendar week? Rolling average?
- How is it enforced? Manual decision? Automatic gate?
- If all-kimi: what happens to Frankincense? Is it kimi too (single-model collapse) or does mio-v2.5-pro still run?
- What's the hysteresis? If volume fluctuates 6→9→7, does the gate oscillate?
- At <8 docs/week, ¥39/mo for mimo is ~¥5/doc. What's the kimi cost at 8 docs? If kimi costs more per doc at 8 docs, the gate logic is inverted.

**Severity: HIGH — cost decision rule is underspecified.**

### 2.4 Circuit breaker recovery undefined

MEMORY.md L16 / SKILL.md L735 (0a-iii #3): *"Circuit breaker: mimo API failure → auto-fallback to all-kimi + alert."*

Gaps:
- What alert mechanism? Where does it go?
- When and how is normal operation restored? Is there a health check endpoint?
- Who monitors the circuit breaker state?
- If the breaker trips mid-document, what happens to in-flight processing?
- How does "all-kimi" interact with Frankincense (normally mimo-v2.5-pro)?

**Severity: MEDIUM — operational gap.**

### 2.5 Per-document cost model missing

SOUL.md says *"三模型全火力"* (full firepower, no downgrade). MEMORY.md claims *"13% weekly quota → ~1%"* for the new architecture. But nowhere is there:

- An actual cost formula or per-document estimate
- What the weekly kimi quota is (absolute tokens or ¥ amount)
- A break-even analysis: at what document volume does mimo ¥39/月 fixed cost beat DS pay-per-use?
- Cost of the all-kimi fallback path vs normal path
- Frankincense (mimo-v2.5-pro) cost — is it included in the ¥39/月 or separate?

**Severity: MEDIUM — claims of cost improvement are unvalidated.**

### 2.6 Tesseract-v2 cross-check undefined

SOUL.md L9 and SKILL.md L70 reference a "Tesseract-v2" cross-check (second Tesseract pass with alternative parameters). README.md L53, L66, L78 also references it. But:

- What alternative parameters? Different PSM mode? Different language pack?
- Is this a separate Tesseract binary or just a second invocation with different flags?
- None of the four sources define what "Tesseract-v2" actually means.

**Severity: LOW — definitional gap, less critical for cost analysis.**

### 2.7 Myrrh/hm dual role in MAGI→QUINTE pipeline

SOUL.md L100 specifies hm is the R3 dual-audit arbitrator in QUINTE. SKILL.md L107/L164 specifies hm is Myrrh (adversarial auditor) in MAGI. When MAGI feeds verified text into QUINTE, hm has already formed opinions about the text as Myrrh before adjudicating as R3 arbitrator. This is a subtle self-review risk not acknowledged in any source.

**Severity: LOW — epistemic gap, may affect audit independence.**

---

## 3. AMBIGUITY 🟠

### 3.1 "三模型全火力不降级" vs cost optimization

MEMORY.md L27: *"三模型全火力不降级"* — no model downgrading, full firepower. But simultaneously the architecture:
- Routes structured forms (90%+ of fields) to cheapest model (mimo-v2.5 Lite ¥39/月)
- Reserves DS and kimi only for low-confidence/ambiguous cases
- Has a volume gate that drops mimo entirely at low volume

Is the design philosophy maximum accuracy or cost-optimized accuracy? The language says one thing, the routing says another. **Ambiguity: is cost or accuracy the primary constraint?**

### 3.2 Gold as one model, two models, or three models?

SOUL.md L7: `Gold: mimo-v2.5+kimi+DS v4-pro` implies Gold is a composite of all three models. But:
- README.md L62: Gold = mimo-v2.5 with kimi fallback (two models, not three)
- SKILL.md L105-109: Gold = mimo-v2.5 → kimi fallback, DS text tier is separate routing, not part of "Gold"
- MEMORY.md L15: 纯文本低置信→DS非kimi (text-only low confidence → DS, not kimi) — DS is a separate text tier

The SOUL.md formulation makes Gold sound like a three-model ensemble. The other sources clearly have Gold as bimodal (mimo+kimi) with DS as a parallel text-only tier. This ambiguity could cause dispatch errors.

### 3.3 SKILL.md scope: OCR-only but 60%+ legacy investigation content

SKILL.md declares MAGI v2.x is OCR verification only (L30, L337). Yet the 858-line file contains ~500 lines of legacy v1.x content: multi-topic investigations, code/architecture analysis, creative/philosophy tasks, batch marathons, token burning. This content is marked "legacy" but exists in the **active** skill file — not in a separate archived reference. When a developer reads SKILL.md, what should they understand MAGI's scope to be?

### 3.4 kimi thinking mode: always_high vs HIGH-vs-auto

| Source | Statement |
|--------|-----------|
| MEMORY.md L25 | `kimi's always_thinking cannot be disabled via CLI or env var` |
| MEMORY.md L27 | `kimi上场即thinking=high` (kimi always runs thinking=high) |
| SKILL.md L733 (0a-ii) | `kimi escalation calls use THINKING=HIGH (not auto)` |

If kimi always has thinking=high (it cannot be disabled), then specifying `THINKING=HIGH` explicitly is redundant. The distinction between "HIGH" and "auto" is meaningless if kimi always_thinking is always on. But SKILL.md treats this as a deliberate choice. This creates ambiguity about whether there is a meaningful configuration option.

### 3.5 MEMORY.md L23 v2.1 — authoritative or stale?

MEMORY.md L23 says *"MAGI v2.1 (Mac): Gold→kimi(-p one-shot batch), Fr→mimo(--pure stdin), Myrrh→DS direct"*. This directly contradicts the newer 田忌赛马 architecture where mimo is Gold primary. Is L23 authoritative (and the rest of the architecture is aspirational) or stale (superseded by L27)? No source clarifies the relationship.

---

## 4. DEPLOYABILITY 🔶

### 4.1 BLOCKED — Two critical unresolved items (0a-iii #1, #5)

The QUINTE audit (2026-06-18, 4/4 agents) identified 6 blocking conditions. Two remain unresolved:
1. **Calibrated threshold TBD** — pipeline cannot route without it
2. **Raw image + OCR input format** — Gold cannot receive its input

Until these are resolved, the MAGI pipeline is not deployable for any document.

### 4.2 Volume gate must be operationalized

The `<8 docs/week → all-kimi` rule needs a concrete implementation. Without it, cost decisions are ad-hoc. This is a **dev-side implementation blocker**: the code needs to know when to skip mimo.

### 4.3 No cost monitoring/metrics specification

Claims about cost improvement (13%→1% weekly quota, ~1/10 token cost, 90% cost reduction) are unverifiable without:
- Token counters per model per document
- Per-document cost breakdown
- Weekly quota tracking
- Baseline measurements

Deployability requires instrumentation that doesn't exist in the spec.

### 4.4 MEMORY.md stale data is an operational risk

MEMORY.md L23 describes a v2.1 architecture where kimi is Gold primary. This is the user's memory file — if the user or a new developer reads MEMORY.md first (it's shorter and more accessible than SKILL.md), they'll operate under the wrong dispatch model. **Recommend: update or delete L23.**

### 4.5 README.md model name exposure

README.md names specific model providers (mimo-v2.5, DeepSeek v4-pro) in the public repo. If the design principle (SKILL.md L86-87) is to keep the public repo provider-agnostic, the README needs to be rewritten. If the principle is abandoned, SKILL.md needs updating. Either way, the inconsistency should be resolved.

---

## Summary

| Category | Count | Critical |
|----------|-------|----------|
| Contradictions | 4 | 2 (Gold dispatch, per-field vs batch) |
| Gaps | 7 | 2 (calibrated threshold, input format) |
| Ambiguity | 5 | 0 |
| Deployability blockers | 2 | 2 (blocking conditions unresolved) |

**Verdict**: Architecture is logically coherent in its broad strokes but has **two deployability blockers** (unresolved calibrated threshold and input format), **two HIGH contradictions** within MEMORY.md and SKILL.md that could cause dispatch errors, and **one operational risk** from stale MEMORY data. The cost model is aspirational with no validation framework. Until 0a-iii items #1 and #5 are resolved, MAGI cannot be deployed.
