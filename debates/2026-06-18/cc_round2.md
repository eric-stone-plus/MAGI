R2 cc cross-review: hm+cw R1

## Overview

Both R1 analyses correctly identify that SOF kimi calls burned ~13% weekly quota and that kimi output in text mode is ~80% thinking. However, both contain claims that are technically impossible, provably incorrect, or fail to account for destructive interactions between strategies. Below I challenge each claim with evidence from the actual kimi-code wire logs and configuration.

---

## hm R1 — Gaps and Challenges

### Claim 1: Single-call 67% savings

**Challenge: Overstated and conditional.**

The 67% figure assumes N=3 calls reduced to 1. For a 3-page SOF, 3→1 = 67% call reduction. But:
- Many SOFs are 1-2 pages. For 2 pages: 2→1 = 50% call reduction.
- The SOF test that burned 13% quota was already 2 calls covering 3 pages (session 960153ab = page 1, session 485903ac = pages 2-3). The savings from 2→1 is 50%, not 67%.
- Single-call with all pages risks context dilution: kimi's attention over 3 full-page images degrades vs focused per-page attention. Accuracy loss on field extraction could create false positives in demurrage calculation — a cost far exceeding token savings.
- **Feasibility gap**: The kimi-code prompt length limit with `-p` is unverified for 3-page image references. If the prompt+picture references exceed the CLI's max argument length, this strategy fails at runtime.

**Verdict**: Realistic savings 33-50%, not 67%. Risk of accuracy degradation unaddressed.

### Claim 2: stream-json → 50% savings

**Challenge: Mechanism misunderstood; actual savings 23-33%.**

The kimi-code reference document (kimi-code-r1-participant.md) explicitly states:
> "Token cost | +30-50% in text mode; stream-json comparable [to DeepSeek baseline]"

This means text mode costs 130-150% of stream-json. The savings from switching are:
- If text = 1.30× stream-json → savings = 23% (1 - 1/1.30)
- If text = 1.50× stream-json → savings = 33% (1 - 1/1.50)

These are output-side savings only. The input tokens (images, system prompt) are identical in both modes. Since images dominate input for vision tasks, the **total** savings are much lower — perhaps 10-15% of total tokens.

**Critical finding from wire logs**: Session 960153ab (stream-json, page 1): `output=269` tokens. Session 485903ac (stream-json, pages 2-3): `output=1946` tokens. These are tiny compared to `inputCacheRead=31488` and `53800`. Output is 0.7-3.1% of total tokens billed. Saving 30% of 3% is negligible. The **real** savings from stream-json come from NOT paying for thinking tokens, but whether kimi bills for hidden thinking tokens is unconfirmed.

**Also**: The model has `always_thinking` capability — thinking IS generated server-side regardless of output format. If billing counts thinking tokens even when hidden, stream-json saves zero tokens on billing (only saves output clutter).

**Verdict**: 50% claim is unsupported. Realistic total savings: 10-15% (output-side only), or 0% if thinking tokens are billed invisibly.

### Claim 3: Template caching → 60% on repeats

**Challenge: Fragile in maritime document reality.**

The scheme stores field coordinates ("NOR time at line 15, position 40-55") and verifies only changed fields. Multiple failure modes:

1. **Scan variability**: Different port agents use different scanners at different DPI. A 150 DPI scan vs 300 DPI scan shifts all coordinates.
2. **OCR non-determinism**: Tesseract OCR on the same image can produce different line counts depending on preprocessing (deskew, threshold, noise removal). The "line 15" you cached may be line 17 on the next run.
3. **Form revisions**: SOF templates change between agents, ports, and years. The caching assumption that "same agent's SOF uses identical layout" fails when the agent updates their stationery.
4. **Photo vs scan**: Many SOFs arrive as smartphone photos with perspective distortion, shadows, and variable crop. Coordinates from a scanned SOF are useless for a photo SOF.
5. **The verification paradox**: To verify "only changed fields changed," you must READ the full document to confirm no other fields changed. You can't partially read and guarantee correctness — a shifted field (e.g., extra weather row) could go undetected.
6. **No evidence of implementation**: Template caching requires a coordinate extraction pipeline that doesn't exist. The MAGI pipeline currently extracts text via OCR and sends images to kimi — there's no intermediate coordinate layer.

**Verdict**: 60% savings is aspirational. Realistic: 20-30% for genuinely identical scans from the same machine/operator. Risk of silent errors from coordinate drift is unacceptable for demurrage (financial liability).

### Claim 4: Text-layer bypass → 90% docs never hit kimi

**Challenge: Reversed reality for maritime documents.**

