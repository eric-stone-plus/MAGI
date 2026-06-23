I now have all the evidence needed. Let me compile the structured review.

---

## TASK: Cross-review R1 findings from multi-agent debate about GitHub MAGI projects landscape analysis

### FINDING 1: README's "MMLU Hell Mode 83.3%" claim has NO verifiable source

**Evidence (from this repo):**

- `README.md:13-17` claims MMLU "Hell Mode" with 83.3% for both Sonnet and MAGI Critique.
- `experiments/three_cobblers.py:9` docstring: "All run on the same 25 built-in benchmark questions."
- `experiments/three_cobblers.py:98`: calls `get_dataset("builtin")` — NOT MMLU.
- `magi/bench/datasets.py:19-184`: `BUILTIN_DATASET` = 50 hand-curated trivia questions across 5 categories (stem, humanities, social_sciences, logic, clinical). These are simple Q&A (e.g., "Who wrote Romeo and Juliet?", "What organ produces insulin?"), not MMLU.
- `experiments/results-2026-03-28.txt:2059-2063`: **Actual results** — Sonnet 76% (19/25), Vote 72% (18/25), Critique 88% (22/25). **Neither is 83.3%.**
- The codebase has `load_mmlu()` (`datasets.py:204-226`) that CAN download real MMLU from HuggingFace, but the experiment never calls it. The CLI accepts `--dataset mmlu:<category>`, but the README's "Hell Mode" claim has no supporting run artifact.

**Verdict: AGREE — FULLY CONFIRMED.** This is the **most critical** finding. The README claims a specific MMLU "Hell Mode" score (83.3%) that does not match any observable artifact. The actual experiment: (a) uses a non-MMLU builtin trivia set, (b) produces 76%/72%/88% not 83.3%/83.3%. The claim is fabricated.

**Additional issues I found that R1 may have missed:**
- The experiment results file says "25 questions" but `BUILTIN_DATASET` now contains 50. The experiment was likely run on an older 25-question version, and the dataset was later expanded. This means the results file cannot be reproduced against the current code.
- The experiment results file is heavily corrupted with `Provider List: https://docs.litellm.ai/docs/providers` spam (~800+ lines), suggesting a buggy run where models failed repeatedly. Despite this, the results are presented as clean benchmark data.

**Confidence: HIGH (0.95)**

---

### FINDING 2: jason-chao/MAGI is the biggest omission

**Evidence:** Cannot verify from this repo alone (requires external analysis of the landscape study). However, `jason-chao/MAGI` appears on PyPI as `magi-core` and is described by R1 agents as having 8 decision modes and deliberative rounds — substantially more feature-rich than some projects included in the analysis.

**Verdict: AGREE — PLAUSIBLE.** The R1 agents' description suggests this project is a direct MAGI-pattern implementation (multi-model deliberation) that competes more directly with fshiori/magi than several projects that were included. Cannot independently verify without reading the external analysis, but the logic is sound: if the analysis included light/EVA-fan projects but omitted a feature-rich deliberative implementation, that's a significant gap.

**Confidence: MEDIUM (0.70)** — depends on R1 agents' external verification quality.

---

### FINDING 3: MAGI psychiatric (ACL 2025) and MAgICoRe (EMNLP 2025) are acronym collisions

**Evidence:** Cannot verify from this repo alone. The logic: "MAGI" is a common acronym in ML (especially medical/psychiatric NLP). These papers likely use "MAGI" as an acronym for something unrelated to the Evangelion-inspired 3-model disagreement pattern. Including them inflates the landscape count with false positives.

**Verdict: AGREE — SOUND CLASSIFICATION.** This is standard lit-review hygiene: distinguish namespace collisions from pattern implementations. The R1 agents' recommendation to reclassify these as "acronym collisions" rather than MAGI-pattern projects is correct methodological practice.

**Confidence: MEDIUM (0.65)** — depends on the actual papers' content.

---

### FINDING 4: magi-core is a Python PyPI package (v1.1.0), not a Rust crate (v0.3.0)

**Evidence:** Cannot verify from this repo. This is about the jason-chao/MAGI project, not fshiori/magi. `fshiori/magi` publishes as `magi-system` v0.1.0 on PyPI (confirmed: `pyproject.toml:7`). `jason-chao/MAGI` publishes as `magi-core`. R1 says the analysis incorrectly labeled magi-core as a Rust crate — likely confusing it with `cargo install magi` (an unrelated Rust CLI tool with no MAGI-pattern connection).

**Verdict: AGREE — LIKELY CORRECT.** Common confusion: `cargo install magi` pulls a Rust tool sharing only the name. Distinguishing `magi-core` (Python, jason-chao) from the Rust `magi` crate is important for analysis accuracy. Fshiori's own project is `magi-system` (Python, PyPI), not `magi-core`.

**Confidence: MEDIUM (0.70)** — depends on R1 agents' external verification.

---

### FINDING 5: QUINTE vs fshiori/magi comparison is structurally biased

**Evidence (from this repo):**

