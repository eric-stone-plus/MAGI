# R3 Final Verdict — MAGI Borrowings Absorption

## Verdict: PASS — D + F ship now, A trial, C/B/E/G deferred/rejected

## Absorption Plan

### Phase 0 — SHIP NOW (1 session)

**D. Error Classification (rate_limit/timeout 2-way)**
- Start with run_cc.py only (~20 lines Python)
- Parse: exit code + stderr for `rate_limit|429` vs `timeout|timed out`
- SKILL.md: replace flat retry with branched recovery table
- ⚠️ Declare ONE retry layer — wrapper OR MAGI delegate, not both
- ⚠️ Grok: 0B/SIGTERM looks like timeout, MUST check grok-400 signature first

**F. Mandatory Citations (tiered gate)**
- R1 prompt: "Every claim must cite file:line or search command+result"
- Code/audit topics: hard gate (no citation → tagged [HYPOTHESIS: uncited])
- Non-code topics: soft downgrade (Invariant #7)
- Phase 2 hm: regex scan before hash — drop uncited from consensus pool
- ⚠️ Fabricated citations > absent ones — tag [CITATION_UNVERIFIED], don't trust

### Phase 1 — MYRRH TRIAL (next session)

**A. Structured JSON (Myrrh-only)**
- Myrrh prompt: append JSON block {verdict, confidence, reasoning_chain, evidence}
- hm: `extract_json_block()` for automated parse
- 5+ sessions validation before expanding to kimi
- Grok waits until headless fixed
- ⚠️ Convergence: MAGI compares markdown (unchanged), JSON is hm's auto-diff input

### Phase 2 — DEFER

**C. Mind-Change Tracking**: Deferred. Agents are stateless — no "initial position" to change from. Needs persistent memory first.

### Phase 3 — REJECT

**B. Anonymous Review**: Conflicts Invariant #4 (cross-model identity needed). Model = identity in QUINTE.

**E. Rapporteur Weighting**: Conflicts dual-consul model. Self-reported confidence is uncalibrated (cc MiMo reports 0.95 on wrong answers).

**G. Adaptive Pre-Check**: BLOCKED. Violates Invariant #2, SOUL.md iron laws.

## R1+R2 Summary

| Agent | D | F | A | C | B | E | G |
|-------|---|---|---|---|---|---|---|
| omp | 2 | 1 | 4 | 3 | 5 | 6 | ⛔ |
| Gold | 1 | 3 | 2 | 4 | 5 | 6 | ⛔ |
| Fr | — | — | — | — | — | — | ⛔ |
| Myrrh | 1 | 2 | 5 | 4 | 3 | 6 | ⛔ |
| hm | 1 | 2 | 4 | 3 | 5 | 6 | ⛔ |
