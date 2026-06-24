# CC Revert: MiMo → DeepSeek v4-pro

**Date**: 2026-06-24
**Action**: Reverted Claude Code backend from Xiaomi MiMo v2.5-pro back to DeepSeek v4-pro

## Changes Made

### 1. `~/.claude/settings.json`
| Field | Before | After |
|-------|--------|-------|
| ANTHROPIC_BASE_URL | `https://api.xiaomimimo.com/anthropic` | `https://api.deepseek.com/anthropic` |
| ANTHROPIC_AUTH_TOKEN | `sk-cx2ce2l60...` (MiMo key) | `sk-bde0f5da...` (DS key from codewhale) |
| ANTHROPIC_MODEL | `mimo-v2.5-pro` | `claude-opus-4-20250514` |
| CLAUDE_CODE_SUBAGENT_MODEL | `mimo-v2.5-pro` | `claude-opus-4-20250514` |
| model (top-level) | `mimo-v2.5-pro` | `claude-opus-4-20250514` |
| ultracode | *(absent)* | `true` |
| ANTHROPIC_API_KEY | *(was removed in prior fix)* | *(absent)* |

### 2. `~/.zshrc`
| Field | Before | After |
|-------|--------|-------|
| ANTHROPIC_MODEL | `mimo-v2.5-pro` | `deepseek-v4-pro` |
| CLAUDE_CODE_SUBAGENT_MODEL | `mimo-v2.5-pro` | `claude-opus-4-20250514` |
| ANTHROPIC_BASE_URL | `https://api.xiaomimimo.com/anthropic` | *(removed)* |
| MIMO_API_KEY | `sk-cx2ce2l60...` | *(removed)* |
| ANTHROPIC_AUTH_TOKEN | `$MIMO_API_KEY` | *(removed)* |
| DEEPSEEK_API_KEY | *(absent)* | `sk-bde0f5da...` (restored) |

### 3. `cc_dispatch.py`
**NOT FOUND** on filesystem. No file matching `cc_dispatch*` exists anywhere under `/Users/ericstone`. Skipped.

### 4. Switching doc
Updated `full-fr.md` context — MiMo switch survey remains as historical record; this revert doc supersedes.

## Key Source
- DS key read from: `/Users/ericstone/.codewhale/config.toml` line 1 (`api_key = "sk-bde0f5da..."`)
- `~/.hermes/profiles/technical/auth.json` also has DS key at `credential_pool.deepseek[0].access_token` (same key confirmed)

## Verification

```
grep -ri 'mimo' settings.json .zshrc → ANTHROPIC vars: CLEAN (zero matches)
grep 'api.deepseek.com' settings.json → FOUND
grep 'ANTHROPIC_API_KEY' settings.json .zshrc → CLEAN (removed)
```

## Notes
- `ANTHROPIC_MODEL=deepseek[0m← [0mWrite Public/MAGI/debates/2026-06-24/cc-switch-mimo/revert-ds.md
Wrote file successfully.
[0m
Done. All three files reverted to DeepSeek v4-pro.

**Summary:**
- **settings.json**: endpoint → `api.deepseek.com/anthropic`, model → `claude-opus-4-20250514`, DS key set, `ultracode: true` restored, MiMo refs purged
- **.zshrc**: `ANTHROPIC_MODEL=deepseek-v4-pro`, `DEEPSEEK_API_KEY` restored, all MiMo/MIMO vars removed
- **cc_dispatch.py**: does not exist on filesystem — skipped
- **Verification**: zero `mimo` hits in ANTHROPIC vars, `api.deepseek.com` confirmed present, `ANTHROPIC_API_KEY` fully removed

Report written to `/Users/ericstone/Public/MAGI/debates/2026-06-24/cc-switch-mimo/revert-ds.md`. Restart shell to pick up env changes.
