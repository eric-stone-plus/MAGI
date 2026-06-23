TASK: MAGI Gold architecture audit.

## 1. Cost Model: Is the Three-Way Structure Optimal?

### Current Spend Profile

| Layer | Resource | Cost Structure | Waste Factor |
|-------|----------|---------------|--------------|
| Gold (primary) | mimo-v2.5 | ¥39/mo fixed | Low (~5-8K tokens/call, no thinking) |
| Gold (fallback) | kimi K2.7 | Weekly quota (binding constraint) | High (always_thinking = ~80% token waste) |
| Frankincense | mimo-v2.5-pro | ¥39/mo (same subscription tier) | N/A (text synthesis, unchanged) |
| Myrrh | DeepSeek v4-pro | Pay-per-use (~$1.38/M tokens output) | Low (targeted reasoning, no forced overhead) |

### Verdict: Optimal _given constraints_, with one meaningful gap.

**What works:**

1. **kimi quota is the bottleneck.** At 13% weekly burn on 2 SOF calls, the all-kimi ceiling is ~15 documents/week. Any volume beyond that requires either more quota (not possible) or a kimi displacement strategy. mimo is the only multimodal alternative with fixed-cost pricing.

2. **mimo fixed cost enables volume scaling.** Below ~20 documents/month, the ¥39/mo fixed cost is worse than just using kimi (assuming quota unused). Above that threshold, the fixed cost becomes negligible per-document while kimi quota remains free for the hard cases. The architecture correctly identifies the crossover point matters, though no break-even calculation is provided. At 500 documents/month, ¥39 amortizes to ¥0.078/document — negligible.

3. **always_thinking is the real villain.** The 80% token waste on kimi thinking isn't a cost problem (quota is already allocated) — it's a _capacity_ problem. It means kimi's effective throughput is 5x lower than its raw token allowance. Per-field escalation partially addresses this by reducing prompt size, but each kimi call still pays the thinking preamble tax.

4. **DeepSeek is correctly left out of Gold.** DeepSeek v4-pro is text-only and pay-per-use. For vision tasks (scanned documents), it would require Tesseract→text preprocessing, introducing OCR error as a new failure mode. Its proper role is downstream reasoning (Myrrh), not upstream extraction.

**The gap: why isn't DeepSeek the text-heavy fallback?**

