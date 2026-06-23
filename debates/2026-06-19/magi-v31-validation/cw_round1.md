# CodeWhale R1 — MAGI v3.1 Model Set Audit

**Date**: 2026-06-19
**Model**: deepseek-v4-pro
**Sources**: grok-build/SKILL.md, kimi-code/SKILL.md, mimo-code/SKILL.md, r1-context.md

---

## Q1: Is grok/kimi/mimo the optimal three-model set?

### Verdict: Optimal among available options, with one structural caveat.

### Heterogeneity scorecard

| Axis | grok (xAI) | kimi (Moonshot AI) | mimo (Xiaomi) | Heterogeneous? |
|------|-----------|-------------------|---------------|----------------|
| Vendor | US | CN | CN | Mixed (2 CN, 1 US) |
| Architecture | grok-build (proprietary) | K2.7 Code (OpenCode-derived) | mimo-v2.5-pro (OpenCode-derived) | Partial — kimi/mimo share framework DNA |
| Modality | Text-only | Text-only (WebBridge separate) | Multimodal (Omni) | Partial |
| Thinking model | Effort-tiered reasoning | always_thinking (unbillable) | Deep thinking (optional) | Yes |
| Agent framework | Custom headless | OpenCode (plan/build/compose) | OpenCode (plan/build/compose) | Partial — kimi/mimo share agent loop |
| CLI interface | `grok -p=...` | `~/.kimi-code/bin/kimi -p ...` | `~/.mimocode/bin/mimo` | Yes — incompatible CLIs |

### The shared-framework problem

Both kimi and mimo are built on the **OpenCode** agent framework:
- kimi: plan/build/compose mode selection, self-narration in text mode, parallel tool dispatch
- mimo: same mode framework, `mimo.ts` plugin for OpenCode, same OpenAI-compatible provider pattern
- Binary decompilation confirms kimi has `KimiChatProvider.withThinking()` alongside OpenAI's `thinkingEffortToReasoningEffort()` — both inherited from OpenCode's multi-provider architecture

This means kimi and mimo share:
1. **Agent loop semantics** — how they decompose tasks, dispatch tools, handle errors
2. **Mode-selection patterns** — plan→build→compose gating
3. **Self-narration overhead** — both waste tokens on "Need perform task. Need read..."
4. **Tool result parsing** — same JSON structure expectations

**Risk**: Correlated failures where kimi and mimo both fail identically due to framework-level bugs, while grok (custom headless) gives the correct but outvoted answer.

### Why not alternatives?

| Set | Problem |
|-----|--]0;🐳 CodeWhale]0;🐋 CodeWhale]0;🐳 CodeWhale]0;🐋 CodeWhale]0;🐳 CodeWhale]0;🐋 CodeWhale**R1 complete.** `/tmp/quinte-audit/magi-v31/cw_round1.md` written — 256 lines, 15,]0;🐳 CodeWhale135 bytes.

**Core findings across 5 questions:**

| Q | Verdict |
|---|---------|
| **Q1 — Optimal set?** | Yes. grok/kimi/mimo is the best available combo. One caveat: kimi and mimo share OpenCode agent framework DNA (correlated failure risk). |
| **Q]0;🐋 CodeWhale2 — Fixed vs dynamic?** | Fixed. Dynamic routing would make one model dominate and destroy MAGI's heterogeneity value. |
| **Q3 — CLI flags optimal?** | No. Three corrections: Gold needs `--effort high` (not `max`) for R1 survey tasks; Fr always needs `--output]0;🐳 CodeWhale-format stream-json` + DS pre-digestion; Myrrh needs explicit `--model mimo-v2.5-pro` + ≥3s call spacing. |
| **Q4 — Blind spots?** | Primary: kimi+mimo OpenCode correlation (both fail identically on framework bugs). Secondary: all three are coding agents (weak]0;🐋 CodeWhale on philosophy), no native web search, CN-vendor correlation. |
| **Q5 — ≥2/3 gate?** | Keep it but add framework-diversity override: when kimi+mimo agree against grok, flag for manual hm review instead of auto-pass. Different frameworks agreeing = genuine; same framework]0;🐳 CodeWhale agreeing against different framework = suspect. |

