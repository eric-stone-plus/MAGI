# auth-fix2 — MiMo ANTHROPIC_AUTH_TOKEN correction

**Date**: 2026-06-24
**Agent**: myrrh (MiMo Code)

## Problem

Claude Code with MiMo provider was hitting API errors. The `claude-code-provider-switching.md` doc specifies MiMo uses `ANTHROPIC_AUTH_TOKEN`, not `ANTHROPIC_API_KEY`. The `.zshrc` was exporting **both** keys, causing a conflict.

## Changes

### ~/.claude/settings.json — no change needed

Already had `ANTHROPIC_AUTH_TOKEN` (not `ANTHROPIC_API_KEY`):

```json
"ANTHROPIC_AUTH_TOKEN": "sk-cx2ce2l60io8ucbb40rrhewno97cd60ycuifr27i6i4gus0x"
```

### ~/.zshrc — commented out conflicting key

**Before:**
```bash
export MIMO_API_KEY=sk-cx2ce2l60io8ucbb40rrhewno97cd60ycuifr27i6i4gus0x
export ANTHROPIC_API_KEY=$MIMO_API_KEY
export ANTHROPIC_AUTH_TOKEN=$MIMO_API_KEY
```

**After:**
```bash
export MIMO_API_KEY=sk-cx2ce2l60io8ucbb40rrhewno97cd60ycuifr27i6i4gus0x
# export ANTHROPIC_API_KEY=$MIMO_API_KEY  # disabled: MiMo uses ANTHROPIC_AUTH_TOKEN
export ANTHROPIC_AUTH_TOKEN=$MIMO_API_KEY
```

## Verification

| File | Key | Status |
|------|-----|--------|
| `~/.claude/settings.json` | `ANTHROPIC_AUTH_TOKEN` | ✅ set |
| `~/.claude/settings.json` | `ANTHROPIC_API_KEY` | ✅ absent |
| `~/.zshrc` | `ANTHROPIC_AUTH_TOKEN` | �[0m← [0mWrite Public/MAGI/debates/2026-06-24/cc-switch-mimo/auth-fix2-myrrh.md
Wrote file successfully.
[0m
Done. The `.zshrc` was exporting **both** `ANTHROPIC_API_KEY` and `ANTHROPIC_AUTH_TOKEN`, causing the conflict. `settings.json` was already correct.

**Changes:**
- `.zshrc:11` — commented out `export ANTHROPIC_API_KEY=$MIMO_API_KEY`
- `settings.json` — no change needed (already had `ANTHROPIC_AUTH_TOKEN`)

**Note:** You'll need to `source ~/.zshrc` or open a new terminal for the shell change to take effect.
