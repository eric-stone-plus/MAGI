I'll audit those four MAGI doc locations for stale dispatch flags, model mappings, and any other contradictions.
[2m2026-06-20T06:12:59.660586Z[0m [31mERROR[0m tool_error: tool_output_error [3msession_id[0m[2m=[0m019ee3a8-761f-7ca0-abbe-09166fe4995a [3mtool_name[0m[2m=[0m"Read" [3meffective_tool_name[0m[2m=[0m"Read" [3mmodel_id[0m[2m=[0m"grok-composer-2.5-fast" [3merror_kind[0m[2m=[0m"tool_output_error"
Here’s an audit of the four places you named, plus cross-cutting issues that show up when you read them together.

## Summary

You found the two biggest problems. Beyond those, there’s a **profile sync gap**: the live `.hermes/profiles/technical/` SKILL already has the corrected Gold dispatch (no `--effort` / `--reasoning-effort` flags, prompt injection instead), but **`Public/hermes-core-rules-mac-x86/` is still on the old commands**. SOUL and QUINTE PROTOCOL §4.5 match the stale Public SKILL, not the fixed profile.

---

## 1. `QUINTE/specs/PROTOCOL.md` §4.5

**Confirmed stale (you already found):**
- Gold command still says `--effort max --reasoning-effort xhigh` — the live SKILL explicitly forbids this (400 from `reasoningEffort` collision).

**Other issues in §4.5 and nearby:**

| Issue | Detail |
|-------|--------|
| **Delegate roles swapped vs MAGI spec** | Gold labeled “Primary arbiter, adversarial reasoning”; Myrrh labeled “Structured verification, multimodal.” MAGI spec/SOUL say Gold = factual verification, Myrrh = adversarial audit. Looks like pre-v3.1 OCR-era role text. |
| **Incomplete Gold command** | Missing `--always-approve`, `--model grok-build`, and full path `~/.local/bin/grok`. Live SKILL uses bare `grok -p="prompt"` with constraints in the prompt body. |
| **Incomplete Myrrh command** | Says `mimo run --dangerously-skip-permissions` with no binary path (`~/.mimocode/bin/mimo`) and no quoted prompt. |
| **Duplicate §4.5 numbering** | MAGI and OMP are both `### 4.5`. OMP should be 4.6; Anti-Drift (currently 4.6) should be 4.7. |
| **Dangling reference** | “Pre-flight health check on Gold per MAGI SKILL.md §Gold Health Check” — **no such section exists anywhere** (grep is empty). |
| **Dangling `MAGI SKILL.md`** | §1.3 also cites `MAGI SKILL.md` for `[MAGI hm-solo]` fallback — **`magi/SKILL.md` does not exist** in the repo tree. |
| **Mode B semantics** | “≤1/3 → escalate to QUINTE R2+” is wrong when MAGI is already embedded in QUINTE R1. Should mean “MAGI collective reports divergence/unavailable; full debate continues to R2,” not “escalate to QUINTE.” |

---

## 2. `SOUL.md` MAGI references

**Mapping is correct** in L34 and L65: `Gold→grok, Fr→kimi, Myrrh→mimo`.

**Confirmed stale (you already found):**
- L73 still says `Gold→grok -p="..." --effort max --reasoning-effort xhigh`.

**Other SOUL inconsistencies:**

| Location | Issue |
|----------|--------|
| **L73 vs L34** | L34 has the right model map; L73 has the wrong dispatch flags and omits `--always-approve`, `--model grok-build`, full paths. |
| **L73 vs live SKILL** | Live profile says: no CLI effort flags for Gold; inject max-effort constraints in prompt; add per-delegate prompt requirements for Fr/Myrrh. None of that is in SOUL L73. |
| **L34 spec pointer** | Points to `MAGI specs/PROTOCOL.md` — correct and intentionally model-agnostic. Fine, but it means **§4.5 is the only place with concrete CLI**, and §4.5 is wrong. |

---

## 3. `skills/multi-agent-debate/SKILL.md` dispatch section

**In `Public/hermes-core-rules-mac-x86/` (canonical public copy):**

**Confirmed stale:**
- L309: `--effort max --reasoning-effort xhigh` on Gold.

**Other issues:**

| Issue | Detail |
|-------|--------|
| **Behind live profile** | `.hermes/profiles/technical/skills/multi-agent-debate/SKILL.md` was updated 2026-06-20 with correct dispatch, `§4a-MAGI` prompt preprocessing, failure recovery, and per-model strategy refs. **Public copy has none of that.** |
| **`magi-v3.1-model-change.md` conflict** | SKILL L163 cites this as canonical rationale, but that file says `--effort high` (not `max+xhigh`, not “no flags”). Three different Gold recipes across docs. |
| **Convergence wording** | L313: “≤1/3 → escalate to QUINTE R2+” — same Mode B semantic problem as PROTOCOL §4.5. |
| **Missing Pre-R1 content** | No `4a-MAGI` checklist, no “Gold 400 → retry without flags,” no Fr/Myrrh prompt injection requirements. |
| **Architecture diagram/table** | L126 and L153 are **correct**: `(grok)(kimi)(mimo)`. Only the dispatch comment block is wrong. |

**Authoritative fixed version** (live profile, not yet in Public):

```313:320:.hermes/profiles/technical/skills/multi-agent-debate/SKILL.md
# Gold (grok): terminal(background=true) ~/.local/bin/grok -p="prompt"
#   ⛔ No --effort max / --reasoning-effort xhigh — both map to reasoningEffort (400 Bad Request). Inject constraint in prompt body instead.
# Frankincense (kimi): terminal(background=true) ~/.kimi-code/bin/kimi -p "prompt"
#   ⛔ Prompt must include: "Use thinking=high mode. Do not shortcut. Every claim needs evidence."
# Myrrh (mimo): terminal(background=true) ~/.mimocode/bin/mimo run --dangerously-skip-permissions "prompt"
```

---

## 4. `references/magi-v3-integration.md`

**Confirmed stale (you already found):**
- L18: `Gold(mimo-v2.5) + Frankincense(kimi) + Myrrh(DS v4-pro)` — fully inverted vs current `grok/kimi/mimo`.

**Other issues:**

| Issue | Detail |
|-------|--------|
| **L21 cost ordering** | “kimi for deep context, mimo for fast facts, DS for adversarial edge” — tied to the **old** mapping. Under current mapping, Myrrh (adversarial) is mimo, not DS. |
| **L27** | References `magi/SKILL.md: Full skill definition` — **file doesn’t exist**. |
| **L35** | “mimo deprecated for some uses due to rate-limiting” — contradicts Myrrh=mimo as a required MAGI delegate. |
| **L34 pitfall** | “v2.0 confusion in SOUL.md and SKILL.md” — still valid; SOUL/SKILL dispatch blocks are indeed stale, though for v3.1 reasons not v2.0 OCR. |

---

## Cross-cutting stale siblings (not in your four, but they’ll mislead anyone following SKILL refs)

These sit next to `magi-v3-integration.md` and still describe the **pre-v3.1** composition:

| File | Stale content |
|------|---------------|
| `magi-v3-operations.md` L37–39 | Gold→mimo, Myrrh→DS |
| `magi-v3-redesign.md` L17–19 | Same old table |
| `magi-v3.1-model-change.md` | Mapping correct, but dispatch says `--effort high` — conflicts with both stale docs (`max+xhigh`) and fixed profile (no flags) |

`MAGI/README.md` is **correct** on mapping (`Gold→grok-build, Fr→kimi, Myrrh→mimo`) and points to §4.5 as canonical — which then sends operators to the broken command.

---

## Recommended single source of truth

After fixes, these four should agree on:

1. **Mapping**: Gold=grok-build, Frankincense=kimi K2.7, Myrrh=mimo-v2.5-pro  
2. **Gold dispatch**: `~/.local/bin/grok -p="..."` — **no** `--effort` / `--reasoning-effort` CLI flags; constraints in prompt body  
3. **Roles**: Gold=factual, Fr=contextual, Myrrh=adversarial (not “primary arbiter” / “multimodal verification”)  
4. **Mode B convergence**: ≤1/3 = MAGI divergence within R1, not “escalate to QUINTE”  
5. **Remove or implement** dangling refs to `MAGI SKILL.md §Gold Health Check`

---

## Priority fix list

| Priority | File | Fix |
|----------|------|-----|
| P0 | PROTOCOL §4.5, SOUL L73, Public SKILL L309 | Align Gold dispatch with live `.hermes` SKILL (no effort flags) |
| P0 | `magi-v3-integration.md` L18–21 | Fix mapping + cost/role text |
| P1 | PROTOCOL §4.5 | Fix delegate role descriptions; complete CLI paths/flags |
| P1 | PROTOCOL §4.5/4.6 | Renumber duplicate §4.5 |
| P1 | Public SKILL | Sync `§4a-MAGI` + failure recovery from live profile |
| P2 | `magi-v3-operations.md`, `magi-v3-redesign.md`, `magi-v3.1-model-change.md` | Update or mark deprecated |
| P2 | PROTOCOL §4.5 | Remove/fix `Gold Health Check` reference; resolve `magi/SKILL.md` pointer |

Want me to apply these fixes across the four canonical files and sync Public from the live `.hermes` profile?
