# R1 Summary for R2 Cross-Review

## R1 Results

### hm (Hermes)
- Analysis mostly accurate, identified 3 minor fixes needed
- Blind spots: fshiori author not noted, magi-core yanked status, Sonnet version

### omp
- **HIGH**: README's 83.3% "MMLU Hell Mode" has NO verifiable source. Experiment results show 76%/88%. Commit aa3c25b was docs-only.
- MEDIUM: 50-question builtin dataset + load_mmlu() omitted from analysis
- MEDIUM: test asserts 25 questions but dataset has 50 (stale test)
- LOW: ICE uses Jaccard word overlap, not LLM judge. No dedicated escalate protocol.

### Fr (kimi)
- 7 missing projects: Miki-Hoshizaki/mcp-magi, nlink-jp/magi-system2, akokubo/magi_system, BolivarTech/magi, heyqule/evangelion_magi, lciel/multi-agent-magi, jason-chao/MAGI
- MAGI psychiatric and MAgICoRe are acronym collisions, not MAGI-pattern projects. Should be reclassified.
- MAD not "first" LLM debate (Du et al. 2023 preceded it)
- fshiori README's "MMLU Hell Mode" claim unsupported — actual experiment uses builtin trivia dataset
- QUINTE comparison structurally biased: self-assessment vs inspectable open-source, asymmetric verifiability
- magi-core v1.1.0, not v0.3.0

### Myrrh (mimo)
- **HIGH**: jason-chao/MAGI (PyPI: magi-core, 8 decision modes) completely omitted
- **HIGH**: "magi-core Rust crate v0.3.0" likely doesn't exist — real magi-core is Python PyPI
- **HIGH**: "albinjal MCP debate server" — 0 search results
- MEDIUM: TomaszRewak/MAGI (140★) and hirakujira (71★) misclassified as "EVA FAN"
- MEDIUM: No non-MAGI-named competitors analyzed (AutoGen, CrewAI, ChatEval)
- QUINTE comparison: unfair — asymmetric verifiability, different scopes

### Gold (grok)
FAILED — 127 bytes, stuck

### cc (Claude Code)
RETRYING — initial auth key error

### cw (CodeWhale)
FAILED — 180s 0 bytes

## Key Consensus
1. fshiori/magi README's "MMLU Hell Mode 83.3%" is unsupported by repo evidence (omp+Fr+Myrrh agree)
2. jason-chao/MAGI is the biggest omission (Fr+Myrrh agree, HIGH severity)
3. MAGI psychiatric/MAgICoRe are acronym collisions, not MAGI-pattern (Fr+Myrrh agree)
4. QUINTE comparison structurally biased toward self-assessment (Fr+Myrrh agree)
5. magi-core version is wrong: v1.1.0 Python PyPI, not v0.3.0 Rust crate
6. 6-7 projects missing from analysis
