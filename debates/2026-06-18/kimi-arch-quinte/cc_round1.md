TASK: MAGI Gold architecture audit

## 1. Cost Analysis

### 1.1 Current Burn Rate

| Metric | Value |
|--------|-------|
| kimi K2.7 cost model | Weekly quota (allocated, capped) |
| Tokens per call | ~50K (always_thinking forces 80% waste → ~40K thinking, ~10K output) |
| Burn rate | 2 SOF calls = 13% weekly quota |
| Implied weekly capacity | ~15.4 calls at current burn rate |
| Effective useful tokens/call | ~10K (the rest is thinking cruft) |

**The binding constraint is quota, not money.** kimi is free (allocated quota), but the quota ceiling caps throughput. At ~15 calls/week, you cannot scale batch processing.

### 1.2 Proposed Architecture Costs

| Component | Cost Model | Est. tokens/call | Notes |
|-----------|-----------|------------------|-------|
| Tesseract OCR | Free (local) | N/A | Already required; pre-processing only |
| mimo-v2.5 (primary) | ¥39/mo fixed | ~5-8K/call | No forced thinking; multimodal |
| kimi K2.7 (fallback) | Quota | ~5-10K/call | Cropped regions only, thinking=auto (not always_thinking) |
| Fr+Myrrh | Unchanged | Unchanged | mimo-v2.5-pro + DeepSeek v4-pro |

**Projected savings (claimed):** ~90% reduction in kimi quota consumption.

### 1.3 Is This Cost-Optimal?

**Yes, conditionally.** The math works IF three assumptions hold:

1. **90% escalation avoidance is real.** If mimo correctly handles 90% of fields at confidence ≥ 0.7, kimi quota consumption drops from ~50K tokens/call to ~5-10K tokens for the 10% of fields that escalate. That's an ~85-90% reduction.

2. **Batch volume justifies the ¥39/mo fixed cost.** At low volume (e.g., <5 docs/week), the quota savings don't matter because you wouldn't exhaust kimi quota anyway. The ¥39/mo is dead weight. **Break-even: ~8 docs/week** — below that, all-kimi is cheaper (quota is sufficient).

3. **mimo vision API is reliable.** If mimo is down frequently and you fall back to all-kimi, you still pay ¥39/mo for nothing.

**Hidden costs not accounted for:**

| Hidden Cost | Impact |
|-------------|--------|
| Per-field kimi escalation overhead | N low-confidence fields = N additional API calls. 20-field form with 15% escalation = 4 extra kimi calls. API latency stacks. |
| Merge/normalization logic | Must reconcile mimo and kimi outputs. Field-level diffing, dedup, conflict resolution. Engineering time. |
| Crop infrastructure | Need bounding box extraction from Tesseract + field-level cropping pipeline. Non-trivial. |
| Monitoring/observability | Confidence distribution tracking, escalation rate alerts, per-model accuracy dashboards. Ongoing infra cost. |

**Verdict:** Cost-optimal at scale (>8 docs/week), but the fixed ¥39/mo and engineering overhead mean it's negative ROI for low-volume operations. Recommendation: implement with a kill-switch to route all-kimi when volume is low.

---

## 2. Implementation Risks

### Risk Matrix

