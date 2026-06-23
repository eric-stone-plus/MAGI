# cc-effort-max Audit

**Scope:** Find every reference to `ultracode` / `xhigh` in cc-related configs, `effort` settings in `~/.claude/settings.json`, and `--effort` in dispatch scripts / `SKILL.md`. For each hit: file, line, current value, and the change required to set effort to `max`.

**Audit date:** 2026-06-23
**Project root:** `/Users/ericstone/Public/hermes-core-rules-mac-x86`

---

## Executive Summary

| Category | Count | Already `max` | Needs change to `max` | Notes |
|----------|-------|---------------|------------------------|-------|
| cc-related configs (incl. backups/history) | 7 files | 0 | 5 active + 3 historical | Primary action: `~/.claude/settings.json` line 80 `effortLevel: "xhigh"` -> `"max"` |
| `~/.claude/settings.json` effort settings | 2 lines | line 7 already `max` | line 80 needs `max` | `ultracode: true` is already correct |
| `--effort` in dispatch scripts / `SKILL.md` | 6 files | all dispatch + most skill refs already `max` | doc language in `skills/autonomous-ai-agents/claude-code/SKILL.md` | Codex `model_reasoning_effort` must stay `xhigh` (Codex rejects `max`) |

**Key compatibility warning from existing docs:** `skills/autonomous-ai-agents/claude-code/SKILL.md` states that for DeepSeek via `ANTHROPIC_BASE_URL` the effective ceiling is `xhigh` (ultracode), and that `settings.json` schema only allows `low/medium/high/xhigh`. Setting `"max"` in `settings.json` may silently fall back to `xhigh` or be ignored when using DeepSeek. The `/effort` UI label `max` internally maps to `xhigh` + `ultracode: true`. This audit lists what *must be edited* to satisfy the request; runtime behavior is subject to those provider/schema constraints.

---

## (1) `ultracode` or `xhigh` in cc-related configs

### Active config files

#### `~/.claude/settings.json`
| Line | Current value | Context | Change to `max`? |
|------|---------------|---------|------------------|
| 80 | `"effortLevel": "xhigh"` | `"alwaysThinkingEnabled": true,` above | **Yes** -> `"effortLevel": "max"` |
| 81 | `"ultracode": true` | boolean flag | No value change; keep `true` (already enables ultracode) |

#### `~/.claude/settings.json.bak`
| Line | Current value | Context | Change to `max`? |
|------|---------------|---------|------------------|
| 83 | `"effortLevel": "xhigh"` | backup of settings.json | **Yes** -> `"effortLevel": "max"` (if keeping backup in sync) |
| 84 | `"ultracode": true` | backup | No value change; keep `true` |

### Historical / versioned config artifacts

#### `~/.claude/file-history/5efb8500-653d-4756-a8de-00ec0b8bed8a/64515cb105c0fe6d@v1`
| Line | Current value | Change to `max`? |
|------|---------------|------------------|
| 82 | `"effortLevel": "max"` | Already `max` (historical) |

#### `~/.claude/file-history/5efb8500-653d-4756-a8de-00ec0b8bed8a/64515cb105c0fe6d@v3`
| Line | Current value | Change to `max`? |
|------|---------------|------------------|
| 83 | `"effortLevel": "xhigh"` | Historical -> `"max"` if maintaining old versions |
| 84 | `"ultracode": true` | Keep `true` |

#### `~/.claude/file-history/5efb8500-653d-4756-a8de-00ec0b8bed8a/64515cb105c0fe6d@v2`
| Line | Current value | Change to `max`? |
|------|---------------|------------------|
| 85 | `"effortLevel": "xhigh"` | Historical -> `"max"` if maintaining old versions |
| 86 | `"ultracode": true` | Keep `true` |

#### `~/.claude/file-history/86f6ba33-e046-4548-8568-43f3834c7325/64515cb105c0fe6d@v1`
| Line | Current value | Change to `max`? |
|------|---------------|------------------|
| 77 | `"effortLevel": "max"` | Already `max` (historical) |

