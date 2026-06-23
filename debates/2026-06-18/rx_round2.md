R2 rx cross-review: hm+cw R1

## 1. OVERLAP ANALYSIS — Are the savings additive?

**Core problem (agreed by both):** Kimi outputs ~80% thinking tokens. This is the single largest lever, and both reviewers target it, but from incompatible angles.
This means several headline savings numbers cannot be stacked — they are alternative routes to the same destination.

### Overlap Map

| hm recommendation | cw recommendation | Relationship | Verdict |
|---|---|---|---|
| hm#2: stream-json (50% savings, strips thinking from output) | cw#1: disable thinking (60-70%) | **Direct overlap** — both eliminate thinking tokens. cw#1 is strictly superior: it saves backend compute, not just output bytes. hm#2 still pays for thinking generation; cw#1 doesn't. | **Cannot stack. Use cw#1.** |
| hm#2: stream-json | cw#3: strip thinking post-processing | **Subset overlap.** cw#3 is a weaker version of hm#2. Both are made redundant by cw#1. | **All three target the same 80%.** |
| hm#1: single call all pages (67%, 3→1) | cw#4: consolidate multi-call (40-50%, 2→1) | **Same strategy, different baselines.** hm assumes 3-call pattern, cw observed 2-call pattern in SOF test. Difference in percentage is purely a denominator artifact. | **Pick one based on actual dispatch count. Cannot stack.** |
| hm#3: template caching (60% on repeat) | cw#5: prefix cache (system prompt) | **Complementary, not overlapping.** Prefix cache is API-level (saves system prompt tokens every call). Template caching is application-level (skips redundant field verification). They operate at different layers. | **Additive.** |
| hm#5: crop to regions (30%) | hm#6: skip obvious fields (20%) | **Partially overlapping.** Cropping to regions already excludes "obvious" fields from the image. The 20% from hm#6 is largely subsumed by the 30% from hm#5. | **Net ~30-35% combined, not 50%.** |

### Dependency/Ordering Effects

Several strategies interact in ways that change their individual savings:

- **cw#1 (disable thinking) must come FIRST.** It's the dominant lever and invalidates hm#2 entirely. All subsequent savings are calculated on the post-thinking-elimination baseline, which is already 60-70% smaller.
- **hm#1/cw#4 (consolidate to single call) interacts with hm#5 (crop to regions).** Consolidation means one call processes all pages — the combined image payload may exceed the context window, forcing compromise on crop granularity or resolution. The 30% crop savings may shrink to ~15-20% when N pages are batched.
- **cw#5 (prefix cache) compounds with consolidation.** Fewer calls = fewer cache misses = higher effective hit rate. But the absolute savings shrink since there are fewer calls to benefit.

---

## 2. REALISTIC COMBINED SAVINGS — Calculated

Baseline: 2 Kimi calls per SOF, burning ~13% weekly quota (6.5% per call). Thinking = 80% of tokens.

### Step-by-step compounding (not additive stacking):

```
Baseline:                    100%  (2 calls, thinking ON)
├── cw#1: disable thinking   -65%  →  35%   (thinking is 80% of total; disabling saves 60-70%)
│   └── Remaining: 1 call equivalent at ~35% of original 2-call cost
├── cw#4: consolidate 2→1    -50%  of remaining
│   └── Now: 1 call at 17.5% of original 2-call baseline
├── cw#5: prefix cache       -5%   of remaining (saves ~500-2000 sys prompt tokens, small relative to vision payload)
│   └── Now: ~16.6%
├── hm#5/6: crop + skip      -25%  of remaining (net after overlap; ~20% on the smaller input)
│   └── Now: ~13.3%
├── hm#3: template caching   -40%  of remaining (on repeat calls only; weighted by repeat rate)
│   └── Now: ~8.0% (for repeat documents from known agents)
└── hm#4: text-layer bypass  SKIP  (already implemented; not additive to new strategies)

**Realistic combined: 87-92% reduction** for repeat documents; **~73-78%** for first-time documents.
Weighted by document mix (assuming 90% already bypassed via text-layer, 50% of remainder are repeats):
  Effective overall savings vs. naive-all-kimi baseline: **~92-94%** (dominated by text-layer bypass).
  Effective savings on documents that DO hit kimi: **~78-84%** (first-time: 73-78%, repeat: 87-92%).
```

