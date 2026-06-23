# Hermes R1: MAGI Dispatch Integrity Audit

**TASK: Audit Gold (grok) and Fr (kimi) invocation consistency across all canonical files.**

## Current State

### Correct invocations (SKILL.md, empirically verified 2026-06-20)
```
Gold: grok -p="prompt"                    # conversational, NO effort flags
Fr:   ~/.kimi-code/bin/kimi -p "prompt"    # + file paths for exploration
Myrrh: mimo run --dangerously-skip-permissions "prompt"
```

### Stale/Wrong commands in canonical files

| File | Line | Current | Should be |
|------|------|---------|-----------|
| **PROTOCOL.md** §4.5 | L253 | `grok -p="..." --effort max --reasoning-effort xhigh` | `grok -p="..."` |
| **SOUL.md** | L73 | `Gold→grok -p="..." --effort max --reasoning-effort xhigh` | `Gold→grok -p="..."` |
| **SOUL.md** | L34 | `Gold→grok-build` | `Gold→grok` (model auto-routed by CLI) |
| **magi-v3-integration.md** | L20 | `Gold(mimo-v2.5) + Frankincense(kimi) + Myrrh(DS v4-pro)` | `Gold(grok) + Frankincense(kimi) + Myrrh(mimo-v2.5-pro)` |

### Model Identity Conflict

| File | Gold = | Frankincense = | Myrrh = |
|------|--------|---------------|---------|
| PROTOCOL §4.5 | grok ✅ | kimi ✅ | (not listed) |
| SOUL L34 | grok-build ⚠️ | kimi K2.7 ✅ | mimo-v2.5-pro ✅ |
| SKILL dispatch | grok ✅ | kimi ✅ | mimo ✅ |
| magi-v3-integration.md | **mimo** ❌ | kimi ✅ | **DS** ❌ |

magi-v3-integration.md has Gold and Myrrh SWAPPED — Gold=mimo, Myrrh=DS. This is the opposite of reality where Gold=grok and Myrrh=mimo.

## Additional Issues Found

### fr_round1.md from 2026-06-20 meta-QUINTE: 829B, all tool output
Fr's conversational prompt triggered tool-search mode (ls, glob). 6245B of tool output, 0B of analysis. This confirms Fr needs FILE PATHS in prompt, not open-ended questions.

### Gold retry pattern (2026-06-20 provider-switch QUINTE)
- Attempt 1: `--reasoning-effort xhigh` → 400 (grok-build)
- Attempt 2: `--effort max` → 400 (grok-composer-2.5-fast)
- Attempt 3: bare `grok -p="..."` → 149 lines
- Conversational: `grok -p="Hey, I'd really..."` → 22KB

## Impact Assessment

| Severity | Issue | Consequence |
|:--------:|-------|-------------|
| HIGH | PROTOCOL/SOUL have broken grok command | Operator following spec gets 400 error, Gold fails silently |
| MEDIUM | magi-v3-integration.md has swapped model mapping | Confusion on which delegate is which model |
| LOW | SOUL says grok-build (stale default) | Minor, CLI auto-routes anyway |

## Recommended Fixes
1. PROTOCOL §4.5 L253: remove `--effort max --reasoning-effort xhigh`
2. SOUL L73: same fix
3. SOUL L34: `grok-build` → `grok` 
4. magi-v3-integration.md: fix model mapping or add stronger DEPRECATED header
5. All files: add Fr's filesystem-exploration role documentation
