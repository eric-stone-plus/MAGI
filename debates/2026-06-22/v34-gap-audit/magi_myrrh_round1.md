# MAGI Myrrh R1: v3.4 Gap Verification

## Method
Read r1_context.md (11 v3.4 features), SOUL.md (185 lines), SKILL.md (148 lines). Systematic keyword/concept search per feature. Cross-referenced hm_round1.md findings.

## Feature-by-Feature Status

| # | Feature | In SOUL? | In SKILL? | Status |
|---|---------|----------|-----------|--------|
| 1 | JSON sidecar (structured MAGI output block) | NO | NO | **GAP** |
| 2 | Evidence Validati[0m
[0m← [0mWrite magi_myrrh_round1.md
Wrote file successfully.
[0m
Now I have full context. Let me produce the Myrrh analysis.
Written to `magi_myrrh_round1.md`. Key findings:

- **9 confirmed gaps** out of 11 features (JSON sidecar, Evidence Gate, 6-tier errors, rx quality gate, Grok recovery, magi_dispatch.py, 憲門, romaji convention)
- **1 false positive**: Agent→MAGI Substitution Table — already codified in SKILL.md L35 and L136
- **BLOCKER**: 憲門 Kennōmon (architecture gate) — the only constitutional-level gap
- **HIGH**: JSON sidecar, Evidence Validation Gate, 6-tier error classification (auditability/robustness foundation)
ji-only body convention | NO | NO | **GAP** |

## Confirmed Gaps: 9

1. **JSON sidecar** — No structured output block (verdict/confidence/reasoning_chain/evidence_citations) defined anywhere. Neither SOUL nor SKILL specifies MAGI output schema.
2. **Evidence Validation Gate** — Myrrh's role is "verification" (SKILL L33) but no rule that citations must resolve to real file:line, no 0.5× weight penalty for fakes.
3. **6-tier error classification** (auth|rate_limit|timeout|interrupted_recoverable|deprecated|unknown) — Zero error taxonomy in either file.
4. **rx quality gate** — No rule that rx output <1500 chars + containing <tool_call> triggers MAGI doctor substitute.
5. **Grok interrupt recovery** — SKILL L116 documents Grok dispatch format but says nothing about exit 143 → `--resume` recovery.
6. **magi_dispatch.py v1** — Not referenced in SKILL dispatch section (L59-76). No unified wrapper mentioned.
7. **憲門 Kennōmon** — Architecture gate (hm cannot solo-modify core architecture files) absent from SOUL. SOUL has Iron Law (L13) and QUINTE architecture mandate (L67) but these are MAGI-gate rules, not a named gate preventing solo modification of README/specs/ontology.
8. **Romaji-only convention** — No language policy for RASHOMON body content in SOUL or SKILL.

## False Positive: 1

**#7 Agent→MAGI Substitution Table** — hm flagged this as missing from SKILL. It is NOT missing. SKILL L35 states "Agent failure -> MAGI substitution" explicitly. SKILL L136 repeats the rule. SOUL L73 bans delegate_task to preserve heterogeneity. The "equal weight" nuance is implicit in the substitution logic. This is a false positive — the concept is fully codified.

## Priority Assessment

| Priority | Feature | Rationale |
|----------|---------|-----------|
| **BLOCKER** | 憲門 Kennōmon | Constitutional gap — without it, hm can solo-edit architecture files. SOUL Iron Law covers MAGI gate but not architecture-file protection specifically. |
| **HIGH** | JSON sidecar | Auditability foundation — structured output enables automated downstream processing. |
| **HIGH** | Evidence Validation Gate | Integrity of MAGI Myrrh's core function — citation verification without enforcement is decorative. |
| **HIGH** | 6-tier error classification | Error handling without taxonomy = ad-hoc responses. Affects all agent dispatch. |
| **MEDIUM** | rx quality gate | Operational robustness — prevents garbage rx output from polluting R2. |
| **MEDIUM** | magi_dispatch.py v1 | Convenience/consistency — unified wrapper reduces dispatch errors. |
| **LOW** | Grok interrupt recovery | Edge case — only matters on thermal kill of Grok process. |
| **LOW** | Romaji-only convention | Style — RASHOMON-specific, not protocol-critical. |

## Cross-Audit: hm_round1.md Verification

hm identified 11 gaps (7 SOUL + 4 SKILL). My analysis:
- **9 confirmed** as genuine gaps (items 1-6, 8-11 above)
- **1 false positive**: #7 (Agent→MAGI Substitution Table) — already in SKILL L35+L136
- **Discrepancy**: hm listed "Grok interrupt recovery" as SOUL missing — I confirm it's missing from BOTH files, not just SOUL. hm also listed "romaji convention" as SOUL missing — correct, it's absent from both.

## Verdict

**9 genuine gaps, 1 false positive.** 憲門 is the only BLOCKER. JSON sidecar + Evidence Gate + 6-tier errors are HIGH priority auditability/robustness gaps. The remaining 5 are MEDIUM-to-LOW operational polish.
