# MAGI Gold Architecture — QUINTE Audit Evidence

## Change Under Review

MAGI Gold routing: kimi-primary → mimo-v2.5 primary + kimi fallback.

## New Architecture

```
Document → Text layer? ─── YES → zlib extract → DS verify → Fr+Myrrh → QUINTE
              │
              NO (scanned)
              │
              ▼
         Tesseract OCR → mimo-v2.5 Gold (primary, ¥39/mo)
              │
              ├─ per-field confidence ≥ 0.7 → accept → Fr+Myrrh
              │
              └─ per-field confidence < 0.7
                   → crop region → kimi Gold (fallback, thinking=auto)
                   → merge → Fr+Myrrh → QUINTE
```

## Cost Reality (2026-06-18)

| Resource | Cost | Model |
|----------|------|-------|
| kimi K2.7 | Weekly quota (allocated), always_thinking | Vision, ~50K tokens/call |
| mimo-v2.5 | ¥39/month subscription | Vision, no thinking, ~5-8K tokens/call |
| mimo-v2.5-pro | ¥39/month (same tier) | Text-only, strong synthesis |
| DeepSeek v4-pro | Pay-per-use (~$0.28/M input, ~$1.10/M output) | Text-only, strongest reasoning |

**Key insight**: kimi quota burns fast (13% on 2 SOF calls), mimo is fixed monthly cost, DeepSeek is variable. The tiered approach shifts bulk work from quota-constrained kimi to fixed-cost mimo.

## Arguments For

1. kimi is the bottleneck (quota), mimo is fixed-cost — batch volume scales
2. mimo-v2.5 multimodal, no thinking overhead → efficient for clean forms
3. kimi's thinking is waste on OCR-alignment, value on ambiguity
4. Per-field escalation: kimi only sees regions it can help with
5. ~90% reduction in kimi quota consumption

## Arguments Against

1. mimo-v2.5 vision accuracy on shipping documents UNTESTED — no benchmark
2. Confidence self-assessment by mimo may be unreliable
3. Clarity gate threshold (0.7) is arbitrary
4. Two-model merge complexity: outputs may disagree
5. mimo API availability for vision calls uncertain
6. If mimo confidence is systematically wrong, escalations frequent → negates savings
7. Per-field kimi calls = more API overhead than batched
8. ¥39/mo mimo ≠ "free" — fixed cost still needs justification vs all-kimi

## Context

- Previous QUINTE (kimi-efficiency): kimi thinking cannot be disabled via CLI
- SOF test: 2 kimi calls = 13% weekly quota
- Myrrh: DeepSeek v4-pro (unchanged)
- Frankincense: mimo-v2.5-pro (unchanged)

## Task

Is mimo-v2.5 primary + kimi fallback the optimal Gold architecture?
Evaluate accuracy/risk/cost tradeoffs. Identify failure modes. Propose improvements.