**7 action items** appended to the file for MAGI v3.1 config updates.
est model):
- Would route most tasks to the "best" model → single-model dominance
- Undermines the core premise: heterogeneity IS the value
- Complex implementation — who decides routing? Another model? Circular.
- Makes convergence meaningless — if you always pick the winner, there's no debate

### Partial dynamic routing (not recommended, but noted)

The one case for partial routing: **kimi token budget management**. When kimi's weekly quota drops below 10%, skip Fr and run with Gold+Myrrh only (2/2 convergence). This is already documented in kimi-code/SKILL.md and is an operational necessity, not a design choice.

### Recommendation

Keep fixed mapping. The consistency benefit outweighs any per-task optimization. MAGI is a debate protocol, not a task router.

---

## Q3: CLI flags — optimal?

### Current flags

| Role | Model | Flags | Status |
|------|-------|-------|--------|
| Gold | grok-build | `--effort max --reasoning-effort xhigh` | ⚠️ Suboptimal for R1 tasks |
| Frankincense | kimi K2.7 | default (config: effort=max, thinking=auto) | ⚠️ Missing stream-json, no pre-digestion |
| Myrrh | mimo-v2.5-pro | default (no explicit model flag) | ⚠️ Model not pinned |

### Gold (grok): flag mismatch by task type

The grok-build SKILL.md effort matrix (2026-06-19 benchmark) says:

| Task type | Recommended effort | Current |
|-----------|-------------------|---------|
| Code review / audit / survey | `high` (triggers cross-referencing) | `max` |
| Code generation / implementation | `max` (depth-dominant) | `max` ✓ |
| Security audit / debugging | `max --reasoning-effort xhigh` | `max --reasoning-effort xhigh` ✓ |

**Problem**: `--effort max` **suppresses exploration** in favor of depth. For MAGI R1 tasks (survey, analysis, cross-referencing), `--effort high` is empirically better because it triggers cross-file reading behavior. Using `max` for R1 means grok dives deep on a narrow slice and misses context that `high` would catch.

**Additionally**: The 2026-06-19 benchmark note says `--reasoning-effort xhigh` "added marginal value at high context cost." For R1/R2 (analysis, not security), skip xhigh.

**Recommended Gold flags by MAGI phase**:
- R1 (survey/analysis): `--effort high` (no reasoning-effort overlay)
- R2 (critique/adversarial): `--effort max --reasoning-effort xhigh`
- R3 (adjudication/synthesis): `--effort max` (depth, no xhigh)
- Implementation (P0/P1): `--effort max` (per existing pattern)

### Frankincense (kimi): missing critical flags

1. **`--output-format stream-json` is NOT in use.** Default `text` format produces verbose self-narration ("• Need perform task. Need read...") wasting ~30-50% of tokens. stream-json filters this to tool calls + final content only. However, stream-json has intermittent failures ("unknown command 'stream-json'") — fallback to text mode when it fails.

2. **No DS pre-digestion.** kimi's `always_thinking` burns thinking tokens on every call. If given a bare topic, kimi spends thinking on **discovery** (grep filesystem, find context) rather than **analysis**. The documented strategy: hm pre-digests all relevant files, distills into ≤400 char prompt, dispatches kimi with only the analysis question.

3. **effort=max is a no-op.** Decompilation confirms `max`, `xhigh`, and `high` all send `reasoning_effort = "high"` to the API. The config setting `effort = "max"` is cosmetic — no actual increase over `high`.

4. **Token budget not checked before dispatch.** kimi Andante ¥49/月 flat plan with weekly quota. Should verify >10% remaining before dispatching Fr. If <10%, skip Fr and run Gold+Myrrh only.