**Key correction to hm's 85% claim:** hm arrived at ~85% by intuition, not calculation. The compounding method above confirms it's in the right ballpark for tuned scenarios but overstates for first-time documents. The 85% is achievable only with template caching (repeat docs). Without it, the ceiling is closer to 75-78%.

**Key correction to cw:** cw's dispatch template correctly disables thinking (the dominant lever) but doesn't account for hm's template caching, which is the second-largest lever for repeat documents. cw's budget caps (cw#7) are governance guardrails, not savings — they prevent overrun but don't reduce per-call cost.

---

## 3. LOGICAL CONTRADICTIONS

### Contradiction 1: Thinking output strategy (hm#2 vs cw#1)
- **hm** says: use stream-json to discard thinking from output → saves 50%.
- **cw** says: disable thinking at API level → saves 60-70%.
- **Resolution:** cw is correct. Receiving thinking tokens and then stripping them (hm#2) still pays for the generation cost. cw's approach eliminates the cost entirely. hm's 50% estimate undercounts the true savings because it only counts output token savings, not the backend compute. This is a **genuine contradiction in approach**, not just different numbers.

### Contradiction 2: Multi-call baseline divergence
- **hm** says: 3 calls → 1 (67% savings).
- **cw** says: the SOF test triggered 2 calls (40-50% savings for consolidation).
- **Resolution:** cw's number is evidence-based (observed 2 calls in the SOF test). hm assumes a 3-call pattern without citing a specific dispatch path. The difference matters because it affects whether consolidation alone saves 67% or 50%, which cascades through all compounding calculations. **hm's assumption is unvalidated.**

### Contradiction 3: Stream-json vs. disable thinking — which layer to solve at
- **hm** approaches thinking as an *output formatting* problem (stream-json strips it).
- **cw** approaches it as a *model configuration* problem (thinking_enabled=false).
- These reflect different mental models: hm treats thinking as unavoidable noise to filter; cw treats it as a controllable feature. **cw's model is more accurate for Kimi's API.**

### Contradiction 4: Template caching assumes repeatability (hm#3)
- **hm** assumes high template reuse (same agent = same SOF layout) → 60% savings on repeats.
- **cw** makes no such assumption — its strategies are call-agnostic.
- If template reuse is LOW, hm's 60% evaporates and cw's analysis is more robust. If it's HIGH, cw is missing a major lever. **Neither quantifies the repeat rate.**

---

## 4. UNEXAMINED ASSUMPTIONS

### A. Kimi's thinking token billing model (neither verifies)
Both reviewers assume thinking tokens are billed at the same rate as output tokens, or that disabling thinking eliminates cost. This needs verification:
- Does Kimi charge for thinking tokens even when `thinking_enabled=false` (hidden reasoning)?
- Are thinking tokens priced identically to output tokens?
- Are vision (image) input tokens priced differently from text input tokens?
- **Impact:** If thinking is zero-cost or differently priced, the entire 60-70% savings from cw#1 could be wrong.

### B. The 13% quota burn is representative (neither questions)
Both build strategy around "2 calls = 13% of weekly quota." Is this an average SOF or an outlier?
- Were these unusually large SOF documents?
- Were images sent at unnecessarily high resolution?
- Is 2 calls the typical dispatch pattern or a worst case?
- **Impact:** If the SOF test was a pathological worst case, all percentage savings overstate real impact. If it's typical, the urgency is justified.

### C. Consolidation doesn't exceed context limits (hm assumes, cw partially addresses)
- hm says "all pages in one call" without checking Kimi's vision context window.
- cw acknowledges this (risk: "only combine when total token count stays under 8K input") but doesn't verify whether typical SOF documents pass that threshold.
- Multiple pages × high-resolution regions × system prompt could easily exceed limits.
- **Impact:** If consolidation fails for 3+ page documents, the strategy degrades to partial batching, reducing the 50% savings.

### D. Thinking quality tradeoff is unquantified (both sidestep)
- cw's whitelist (diagnose/audit/complex_plan get thinking) acknowledges risk but provides no threshold: how do we know thinking isn't needed for a seemingly straightforward extraction?
- hm assumes extraction tasks work fine without thinking — no evidence cited.
- **Impact:** If accuracy drops on extraction tasks without thinking, the token savings could be offset by rework/errors downstream.

### E. Template caching depends on agent behavior stability (hm#3)
- Assumes agents don't change SOF templates over time.
- Assumes field positions are deterministic across renderings (same PDF generator, same font metrics).
- **Impact:** One font change or template revision invalidates cached coordinates, requiring re-verification and eliminating the 60% savings.

### F. Text-layer bypass's "90% already implemented" claim (hm#4)
- hm states this as fait accompli but provides no evidence: what's the actual hit rate of embedded text layers in shipping PDFs?
- Port/agent documents may be scanned or fax-originated at higher rates than generic office PDFs.
- **Impact:** If the actual rate is 70% not 90%, the pool of documents hitting Kimi triples in size, making per-call savings 3x more impactful.

### G. cw#6 (remove temp/top_p) — billing impact is speculative
- cw says "some providers bill extra tokens for explicit sampling overrides" — is Kimi one of them?
- Without verification, this is a micro-optimization that may save zero tokens.
- **Impact:** Near-zero if the assumption is wrong. Harmless, but shouldn't be counted in combined savings.

### H. Budget caps (cw#7) as a savings mechanism
- Budget caps prevent overrun but don't reduce per-call cost. They're a circuit breaker, not an efficiency measure.
- Including them in a "savings strategies" list conflates cost avoidance with efficiency improvement.
- **Impact:** Misleading framing — budget caps should be presented as governance, not savings.

---

## 5. SYNTHESIS — Recommended Combined Strategy

**Phase 1 (immediate, zero-risk):**
1. Set `thinking_enabled=false` for all non-whitelisted dispatch tags (cw#1 + cw#8). → **60-70% savings on most calls.**
2. Remove explicit temp/top_p params (cw#6). → negligible but harmless.
3. Consolidate multi-call patterns where total input stays under 8K tokens (cw#4 + risk guard). → **40-50% further savings on affected paths.**

**Phase 2 (requires validation):**
4. Implement prefix cache for stable system prompts (cw#5). → **5-10% additional.**
5. Crop images to relevant regions; skip text-layer-reliable fields (hm#5 + hm#6). → **20-30% on image payload.**
6. Test thinking-off accuracy on extraction tasks with a benchmark set of 20+ SOF documents. Only proceed if error rate remains within acceptable bounds.

**Phase 3 (requires data):**
7. Measure SOF template reuse rate across agents. If >40% repeat rate, implement template caching (hm#3). → **40-60% on repeat docs.**
8. Implement budget guardrails (cw#7) — but frame as governance, not savings.

**Expected total (kimi-hitting documents): 78-92% reduction vs. naive baseline**, with the higher end depending on template reuse rates and consolidation viability.

---

## 6. VERDICT

**hm's strengths:** Identified template caching and text-layer bypass — high-value, application-level strategies cw missed. Correctly identified multi-call consolidation as a major lever.

**hm's weaknesses:** ~85% claim is not derived from a compounding calculation and is overly optimistic for first-time documents. stream-json approach is inferior to API-level thinking disable. Doesn't address thinking quality tradeoffs.

**cw's strengths:** Correctly identifies thinking disable as the dominant lever and addresses it at the API level (superior to hm's output-filter approach). Provides risk analysis and tiered rollout. Budget guardrails prevent recurrence of the 13% disaster.

**cw's weaknesses:** Misses template caching as a major second-order optimization. Budget caps are misclassified as "savings" — they're governance. Overly conservative on some estimates (e.g., consolidation at 40-50% when 2→1 is 50% by definition).

**Synthesis value:** The two reviews are more complementary than contradictory once the thinking-token overlap is resolved. cw's approach to the thinking problem is structurally correct; hm's template caching and text-layer bypass add layers cw overlooked. Combined, they cover the problem from both the API-configuration angle (cw) and the document-workflow angle (hm).
