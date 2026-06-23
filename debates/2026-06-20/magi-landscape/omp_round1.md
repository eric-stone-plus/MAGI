Now I have a complete picture. Let me compile the review.

---

## Landscape Analysis Review: Findings

### 1. FACTUAL ERRORS

**A. Benchmark description — "7-question PoC, not full MMLU" is imprecise.**

The repo has:
- **50-question hand-curated builtin dataset** (10 each × stem, humanities, social_sciences, logic, clinical). The analysis didn't acknowledge this exists.
- **Real MMLU loading** via `load_mmlu()` — pulls from HuggingFace `cais/mmlu` by category. Works, just rarely used.
- **The 7 MMLU questions** (5 `abstract_algebra` + 2 `professional_law`) documented in `BENCHMARK_UPGRADE.md` were a one-off PoC — that is correct.
- The builtin dataset is hand-curated trivia, NOT MMLU. Calling the README's "MMLU Hell Mode" label accurate is misleading.

**Verdict**: The analysis is *directionally correct* that the MMLU evaluation is a PoC, but omits the 50-question builtin dataset and the `load_mmlu()` capability entirely.

**B. The 83.3% number has no repo-verifiable source.**

The README claims 83.3% for both Sonnet 4.6 and MAGI Critique on "MMLU Hell Mode." The only actual experiment results on disk (`experiments/results-2026-03-28.txt`) show:
- Single Sonnet 4.6: **19/25 = 76%**
- MAGI Critique: **22/25 = 88%**

The `BENCHMARK_UPGRADE.md` shows different numbers again (80% vs 100% on 5 questions, 50% vs 100% on 2 questions). The git log shows the 83.3% was added in commit `aa3c25b` ("docs: update benchmark to fair comparison with Sonnet 4.6 (matched at 83.3%)") — a docs-only commit with no accompanying results file. The analysis either didn't check or didn't report this discrepancy.

**Verdict**: The 83.3% headline number cannot be reproduced from any file in this repo. The analysis didn't catch this.

**C. Dataset count inconsistency.**

`magi/bench/datasets.py` line 17 comment says "50 curated questions." The raw file confirms 50. But `tests/test_bench.py:18` asserts `len(questions) == 25`. The test is stale — it would fail against the current dataset. The analysis missed this.

### 2. MISCLASSIFICATIONS

The tier placement of `fshiori/magi` as "ENGINEERED" is reasonable — it's a functional pip package with a CLI, web dashboard, and benchmarking. No dispute there.

Without web search I cannot verify the other ~14 repos' classifications. But the analysis's description of fshiori/magi's features is mostly accurate:
- "ICE multi-round critique" ✓ (but Jaccard word-overlap, not LLM judge)
- "MMLU benchmark claiming 83% = Sonnet with 3 cheap models" — the claim exists in README, but see §1B above
- "pip package" ✓

### 3. BLIND SPOTS

**A. Consensus heuristic is primitive.** The ICE critique protocol measures agreement via `_estimate_agreement()` — pairwise Jaccard similarity on word sets. `CLAUDE.md` itself flags this: "MVP — should be replaced with LLM-as-judge." The landscape analysis doesn't mention this as a limitation.

**B. Adaptive protocol is thin routing.** It's ~50 lines: vote → check Jaccard → route to vote/critique/escalate. No calibration, no historical priors, no model-specific trust scores. The analysis presents "adaptive protocol selection" as a differentiating feature without noting how simple the implementation is.

**C. Fault tolerance is bare try/except.** Three `except` branches in `MagiNode.query()` — timeout, auth error, generic. No retry with backoff (the `num_retries=3` is LiteLLM's own retry, not MAGI's), no circuit breaker, no degraded-mode strategy beyond "skip failed node." The README's fault tolerance table overstates the sophistication.

**D. "File:line evidence" for code review.** The `magi diff` command sends the full git diff to three models and returns their reviews. There is no structured file:line evidence extraction — it's free-text LLM responses. The landscape analysis attributes "file:line evidence" to `gumbel-ai/agent-debate`, not fshiori/magi, so this isn't an error about fshiori/magi. But if the analysis claimed fshiori/magi has file:line evidence, that would be wrong.

**E. No "escalate" as an independent protocol.** The CLI offers `--mode escalate`, but `magi/core/engine.py:54-55` shows it's just `critique(query, nodes, max_rounds=2)` — critique with a round cap. The adaptive protocol's "escalate" path is the same. There's no dedicated escalate protocol with a designated tiebreaker node or forced ruling logic.

### 4. QUINTE COMPARISON — IS IT FAIR?

**"Lacks supervisor"** — Fair. No supervisor node exists. The engine `MAGI.ask()` calls a protocol function, not a supervisor model.

**"Lacks gate mechanisms"** — Fair. There's no quality gate, no confidence threshold that rejects low-quality outputs, no filtering between critique rounds. The decision dossier is always returned regardless of quality.

**"Lacks theoretical framework"** — Fair. The project is openly an engineering effort. No formal guarantees, no convergence proofs, no game-theoretic grounding.

**"7-question PoC"** — Needs qualification (see §1A). The builtin dataset is 50 questions, and `load_mmlu()` can load full MMLU categories. But the only *documented* MMLU run against actual MMLU questions was 7 questions. And the README's 83.3% "MMLU Hell Mode" claim cannot be traced to any results file.

### 5. MISSING PROJECTS

Cannot assess — web search unavailable. The analysis lists ~15 repos; without external search, I can't identify omissions.

### SUMMARY OF ACTIONABLE ISSUES

| # | Severity | Finding |
|---|----------|---------|
| 1 | HIGH | README's 83.3% "MMLU Hell Mode" claim has **no verifiable source** in the repo. Experiment results show different numbers (76%/88%). The landscape analysis should have flagged this. |
| 2 | MEDIUM | 50-question builtin dataset and `load_mmlu()` capability omitted from analysis — the "7-question PoC" framing is reductive. |
| 3 | MEDIUM | `test_builtin_dataset_exists` asserts 25 questions but dataset has 50 — stale test, analysis didn't catch. |
| 4 | LOW | ICE consensus uses Jaccard word overlap, not LLM judge — undocumented crudeness of the "critique" quality measurement. |
| 5 | LOW | No dedicated escalate protocol — it's just critique with `max_rounds=2`. |

The strongest finding is #1: the headline benchmark number in the README doesn't match any results file in the repository. If the landscape analysis aims to be a critical evaluation rather than a summary of self-reported claims, this is the most significant omission.
