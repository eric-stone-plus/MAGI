TASK: Kimi efficiency

---

# OMP R1 — Kimi Token Efficiency for MAGI Gold

## 1. CLAIM VERIFICATION

### 1.1 hm Claims

| # | Claim | Verdict | Reasoning |
|---|-------|---------|-----------|
| 1 | Single call all pages: 67% savings | **OPTIMISTIC but directionally correct** | 3→1 calls saves 2 rounds of (system_prompt + output_overhead). If thinking is 80% of output, overhead dominates per-page image tokens, making 67% arithmetically possible. But the combined call has 3× input tokens (all pages), so actual savings ≈ 44-67% depending on input:overhead ratio. Claim assumes page tokens are negligible — true for small pages, not guaranteed. |
| 2 | stream-json: 50% savings | **PLAUSIBLE, aligns with cw#1** | If thinking is 80% of output tokens and output ≈ input, eliminating thinking saves ~40% total. Stream-json also strips non-content formatting. 50% is within range but at the conservative end vs. cw's 60-70%. These are the same optimization viewed from different angles. |
| 3 | Template caching: 60% savings | **CONCEPTUALLY SOUND, unverified** | Premise is correct: same-agent SOFs have identical layouts. After first verification, only changed fields need re-checking. 60% is plausible for highly static forms. BUT: no implementation exists, no measured baseline, no mechanism described for cache invalidation or drift detection. This is a design proposal, not a verified claim. |
| 4 | Text-layer bypass: 90% never hit kimi | **LIKELY ACCURATE, needs deployment audit** | Claimed as "already implemented." If true, this is the single highest-impact measure and makes all other optimizations apply only to ~10% of documents. However: the 90% figure may be environment-specific (depends on document source age/quality). No evidence cited. |
| 5 | Crop to relevant regions: 30% input savings | **PLAUSIBLE** | Smaller images = fewer vision tokens. Plausible if SOF pages are ~30-40% relevant region. Only applies to the ~10% of docs that lack text layers (per #4), limiting real-world impact. |
| 6 | Skip obvious fields: 20% input savings | **PLAUSIBLE** | 20% reduction in fields to verify is modest and achievable. Reasonable call on printed-text reliability vs. OCR. Again, limited to image-based docs. |
| 7 | Combined dispatch template | **STRUCTURALLY SOUND, missing guardrails** | The template is well-formed and captures the optimizations. Missing: max_tokens cap on output, timeout handling, fallback for >N pages, and budget awareness (cw's contribution). |

### 1.2 cw Claims

| # | Claim | Verdict | Reasoning |
|---|-------|---------|-----------|
| 1 | Disable thinking: 60-70% savings | **PLAUSIBLE, upper-bound estimate** | If thinking is 80% of output and output ≈ input + system_prompt, total savings ≈ 40-57%. 60-70% only achievable if thinking utterly dominates (e.g., thinking = 4× output content, output content ≫ input). Realistic range: 50-60% for verbose reasoning calls. |
| 2 | Cap thinking_max_tokens at 800: 30-40% | **PLAUSIBLE** | Default ceiling ~4096 → 800 is 80% reduction in thinking budget. 30-40% total savings implies thinking is ~37-50% of total tokens. Internally consistent. |
| 3 | Strip thinking from response | **ACCURATE, context mgmt** | Not a per-call savings measure — prevents thinking tokens from polluting downstream context windows. Real savings accrue across conversation turns. Correct mechanism. |
| 4 | Consolidate multi-call: 40-50% | **PLAUSIBLE** | 2→1 calls saves one round of system prompt + overhead. 40-50% range accounts for increased input in the combined call. Aligns with hm#1. |
| 5 | Cache system prompt as prefix | **ACCURATE if Kimi supports it** | prefix_cache is a documented Kimi feature. System prompt (500-2000 tokens) saved after cache warm. Real but modest per-call impact; meaningful at scale. |
| 6 | Remove explicit temp/top_p | **NEGLIGIBLE, possibly inaccurate** | Claim that "some providers bill extra tokens for explicit sampling overrides" is questionable — most providers don't charge differently. Even if true, savings are in single-digit tokens. Zero-risk but near-zero impact. Should not be counted toward total savings estimates. |
| 7 | Budget-aware dispatch | **VALID SAFEGUARD, not efficiency** | This is operational risk management, not a token efficiency. Prevents quota exhaustion but doesn't reduce tokens per task. Important but mis-categorized. |
| 8 | Response compression pipeline | **PLAUSIBLE, implementation-dependent** | Post-processing compression could reduce downstream token usage. But: compression itself costs compute and may introduce errors. Savings are speculative without a concrete compression strategy. |

### 1.3 Cross-Claim Analysis

**Overlap between hm and cw:**
- hm#1 (single call) ↔ cw#4 (consolidate): Same optimization, 67% vs. 40-50% — hm is more aggressive.
- hm#2 (stream-json) ↔ cw#1 (disable thinking): Same root cause, different mechanism. hm's 50% and cw's 60-70% differ. The lower bound (50%) is safer for planning.
- hm#4 (text-layer bypass) ↔ no cw equivalent: This is the most impactful claim and cw doesn't address it. If 90% of docs bypass Kimi entirely, most cw strategies only apply to 10% of traffic.

**cW's unique contributions (not in hm):**
- Thinking token cap (cw#2): hm doesn't address partial thinking retention.
- Budget-aware dispatch (cw#7): Operational guardrail, missing from hm's pure-efficiency view.
- Response compression (cw#8): Downstream optimization, missing from hm.
- Dispatch template with tag-based overrides: More granular than hm's one-size-fits-all template.

---

## 2. MISSED OPTIMIZATIONS

### 2.1 Image Resolution Control
Neither report mentions reducing input image resolution/DPI before sending to Kimi. Vision model token counts scale with image dimensions. A 50% DPI reduction could yield 25-50% input savings on image-based PDFs with minimal accuracy impact for structured forms. This applies to the 10% non-text-layer documents.

### 2.2 Model Tiering / Routing
Not every field requires Kimi's vision capabilities. Simple OCR (dates, printed numbers) can be handled by cheaper models (e.g., deepseek-v3 with vision, or even tesseract for text-layer docs that need layout parsing). Neither report proposes tiered routing:
- **Tier 1**: Text-layer extraction (free, already done per hm#4)
- **Tier 2**: Cheap vision model for structured fields
- **Tier 3**: Kimi only for ambiguous/handwritten/weather-event fields

### 2.3 JSON Schema Enforcement (Structured Output)
hm mentions JSON output but neither report specifies using Kimi's structured output / JSON mode with a strict schema. Schema enforcement reduces output tokens by eliminating prose, whitespace, and field-name verbosity. It also eliminates parsing errors — a reliability benefit, not just efficiency.

### 2.4 Per-Call max_tokens Output Cap
cw's dispatch template sets max_tokens per tag (e.g., classify=256, generate=4096) but hm's combined dispatch template has no cap. Without a max_tokens ceiling, a runaway Kimi response could burn thousands of tokens before the system detects the error.

### 2.5 Negative Prompting / Conciseness Directive
Neither report mentions instructing Kimi to maximize token efficiency in the system prompt itself (e.g., "Be maximally concise. Output only the specified JSON. Do not elaborate."). This is zero-cost and can reduce output bloat even with thinking disabled.

### 2.6 Incremental / Delta Updates
Extending hm#3 (template caching): when only one field changes between consecutive SOFs from the same agent (e.g., only the date advances), send only the changed region, not the entire document. This is hm#5 (crop) applied temporally across calls, not just spatially within a call.

### 2.7 Cross-Agent Batching
If multiple agents submit SOFs in the same time window, batch them into one Kimi call with structured per-agent output. Saves N-1 system prompts. Neither report considers multi-agent batching.

### 2.8 Fallback / Circuit Breaker Patterns
Neither report addresses what happens when optimizations fail:
- What if a combined call exceeds context limits?
- What if prefix cache is cold?
- What if template cache is poisoned?
- What if thinking truncation cuts off a critical mid-chain step?

---

## 3. SYSTEMIC RISK ASSESSMENT (OMP Perspective)

### 3.1 Interaction Risk: Optimization Stacking Creates Fragile Pipeline

All eight optimizations operate simultaneously on the same document flow:

```
Document → [text-layer bypass?] → [crop regions] → [skip fields] → 
[template cache?] → [single combined prompt] → [thinking disabled?] → 
[stream-json] → [strip thinking] → [compress response] → MAGI Gold
```

Each stage assumes the previous stage succeeded correctly. A failure at any stage cascades silently because:
- Thinking is disabled (no reasoning trace)
- Output is stream-json (no verbose context)
- Response is stripped (no audit trail)
- Response is compressed (errors may be obscured)

**Risk: Silent data corruption.** Wrong field values enter Gold's demurrage pipeline with no detectability until financial impact materializes.

### 3.2 Cache Coherence Risk

Two independent caching layers (template cache hm#3, prefix cache cw#5) with no coordination mechanism:
- **Template cache drift**: Agent changes their SOF layout (new form version). Template cache returns stale coordinates. Extracted fields are now reading wrong positions. No invalidation trigger described.
- **Prefix cache consistency**: If system prompt changes (new dispatch tags, new field requirements), the prefix cache is stale. cw mentions hashing but no mechanism for detecting prompt changes in production.
- **Combined failure mode**: Both caches go stale simultaneously (e.g., after a MAGI Gold config update). Every document in the first batch post-update gets incorrect extractions.

### 3.3 Quota Cliff Edge with Budget-Aware Dispatch

cw#7's budget-aware dispatch creates a non-linear failure mode:
- Near quota: calls get downgraded from Kimi → deepseek-v3
- Downgraded model lacks Kimi's vision capabilities
- Image-based documents fail or return garbage
- The system doesn't distinguish "cheap model failure" from "no data available"
- Demurrage calculations proceed with missing/wrong values

**Risk: Budget pressure creates data quality degradation that is worse than clean failure.** A hard stop at quota exhaustion is safer than silent quality degradation.

### 3.4 Cold Start Amplification

When a new agent appears with no template cache and no prefix cache warmth:
- Template cache miss → full document verification (3× tokens)
- Prefix cache miss → system prompt re-billed
- No text layer → full Kimi vision call
- All three hits occur simultaneously

One new agent's SOF could burn 5-10× the budgeted tokens. At current rates (13% quota for 2 calls), a cold-start agent could exhaust 30-50% of quota in one document.

### 3.5 Latency Accumulation from Combined Prompts

hm#1 and cw#4 consolidate multi-call into single prompts. For long documents (5+ pages), the combined input approaches context limits and latency increases non-linearly:
- A timeout on a combined call loses ALL pages, not just one
- Retry on combined call re-processes everything
- No partial-result recovery mechanism

**Risk: Combined call failure is catastrophic where paginated calls would have been recoverable.**

### 3.6 Provider Lock-in Through Optimization Surface

Five of the identified optimizations are Kimi-specific:
- stream-json (hm#2)
- thinking_enabled / thinking_max_tokens (cw#1, cw#2)
- prefix_cache (cw#5)
- Output format parameters

If MAGI Gold ever needs to switch vision providers (price change, deprecation, reliability), these optimizations don't port. The system's cost model becomes dependent on Kimi's specific API surface.

### 3.7 Text-Layer Bypass Blind Spot

hm#4 claims 90% of documents bypass Kimi. This makes the entire efficiency model brittle to changes in document sources:
- A new agent using scanned/image-only PDFs (older operations, international partners)
- A shift toward handwritten SOFs
- PDF generation changes that break text-layer extraction

If the 90% figure drops to 70%, Kimi usage triples (from 10% to 30% of documents). The budget model doesn't account for this variance.

### 3.8 Thinking Disablement Creates Unauditable Decisions

The dispatch template (cw) disables thinking for: classify, generate, summarize. But:
- **classify without thinking**: If Kimi misclassifies a document type, the wrong extraction template is applied, and there's no reasoning trace to debug why.
- **generate without thinking**: Generated demurrage statements have no chain-of-reasoning. In a dispute, MAGI Gold can't explain how it calculated a figure.
- **summarize without thinking**: Summarized weather events may omit critical details without the reasoning trace showing what was considered vs. discarded.

Only whitelisting `magi:diagnose`, `magi:audit`, and `magi:complex_plan` for thinking assumes everything else is simple enough to not need it. This is a dangerous assumption for financial/legal documents.

### 3.9 Summary Risk Matrix

| Risk | Severity | Likelihood | Detectability | Mitigation Priority |
|------|----------|------------|---------------|---------------------|
| Silent data corruption from stacked optimizations | CRITICAL | Medium | Very Low | P0: Add validation checkpoints |
| Cache coherence failure (template + prefix) | HIGH | Medium | Low | P1: Cache versioning + TTL |
| Cold-start quota spike for new agents | HIGH | Medium | Medium | P1: Cold-start detection + throttling |
| Budget-driven model downgrade data degradation | HIGH | Low-Medium | Low | P1: Hard quota stop vs. degrade |
| Combined call catastrophic failure | MEDIUM | Low | High (timeout visible) | P2: Partial-result fallback |
| Provider lock-in | MEDIUM | Certain | High | P2: Abstraction layer |
| Text-layer bypass assumption shift | MEDIUM | Low | Medium | P2: Monitor bypass rate |
| Unauditable decisions (no thinking traces) | MEDIUM | High | Very Low | P2: Archive thinking even when disabled for context |
| Per-call runaway with no max_tokens | LOW | Low | Medium | P3: Add max_tokens everywhere |

### 3.10 Overall Assessment

The combined optimizations could reduce Kimi token usage by 70-85% in the best case. However, the **systemic risk profile is elevated** because:

1. **No validation checkpoints** between optimization stages — errors propagate silently.
2. **Two independent caching layers** with no cross-invalidation mechanism.
3. **Binary thinking toggle** (on/off per tag) rather than graduated or context-sensitive.
4. **No cold-start handling** for the case where all optimizations fail simultaneously.
5. **Budget-aware downgrade is a quality cliff, not a graceful degradation.**

**Recommendation**: Implement optimizations incrementally with monitoring checkpoints between each stage. Do not deploy the full stack simultaneously. Start with thinking disablement + stream-json (highest savings, lowest risk), add caching layers with TTL and versioning, and only then add template caching with explicit invalidation triggers. Budget-aware dispatch should hard-stop rather than silently degrade to cheaper models.
