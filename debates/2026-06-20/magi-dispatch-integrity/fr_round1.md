• The user wants me to audit several markdown files for dispatch consistency. I need to read specific files and check grok/kimi commands and model mappings. Let me read all four files in parallel.

• I'll read all four files now and check the dispatch commands and mappings.• Let me analyze what I found in each file.

  1. **PROTOCOL.md** (lines 240-260):
     - Gold (grok) command: `grok -p="..." --effort max --reasoning-effort xhigh`
     - This is WRONG - uses both `--effort max` and `--reasoning-effort xhigh` which both map to reasoningEffort causing 400 Bad Request.
     - Fr (Frankincense): `~/.kimi-code/bin/kimi -p "..."` - this looks correct, matches SKILL.md
     - Myrrh (mimo): `mimo run --dangerously-skip-permissions` - this looks correct, matches SKILL.md
     - Model mapping in PROTOCOL: Gold=grok, Fr=kimi, Myrrh=mimo - correct mapping

  2. **SOUL.md**:
     - Line 73: "Gold→grok -p="..." --effort max --reasoning-effort xhigh, Fr→kimi -p, Myrrh→mimo run."
     - This is WRONG - has the stale grok command with both flags.
     - Line 34: "Gold→grok-build, Frankincense→kimi K2.7, Myrrh→mimo-v2.5-pro" - model mapping is correct.
     - So grok command is wrong, model mapping is correct.

  3. **SKILL.md**:
     - Line 313: Gold (grok): `~/.local/bin/grok -p="prompt"` and explicitly notes "No --effort max / --reasoning-effort xhigh — both map to reasoningEffort (400 Bad Request). Inject constraint in prompt body instead."
     - This is CORRECT.
     - Line 315: Frankincense (kimi): `~/.kimi-code/bin/kimi -p "prompt"` - correct.
     - Line 317: Myrrh (mimo): `~/.mimocode/bin/mimo run --dangerously-skip-permissions "prompt"` - correct.
     - Model mapping: Architecture diagram shows Gold=grok, Fr=kimi, Myrrh=mimo. Correct.

  4. **magi-v3-integration.md**:
     - This file is marked DEPRECATED since 2026-06-19. v3.1 active.
     - Line 20: "Gold(mimo-v2.5) + Frankincense(kimi) + Myrrh(DS v4-pro). No two may share base model."
     - This is the backwards mapping the user mentioned! Gold=mimo, Myrrh=DS v4-pro. 
     - But the file is deprecated, so it describes the old v3.0 integration where the mapping was apparently different. The user said "might have model mapping backwards" - yes, compared to current v3.1 (Gold=grok, Fr=kimi, Myrrh=mimo), this old doc has Gold=mimo and Myrrh=DS v4-pro which is definitely backwards/wrong for current state.

  Let me summarize:
  - PROTOCOL.md: grok command WRONG (has stale --effort max --reasoning-effort xhigh). Kimi and mimo correct. Mapping correct (Gold=grok, Fr=kimi, Myrrh=mimo).
  - SOUL.md: grok command WRONG (stale flags). Kimi and mimo correct via shorthand. Mapping correct (Gold=grok, Fr=kimi, Myrrh=mimo).
  - SKILL.md: grok command CORRECT (no flags, prompt-injected constraints). Kimi and mimo correct. Mapping correct.
  - magi-v3-integration.md: DEPRECATED file. Model mapping is backwards/old: Gold=mimo, Myrrh=DS v4-pro (current should be Gold=grok, Myrrh=mimo). Since it's deprecated history, maybe should stay as-is but with clear deprecation warning. The current warning says deprecated and points to SOUL.md L34 and SKILL.md §MAGI dispatch. That's good, but the mapping table inside is stale.

  Now I should present this clearly to the user.