### Myrrh (mimo): model not pinned

1. **No explicit `--model` flag.** Should specify `--model mimo-v2.5-pro` to ensure the flagship model is used. Without it, the default model is unspecified and may vary.

2. **No structured output mode for R3.** mimo-v2.5-pro supports `response_format={"type": "json_object"}` via `chat_json()`. For R3 adjudication where structured verdicts are needed, this should be used instead of free-text `chat()`.

3. **Rate limiting not accounted for.** token-plan-cn gateway has 429 rate limiting. Concurrent MAGI phases that all hit mimo simultaneously could trigger cascade failure. Minimum 3s between calls needed.

### Recommended flag matrix

| Phase | Gold (grok) | Frankincense (kimi) | Myrrh (mimo) |
|-------|------------|---------------------|--------------|
| R1 | `--effort high` | `--output-format stream-json` + DS pre-digestion | `--model mimo-v2.5-pro` |
| R2 | `--effort max --reasoning-effort xhigh` | same + adversarial prompt | `--model mimo-v2.5-pro` |
| R3 | `--effort max` | same + synthesis prompt | `--model mimo-v2.5-pro` + `chat_json()` |
| P0/P1 | `--effort max` | skip (use grok) | skip (use grok) |

### Critical additions for all phases

- **Gold**: Use `--effort high` for R1 (survey/analysis), not `max`. `max` suppresses the cross-referencing behavior needed for thorough analysis.
- **Fr**: Always use DS pre-digestion before dispatch. Always use `--output-format stream-json` (with text-mode fallback). Always check token quota before dispatch.
- **Myrrh**: Always pin `--model mimo-v2.5-pro`. Space MAGI calls ≥3s apart to avoid 429 cascades.

---

## Q4: Blind spots — correlated failure modes

### Tier 1: Structural (shared architecture)

**OpenCode framework correlation (kimi + mimo)**:
- Both use plan/build/compose mode selection
- Both self-narrate in text mode ("Need perform task...")
- Both handle parallel tool dispatch identically
- Both parse tool results through the same JSON structures
- **Impact**: Framework-level bugs affect both identically. If a tool result format changes, both fail the same way. grok (custom headless) would handle it differently.

**Chinese vendor correlation (kimi + mimo)**:
- Similar training data availability (both CN-first)
- Similar knowledge cutoff patterns
- Similar safety/alignment constraints
- **Impact**: Both may share blind spots on topics sensitive in CN regulatory context. grok (US vendor) would not share these constraints.

### Tier 2: Task-type blind spots

| Task type | Risk | Why |
|-----------|------|-----|
| Philosophical/ethical debate | All three shallow | Coding agents, not reasoning agents. None are o3/o4-class reasoners. |
| Web-dependent verification | All three blind | None have native agent web search. kimi has WebBridge but it's a separate daemon, not integrated into reasoning. |
| Long-context (>200K tokens) | All three degrade | Theoretical 1M context, but effective reasoning depth drops after ~100K. MAGI debates with full repo context may exceed this. |
| Multimodal reasoning | grok + kimi blind | Only mimo has vision. If R1 requires diagram/chart analysis, 2/3 models can't participate. |
| Adversarial inputs | All three vulnerable | No model has formal adversarial robustness. Prompt injection or jailbreak attempts could produce correlated garbage outputs. |

### Tier 3: Operational blind spots

| Failure mode | Models affected | Consequence |
|-------------|----------------|-------------|
| kimi weekly quota exhaustion | Fr | MAGI degrades to 2-party (Gold+Myrrh). 2/2 convergence is weaker. |
| mimo 429 cascade death | Myrrh | MAGI degrades to 2-party (Gold+Fr). Both remaining are CN-vendor. |
| kimi stream-json failure | Fr | Falls back to text mode with +30-50% token burn. May hit quota faster. |
| grok `-p=` syntax error | Gold | Silent failure if `-p "prompt"` (no equals) is used. Documented pitfall. |
| All three timeout simultaneously | All | Network outage, API degradation. No fallback. |

