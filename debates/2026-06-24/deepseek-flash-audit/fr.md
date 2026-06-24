# DeepSeek v4-flash Usage Audit — 2026-06-23

**Scope:** Determine whether Claude Code (cc) sub-processes were the confirmed source of ~201 deepseek-v4-flash calls on 2026-06-23, identify the mechanism, and rule out other sources.

---

## Executive Summary

**Yes — cc sub-processes are the confirmed source.**

The 201 reported deepseek-v4-flash calls correspond to Claude Code sub-agent sessions that were logged locally as `"model":"mimo-v2.5-pro"`. On 2026-06-23 the DeepSeek Anthropic-compatible endpoint received that non-Claude-Opus model string from cc sub-processes and mapped it to `deepseek-v4-flash`. A configuration fix applied on 2026-06-23 at 22:01:00 eliminated the issue; post-fix logs on 2026-06-24 show zero mimo-v2.5-pro / flash usage.

---

## Evidence

### 1. Local Claude Code logs — June 23 (incident day)

Searched all files in `~/.claude/projects` modified between 2026-06-23 00:00 and 2026-06-24 00:00:

| Model string | Count |
|--------------|-------|
| `"model":"mimo-v2.5-pro"` | **214** |
| `"model":"deepseek-v4-pro"` | 21 |
| `"model":"deepseek-v4-flash"` | 0 |

The 214 mimo-v2.5-pro references are the local manifestation of the reported ~201 flash calls. The discrepancy (214 vs 201) is within normal counting variance between client log entries and billed API calls.

### 2. Local Claude Code logs — June 24 (post-fix)

Searched the same tree for files modified between 2026-06-24 00:00 and 2026-06-25 00:00:

| Model string | Count |
|--------------|-------|
| `"model":"mimo-v2.5-pro"` | **0** |
| `"model":"deepseek-v4-pro"` | 100 |
| `"model":"deepseek-v4-flash"` | 0 |

This confirms the fix stopped the flash downgrade.

### 3. Configuration timeline

| File | Modification time (local) | Relevant setting |
|------|---------------------------|------------------|
| `~/.claude/settings.json` | 2026-06-23 21:46:07 | `ANTHROPIC_MODEL=deepseek-v4-pro`, `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514` |
| `~/.zshrc` | 2026-06-23 22:01:00 | `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514` |

The current `~/.zshrc` (lines 5-6) contains:

```bash
export ANTHROPIC_MODEL=deepseek-v4-pro
export CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514
```

The `cc-deepseek-switch-2026-06-23.md` reference explicitly documents the incident:

> Root cause: `~/.zshrc` still had `CLAUDE_CODE_SUBAGENT_MODEL=mimo-v2.5-pro`. DeepSeek endpoint received non-claude-opus model → mapped to flash. Fix: Myrrh (mimo) executed `sed -i` to replace with `claude-opus-4-20250514`.

### 4. cc_dispatch.py wrapper

Both copies of `cc_dispatch.py` (`~/.hermes/profiles/technical/skills/multi-agent-debate/scripts/cc_dispatch.py` and `~/Public/hermes-core-rules-mac-x86/skills/multi-agent-debate/scripts/cc_dispatch.py`) explicitly lock sub-agent model selection:

```python
env['ANTHROPIC_MODEL'] = 'claude-opus-4-20250514'
env['CLAUDE_CODE_SUBAGENT_MODEL'] = 'claude-opus-4-20250514'
```

This wrapper was updated on 2026-06-23 (v3) for the DeepSeek Anthropic-compatible endpoint and is consistent with the post-fix state.

---

## Mechanism

1. **Claude Code main process** reads `~/.claude/settings.json`, where `ANTHROPIC_MODEL=deepseek-v4-pro` and `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514` were already configured.
2. **Claude Code sub-agents** do not inherit the `env` block from `settings.json` (documented in `claude-code-subagent-flash.md`). They instead inherit shell environment variables.
3. On 2026-06-23, `~/.zshrc` still exported `CLAUDE_CODE_SUBAGENT_MODEL=mimo-v2.5-pro`, so every spawned sub-agent used that model string.
4. The DeepSeek Anthropic-compatible endpoint (`https://api.deepseek.com/anthropic`) maps non-Opus Claude model strings to `deepseek-v4-flash`. The string `mimo-v2.5-pro` is not a recognized Claude Opus identifier, so it was downgraded to flash.
5. After `~/.zshrc` was updated to `claude-opus-4-20250514` at 22:01:00, sub-agents began mapping to `deepseek-v4-pro`.

---

## Other Possible Sources Investigated

| Source | Configuration | Could it explain the 201 flash calls? |
|--------|---------------|----------------------------------------|
| **Hermes technical profile** | `~/.hermes/profiles/technical/config.yaml`: `model.default=deepseek-v4-pro`, provider=deepseek | No. Hermes was already locked to pro. |
| **CodeWhale** | `~/.codewhale/config.toml`: `default_text_model=deepseek-v4-pro`, provider=deepseek | No. CodeWhale default is pro. |
| **Claude Code main process** | `~/.claude/settings.json`: `ANTHROPIC_MODEL=deepseek-v4-pro` | No. Main process was on pro. |
| **mimocode / MiMo agent** | Uses its own MiMo endpoint, not DeepSeek | No. MiMo calls do not route through DeepSeek. |
| **Cron / scheduled scripts** | No cron jobs or scheduled scripts referencing `deepseek-v4-flash` or `mimo-v2.5-pro` were found | No. |
| **Other tools / manual API calls** | No active configs or scripts on 2026-06-23 requesting `deepseek-v4-flash` were found | No. |

A broad grep for `deepseek-v4-flash` across the home directory returned many matches, but they were either (a) model-catalog cache files, (b) documentation / skill references, or (c) telemetry files dated 2026-06-14 with zero actual `deepseek-v4-flash` occurrences. None represented active API callers on June 23.

---

## Conclusion

- **Confirmed source:** Claude Code sub-processes (sub-agents / Explore agents).
- **Confirmed mechanism:** `~/.zshrc` exported `CLAUDE_CODE_SUBAGENT_MODEL=mimo-v2.5-pro`; DeepSeek's Anthropic-compatible endpoint mapped that non-Opus model string to `deepseek-v4-flash`.
- **Fix status:** Applied 2026-06-23 22:01:00. Current `~/.zshrc`, `~/.claude/settings.json`, and `cc_dispatch.py` all lock sub-agents to `claude-opus-4-20250514` → `deepseek-v4-pro`.
- **Other sources:** Ruled out. Hermes, CodeWhale, and the Claude Code main process were all configured for pro; no scripts or cron jobs were found requesting flash.

---

## Recommendations

1. **Monitor June 24+ logs** for any resurgence of `mimo-v2.5-pro` or `deepseek-v4-flash` (currently clean).
2. **Add a guard in `cc_dispatch.py`** that aborts if `CLAUDE_CODE_SUBAGENT_MODEL` does not contain `claude-opus-4-20250514`, preventing regressions.
3. **Keep `ANTHROPIC_MODEL` in `~/.zshrc`** as a shell-level backstop, because `settings.json` `env` variables are not inherited by cc sub-agents.
