# R3 · hm+KANSA — MAGI Gold Architecture Final Verdict

## Evidence Base

| Round | Agent | File |
|-------|-------|------|
| R1 | hm | `hm_round1.md` |
| R1 | cc | `cc_round1.md` |
| R1 | cw | `cw_round1.md` |
| R1 | omp | `omp_round1.md` |
| R2 | hm | `hm_round2.md` |

4/4 R1 + hm R2 cross-review. All DeepSeek v4-pro.

---

## KANSA B Audit

KANSA B reviews R1+R2 evidence independently.

### Finding 1: Convergence is real, not groupthink

Four independent agents, four different perspectives (hm=cost+arch, cc=dev+cost, cw=systems+accuracy, omp=operations+risk), arrived at the same conclusion: **architecture directionally correct, operationally incomplete.** Three blocking gaps identified by ≥2 agents each:
- No calibration (4/4)
- No circuit breaker (2/4, elevated to blocking by KANSA)
- Per-field escalation amplifies thinking waste (4/4)

This is genuine convergence from different angles, not shared blind spots.

→ KANSA: **Convergence validated.**

### Finding 2: cc's cost correction is the most impactful single finding

cc identified that volume determines ROI: <8 docs/week = all-kimi cheaper (¥39/mo dead weight). This was missed by hm and cw. omp touched on it ("break-even calculation not provided") but cc quantified it.

→ KANSA: **Volume gate is a must-have operational control, not nice-to-have.**

### Finding 3: cw's pipeline ambiguity question is deployment-blocking

"Does mimo receive image or just OCR text?" — this single question determines whether the accuracy comparison to kimi is even valid. If text-only, the tiered architecture might collapse (mimo accuracy on noisy OCR text may be worse than kimi on raw images).

→ KANSA: **Must resolve before any deployment decision.** Elevate from cw's "H" recommendation to blocking item #5.

### Finding 4: DS text tier (hm+omp) is the most underrated optimization

Both hm and omp independently identified DeepSeek as a text-only fallback between mimo and kimi. Once Tesseract produces clean text, kimi's vision is wasted. DS v4-pro costs less per-token than kimi quota burn and has no thinking overhead.

→ KANSA: **DS text tier should be blocking, not should-do.** If deployed without it, text-only fields that mimo flags as low-confidence will unnecessarily burn kimi quota on text extraction that DS could handle.

### Finding 5: omp's observability is table stakes

7 failure modes identified by omp. Without telemetry, none are detectable until QUINTE output is wrong. This is not "nice-to-have" — it's the minimum viable safety net.

→ KANSA: **Observability must be in should-do tier, not deferred.** Minimum: confidence histogram, escalation rate, quota remaining, error rate.

### KANSA Verdict

R1+R2 quality: HIGH. All agents identified complementary risks. No false claims detected. Convergence is cross-perspective, not echo chamber.

KANSA overrides:
- DS text tier: should-do → blocking
- Volume gate: nice-to-have → should-do  
- Observability: deferred → should-do
- Pipeline input ambiguity: add to blocking list

---

## R3 Final Verdict

### Core Decision: APPROVED with 6 blocking conditions

The MAGI Gold architecture (mimo-v2.5 primary + kimi fallback) is the correct direction. kimi is the most expensive resource with 80% thinking waste on structured forms — shifting bulk work to fixed-cost mimo is cost-optimal at scale (>8 docs/week).

**Blocking (must resolve before deployment):**

| # | Condition | Source | Rationale |
|---|-----------|--------|-----------|
| 1 | Calibrate mimo-v2.5 on 50-200 labeled shipping docs | 4/4 | Untested accuracy. Must achieve ≥95% precision at chosen threshold. If calibration fails, abort migration. |
| 2 | Derive empirical confidence threshold from calibration data | 4/4 | 0.7 is arbitrary. Use precision-recall curve. |
| 3 | Batch kimi escalations per-document (not per-field) | 4/4 | Per-field = N× thinking waste. Single composite call. |
| 4 | Circuit breaker: mimo failure → auto-fallback to all-kimi | omp+cc+KANSA | Pipeline must not stall on API outage. Alert on degradation. |
| 5 | Resolve pipeline input: image+text or text-only to mimo? | cw+KANSA | If text-only, accuracy model collapses. If image+text, verify mimo uses visual signal. |
| 6 | Add DS text tier for text-only low-confidence fields | hm+omp+KANSA | kimi most expensive — text-only fields should never touch it. DS v4-pro cheaper, no thinking waste. |