- `README.md:29-40`: The comparison table pits "Voting projects" (a generic, undefined category) against MAGI. Every row is "Yes" for MAGI, "No" for "Voting projects."
- The table header says "Voting projects" — no specific project (certainly not QUINTE) is named or benchmarked.
- The README `:25-28` section "How MAGI Differs" sets up the comparison as "Other projects do voting. Three models answer, pick the majority. That's it." — reducing all alternatives to a strawman.
- There is **no** head-to-head benchmark, no shared dataset comparison, no reproducible methodology for the comparison.

**Verdict: AGREE — FULLY CONFIRMED.** The comparison is structurally biased in two ways: (1) it self-assesses against an undefined category rather than a specific named project, and (2) it defines the competitor in the weakest possible terms ("pick the majority. That's it.") while listing its own advanced features. This is marketing, not comparative analysis. A fair comparison would name a specific project (e.g., QUINTE), describe its actual feature set accurately, and ideally run a shared benchmark.

**Confidence: HIGH (0.90)**

---

### FINDING 6: 6-7 missing projects (mcp-magi, magi-system2, akokubo/magi_system, BolivarTech/magi, etc.)

**Evidence:** Cannot verify from this repo. The R1 agents found these through external search.

**Verdict: AGREE — PLAUSIBLE.** GitHub search for "MAGI" yields many projects. A landscape analysis that misses 6-7 known projects has significant coverage gaps. However, some of these may be trivial forks or unrelated. The quality of the omissions matters — missing jason-chao/MAGI (8 decision modes) is far more significant than missing a zero-star stub.

**Confidence: MEDIUM (0.60)** — list quality unverified; significance varies by project.

---

### DISPUTED: Question count (25 vs 50)

**Evidence (from this repo):**

- `BUILTIN_DATASET` = 50 questions (5 categories × 10). Source: `magi/bench/datasets.py:19-184`.
- `get_dataset("builtin")` returns all 50. Source: `datasets.py:194-195`.
- `three_cobblers.py:98`: calls `get_dataset("builtin")`, receives all 50 in current code.
- `three_cobblers.py:9` docstring: "All run on the same 25 built-in benchmark questions."
- `results-2026-03-28.txt:1`: "Benchmark: 25 questions"
- Results show exactly 25 questions per group, corresponding to the first 25 of the 50-item BUILTIN_DATASET (10 STEM + 10 Humanities + first 5 Social Sciences).

**Verdict: ALL PARTIES ARE PARTIALLY CORRECT.**
- **Fr ("25 questions")** is correct about the *experiment run* — the results file shows 25.
- **omp ("50 builtin questions exist")** is correct about the *codebase* — BUILTIN_DATASET has 50.
- The experiment was likely run when the dataset had only 25 questions, then expanded to 50 later. The docstring still says "25" despite the code now using `get_dataset("builtin")` which returns 50. This is a code/docstring inconsistency.
- **Neither 25 nor 50 is "7"** — no party claimed 7. The "7-question PoC" claim in the disputed section was likely from the landscape analysis document describing a different test, not the experiment results file.

---

### REMAINING BLIND SPOTS (missed by R1 agents)

1. **The results file is corrupted.** `results-2026-03-28.txt` contains ~800+ lines of LiteLLM "Provider List" spam interspersed with actual results. The Critique group took 1,577 seconds (26 minutes) for 25 questions, which suggests massive retry/error overhead. Yet the README presents these as clean benchmark results. No R1 agent flagged this data quality issue.

2. **The "match" claim is self-contradictory.** README says Sonnet=83.3% and MAGI=83.3% ("MATCHED"). But the experiment results show Sonnet=76% and MAGI Critique=88%. The README fabricates a tie story where the actual data shows MAGI winning (88% > 76%). The narrative changes to fit the "three cobblers equal one master" framing — but the actual numbers don't support that either.

3. **The `cli.py:84` README example `magi bench --dataset mmlu:abstract_algebra --use-judge` implies MMLU benchmarking exists.** The `load_mmlu()` function exists but has never been run in the published experiment. This is a feature-gap: the CLI advertises MMLU capability that has no published results, while the README claims MMLU results that weren't produced by the code.

4. **No statistical validity.** 25 questions is a tiny sample. The results (76% vs 88%) are separated by 3 questions on a 25-question set. No confidence intervals, no significance testing. The README presents this as conclusive evidence of a "Sonnet Ceiling."

5. **Model names are inconsistent.** The README says "Claude Sonnet 4.6" but the code uses `claude-sonnet-4.6` (hyphen, not space). "Xiaomi Mimo-v2-pro" in README vs `xiaomi/mimo-v2-pro` in code. These are minor but contribute to the sloppiness pattern.

---

### SUMMARY RATINGS

| Finding | Verdict | Confidence | Criticality |
|---------|---------|------------|-------------|
| 1. MMLU 83.3% fabricated | **AGREE** | 0.95 HIGH | **CRITICAL** |
| 2. jason-chao/MAGI omission | **AGREE** | 0.70 MEDIUM | HIGH |
| 3. Acronym collisions | **AGREE** | 0.65 MEDIUM | MODERATE |
| 4. magi-core is Python, not Rust | **AGREE** | 0.70 MEDIUM | LOW |
| 5. QUINTE comparison biased | **AGREE** | 0.90 HIGH | **HIGH** |
| 6. Missing projects | **AGREE** | 0.60 MEDIUM | MODERATE |

**Disputed — question count:** All partially correct. 25 was the run, 50 is the codebase. Docstring is stale.
