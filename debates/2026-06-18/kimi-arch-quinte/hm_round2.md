# R2 · hm — MAGI Gold Architecture Cross-Review

## Agent Convergence Analysis

| Issue | hm | cc | cw | omp | Consensus |
|-------|----|----|----|-----|-----------|
| Architecture directionally correct | ✅ | ✅ | ✅ | ✅ | 4/4 |
| Calibrate before deploy | ✅ | ✅ | ✅ | ✅ | 4/4 |
| Batch kimi escalation (not per-field) | ✅ | ✅ | ✅ | ✅ | 4/4 |
| DS text tier between mimo and kimi | ✅ | — | — | ✅ | 2/4 |
| Circuit breaker for mimo failure | — | ✅ | — | ✅ | 2/4 |
| Merge consistency gate | — | ✅ | ✅ | ✅ | 3/4 |
| Pre-OCR quality gate | — | ✅ | — | ✅ | 2/4 |
| Observability telemetry | — | — | — | ✅ | 1/4 |
| kimi thinking=high on fallback | — | ⚠️ | ✅ | — | 1/4+⚠️ |

⚠️ = cc says thinking=auto is fine but would switch to always_thinking if auto performs worse.

## Key Divergences to Resolve

### 1. DS Text Tier (hm+omp vs cc+cw silence)

hm and omp propose DeepSeek as text-only fallback between mimo and kimi:
- Once Tesseract has produced text, kimi's vision is redundant
- DS v4-pro can verify/extract text fields cheaper than kimi quota
- kimi reserved ONLY for vision-requiring cases

cc and cw don't address this. Not opposition — just focused on other dimensions.

**Resolution**: Add DS text tier. Cost trumps silence. kimi is most expensive resource — any call that doesn't need vision shouldn't touch kimi.

### 2. kimi Thinking on Fallback (cw vs cc)

cw: thinking=high on fallback calls (these are ambiguous cases — use kimi's strength)
cc: thinking=auto is fine, monitor and switch if auto underperforms

**Resolution**: Accept cw's position. Escalated fields are definitionally the hard cases. If we're burning most-expensive-resource on them, use it fully. thinking=high. The token cost is marginal since escalation rate should be <15%.

### 3. Circuit Breaker Priority (omp vs cc vs hm)

omp: "no circuit breaker" = deployment-blocking gap
cc: circuit breaker needed, with auto-fallback to all-kimi
hm: didn't explicitly call it out but agrees

**Resolution**: Add to must-do list. mimo API outage with no degraded path is unacceptable for production.

## Cross-Agent Challenge: cc R1 to Others

### cc challenges hm: kill-switch at <8 docs/week
cc correctly notes that ¥39/mo is dead weight below ~8 docs/week. hm didn't address volume scaling.
→ **Accepted.** Add volume gate.

### cc challenges cw+omp: hidden engineering costs
cc flags merge logic, crop infrastructure, observability as unaccounted costs.
→ **Accepted.** But these are one-time engineering costs amortized over volume.

## Cross-Agent Challenge: cw R1 to Others

### cw challenges ALL: pipeline ambiguity (image or text to mimo?)
Most critical unaddressed question. Does mimo get raw image + OCR text, or just OCR text? This changes the entire accuracy equation.
→ **Must resolve before deployment.** If text-only, mimo accuracy expectation drops significantly.

### cw challenges hm: structural validation layer
cw proposes schema validation (numeric ranges, format patterns, cross-field consistency) BEFORE confidence gating.
→ **Accepted.** Catches errors confidence scores miss. Zero cost.

## Synthesis: Revised Architecture (post R2)

```
Document
  │
  ├─ Pre-OCR quality gate ─── FAIL (DPI<150, low contrast, >15° skew)
  │     → kimi full-doc, thinking=high → Fr+Myrrh → QUINTE
  │
  └─ PASS
       │
       ▼
    Tesseract OCR
       │
       ├─ OCR confidence check ─── FAIL (Tesseract mean conf <0.6)
       │     → kimi full-doc, thinking=high → Fr+Myrrh → QUINTE
       │
       └─ PASS → mimo-v2.5 Gold (raw image + OCR text)
              │
              ├─ Structural validation (schema, ranges, consistency)
              ├─ per-field confidence ≥ calibrated_threshold → accept
              │
              └─ per-field confidence < calibrated_threshold
                   │
                   ├─ field is text-only (clean OCR exists) → DS v4-pro text verify
                   │
                   └─ field requires vision (handwriting, stamps, ambiguity)
                        → batch into single composite kimi call (thinking=high)
                        → merge into mimo output
                        │
                        ▼
                   Merge consistency gate
                        │
                        ▼
                   mimo-v2.5-pro synthesis (Fr) → Myrrh (DS v4-pro) → QUINTE
```

### Operational Safeguards

| Gate | Condition | Action |
|------|-----------|--------|
| Volume gate | <8 docs/week | All-kimi (¥39/mo not justified) |
| Circuit breaker | mimo error >5% or p95 latency >10s (1h window) | Auto-fallback to all-kimi, alert |
| Quota guard | kimi <20% remaining | Alert, throttle escalations |
| Calibration guard | Precision <90% at threshold on weekly sample | Freeze mimo-primary, revert to kimi |

## Updated Must-Do vs Should-Do

**Blocking (pre-deploy):**
1. Calibrate mimo-v2.5 on labeled shipping docs (50-200 samples)
2. Determine empirical confidence threshold (target: ≥95% precision)
3. Add circuit breaker for mimo API failure
4. Batch kimi escalations per-document (not per-field)
5. Resolve pipeline input: image+text or text-only to mimo?

**Should-do (first week):**
6. Add DS text tier between mimo and kimi
7. Structural validation layer before confidence gate
8. Pre-OCR quality gate
9. Merge consistency gate

**Nice-to-have (ongoing):**
10. Observability telemetry
11. Volume gate (<8 docs/week → all-kimi)
