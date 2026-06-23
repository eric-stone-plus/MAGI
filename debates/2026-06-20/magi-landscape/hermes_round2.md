# Hermes R2 — Cross-Review of R1 Findings

## 1. Consensus Finding #1: README's 83.3% MMLU claim unsupported

**Review**: STRONGLY CONFIRMED. omp traced the claim to commit aa3c25b which was docs-only with no results file. Fr found that experiments/three_cobblers.py uses `get_dataset("builtin")` — basic trivia, not MMLU. Myrrh confirmed 9 actual MMLU questions total. The 83.3% number in README cannot be reproduced.

**Confidence**: HIGH. Three agents independently verified with different methods.

## 2. Consensus Finding #2: jason-chao/MAGI is biggest omission

**Review**: CONFIRMED. Myrrh found it has 8 decision modes, PyPI published, deliberative rounds with anonymous peer review. This is a significant omission. Fr also listed it.

**Confidence**: HIGH. Two agents independently identified. My hm R1 missed this entirely — blind spot confirmed.

## 3. Consensus Finding #3: Acronym collisions

**Review**: CONFIRMED. MAGI psychiatric uses 4 clinical agents, not 3-vote. MAgICoRe is coarse-to-fine refinement, not MAGI-pattern. Both Fr and Myrrh flag this. My analysis should have separated "MAGI-pattern" from "acronym MAGI."

**Confidence**: HIGH.

## 4. Consensus Finding #4: magi-core version

**Review**: CONFIRMED. I claimed "Rust crate v0.3.0" but Myrrh found no evidence this exists on crates.io. The real magi-core is a Python PyPI package (v1.1.0) from jason-chao/MAGI. This was my factual error — I saw crates.io references in web search but didn't verify.

**Confidence**: HIGH. My error, agents corrected.

## 5. Consensus Finding #5: QUINTE comparison structural bias

**Review**: PARTIALLY CONFIRMED with qualification. Fr and Myrrh both flagged that comparing QUINTE (self-described protocol) to fshiori/magi (open-source product) is asymmetric. This is a valid methodological concern. However, the analysis was transparent about what QUINTE is and where its features come from. The bias is in the framing ("QUINTE has X, fshiori lacks X") vs more neutral ("QUINTE claims X, fshiori ships Y").

**Confidence**: MEDIUM-HIGH. Valid point, but QUINTE's features are documented in the multi-agent-debate skill and SOUL.md — not fabricated.

## 6. Blind Spots R1 Missed

**6a. fshiori/magi author identity**: Eric Chen — noted by hm audit, not in main analysis. Minor.

**6b. gumbel-ai/agent-debate classification**: Fr correctly notes it's not really a MAGI project — adversarial markdown editing, no MELCHIOR/BALTHASAR/CASPER. Should be in "OTHER" tier.

**6c. Non-MAGI-named competitors**: Myrrh raises valid point about AutoGen, CrewAI, ChatEval as multi-agent frameworks doing similar things. But the analysis scope was specifically "GitHub MAGI-named projects."

**6d. Benchmark sample size dispute**: Fr says 25, omp says 50 builtin + 9 MMLU. Resolution: builtin dataset has 50 questions; experiment ran 25 of them; BENCHMARK_UPGRADE.md documents 9 MMLU questions (5+2+2). All parties partially correct depending on which dataset they reference.

## 7. My R2 Verdict on R1 Consensus

| Finding | Verdict | Action |
|---------|---------|--------|
| 83.3% unverifiable | ✅ CONFIRMED | Must flag in final report |
| jason-chao/MAGI omission | ✅ CONFIRMED | Add to analysis |
| Acronym collisions | ✅ CONFIRMED | Reclassify MAGI psych + MAgICoRe |
| magi-core version error | ✅ CONFIRMED | Correct to Python PyPI v1.1.0 |
| QUINTE bias | ⚠️ PARTIAL | Add verifiability caveat to comparison |
| Missing 6-7 projects | ✅ CONFIRMED | Add to analysis |
| TomaszRewak tier dispute | ⚠️ DEBATABLE | 140★ is notable but tech is GPT-3.5 era |
