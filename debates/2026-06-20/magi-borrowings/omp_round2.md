I now have all R1 agent outputs and read the key constraint docs. Here's the cross-review.

---

## R2 Cross-Review: MAGI Borrowings

### Which 2-3 to Implement First

**1. D — Error Classification (rate_limit vs timeout split)**

Consensus #1 across 3/4 agents. Every wasted retry burns minutes + API cost. But the "~45 lines of Python" estimates are wrong — each of 6 dispatch wrappers has different error formats:
- cc: Anthropic-style stderr JSON
- cw: exit codes + stdout (exec --auto swallows stderr, per Myrrh)
- omp: OpenAI-style proxy errors
- MAGI grok/kimi/mimo: three different CLI error formats

MVI: start with ONE wrapper (run_cc.py). Parse exit code + stderr for `rate_limit`/`429` vs `timeout`/`timed out`. Ship → validate → fan out to remaining 5 wrappers. Don't tackle all 6 at once.

**Blind spot**: MAGI's existing per-delegate retry (max 3) will fight the new wrapper-level retry. Need to pick ONE retry layer — either wrapper retries OR MAGI delegate retries, not both (N×M retries).

**2. F — Mandatory file:line Citations (tiered gate)**

Consensus #1-3 across all agents. High value, genuine low cost. But the flat "exclude from voting" is wrong. Go with Gold's tiered approach:
- Code/audit topics: hard gate (file:line or command output)
- Non-code topics (strategy, economics): soft downgrade (keep Invariant #7)
- Add ⛔: fabricated citations are worse than none — tag `[CITATION_UNVERIFIED]` in R2

**Blind spot nobody fully weighted**: agents WILL fabricate `file:line` to comply. The regex gate catches absence, not fabrication. A false citation entering the consensus pool is WORSE than a missing claim (which is at least honest about its uncertainty). Gold and Fr both flag this but the summary underplays it. The citation verifier omp sketched (read/search the cited file) is the real fix, but it's expensive — deferred to Phase 2.

**3. A — Structured JSON (Myrrh-only trial first, not MAGI three doctors)**

Gold and omp both put A at #2. But the constraint analysis reveals: only mimo (Myrrh) handles structured output reliably. Grok headless is broken, kimi has 80% thinking tax before JSON body. The "MAGI three doctors trial" in the summary is wrong — start with Myrrh ONLY. If Myrrh produces reliable JSON for 5+ sessions, add kimi with a tail-scan parser. Grok waits until headless is fixed.

### What NOT to Do First

- **C (Mind-change)**: Fr and omp both note R2 agents are stateless — they have no "initial position" to change FROM. C depends on position persistence that doesn't exist in the CLI dispatch model. Omp's "one prompt line" is theater without stateful agents. Defer until you have either persistent agent memory or a simpler proxy.

- **B (Anonymous review)**: Cosmetic. Model identity IS agent identity in QUINTE (cc=MiMo, cw=DS). Fr correctly calls it "自欺欺人." Negative value — skip.

- **E (Rapporteur weighting)**: Governance rewrite needed. Self-reported confidence is uncalibrated (Gold: "cc MiMo reports 0.95 on wrong answers routinely"). Skip until there's per-model calibration data.

### Blind Spots in the Constraint Analysis

1. **cw `exec --auto` stderr suppression**: Myrrh flags it, but the summary says "D needs stdout parsing too." This is worse than stated: cw's error format is closed-source and can change silently. D's cw wrapper needs a defense-in-depth fallback — if neither stderr nor stdout yields a classification, treat as `unknown` and use existing 180s kill→retry. Never crash on unparseable output.

2. **F's per-agent capability asymmetry**: omp has LSP (good at file:line), cw R1 is sandbox-blind (can't produce file:line), Fr/kimi is web-oriented. A flat file:line requirement structurally advantages omp and disadvantages cw. The tiered gate partially addresses this, but cw's embedded summary constraint (≤500 chars, no /tmp/ access per dispatch-constraints) means cw literally cannot verify claims from other agents. This makes F a disadvantage engine unless exemptions are explicit.

3. **A's convergence gate interaction**: MAGI's ≥2/3 convergence gate compares text output. Changing MAGI output to JSON changes the convergence comparison surface. The summary says "MAGI convergence gate depends on text comparison → A adjusts convergence" but doesn't specify HOW. The fix: MAGI delegates produce JSON sidecar AND markdown prose; convergence is computed on markdown (unchanged); JSON is consumed by hm's Phase 2 auto-diff.

4. **D's grok misclassification risk**: Gold flags that grok failures (0B, SIGTERM at 300s) look like `timeout`, not `deprecated`. Misclassification → 3 useless retries burning 9+ minutes. The grok wrapper MUST check for the specific grok 400/123B signature BEFORE falling through to the generic timeout check.

### Implementation Sequencing

```
Session 1: D (run_cc.py only) + F (prompt line + regex, tiered gate)
Session 2: A (Myrrh-only trial) + D (fan out to omp + cw wrappers)
Session 3+: Evaluate Myrrh JSON quality → expand A; evaluate D hit rate → fan out to MAGI wrappers
```

**Total cost**: 1 prompt line (F), 1 regex (F), ~20 lines of Python in run_cc.py (D), 1 MAGI prompt template change (A). Ship in one session for D+F, second for A pilot.
