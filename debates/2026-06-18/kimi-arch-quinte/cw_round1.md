TASK: MAGI Gold architecture audit. ONLY: accuracy analysis, confidence gate, changes.

## 1. Accuracy Risks — mimo-v2.5 Vision vs kimi on Shipping Docs

**Pipeline ambiguity matters.** The architecture says "Tesseract OCR → mimo-v2.5 Gold." If mimo receives only Tesseract's text output (no image), the vision comparison to kimi is moot — kimi operates on raw document images and benefits from visual layout/spatial reasoning. If mimo receives both OCR text + original image, the visual cross-reference could compensate for OCR errors, but this capability is unverified at mimo's tier.

**Document quality spectrum.** Shipping documents span clean digital PDFs to Nth-generation fax scans with stamps, handwriting, bleed-through, skew, and multi-language text. kimi K2.7's always_thinking mode, while wasteful on clean forms, excels at disambiguation in degraded conditions. mimo-v2.5, a ¥39/mo subscription model, lacks dedicated reasoning tokens for ambiguity resolution.

**Specific failure modes:**

| Failure Mode | Severity | Rationale |
|---|---|---|
| Handwriting extraction | High | kimi's thinking disambiguates cursive/stamps; mimo likely guesses or returns garbage |
| Stamped/overlay text | High | Stamps overlapping data fields confuse extraction without spatial reasoning |
| Low-contrast/scanned forms | Medium | Tesseract produces noise; mimo field extraction degrades on noisy input |
| Multi-column tables | Medium | Column association errors (wrong value to wrong field) |
| Mixed Chinese/English | Medium | Language-switching within fields (e.g., consignee names) |
| Currency/date formats | Low-Medium | Ambiguous formats (MM/DD vs DD/MM, ¥ vs CNY vs RMB) |

**Untested baseline.** No benchmark exists comparing mimo-v2.5 vs kimi on shipping document extraction. Claiming ~90% kimi quota reduction assumes mimo will achieve comparable accuracy, which is unvalidated. The risk of silent extraction errors propagating through Fr+Myrrh into QUINTE is material.

**Structural dependency.** Because Fr+Myrrh consume Gold output as ground truth, any extraction error at Gold tier cascades undetected. QUINTE has no feedback loop from downstream to correct Gold.

## 2. Confidence Gate Reliability

**Self-assessment is uncalibrated.** LLM-generated confidence scores are well-documented to suffer from miscalibration — models can be overconfident on errors and underconfident on correct outputs. A threshold of 0.7 chosen without calibration data is an arbitrary decision boundary. Without a calibration study (mimo output vs ground truth across document types), we cannot know whether 0.7 yields 95% precision or 60%.

**Per-field independence assumption breaks.** The architecture evaluates confidence per-field, but shipping document fields have dependencies. A correct consignee name doesn't guarantee correct address; a correct container number doesn't guarantee correct seal number. Low confidence on one field should raise suspicion on adjacent fields, but the gate treats each field in isolation.

**Systematic bias risk.** If mimo-v2.5 is systematically overconfident, most errors pass silently. If systematically underconfident, escalation volume defeats the cost saving. The propensity likely varies by document type (clean = overconfident, degraded = underconfident), creating a bimodal failure distribution.

**Merge integrity.** When kimi overrides low-confidence fields, there is no consistency check against mimo-accepted fields. Scenario: mimo accepts "port of discharge: Shanghai" (confidence 0.85) but kimi overrides "vessel name: Ever Given" (confidence 0.55) to "Evergreen". The vessel/port pair may be inconsistent, and no reconciliation step catches this.

**Confidence mechanisim unspecified.** Is this a numeric prompt output, logprob aggregation, or token-probability extraction? Each method has different reliability characteristics. Logprob-based confidence on structured outputs is more reliable than prompted scores, but the architecture doesn't specify.

## 3. Recommended Changes

### A. Calibrate Before Deploying (Critical)
Run a side-by-side benchmark: 200 shipping documents through both mimo-v2.5 and kimi. Use kimi output as ground truth (or human-verified). Plot mimo confidence vs actual correctness. Determine:
- Precision at threshold 0.7 (how many "high confidence" fields are actually wrong?)
- Recall at threshold 0.7 (how many correct fields get unnecessarily escalated?)
- Optimal threshold per document type and per field type

Do not deploy until calibration confirms threshold viability.

### B. Add Structural Validation Layer
Before confidence-gating, validate extracted fields against expected schemas:
- Numeric ranges (container numbers, weights, quantities)
- Format patterns (dates, currencies, BL numbers)
- Cross-field consistency (net weight ≤ gross weight, container count matches seal count)
- Flag structural violations for escalation regardless of confidence score.

### C. Batch kimi Escalations Per Document
Replace per-field kimi calls with one batched call per document containing all low-confidence fields + their image regions. Reduces API overhead (point 7 against) and allows kimi to reason about inter-field consistency on the escalated subset.

### D. Implement Merge Reconciliation
When kimi overrides even a single field, run a lightweight consistency check across the merged result. Flag documents with cross-field inconsistencies for human review or a second pass.

### E. Set kimi Fallback to thinking=high
The escalated cases are definitionally ambiguous — they are the fields mimo couldn't confidently extract. Disabling thinking on these calls (or leaving it at auto) wastes kimi's core advantage on exactly the cases that need it. Accept the token cost for fallback calls.

### F. Staged Rollout with Shadow Mode
Deploy mimo-primary in parallel with existing kimi-primary for 2 weeks. Route every Nth document through both pipelines. Compare outputs. Measure:
- Field-level agreement rate
- Error rate on mimo vs kimi
- Actual cost savings achieved
- Escalation frequency by document type

Only cut over fully when agreement rate exceeds 95% and escalation rate is under 15% of fields.

### G. Add Ongoing Monitoring
Sample 1% of mimo-accepted fields and verify against kimi. Track confidence calibration over time. Alert if precision drops below threshold. Model behavior can drift.

### H. Clarify Pipeline: Image or Text-Only?
Specify whether mimo-v2.5 receives the raw document image alongside Tesseract OCR output. If text-only, the vision comparison to kimi is invalid and accuracy expectations should be lowered. If image+text, test whether mimo effectively uses the visual signal for error correction.
