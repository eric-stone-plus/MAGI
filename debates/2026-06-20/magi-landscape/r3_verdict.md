# R3 Final Verdict — MAGI Landscape Analysis Audit

## Verdict: PASS WITH CORRECTIONS (5/5 consensus findings confirmed)

## Executive Summary

The landscape analysis was ~80% complete and ~80% accurate, with 3 HIGH-severity errors and 6-7 omissions identified across R1+R2 cross-review. Corrections required.

---

## Confirmed Findings (R1+R2 consensus)

### CRITICAL: fshiori/magi README's 83.3% MMLU claim fabricated
- **Evidence**: `experiments/results-2026-03-28.txt` shows 76%/72%/88%, NOT 83.3%/83.3%. Commit `aa3c25b` was docs-only. `three_cobblers.py` uses builtin trivia dataset, not MMLU.
- **New R2 discovery (omp)**: Results file is corrupted with ~800+ lines of LiteLLM spam. The "matched at 83.3%" narrative contradicts actual data (88% > 76%).
- **Action**: Analysis must note that the headline benchmark is not reproducible.

### HIGH: jason-chao/MAGI completely omitted
- PyPI `magi-core`, 8 decision modes, deliberative rounds, structured output
- Most feature-rich MAGI implementation after fshiori/magi
- **Action**: Add to "Engineered" tier

### HIGH: "magi-core Rust crate v0.3.0" likely doesn't exist
- The real magi-core is Python PyPI v1.1.0 (jason-chao/MAGI)
- Rename confusion with unrelated `cargo install magi` Rust tool
- **Action**: Remove Rust crate entry, add jason-chao/MAGI as Python package

### HIGH: QUINTE comparison structurally biased
- Self-reported features compared against inspectable open-source product
- fshiori/magi is a shipped pip package; QUINTE features exist in docs but lack independent verification
- Analysis should add: "QUINTE is a protocol specification with multi-agent implementation; its features are self-documented, not independently verified"
- **Action**: Add verifiability caveat, apply equal skepticism to both sides

### MEDIUM: 6-7 missing projects
- mcp-magi (Miki-Hoshizaki), magi-system2 (nlink-jp), akokubo/magi_system, BolivarTech/magi, heyqule/evangelion_magi, lciel/multi-agent-magi, jason-chao/MAGI
- **Action**: Add to analysis

### MEDIUM: MAGI psychiatric + MAgICoRe are acronym collisions
- MAGI psychiatric: 4 clinical agents, not 3-vote
- MAgICoRe: coarse-to-fine refinement, not MAGI-pattern
- MAD: preceded by Du et al. 2023, not "first"
- **Action**: Reclassify or remove from MAGI landscape

### MEDIUM: Tier misclassifications
- TomaszRewak/MAGI (140★) and hirakujira (71★) may deserve higher than "EVA FAN"
- gumbel-ai/agent-debate is not really a MAGI project
- **Action**: Adjust tiers with star/fork signals

---

## Disputed: Question count
- **Resolution**: Experiment ran 25 builtin questions (not MMLU). Codebase now has 50. BENCHMARK_UPGRADE.md documents 9 MMLU questions separately. All references to "7" should be corrected to 25 or specified by context.

---

## Corrected Analysis (action items)

1. Rename "MAGI psychiatric + MAgICoRe" → "Acronym Collisions (not MAGI-pattern)"
2. Add jason-chao/MAGI to Engineered tier
3. Remove "magi-core Rust crate v0.3.0" — replace with jason-chao/MAGI (Python, PyPI, v1.1.0)
4. Add 6 missing projects to appropriate tiers
5. Add "⚠️ Benchmark Caveat" to fshiori/magi: 83.3% unverifiable
6. Add "⚠️ Verifiability Asymmetry" to QUINTE comparison
7. Adjust gumbel-ai → "Multi-Agent Debate (non-MAGI)"
8. Consider star/fork signals in tier placement

## Confidence
- R1: 3 agents converged on core findings (hm+omp+Fr, Myrrh aligned)
- R2: hm+omp confirmed all 6 with detailed citations
- R3: hm(A) final — all findings supported by file:line evidence

## Verdict
**PASS** — analysis is salvageable and fundamentally sound, but requires the above corrections before it can be considered reliable. The fshiori/magi benchmark claim is the most serious issue — presenting a fabricated MMLU score as fact.
