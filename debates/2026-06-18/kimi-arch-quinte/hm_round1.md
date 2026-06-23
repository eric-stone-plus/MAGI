# R1 · hm — MAGI Gold Architecture Audit

## Cost Reality (CORRECTED 2026-06-18)

| Resource | Cost Rank | Model | Vision | Thinking Cost | Best For |
|----------|----------|-------|--------|---------------|----------|
| **kimi K2.7** | **Most expensive** | K2.7 Code | ✅ | always_thinking (80% waste on forms) | Complex ambiguity only |
| **mimo-v2.5** | Mid (¥39/mo) | v2.5 | ✅ | None | Bulk form extraction |
| **DeepSeek v4-pro** | Pay-per-use | v4-pro | ❌ | On-demand | Text reasoning, Myrrh attack |

## Key Insight: This Is Backwards From Earlier Assumption

Previous architecture discussions assumed kimi quota was "free/allocated" and DeepSeek was the expensive one. Reality: kimi is the MOST expensive per effective token. mimo is fixed monthly cost — cheapest per document at volume.

This means:
1. **kimi-primary was doubly wrong**: most expensive model + 80% thinking waste = worst accuracy/token ratio
2. **mimo-primary is triply right**: cheapest model + no thinking overhead + multimodal
3. **kimi-fallback needs reevaluation**: if kimi is most expensive, every escalation costs disproportionately

## Revised Cost Model

```
Single SOF document (3 pages, scanned):

Old (kimi-primary):
  3-page kimi call: ~50K tokens → expensive
  Cost: 1 kimi inference (most expensive)
  
New (mimo-primary + kimi fallback):
  mimo-v2.5: ~5K tokens → ¥39/mo fixed
  + kimi escalation on 1-3 fields: ~3-8K tokens → expensive
  Cost: 1 mimo call (cheap) + 0-3 kimi calls (expensive only if needed)
```

## Revised Assessment

### Pro-mimo Arguments (strengthened by cost correction)

1. **Cost ordering aligns with architecture**: cheapest model does bulk work, most expensive does only essential work
2. **mimo fixed cost enables scaling**: ¥39/mo covers unlimited SOFs (within rate limits)
3. **kimi quota preserved for irreplaceable scenarios**: handwriting, stamps, legal disputes where thinking adds real value

### New Concerns (from cost correction)

4. **Kimi fallback is now a premium luxury**: every escalation burns the most expensive resource. The confidence threshold becomes a cost lever — too low = lots of expensive kimi calls, too high = accuracy risk
5. **Clarity gate threshold (0.7) not calibrated to cost**: should be HIGHER if kimi is most expensive — maybe 0.5 or 0.6 to reduce escalations
6. **Need to measure actual escalation rate**: if 30% of fields trigger kimi, the cost advantage over all-kimi shrinks

## Architecture Recommendation (Revised)

```
Tier 1: Text-layer PDFs → zlib → DS verify → Fr+Myrrh → QUINTE
         Cost: ~0 (no vision model needed)

Tier 2: Clean scanned PDFs → Tesseract OCR → DS text-verify → Fr+Myrrh → QUINTE
         Cost: ~0 (DS text verification, minimal tokens)
         ⚠️ Depends on OCR accuracy — test first

Tier 3: OCR-unreliable scanned PDFs → mimo-v2.5 Gold → Fr+Myrrh → QUINTE
         Cost: ¥39/mo fixed
         kimi escalation ONLY if field is BOTH low-confidence AND high-stakes
         
         High-stakes fields: NOR time, cargo tons, weather events
         Low-stakes fields: agent address, vessel name (OCR reliable)

Tier 4: kimi Gold — only for documents where mimo can't help
         Cost: most expensive
         Triggers: handwriting SOFs, faxed documents, stamps/overprints
```

## Critical Addition: DS Text-Verify Tier

Between zlib extraction and mimo vision, there's an untapped tier: DeepSeek text verification. If Tesseract OCR produces text with reasonable accuracy, DeepSeek v4-pro can verify field extraction at minimal token cost (text-only, no vision). This handles the "OCR is good enough for DS to catch errors" case without touching kimi or mimo at all.

Example:
```
Tesseract output: "NOR tendered: 2026-06-15 14:30"
DS verifies: date format valid, within voyage window, consistent with other fields
→ Accepted. No vision model needed.
```

This could handle 60-80% of scanned PDFs if OCR quality is decent — leaving mimo and kimi for the genuinely hard cases.

## Concerns

1. **mimo vision accuracy is untested** — need a benchmark on 10-20 real SOFs
2. **Confidence threshold is the critical parameter** — wrong value = either overspend (too many kimi calls) or accuracy risk (too few)
3. **Three tiers add operational complexity** — but each tier has a clear trigger condition
4. **DS text-verify tier is speculative** — haven't tested Tesseract+DS combo on SOFs