#### `~/.claude/file-history/86f6ba33-e046-4548-8568-43f3834c7325/64515cb105c0fe6d@v2`
| Line | Current value | Change to `max`? |
|------|---------------|------------------|
| 78 | `"effortLevel": "max"` | Already `max` (historical) |

#### `~/.claude/file-history/26e28dc7-6516-4c09-88d8-bf1bad08d215/64515cb105c0fe6d@v3`
| Line | Current value | Change to `max`? |
|------|---------------|------------------|
| 77 | `"effortLevel": "max"` | Already `max` (historical) |

### Project cc skill docs / reference configs

#### `skills/autonomous-ai-agents/claude-code/SKILL.md`
| Line | Current value / snippet | Change to `max`? |
|------|-------------------------|------------------|
| 396 | `| /effort [level] | Set reasoning effort: low, medium, high, xhigh (settings.json) or max (Anthropic-native only, via /effort UI). DeepSeek effective ceiling: xhigh. |` | **Docs** -> update to state target policy is `max`; remove "DeepSeek effective ceiling: `xhigh`" if policy changes |
| 473 | `### Effort Level: xhigh on DeepSeek, max on Anthropic` | **Docs** -> revise heading if policy changes |
| 475 | `effort hierarchy: low -> medium -> high -> xhigh -> max. ... For DeepSeek via ANTHROPIC_BASE_URL, the effective ceiling is **xhigh** (ultracode) ...` | **Docs** -> update DeepSeek guidance if policy changes |
| 731 | `0. **effortLevel schema: only low/medium/high/xhigh are valid.** ... For DeepSeek, effective ceiling is xhigh.` | **Docs** -> update schema/ceiling note if policy changes |
| 762 | `- **effort ceiling is xhigh** — DeepSeek doesn't support Anthropic-native maxThinkingTokens: 32000. xhigh (ultracode) is the effective maximum.` | **Docs** -> update if policy changes |

#### `skills/autonomous-ai-agents/claude-code/references/0011ai-provider.md`
| Line | Current value | Context | Change to `max`? |
|------|---------------|---------|------------------|
| 30 | `export CLAUDE_CODE_EFFORT_LEVEL="max"` | 0011.ai env vars for Claude Code | Already `max` |
| 51 | `model_reasoning_effort = "xhigh"` | **Codex** `~/.codex/config.toml` (not cc) | **No** — Codex rejects `max` with "unknown variant" (per `skills/autonomous-ai-agents/codex/SKILL.md` lines 162, 286-288). Keep `xhigh` for Codex. |

### Plan file

#### `~/.claude/plans/indexed-spinning-cerf.md`
| Line | Current value | Change to `max`? |
|------|---------------|------------------|
| 36 | `(v4 xhigh)      (v4 max)       (v4 max)      (v4 xhigh)` | Diagram labels; `cc` already `max`, `hm`/`omp` `xhigh` |
| 46 | `(v4 xhigh)      (v4 max)       (v4 max)       (v4 max)      (v4 xhigh)` | Diagram labels; same as above |
| 82 | `(v4 xhigh)      (v4 max)       (v4 max)` | Diagram labels |
| 92 | `(v4 xhigh)      (v4 max)       (v4 max)` | Diagram labels |

> These plan files describe `hm`/`omp` as `xhigh` and `cc`/`cw` as `max`. If the goal is to make **cc** `max`, it already is in these diagrams. If the goal is to make all agents `max`, then `hm`/`omp` `xhigh` labels also need updating.

---

## (2) `effort` settings in `~/.claude/settings.json`

| Line | Key | Current value | Change required |
|------|-----|---------------|-----------------|
| 7 | `env.CLAUDE_CODE_EFFORT_LEVEL` | `"max"` | None — already `max` |
| 80 | `effortLevel` | `"xhigh"` | **Change to `"max"`** |

**Related boolean:**
| Line | Key | Current value | Change required |
|------|-----|---------------|-----------------|
| 81 | `ultracode` | `true` | None — already enabled |

---

## (3) `--effort` in dispatch scripts and `SKILL.md`

### Dispatch scripts