**Should-do (first week of deployment):**

| # | Item | Source |
|---|------|--------|
| 7 | Structural validation layer (schema, ranges, cross-field consistency) before confidence gate | cw |
| 8 | Merge consistency gate (cross-field reconciliation after kimi override) | cw+omp |
| 9 | Pre-OCR quality gate (DPI, contrast, skew → skip mimo, direct to kimi) | omp+cc |
| 10 | Observability: confidence histogram, escalation rate, quota remaining, error rate | omp+KANSA |
| 11 | Volume gate: <8 docs/week → all-kimi (¥39/mo not justified) | cc+KANSA |

**Nice-to-have:**
| 12 | kimi thinking=high on fallback calls (ambiguous = need reasoning) | cw |
| 13 | mimo-v2.5-pro for Fr synthesis (same ¥39/mo tier, stronger text model) | cc |

### Agent Agreement Matrix

| Finding | hm | cc | cw | omp | KANSA |
|---------|----|----|----|-----|-------|
| Architecture correct | ✅ | ✅ | ✅ | ✅ | ✅ |
| Calibrate first | ✅ | ✅ | ✅ | ✅ | ✅ |
| Batch escalation | ✅ | ✅ | ✅ | ✅ | ✅ |
| Circuit breaker | — | ✅ | — | ✅ | ✅ |
| Pipeline input question | — | — | ✅ | — | ✅ |
| DS text tier | ✅ | — | — | ✅ | ✅ |
| Structural validation | — | — | ✅ | — | ✅ |
| Merge consistency | — | ✅ | ✅ | ✅ | ✅ |
| Pre-OCR quality gate | — | ✅ | — | ✅ | ✅ |
| Observability | — | — | — | ✅ | ✅ |
| Volume gate | — | ✅ | — | — | ✅ |
| kimi thinking=high | — | ⚠️ | ✅ | — | ⚠️ |

### Key Dissent

- **cc vs cw on kimi thinking mode**: cc says auto is fine for fallback, cw says high (these are ambiguous cases). KANSA defers — test both in calibration study, use whichever produces better accuracy on low-confidence fields. Low stakes since escalation rate should be <15%.

### Cost Model (corrected 2026-06-18)

| Resource | Cost | Role | Token Waste |
|----------|------|------|-------------|
| kimi K2.7 | Most expensive | Vision fallback (surgical) | High (always_thinking) — justified on hard cases |
| mimo-v2.5 | ¥39/mo fixed | Primary Gold | None |
| mimo-v2.5-pro | ¥39/mo (same) | Frankincense | None |
| DeepSeek v4-pro | Pay-per-use | Myrrh + DS text tier | None (on-demand) |

**Break-even**: ~8 docs/week. Below this, all-kimi is cheaper. Above this, mimo fixed cost amortizes to near-zero per document.

### Deployment Sequence

1. Calibration study (1-2 days): labeled data → empirical threshold → go/no-go
2. Shadow mode (1-2 weeks): run both pipelines, compare, measure real savings
3. Cut-over: activate mimo-primary with circuit breaker + DS text tier + batched escalation
4. Iterate: adjust threshold, add structural validation, monitor drift

### Risk

The primary risk is calibration failure: if mimo-v2.5 cannot achieve ≥95% precision on shipping documents at any confidence threshold, the entire tiered architecture is invalid. In that case, fall back to all-kimi with optimizations (stream-json, single call, DS text preprocessing where possible).

*Verdict issued 2026-06-18. QUINTE archive: /tmp/quinte-audit/kimi-arch-quinte/*
