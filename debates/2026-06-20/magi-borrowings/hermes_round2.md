# Hermes R2 — Cross-Review of MAGI Borrowings R1

## R1 Cross-Review Verdict

All 4 R1 agents (omp/Gold/Fr/Myrrh) converge on same core structure. No disputes to resolve.

### Confirmed Consensus

| Item | 4/4 Agree | Verdict |
|------|-----------|---------|
| G blocked | ✅ | Violates Invariant #2 |
| D high priority | ✅ | Error classification = P0 |
| F high priority | ✅ | Citations = P1 |
| B marginal | ✅ | Pseudonyms = theater |
| E conflicted | ✅ | Rapporteur = governance clash |

### Remaining Blind Spots

**1. D implementation gotcha no one caught**: Current dispatch is `terminal(background=true, notify_on_complete=true)`. Error classification requires *structured* error returns from each dispatch wrapper. But `terminal()` returns raw stdout/stderr strings — no typed error codes. We'd need to either:
- Parse stdout/stderr patterns post-hoc (fragile)
- Or add a wrapper layer that captures exit codes + stderr patterns before returning

**2. F exclusion vs downgrade tension**: omp says "hard gate — no citation = excluded". Gold says "tiered — hard on code topics, soft elsewhere". Fr didn't address. This is the key implementation decision for F.

**3. Implementation sequence dependency**: Myrrh notes E depends on A. Gold notes C's quantification depends on A. So A (JSON) is a *dependency* for E and advanced C, even if A itself is P2.

## Recommended Absorption Plan

```yaml
Phase 0 (NOW, 1 session):
  D: error classification (rate_limit vs timeout 2-way split)
     → cc_dispatch.py + omp_run.py + SKILL.md retry table
  F: mandatory citations (prompt-only, tiered gate)
     → SKILL.md R1 prompt template + Phase 2 regex filter

Phase 1 (next session):  
  C: mind-change tracking (prompt-only)
     → SKILL.md R2 prompt template + R3 merge logic

Phase 2 (MAGI trial, 2-3 sessions):
  A: structured JSON (MAGI doctors only first)
     → Gold/Fr/Myrrh prompt + hm extract_json_block()

Phase 3 (defer):
  B: anonymity — rejected (conflicts Invariant #4)
  E: rapporteur — rejected (conflicts dual-consul)
  G: adaptive — BLOCKED (violates Invariant #2)
```

## R2 Vote
- D: PASS (4/4 R1 agree, zero conflict)
- F: PASS (3/4 R1 agree, Gold had F at #3 after D+A)
- C: PASS (3/4 agree, low cost)
- A: CONDITIONAL (MAGI trial first, full rollout after validation)
- B: REJECT (theater, conflicts model-identity thesis)
- E: REJECT (governance conflict, unreliable confidence)
- G: BLOCKED (iron law)