### Most dangerous blind spot

**kimi + mimo both confirm a wrong conclusion due to shared OpenCode framework behavior, grok correctly dissents, but 2/3 convergence gate passes the wrong answer.** This is the direct consequence of the shared-framework problem identified in Q1. See Q5 for mitigation.

---

## Q5: Convergence gate ≥2/3 — still correct?

### Verdict: ≥2/3 is correct, but needs a framework-diversity override.

### Why 2/3 works

Three independent vendors, three different model families. Uncorrelated errors are far more likely than correlated ones. Two models independently arriving at the same conclusion is strong signal.

### The kimi-mimo correlation risk

If kimi and mimo share a framework-level blind spot, they could both produce the same wrong answer. grok, with its different agent architecture, might produce the correct one. 2/3 would then amplify the error.

**Specific scenario**: MAGI debates a code change. kimi and mimo both use OpenCode's file-reading patterns. A subtle bug in how OpenCode parses a particular file format causes both to misinterpret it identically. grok uses its own parser and reads it correctly. The 2/3 gate would pass the misinterpretation.

### Recommendation: Framework-diversity gate (additive, not replacement)

Keep ≥2/3 as the primary gate. Add a secondary check:

```
if kimi_conclusion == mimo_conclusion AND grok_conclusion != kimi_conclusion:
    → FLAG for hm review (R3 manual adjudication override)
    → Do NOT auto-pass on 2/3
    → hm evaluates whether the agreement is genuine or framework-correlated
```

This means:
- **grok + kimi agree, mimo dissents** → pass (different frameworks agreeing)
- **grok + mimo agree, kimi dissents** → pass (different frameworks agreeing)
- **kimi + mimo agree, grok dissents** → **FLAG** (same framework agreeing, different framework dissenting)
- **All three agree** → pass (strongest signal)
- **All three disagree** → fail (no convergence)

### Weighted voting considered and rejected

Weighting grok higher because it's the most architecturally distinct would break MAGI's egalitarian premise. The framework-diversity gate preserves equal voting while adding a safety check for the specific known correlation.

### Implementation

This gate should be applied at R3 (adjudication) by hm, who already has the role of synthesizing the three inputs. No change to R1/R2 — each model operates independently without knowledge of the others' conclusions.

---

## Summary

| Question | Answer |
|----------|--------|
| Optimal model set? | Yes — grok/kimi/mimo. Only caveat: kimi+mimo share OpenCode DNA (mitigated by Q5 gate). |
| Fixed vs dynamic? | Fixed. Dynamic routing undermines heterogeneity — MAGI's core value. |
| CLI flags optimal? | No. Gold needs `--effort high` for R1 (not `max`). Fr needs stream-json + DS pre-digestion. Myrrh needs explicit model pin + rate-limit spacing. |
| Blind spots? | Primary: kimi+mimo OpenCode correlation. Secondary: all three are coding agents (shallow on philosophy), no native web search, CN-vendor correlation for kimi+mimo. |
| ≥2/3 gate correct? | Yes, with one addition: when kimi+mimo agree against grok, flag for manual hm review (framework-diversity override). |

### Action items for MAGI v3.1 config

1. **Gold R1 flag**: Change `--effort max` → `--effort high` for survey/analysis phases
2. **Fr pre-digestion**: Always run DS pre-digestion before kimi dispatch; ≤400 char prompt
3. **Fr output format**: Add `--output-format stream-json` with text-mode fallback
4. **Fr quota gate**: Check kimi weekly quota; skip Fr if <10%
5. **Myrrh model pin**: Add explicit `--model mimo-v2.5-pro`
6. **Myrrh rate limiting**: Space MAGI calls ≥3s apart
7. **R3 gate**: Add framework-diversity override when kimi+mimo agree against grok
