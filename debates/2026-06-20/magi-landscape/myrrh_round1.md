[0m
> build · mimo-v2.5-pro
[0m
[0m◈ [0mWeb Search "GitHub MAGI multi-agent LLM disagreement framework"
[0m◈ [0mWeb Search "GitHub MAGIS NeurIPS 2024 LLM issue resolution"
[0m◈ [0mWeb Search "GitHub MAD multi-agent debate LLM 2023"
I'll systematically verify every claim in this analysis by searching GitHub and the web for each project mentioned, plus looking for missing ones.
[0m% [0mWebFetch https://github.com/fshiori/magi
Web search is down. Let me fetch GitHub directly for each project and verify claims.
[0m% [0mWebFetch https://github.com/search?q=magi+multi-agent+LLM&type=repositories
[0m% [0mWebFetch https://github.com/CosmoJelly/MAGI-PROTOCOL
[0m% [0mWebFetch https://github.com/gumbel-ai/agent-debate
[0m% [0mWebFetch https://github.com/hirakujira/MAGI-System
Now let me verify the remaining projects mentioned in the analysis.
[0m% [0mWebFetch https://github.com/TomaszRewak/MAGI
[0m% [0mWebFetch https://github.com/lordpba/AI_Magi
[0m% [0mWebFetch https://github.com/07JP27/MagiSystem
[0m% [0mWebFetch https://github.com/just-every/magi
[0m% [0mWebFetch https://github.com/search?q=magi+evangelion+LLM+agent&type=repositories
Now let me check the remaining projects and search for missing MAGI repos.
[0m% [0mWebFetch https://github.com/co-evolve-lab/magis
[0m% [0mWebFetch https://github.com/search?q=magi+three+AI+debate+vote&type=repositories
[0m% [0mWebFetch https://github.com/jason-chao/MAGI
[0m% [0mWebFetch https://github.com/eashwar18/magi-synth-vote
Let me check the remaining projects and search for missing ones.
[0m% [0mWebFetch https://github.com/nlink-jp/magi-system
[0m% [0mWebFetch https://github.com/fshiori/magi/blob/main/BENCHMARK_UPGRADE.md
Now I have enough data for a thorough analysis. Let me also check for the local fshiori/magi codebase to verify benchmark claims.
[0m% [0mWebFetch https://github.com/search?q=magi+MCP+debate+server&type=repositories
Here is my thorough, evidence-based review of the landscape analysis.

---

## 1. MISSING PROJECTS (6 repos omitted)

**jason-chao/MAGI** — Published on PyPI as `magi-core`. Sophisticated: 8 decision modes (Synthesis, Probability, VoteYesNo, VoteOptions, Majority, Consensus, Minority, Compose), deliberative rounds with anonymous peer review, rapporteur-by-confidence, fallback chains. This is arguably the most feature-rich MAGI implementation after fshiori/magi. Completely absent from the analysis.

**nlink-jp/magi-system** — Japanese-language discussion system with: Maximum Disagreement speaker selection, novelty detection via bigram similarity, emotional state tracking between personas, coverage checks with facilitator intervention, convergence voting with multi-condition logic. 44 commits. Not mentioned.

**nlink-jp/magi-system2** — Follow-up project with dynamic persona generation, dual memory, adaptive facilitation via Vertex AI Gemini. Not mentioned.

**eashwar18/magi-synth-vote** — "MAGI 2.0 Multi-Agent Orchestrator" with weighted voting. 0 stars, 1 commit, likely a README-only placeholder, but exists.

**calvpang/MAGI-01** and **calvpang/MAGI-02** — EVA-inspired multi-agent LLM council/swarm. 0 stars each but explicitly MAGI-themed.

**revkahoptimum106/MAGI-System** — Another EVA-inspired three-unit debate system (appeared 3 days ago).

---

## 2. MISCLASSIFICATIONS

**TomaszRewak/MAGI** — Classified as "EVA FAN" but has **140 stars** (more than fshiori/magi's 114) and 21 forks. It's the most-starred MAGI project on GitHub. Dismissing it as fan art is misleading. It's a working decision-support system with yes/no classification and conditional logic. Should be at minimum "COMMUNITY" tier.

**hirakujira/MAGI-System** — Classified as "EVA FAN" but has **71 stars**, multi-model support (GPT-4o-mini, Claude Haiku 4.5, Gemini 2.5 Flash), Docker deployment, i18n (EN/ZH/JA), and a "Critical Matter" unanimous-rule safety feature. This is more engineered than the analysis suggests.

**CosmoJelly/MAGI-PROTOCOL** — Labeled "FastAPI+Next.js full-stack" which is correct, but it also has: CI/CD workflows, Docker publishing, Redis message broker, Ollama local LLM support, ARBITER synthesis system. Still only 1 star, so the tier is roughly right, but the description undersells the architecture.

**gumbel-ai/agent-debate** — Correctly identified but the analysis says "code review debates, file:line evidence" — it's actually broader: 2-4 agent debates (Claude, Codex, Gemini, Copilot), shared markdown with strikethrough edits, watch mode with ledger gates, auto-orchestration. 14 stars, 11 releases, actively maintained.

---

## 3. FACTUAL ERRORS

**"MMLU benchmark claiming 83% = Sonnet with 3 cheap models"** — The README says this, but the actual BENCHMARK_UPGRADE.md reveals the real test: **9 questions total** (5 abstract algebra + 2 law + 2 implied others), not "full MMLU." The file itself calls it a "概念驗證 (PoC)" (proof of concept). The QUINTE comparison's claim of "7-question PoC" is close to accurate (9 questions, not 7, but the spirit is correct). The README's "MMLU Hell Mode" framing is marketing spin on a tiny sample.

**"magi-core (Rust crate v0.3.0)"** — I could not verify this exists. The search found `magi-core` as a **Python** PyPI package (from jason-chao/MAGI), not a Rust crate. This claim needs citation. If it doesn't exist, it's a fabricated entry.

**"albinjal MCP debate server"** — GitHub search for "magi MCP debate server" returns **0 results**. This repo either doesn't exist, has been deleted, or the name is wrong. Needs verification.

**MAD "first LLM debate, 2023"** — The Multi-Agent Debate paper (Liang et al.) is from 2023, but claiming it's the "first" is debatable. Society of Mind (Minsky, 1986) and various multi-agent debate frameworks predate it. The claim needs qualification.

**"MAGI psychiatric (ACL 2025)"** — Not verified. No GitHub repo found. May be a paper without code, or the name may be wrong.

---

## 4. BLIND SPOTS

**The analysis ignores the jason-chao/MAGI project entirely**, which is a major omission. It's published on PyPI (`pip install magi-core`), has 8 decision modes, deliberative rounds with anonymous peer review, fallback chains, structured JSON output, and a CLI. This is the closest competitor to fshiori/magi in terms of engineering quality.

**No discussion of non-MAGI-named projects doing the same thing.** The analysis only searches for "MAGI" in repo names. Major multi-agent debate frameworks like:
- **ChatEval** (multi-agent debate for evaluation)
- **AutoGen** (Microsoft's multi-agent framework)
- **CrewAI** (used by lordpba/AI_Magi)
- **LangGraph** multi-agent patterns

...are doing structured disagreement without the EVA branding. The landscape is artificially narrowed.

**No analysis of the academic papers' code availability.** MAGIS (NeurIPS 2024) has code on GitHub. Does MAD? Does MAGI-CORE (EMNLP 2025)? If they don't, classifying them alongside working repos is misleading.

**The tier system conflates maturity with quality.** "ACADEMIC" vs "ENGINEERED" vs "EVA FAN" is a strange taxonomy. A better split: Published Papers / Production-Ready / Community Projects / Proof-of-Concept.

**No star/fork/commit analysis.** The most-starred project (TomaszRewak/MAGI, 140★) is buried in "EVA FAN." The most actively developed (just-every/magi, 387 commits) is in "OTHER." These signals matter.

---

## 5. IS THE FSHIORI/MAGI vs QUINTE COMPARISON FAIR?

**Partially fair, partially unfair.**

**Fair criticisms:**
- The benchmark IS a PoC (9 questions, self-reported). The README's "MMLU Hell Mode" framing overstates it.
- fshiori/magi lacks a formal supervisor/gate mechanism — critique rounds are self-organized.
- No theoretical framework is published.

**Unfair criticisms:**
- "7-question PoC" is slightly wrong (it's 9 questions from 3 MMLU subjects).
- Comparing to QUINTE (which I haven't seen) without knowing QUINTE's own benchmark size is a double standard. If QUINTE also tested on a small sample, the criticism is hypocritical.
- fshiori/magi has real engineering: fault tolerance, adaptive protocol selection, NERV dashboard, CLI toolchain, PyPI package, 114 stars. Calling it merely a "PoC" undersells the production infrastructure.
- The ICE critique protocol is genuinely novel among MAGI-themed repos — no other project does multi-round cross-model critique with mind-change tracking.

**Key missing context:** fshiori/magi's BENCHMARK_UPGRADE.md explicitly acknowledges the limitations and plans for HuggingFace dataset integration, LLM-as-judge scoring, consistency testing, and adversarial testing. The project knows its benchmark is weak and has a roadmap to fix it. The analysis should note this self-awareness.

---

## SUMMARY OF CRITICAL FINDINGS

| Finding | Severity |
|---------|----------|
| jason-chao/MAGI (PyPI: magi-core) completely omitted | **HIGH** |
| "magi-core Rust crate v0.3.0" — likely doesn't exist | **HIGH** |
| "albinjal MCP debate server" — 0 search results | **HIGH** |
| TomaszRewak/MAGI (140★) misclassified as "EVA FAN" | **MEDIUM** |
| Benchmark is 9 questions, not "full MMLU" — README misleading | **MEDIUM** |
| hirakujira/MAGI-System (71★) undersold as "EVA FAN" | **MEDIUM** |
| No non-MAGI-named competitors analyzed | **MEDIUM** |
| nlink-jp/magi-system (sophisticated) omitted | **LOW** |
| Tier taxonomy conflates project type with quality | **LOW** |