Audit complete. Here's what's wrong in each file:

  ## 1. `~/Public/QUINTE/specs/PROTOCOL.md` (line 253)

  | Doctor | Command shown | Status |
  |--------|--------------|--------|
  | Gold (grok) | `grok -p="..." --effort max --reasoning-effort xhigh` | **WRONG** — uses stale flags |
  | Fr (Frankincense/kimi) | `~/.kimi-code/bin/kimi -p "..."` | ✅ Correct |
  | Myrrh (mimo) | `mimo run --dangerously-skip-permissions` | ✅ Correct |

  **Mapping:** `Gold=grok, Fr=kimi, Myrrh=mimo` — ✅ consistent with v3.1.

  **Problem:** PROTOCOL still carries the exact stale grok command that causes 400s. It should drop `--effort max --reasoning-effort xhigh` and inject effort constraints in the prompt body instead.

  ---

  ## 2. `~/.hermes/profiles/technical/SOUL.md` (line 73)

  | Doctor | Command shown | Status |
  |--------|--------------|--------|
  | Gold (grok) | `grok -p="..." --effort max --reasoning-effort xhigh` | **WRONG** — stale flags |
  | Fr (kimi) | `kimi -p` | ✅ Correct (shorthand) |
  | Myrrh (mimo) | `mimo run` | ✅ Correct (shorthand) |

  **Mapping:** Line 34 says `Gold→grok-build, Frankincense→kimi K2.7, Myrrh→mimo-v2.5-pro` — ✅ correct.

  **Problem:** The dispatch line (L73) still has the stale grok flags, contradicting the correct mapping above.

  ---

  ## 3. `~/.hermes/profiles/technical/skills/multi-agent-debate/SKILL.md`

  | Doctor | Command shown | Status |
  |--------|--------------|--------|
  | Gold (grok) | `~/.local/bin/grok -p="prompt"` with explicit note **not** to use `--effort`/`--reasoning-effort` | ✅ Correct |
  | Fr (kimi) | `~/.kimi-code/bin/kimi -p "prompt"` | ✅ Correct |
  | Myrrh (mimo) | `~/.mimocode/bin/mimo run --dangerously-skip-permissions "prompt"` | ✅ Correct |

  **Mapping:** Architecture diagram and dispatch section both say `Gold=grok, Fr=kimi, Myrrh=mimo` — ✅ consistent and current.

  **Status:** This is the only one of the four that is fully correct and internally consistent.

  ---

  ## 4. `~/.hermes/profiles/technical/skills/multi-agent-debate/references/magi-v3-integration.md`

  This file is **marked DEPRECATED** (line 3) as of 2026-06-19, with v3.1 active.

  **Mapping table (line 20):**
  - Gold → **mimo-v2.5**
  - Frankincense → **kimi**
  - Myrrh → **DS v4-pro**

  **Status:** **Backwards/wrong** relative to current v3.1 mapping (`Gold=grok, Myrrh=mimo`). Since it's a preserved historical doc, the mapping inside accurately reflects v3.0, but the deprecation warning is there and points to current sources (SOUL.md L34 and SKILL.md §MAGI dispatch).

  ---

  ## Summary

  | File | Grok command correct? | Kimi invocation correct? | Mimo invocation correct? | Model mapping consistent with v3.1? |
  |------|----------------------|--------------------------|--------------------------|-------------------------------------|
  | `PROTOCOL.md` | ❌ stale flags | ✅ | ✅ | ✅ |
  | `SOUL.md` | ❌ stale flags | ✅ | ✅ | ✅ |
  | `SKILL.md` | ✅ | ✅ | ✅ | ✅ |
  | `magi-v3-integration.md` | N/A (no commands) | N/A | N/A | ❌ backwards, but file is deprecated history |

  **Action needed:** Fix the stale grok command in `PROTOCOL.md` §4.5 and `SOUL.md` L73 to match `SKILL.md` (no CLI reasoning flags, prompt-injected constraints). `magi-v3-integration.md` is deprecated history, so leave it but keep the deprecation banner intact.

To resume this session: kimi -r session_d1516d2e-3881-4316-9a52-2080f6f92051