For fields that become text-only after Tesseract OCR (the document has already been OCR'd by the time we hit the confidence gate), kimi's vision capability is redundant. DeepSeek could serve as a cheaper, no-thinking-waste fallback for text-based field extraction from OCR output. This would:

- Zero thinking-token waste (DeepSeek has no forced thinking)
- Lower per-token cost (~$0.28/M input vs kimi quota burn)
- Preserve kimi quota exclusively for image-dependent fields (handwriting, stamps, unusual layouts)

This is the one missed optimization in the current cost model. A three-tier Gold (mimo → DeepSeek-text → kimi-vision) would be more efficient than two-tier (mimo → kimi).

---

## 2. Systemic Failure Modes

### FM-1: Confidence Calibration Collapse (HIGH SEVERITY)

**Mechanism:** mimo-v2.5 has no documented benchmark on shipping documents. If it systematically overestimates confidence (reports 0.85 when extraction is wrong), incorrect data passes the 0.7 gate silently. If it systematically underestimates (reports 0.55 when extraction is correct), kimi burns quota on unnecessary escalations.

**No recovery mechanism exists.** There is no downstream validation step between Gold merge and Fr+Myrrh. A bad extraction with high confidence propagates through the entire pipeline and lands in QUINTE output. The only guard is the confidence score itself — which is self-reported by the model doing the extraction. This is [Goodhart's law](https://en.wikipedia.org/wiki/Goodhart%27s_law) in production: when a metric becomes a gate, it ceases to be a reliable metric.

### FM-2: Merge Induced Inconsistency (MEDIUM SEVERITY)

**Mechanism:** When kimi overrides specific fields from mimo, the merged document contains data from two different models with different parsing conventions, date formats, and unit interpretations. A date parsed as "2024-03-15" by mimo might become "March 15, 2024" from kimi. A total parsed as "1,234.56" might become "1234.56." Downstream systems (Fr, Myrrh, QUINTE) may not handle these inconsistencies.

**Worst case:** kimi and mimo disagree on the _type_ of document (invoice vs. bill of lading), leading to fundamentally incompatible field structures. The merge step has no schema reconciliation logic.

### FM-3: kimi Quota Exhaustion Cascade (HIGH SEVERITY)

**Mechanism:** If mimo confidence drops below 0.7 for many fields in a single batch (e.g., a new document format, degraded scans, API model update), kimi receives a flood of per-field escalations. At 5-10 fields per document and 50 documents in a batch, that's 250-500 kimi calls — each with the always_thinking preamble tax. A single bad batch can exhaust the weekly quota in minutes.

**Amplifier:** The per-field design makes this worse than batched kimi calls. Each per-field call pays the thinking overhead independently. Batched escalation (one kimi call per document with all sub-threshold fields) would reduce the thinking-tax multiplier.

### FM-4: mimo API Unavailability (HIGH SEVERITY — NO CIRCUIT BREAKER)

**Mechanism:** The architecture has no fallback for mimo API outage. The pipeline is:

```
Tesseract OCR → mimo-v2.5 [BLOCKS HERE ON FAILURE] → per-field gate → kimi
```

kimi is only reachable through the confidence gate, which requires mimo to return a result first. If mimo returns HTTP 503, the entire Gold pipeline stalls with no alternative path. There is no timeout-to-kimi, no degraded mode, no queue-and-retry.

**Contrast:** The text-layer check at the top has an explicit branch (YES → zlib extract, NO → Tesseract). The mimo step has no equivalent. This is an architectural asymmetry.

### FM-5: Tesseract → mimo Error Propagation (MEDIUM SEVERITY)

**Mechanism:** Tesseract OCR quality directly determines mimo's input quality. If Tesseract produces garbled text from a low-quality scan, mimo may:

- **Confidently misread** the garbled text (high confidence on wrong answer → FM-1)
- **Correctly flag low confidence** → kimi escalation (which is the intended path, but wastes kimi quota on what should be a preprocessing fix)
- **Hallucinate** fields that don't exist in the document (OCR noise as input → model fills gaps)

No OCR quality check exists between Tesseract and mimo. A simple heuristic (character confidence from Tesseract, text coherence score) could gate whether kimi should handle the document from the start.

### FM-6: Latency Amplification Under Degradation (LOW SEVERITY)

**Mechanism:** If per-field kimi escalations are serial (each field waited on before processing the next), a document with N low-confidence fields adds N × kimi_latency to pipeline duration. At ~10-30 seconds per kimi call, a 5-field escalation adds 50-150 seconds per document. This is manageable at low volume but compounds under batch processing.

### FM-7: No Observability Surface (MEDIUM SEVERITY)

**Mechanism:** The pipeline has no telemetry on:
- Confidence score distribution over time (drift detection)
- kimi escalation rate per batch (quota burn rate)
- mimo vs. kimi agreement rate on escalated fields (merge quality)
- End-to-end accuracy (requires labeled test set — doesn't exist)
- API error rates and latency (availability monitoring)

Without these, failures in FM-1 through FM-6 are invisible until QUINTE output is wrong. The pipeline is a black box between document ingestion and final output.

---

## 3. What I Would Change

### Change 1: Add a DeepSeek Text Fallback Tier (Cost Optimization)

```
Tesseract OCR → mimo-v2.5 (primary)
  ├─ confidence ≥ 0.7 → accept
  └─ confidence < 0.7
       ├─ field is text-only (extracted from OCR text) → DeepSeek v4-pro
       └─ field requires vision (handwriting, layout) → kimi K2.7
```

**Rationale:** Once Tesseract has produced text, kimi's vision capability is unnecessary for text-only fields. DeepSeek is cheaper per-token than kimi quota burn, has zero thinking overhead, and is stronger at reasoning over noisy OCR text. kimi quota is reserved exclusively for vision-requiring fields.

**Risk:** Requires a field classifier to determine "text-only vs. vision-requiring." This could be heuristic (does the field have a clean OCR text extraction?) or a fast classifier model. Added complexity but ~50-70% further reduction in kimi quota consumption.

### Change 2: Add a mimo Circuit Breaker (Availability)

```
mimo-v2.5 call → timeout 30s, retries=2
  ├─ success → proceed
  └─ failure (timeout/503/rate-limit)
       → fallback: kimi full-document extraction (single call, not per-field)
       → alert: "mimo Gold unavailable, running degraded on kimi"
```

**Rationale:** The pipeline must not stall on mimo unavailability. The degraded mode uses kimi for full documents (not per-field) to minimize thinking-token waste during the degradation window. An alert ensures the operations team knows to investigate mimo API status.

### Change 3: Batch kimi Escalations Per Document (Efficiency)

```
Current:  per-field → kimi call → per-field → kimi call → ...
Changed: collect all sub-threshold fields → single kimi call with all regions → parse response
```

**Rationale:** Each kimi call pays the always_thinking preamble cost (~40K tokens of forced reasoning before the actual extraction begins). Batching N fields into one call saves (N-1) × thinking_tax. For a document with 5 low-confidence fields, this reduces token waste from ~200K to ~40K thinking tokens. The kimi prompt would present all cropped regions with field labels and ask for extraction of each.

**Downside:** Larger prompt per kimi call, but the thinking preamble dominates. Net savings for N ≥ 2.

### Change 4: Confidence Threshold from Data, Not Intuition (Calibration)

**Before deployment:**
1. Run mimo-v2.5 against a labeled test set of 50-100 shipping documents
2. Record confidence scores and actual accuracy per field
3. Produce a calibration curve (confidence vs. actual accuracy)
4. Set the gate threshold where precision ≥ 0.95 (not 0.7 arbitrarily)
5. If mimo cannot achieve 0.95 precision at any threshold, the two-model architecture is invalid and shouldn't deploy

**Rationale:** The 0.7 threshold is arbitrary. A miscalibrated model at 0.7 either wastes kimi quota (threshold too high) or passes bad data (threshold too low). The threshold must be set empirically. If mimo-v2.5 can't achieve high precision at any confidence level, the premise of "mimo handles clean fields, kimi handles hard fields" collapses — kimi must remain primary.

### Change 5: Add a Merge Consistency Gate (Data Quality)

After mimo + kimi fields are merged but before Fr+Myrrh:

```
Merge result → consistency checks:
  ├─ All date fields parse to valid dates? (no "Feb 30" or "2024-13-01")
  ├─ Numeric fields sum consistently? (line items ≈ total?)
  ├─ Document type inferred matches field structure?
  └─ Failures → flag for human review queue, do NOT auto-propagate
```

**Rationale:** Model disagreement in merged output is a signal of extraction uncertainty that the confidence gate missed. Rather than silently propagating potentially inconsistent data, flag for review. This adds a human-in-the-loop step but only for the small fraction of documents where models disagree — which is exactly the fraction that needs human judgment.

### Change 6: Add Observability from Day One (Operations)

Minimum viable telemetry, emitted per batch:

```
- mimo_confidence_histogram: distribution of confidence scores
- kimi_escalation_rate: % of fields escalated to kimi
- kimi_quota_remaining: weekly quota before/after batch
- mimo_api_latency_p50/p99: response time distribution
- mimo_api_error_rate: 5xx/timeout rate
- merge_disagreement_rate: % of escalated fields where kimi ≠ mimo
- pipeline_end_to_end_latency: document ingestion to QUINTE output
```

**Rationale:** FM-1 through FM-6 are invisible without telemetry. The confidence histogram alone would catch calibration drift within the first batch. Quota tracking prevents FM-3 (exhaustion cascade) by alerting before quota hits zero. All metrics are cheap to collect (counters and timers at pipeline boundaries).

### Change 7: Pre-mimo OCR Quality Gate (Waste Reduction)

```
Tesseract OCR → OCR quality check:
  ├─ Tesseract confidence ≥ 0.6 AND text coherence score ≥ 0.5 → mimo
  └─ Below threshold → skip mimo, go directly to kimi full-document
```

**Rationale:** If Tesseract produces garbage, mimo will either confidently misread it (FM-1) or correctly escalate to kimi (wasting time and a mimo call). Skip the middleman. The quality gate uses Tesseract's own confidence scores plus a simple coherence heuristic (ratio of dictionary words to total tokens, or character-level confidence mean). This prevents both failure modes and saves one API call per garbage-quality document.

---

## Summary

The mimo-primary + kimi-fallback architecture is directionally correct but operationally incomplete. Three gaps dominate:

1. **No calibration evidence** — the 0.7 confidence gate is a guess. Without labeled benchmarks, the architecture's core premise (mimo can reliably distinguish correct from incorrect extractions) is unproven. This is a deployment-blocking gap.

2. **No circuit breaker** — mimo API failure halts the pipeline with no degraded path. This is an availability risk that should be addressed before production.

3. **Per-field kimi escalation amplifies thinking waste** — the always_thinking preamble is paid per kimi call. Batching escalations per document would significantly reduce quota burn with no accuracy impact.

The three-way cost model (mimo fixed + kimi quota + DeepSeek pay-per-use) is optimal given current constraints, but a DeepSeek text-fallback tier for OCR'd fields would further reduce kimi dependence by ~50-70%.