#### `skills/multi-agent-debate/scripts/cc_dispatch.py`
| Line | Current value | Change required |
|------|---------------|-----------------|
| 50 | `env['CLAUDE_CODE_EFFORT_LEVEL'] = 'max'` | None — already `max` |
| 55 | `['claude', '-p', '--permission-mode', 'bypassPermissions', '--effort', 'max', prompt]` | None — already `--effort max` |

### `SKILL.md` files

#### `skills/multi-agent-debate/SKILL.md`
| Line | Current value | Change required |
|------|---------------|-----------------|
| 27 | `| cc | DeepSeek v4-pro | R1+R2 | claude -p --permission-mode bypassPermissions --effort max |` | None — already `max` |
| 73 | `claude -p --permission-mode bypassPermissions --effort max "TASK: <prompt>" > file 2>&1` | None — already `max` |

#### `skills/autonomous-ai-agents/claude-code/SKILL.md`
| Line | Current value | Change required |
|------|---------------|-----------------|
| 272 | `| --effort <level> | Reasoning depth: low, medium, high, max, auto |` | Already lists `max`; no change |
| 719 | `3. **Use --effort low** for simple tasks ... **high** or **max** for complex reasoning.` | Already references `max`; no change |

#### `skills/meta/privacy-audit/SKILL.md`
| Line | Current value | Change required |
|------|---------------|-----------------|
| 67 | `HOME=/Users/ericstone reasonix run --model deepseek-v4-pro --effort max "Cross-review R1 PII findings ..."` | None — already `--effort max` |

#### `skills/devops/demurrage-monthly/SKILL.md`
| Line | Current value | Change required |
|------|---------------|-----------------|
| 144 | `HOME=/Users/ericstone reasonix run --model deepseek-v4-pro --effort max "[prompt]" &` | None — already `--effort max` |
| 152 | `- reasonix run supports --model deepseek-v4-pro --effort max parameters` | None — already `max` |

#### `skills/magi/SKILL.md`
| Line | Current value | Change required |
|------|---------------|-----------------|
| 62 | `| 400 | Gold | Retry, no --effort flag |` | No value; docs describe fallback behavior; no change needed |

---

## Action Checklist

1. **Primary edit** — `~/.claude/settings.json` line 80: `"effortLevel": "xhigh"` -> `"effortLevel": "max"`.
2. **Backup sync** — `~/.claude/settings.json.bak` line 83: `"effortLevel": "xhigh"` -> `"max"` (optional, but recommended if the backup is meant to be a hot standby).
3. **Historical file-history versions** — optionally update old `settings.json` snapshots if they are referenced by recovery scripts.
4. **Project docs** — update `skills/autonomous-ai-agents/claude-code/SKILL.md` lines 396, 473-475, 731, 762 to reflect the new target policy if `max` is intended to be the canonical level, **with the caveat that DeepSeek may still enforce `xhigh` as the runtime ceiling**.
5. **Do not change** `skills/autonomous-ai-agents/claude-code/references/0011ai-provider.md` line 51 (`model_reasoning_effort = "xhigh"`) because that is **Codex** config and Codex's enum rejects `max`.
6. **No edits needed** for dispatch scripts (`cc_dispatch.py`) or `SKILL.md` invocation examples that already use `--effort max` / `CLAUDE_CODE_EFFORT_LEVEL=max`.

---

## Files Not Requiring Change (already `max` or not applicable)

| File | Reason |
|------|--------|
| `skills/multi-agent-debate/scripts/cc_dispatch.py` | Already sets `CLAUDE_CODE_EFFORT_LEVEL=max` and `--effort max` |
| `skills/multi-agent-debate/SKILL.md` | Already documents `--effort max` |
| `skills/multi-agent-debate/references/claude-code-bare-setup.md` | Already sets `CLAUDE_CODE_EFFORT_LEVEL=max` |
| `skills/meta/privacy-audit/SKILL.md` | Already uses `--effort max` |
| `skills/devops/demurrage-monthly/SKILL.md` | Already uses `--effort max` |
| `skills/magi/SKILL.md` | `--effort` appears without a value; no change |

---

*End of audit.*