| # | Risk | Severity | Likelihood | Mitigation |
|---|------|----------|------------|------------|
| R1 | **mimo confidence miscalibration** — self-assessed confidence scores are untested on shipping documents. If mimo is systematically overconfident, incorrect extractions pass the 0.7 gate silently. | HIGH | HIGH | Run calibration study against ground-truth labeled forms before deploying. Measure ECE (expected calibration error). |
| R2 | **Threshold (0.7) is arbitrary** — no empirical basis. Too high → excessive kimi escalations (negates savings). Too low → errors leak through. | MEDIUM | HIGH | Derive threshold from ROC/precision-recall tradeoff on labeled data. Start at 0.85 and relax based on observed error tolerance. |
| R3 | **mimo vision API availability** — multimodal API endpoints are newer, less stable, often have separate rate limits. If mimo vision is down, pipeline fails or falls back to all-kimi (paying ¥39/mo for nothing). | HIGH | MEDIUM | Implement health-check + circuit breaker. If mimo failure rate >5% in a window, auto-fallback to all-kimi. |
| R4 | **Merge inconsistency** — mimo and kimi may disagree on extracted values for the same field. E.g., "ABC Corp" vs "ABC Corporation." Without normalization rules, merged output is ambiguous. | MEDIUM | HIGH | Define field-level normalization (canonical forms, fuzzy matching). Prefer kimi on escalated fields (it's the "expert" fallback). |
| R5 | **Crop boundary errors** — Tesseract bounding boxes may be imprecise, especially on skewed/low-quality scans. Cropped region may omit critical context or include adjacent field noise, degrading kimi's fallback quality. | MEDIUM | MEDIUM | Add padding (10-15% margin) to crops. If adjacent fields overlap after padding, batch them into a single kimi call. |
| R6 | **Latency compounding** — Current: 1 kimi call. Proposed: Tesseract → mimo (1 call) → N kimi calls (for low-confidence fields). Best case: 2 calls. Worst case (all fields low confidence): 1 + N calls. 20-field form = up to 21 API calls. | MEDIUM | MEDIUM | Batch all low-confidence fields into a single composite kimi call (see §3.2). Timeout at 60s, fall back to mimo-only output. |
| R7 | **thinking=auto degradation** — Current always_thinking may produce better reasoning on ambiguous fields. Switching to auto means kimi may skip thinking when it shouldn't on edge cases. | LOW | MEDIUM | Monitor fallback accuracy. If kimi-auto produces worse results than kimi-always_thinking on escalated fields, switch back to always_thinking for fallback only (small token cost since fallbacks are rare). |
| R8 | **Tesseract OCR quality baseline** — If Tesseract output is poor (low-res scans, handwriting, heavy noise), mimo inherits garbage input regardless of its own capability. | MEDIUM | LOW | Add pre-Tesseract quality gate (see §3.3). If scan DPI < 150 or contrast < threshold, route directly to kimi. |

### Risk Interdependencies

- **R1 + R2 compound:** Poor confidence calibration + wrong threshold = either massive error leakage or massive unnecessary escalation. Both must be solved together.
- **R3 + R6 compound:** mimo downtime + high latency from per-field calls = pipeline stalls for minutes. Circuit breaker must kick in fast.
- **R4 + R5 compound:** Merge inconsistencies on incorrectly cropped regions = cascading errors that are hard to debug.

### Top 3 Killers

1. **R1 (confidence miscalibration):** If mimo systematically rates wrong answers as confident, the whole tiered architecture is worse than all-kimi — it adds latency and cost while silently degrading accuracy.
2. **R3 (mimo vision API reliability):** If the primary model is frequently unavailable, the architecture collapses to all-kimi. ¥39/mo becomes a sunk cost with no benefit.
3. **R4 (merge inconsistency):** If merged outputs require manual review/reconciliation, the labor savings evaporate.

---

## 3. Recommended Changes

### 3.1 Calibrate Before Deploying (Critical)

**Problem:** 0.7 threshold + untested confidence scores = blind gamble.

**Change:** Before switching routing, run a calibration experiment:
- Collect 50-100 labeled shipping documents with ground-truth field values
- Run mimo-v2.5 extraction on all of them, recording per-field confidence + correctness
- Plot confidence vs. accuracy, compute ECE
- Use precision-recall curve to find the threshold that meets accuracy SLA (e.g., 95% precision on accepted fields)
- If mimo's raw confidence is poorly calibrated, apply Platt scaling or isotonic regression on a holdout set

**Decision gate:** If mimo cannot achieve >90% precision at any threshold on the calibration set, abort the migration. mimo is not ready for this domain.

### 3.2 Batch kimi Fallbacks (High Impact)

**Problem:** Per-field kimi escalation means 1 kimi call per low-confidence field. A 20-field form with 5 low-confidence fields = 6 total API calls (1 mimo + 5 kimi). This adds latency, API overhead, and loses cross-field context.

**Change:** Instead of N individual kimi calls:
```
mimo output → identify low-confidence fields → composite crop (all low-confidence regions in one image) → single kimi call with structured prompt listing each field to extract → merge results
```

Benefits:
- 1 kimi call instead of N (reduces API overhead, preserves quota)
- kimi sees all ambiguous regions together, can use cross-field context (e.g., "this invoice number looks like it matches the PO number format")
- Simpler merge: one kimi output block, not N separate ones to reconcile

**Tradeoff:** Larger crop image = slightly more tokens. But still far less than full-document kimi calls. Acceptable.

### 3.3 Add Pre-OCR Quality Gate (Medium Impact)

**Problem:** Tesseract output quality is bounded by scan quality. Feeding garbage OCR to mimo wastes both the ¥39/mo subscription and kimi fallback quota.

**Change:** Before Tesseract, assess scan quality:
```
Scan → check DPI (<150 → skip) → check contrast (std dev of pixel intensities < threshold → skip) → check skew (>15° → deskew, else skip) → Tesseract
```

If scan fails quality gate, route directly to kimi (single full-document call with always_thinking). This avoids the worst-case where mimo + kimi fallback produces worse results than kimi alone on a bad scan.

### 3.4 Use mimo-v2.5-pro for Synthesis (Low Impact)

**Observation:** The evidence notes mimo-v2.5-pro is same tier (¥39/mo) but "text-only, strong synthesis." The proposed architecture uses mimo-v2.5 for vision extraction and keeps Fr+Myrrh unchanged.

**Change:** In the Fr stage, use mimo-v2.5-pro (not mimo-v2.5) for text synthesis after extraction. Since the extracted fields are already text, multimodal capability is irrelevant — use the stronger text model. This is zero marginal cost (same ¥39/mo tier).

### 3.5 Kill-Switch + Volume Gate (Operational)

**Change:** Implement two operational safeguards:
1. **Volume gate:** If weekly document count < 8, route all-kimi (quota is sufficient, ¥39/mo isn't justified)
2. **Circuit breaker:** If mimo error rate > 5% or latency > 10s p95 in a rolling 1-hour window, auto-fallback to all-kimi. Alert on escalation.

### 3.6 Revised Architecture (Post-Changes)

```
Document → Pre-OCR quality gate ─── FAIL → kimi (always_thinking, full doc)
              │
              PASS
              │
              ▼
         Tesseract OCR → mimo-v2.5 Gold (primary, ¥39/mo)
              │
              ├─ per-field confidence ≥ calibrated_threshold → accept
              │     → mimo-v2.5-pro synthesis (Fr) → Myrrh (DeepSeek) → QUINTE
              │
              └─ per-field confidence < calibrated_threshold
                   → batch all low-confidence regions
                   → single composite kimi call (thinking=auto, cropped composite)
                   → merge kimi fields into mimo output
                   → mimo-v2.5-pro synthesis (Fr) → Myrrh (DeepSeek) → QUINTE
```

### 3.7 Cost Delta Summary

| Scenario | Old (all-kimi) | New (proposed) | New (with changes) |
|----------|---------------|----------------|---------------------|
| Quota usage | 100% baseline | ~10% of baseline | ~5-8% of baseline (batched fallbacks) |
| Fixed cost | ¥0 | ¥39/mo | ¥39/mo |
| API calls/doc | 1 | 1 + N_fallback | 1 + 1 (max 2) |
| Latency p50 | ~8s | ~5-12s (variable) | ~5-8s (predictable) |
| Accuracy risk | Known (kimi baseline) | Unknown (mimo untested) | Measured (post-calibration) |

---

## Summary

The architecture is **directionally correct** — shifting bulk work from quota-constrained kimi to fixed-cost mimo is the right economic move at scale. However, it deploys with **unacceptable unknowns**: untested confidence calibration, an arbitrary threshold, and unbounded per-field API call fan-out.

**Must-do before deploy:** Calibrate mimo confidence on labeled shipping documents. If calibration fails, abort.

**Must-change in architecture:** Batch kimi fallbacks into single composite calls (eliminates N+1 API problem).

**Nice-to-have:** Pre-OCR quality gate, pro model for synthesis, volume-based kill-switch.