This is already implemented (zlib extraction) but the 90% figure is for ALL documents. In maritime demurrage:
- SOFs arrive as **scanned PDFs** (faxed, photocopied, scanned from thermal paper) — these have NO text layer.
- The SOF test document (MV HONG YU) explicitly required OCR because zlib extraction FAILED: "qpdf decrypt → zlib text (failed, no text layer)."
- Digitally-generated PDFs with embedded text are the exception in shipping, not the norm.
- A more realistic estimate: 30-50% of maritime documents have extractable text layers. The rest hit OCR → kimi.

**Verdict**: The 90% figure is misleading for this domain. Actual bypass rate for SOFs: probably 20-40%.

### Claim 5: Crop to relevant regions → 30% input savings

**Challenge: Chicken-and-egg problem.**

You need to FIND the relevant regions before you can crop to them. This requires either:
- A preliminary full-image scan to locate fields (which burns the tokens you're trying to save), or
- Template-based coordinate lookups (same fragility as Claim 3).

If you use a cheap model for preliminary localization, the two-call pattern (cheap-locate → kimi-extract) may cost more than one full-image kimi call. Also, kimi's vision token billing may not scale linearly with image area — partial images may still consume significant tokens.

**Verdict**: 30% is optimistic. Realistic: 10-20% IF template coordinates are reliable. Net savings could be zero or negative after adding a localization step.

### Claim 6: Skip obvious fields → 20% input savings

**Challenge: False economy with legal risk.**

"Agent address" is deemed "obvious" and reliable via OCR. But in demurrage disputes:
- The agent's address sometimes determines jurisdiction (which port, which legal venue).
- OCR errors on addresses are COMMON — "Suite 1400" → "Suite 140G", "Pte Ltd" → "PteLtd", "Houston" → "Houst on".
- Skipping verification on "obvious" fields saves 20% tokens but introduces a legal risk that a single OCR error on an address could invalidate a demurrage claim worth $50K-500K.
- The cost-benefit of saving <100 tokens vs risking a six-figure claim is absurd.

**Verdict**: 20% savings claim ignores risk-adjusted cost. Not recommended for production.

### Claim 7: Combined savings ~85%

**Challenge: Additive fallacy — strategies overlap, not stack.**

The strategies affect different parts of the token budget, but they interact:
- Single-call (hm#1) already eliminates duplicate system prompts for pages 2-N. If you also use prefix caching (cw#5), the marginal benefit of caching shrinks to near-zero.
- If you use stream-json (hm#2), stripping thinking (cw#3) saves nothing additional — it's already hidden.
- If you use template caching (hm#3), cropping (hm#5) and skip-fields (hm#6) are redundant — you already know where fields are.
- If text-layer bypass (hm#4) works, NONE of the kimi strategies are needed.

A more realistic composite:
- Base: 100 tokens (text mode, multi-call)
- After text-layer bypass (40% of docs): 60 tokens (only scanned docs hit kimi)
- After single call (50% call reduction for scanned docs): 30 tokens
- After stream-json (15% total savings): 25.5 tokens
- After template caching (25% on repeats, where applicable): varies

**Realistic composite: 40-75% savings**, not 85%. The range depends on document type distribution and repeat rate.

---

## cw R1 — Gaps and Challenges

### Claim 1: Disable thinking → 60-70% savings

**Challenge: TECHNICALLY IMPOSSIBLE with current kimi-code.**

The kimi-code model configuration:
```toml
[models."kimi-code/kimi-for-coding"]
capabilities = [ "thinking", "always_thinking", "image_in", "video_in", "tool_use" ]
```

`always_thinking` means the model generates reasoning tokens on EVERY call. There is:
- **No `--thinking` CLI flag** in kimi-code (verified via `kimi --help`)
- **No `thinking_enabled` parameter** in config.toml beyond `default_thinking = true`
- **No API-level override** exposed through the CLI

The config.toml has `[thinking] mode = "auto"` and `effort = "high"` but these control thinking style, not on/off. The dispatch template in cw's recommendation uses `"thinking_enabled": false` — this parameter simply does not exist in the kimi-code ecosystem.

**To actually disable thinking would require**:
- Switching to a different model that lacks `always_thinking` (but then you lose vision capabilities needed for SOF), OR
- Using the raw API directly (bypassing kimi-code CLI), which would require a complete rewrite of the Gold dispatch path, OR
- Moonshot AI adding a thinking toggle to kimi-code (not under our control).

**Verdict**: 60-70% savings is theoretically correct for the API but **impossible to implement** with the current tooling. This is the single biggest gap in either R1 analysis — it recommends a feature that doesn't exist.

### Claim 2: Cap thinking_max_tokens at 800 → 30-40% savings

**Challenge: Parameter doesn't exist in kimi-code.**

The CLI has no `--thinking_max_tokens` flag. The config.toml has no such setting. Even if thinking could be capped, the claim that diagnostic traces "rarely benefit from more than a few hundred tokens of reasoning" is unsubstantiated — kimi's internal reasoning may legitimately need more tokens for complex visual verification tasks involving multiple fields across multiple pages.

**Verdict**: Impossible to implement. Savings estimate is speculative.

### Claim 3: Strip thinking from response

**Challenge: Already solved by stream-json; irrelevant otherwise.**

When using `--output-format stream-json` (which hm correctly recommends), thinking is already hidden from output. When using `--output-format text`, stripping thinking requires fragile text parsing (thinking format varies). Either way, the thinking tokens were already generated and billed — stripping saves downstream context but not quota.

**Verdict**: Redundant if hm#2 is implemented. Minimal standalone value.

### Claim 4: Consolidate multi-call → 40-50% savings

**Challenge: Overstated; prefix caching already handles much of this.**

Wire log evidence shows `inputCacheRead: 14592-53800` across sessions, with `inputCacheCreation: 0`. This means the kimi-code system prompt is ALREADY cached and re-read from cache on subsequent calls. The 40-50% savings estimate assumes system prompt is re-billed on every call — it's not.

Actual savings from consolidation:
- Eliminates second round-trip latency (real, but not token savings)
- Eliminates second per-call overhead (model loading, context initialization) — maybe 5-10% of tokens
- May increase per-call token count enough to trigger different pricing tier (negative savings)

**Also**: cw's risk note says "only combine when total combined token count stays under 8K input." The SOF sessions show 36K-62K input tokens per call — already far above 8K. Combining them would produce a ~99K token call, which violates cw's own constraint.

**Verdict**: 40-50% is 4-5× too high. Realistic: 5-10% for eliminating second-call overhead. Strategy may be impossible if combined input exceeds provider limits.

### Claim 5: Cache system prompt as prefix

**Challenge: ALREADY ACTIVE.**

Wire log evidence conclusively shows prefix caching is working:
- `inputCacheRead: 14592` (session 960153ab), `53800` (session 485903ac)
- `inputCacheCreation: 0` (cache already warm)

The config.toml doesn't expose a `prefix_cache` toggle because it's handled automatically by the kimi-code runtime. cw is recommending a feature that's already implemented and working.

**Verdict**: Redundant — zero additional savings. This recommendation suggests cw didn't inspect actual system behavior before writing R1.

### Claim 6: Remove explicit temp/top_p params

**Challenge: Irrelevant to kimi-code.**

kimi-code CLI has no `--temperature` or `--top_p` flags. The provider manages these internally. There's nothing to remove. The recommendation is copied from general API optimization advice without checking whether it applies to this specific tool.

**Verdict**: Zero savings — nothing to optimize. Inapplicable to kimi-code.

### Claim 7: Budget-aware dispatch

**Challenge: Architecture gap — no middleware exists.**

This is a good long-term idea but:
- No token-tracking middleware exists in the MAGI pipeline
- The `session_cap_tokens: 100000` would trigger on the FIRST SOF document (~101K tokens for 2 calls in the test), making it effectively a "one SOF per session" limit
- Fallback to `deepseek-v3` assumes deepseek-v3 has vision capabilities for SOF reading (it doesn't — SOF verification requires vision)
- `hourly_cap_tokens: 80000` is below the per-SOF consumption, meaning every SOF triggers a downgrade — the "budget-aware" system would NEVER use kimi

**Verdict**: Conceptually sound but parameters are misconfigured. With current caps, kimi would never be usable for SOF. Requires significant middleware development.

### Claim 8: Whitelist thinking for magi:diagnose/audit/complex_plan

**Challenge: Dispatch tags may not map to actual MAGI workflow.**

The MAGI protocol (v1.0) uses phases (R1→R2→R3), not dispatch tags like "diagnose" or "audit." The Gold role in SOF processing performs visual field verification — it's neither "diagnose" nor "audit" nor "complex_plan." The whitelist categories don't cleanly map to actual MAGI Gold tasks.

More importantly: since thinking CANNOT be disabled (Claim 1), the whitelist is moot regardless.

**Verdict**: Misaligned with actual MAGI dispatch taxonomy. Moot since thinking can't be toggled.

---

## Cross-Cutting Interactions That Cancel Benefits

### Interaction 1: Single-call + prefix caching = diminishing returns
hm recommends single-call to avoid multiple system prompts. cw recommends prefix caching to avoid re-billing system prompts. But if you do single-call, there IS no second system prompt to cache. The strategies compete for the same pool of savings.

### Interaction 2: Stream-json + strip thinking = redundant
hm's stream-json already hides thinking from output. cw's "strip thinking from response" adds nothing. Two strategies targeting the same waste.

### Interaction 3: Template caching + crop/skip = redundant
If template caching works (hm#3), you already know field positions. Cropping (hm#5) and skipping fields (hm#6) provide no additional benefit — they're alternative approaches to the same problem (reducing what kimi needs to read).

### Interaction 4: Low output token ratio undermines output-side strategies
Wire logs show output is 0.7-3.1% of total tokens. Any strategy that only reduces output (stream-json, strip thinking, response compression) has a ceiling of 3% total savings. The real waste is on the input side (images, system prompts) which none of the output-side strategies address.

### Interaction 5: Combined prompt + context limits = impossible for SOF
cw's combined prompt strategy requires total input <8K tokens. Actual SOF calls are 36K-62K. Combining them would produce a 99K+ token call that may exceed kimi's context window or trigger different pricing. The strategy is self-contradictory for the actual workload.

---

## Implementation Risks Neither R1 Author Identified

### Risk 1: kimi-code version lock-in
Both R1s assume stable kimi-code behavior. But kimi-code is version 0.15.0 — pre-1.0 software. A version bump could change thinking behavior, output format, caching behavior, or pricing. Strategies that depend on specific kimi-code behavior (stream-json suppressing thinking in billing vs just output) could break silently.

### Risk 2: Quota accounting opacity
The 13% burn claim is based on observed quota changes (37%→24%). But kimi's quota meter may include non-token usage (tool calls, image processing, search). The actual per-token cost and total quota are opaque. All savings estimates are therefore percentages of an unknown denominator.

### Risk 3: Stream-json accuracy degradation
The kimi-code reference notes stream-json suppresses "self-narration" and "mode selection overhead." These narrative elements may serve as the model's working memory — suppressing them could reduce answer quality even if thinking still happens server-side. No A/B test has been done comparing stream-json vs text mode extraction accuracy on SOF fields.

### Risk 4: Image preprocessing as hidden token cost
The SOF pipeline currently does qpdf decrypt → OCR → page images. The page images sent to kimi may include OCR overlay text, which increases image complexity and token cost. Optimizing image preprocessing (lower DPI, grayscale, remove OCR overlay before sending to kimi) could save more tokens than any prompt-engineering strategy — and was not mentioned by either R1.

### Risk 5: Demurrage liability from false negatives
All efficiency strategies reduce what kimi sees. Template caching verifies "only changed fields." Cropping removes context. Skipping fields removes safety checks. In demurrage, a missed weather event or incorrect cargo tonnage can mean $10K-100K in incorrect charges. The token savings from any strategy must be weighed against the expected cost of errors — neither R1 does this risk-adjusted calculation.

---

## Summary of Viability

| Strategy | Claimed Savings | Realistic Savings | Feasible? |
|---|---|---|---|
| hm#1 single-call | 67% | 33-50% | Yes, with accuracy caveat |
| hm#2 stream-json | 50% | 10-15% (output only) | Yes (already used in test) |
| hm#3 template caching | 60% | 20-30% (fragile) | Partial — coordinate drift risk |
| hm#4 text-layer bypass | 90% | 20-40% for maritime | Already implemented |
| hm#5 crop regions | 30% | 0-20% (chicken-egg) | Requires localization step |
| hm#6 skip fields | 20% | Not recommended | Legal risk > token savings |
| hm combined | 85% | 40-75% | Overstated due to interactions |
| cw#1 disable thinking | 60-70% | 0% | **IMPOSSIBLE** (always_thinking) |
| cw#2 cap thinking | 30-40% | 0% | **IMPOSSIBLE** (no param) |
| cw#3 strip thinking | N/A | 0% new | Already done by stream-json |
| cw#4 consolidate calls | 40-50% | 5-10% | Conflicts with own 8K limit |
| cw#5 prefix cache | ~2K/call | 0% | **Already active** |
| cw#6 remove temp/top_p | minimal | 0% | **Inapplicable** to kimi-code |
| cw#7 budget dispatch | N/A | N/A | Caps misconfigured for SOF |
| cw#8 whitelist thinking | N/A | N/A | Moot (can't toggle thinking) |

**Bottom line**: Of cw's 8 recommendations, 5 are either impossible, already implemented, or inapplicable. hm's recommendations are more grounded but the combined 85% estimate is ~10-45 points too high and ignores accuracy/degradation risks. The single highest-impact, actually-implementable change is hm#1 (single call) + hm#2 (stream-json), which together deliver 35-55% real savings with no new infrastructure.
