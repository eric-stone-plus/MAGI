# SURVEY: `ANTHROPIC_AUTH_TOKEN` & `token-plan-cn` references + cc→MiMo auth verification

**Date:** 2026-06-24  
**Scope:** `~/.hermes/`, `~/Public/`, `~/.claude/`, `~/.zshrc`  
**Report file:** `/Users/ericstone/Public/MAGI/debates/2026-06-24/cc-switch-mimo/full-fr.md`

---

## 1. Executive summary

- **Live cc config is now correct.** `~/.claude/settings.json` and `~/.zshrc` currently use:
  - `ANTHROPIC_BASE_URL=https://api.xiaomimimo.com/anthropic`
  - `ANTHROPIC_AUTH_TOKEN=<MiMo sk-... key>`
  - `ANTHROPIC_MODEL=mimo-v2.5-pro`
- **Verification:** A direct `POST https://api.xiaomimimo.com/anthropic/v1/messages` with `x-api-key: <ANTHROPIC_AUTH_TOKEN>` returned **HTTP 200** and a valid `mimo-v2.5-pro` response.
- **Answer to the user’s question:** `ANTHROPIC_API_KEY` + `api.xiaomimimo.com/v1` is **NOT** the correct way for Claude Code to authenticate with MiMo’s standard endpoint. The official MiMo integration guide and the live test both require:
  - `ANTHROPIC_AUTH_TOKEN` (not `ANTHROPIC_API_KEY`)
  - Base URL `https://api.xiaomimimo.com/anthropic` (not `/v1`)
- **The main remaining work is documentation drift:** several Hermes skills, reference docs, and helper scripts still describe the old `token-plan-cn.xiaomimimo.com` gateway or, worse, the incorrect `api.xiaomimimo.com/v1` + `ANTHROPIC_API_KEY` combination.

---

## 2. Auth verification — is `ANTHROPIC_API_KEY` the right way?

### 2.1 Official MiMo documentation

MiMo’s published Claude Code integration doc (2026-06-12, `https://mimo.mi.com/docs/en-US/tokenplan/integration/claudecode`) states:

| Usage method | Anthropic-compatible base URL | Key format | settings.json field |
|---|---|---|---|
| **Pay-as-you-go MiMo API** (standard) | `https://api.xiaomimimo.com/anthropic` | `sk-xxxxx` | `ANTHROPIC_AUTH_TOKEN` |
| **Token Plan CN** | `https://token-plan-cn.xiaomimimo.com/anthropic` | `tp-xxxxx` | `ANTHROPIC_AUTH_TOKEN` |

It explicitly tells users to **clear** `ANTHROPIC_AUTH_TOKEN` / `ANTHROPIC_BASE_URL` conflicts before configuring, and the example `settings.json` uses `ANTHROPIC_AUTH_TOKEN`.

### 2.2 Local contradiction

`~/.hermes/profiles/technical/skills/multi-agent-debate/references/claude-code-provider-switching.md` claims the opposite:

> ```json
> "ANTHROPIC_BASE_URL": "https://api.xiaomimimo.com/v1",
> "ANTHROPIC_API_KEY": "sk-...",
> ```
> Token-plan endpoint is stale/broken and removed. Always use the standard `api.xiaomimimo.com/v1` + `ANTHROPIC_API_KEY`.

This is **wrong** for Claude Code:
- `api.xiaomimimo.com/v1` is the **OpenAI-compatible** Chat Completions endpoint.
- Claude Code speaks the **Anthropic Messages** protocol, so its `ANTHROPIC_BASE_URL` must end in `/anthropic`.
- The working live config already contradicts this reference file.

### 2.3 Live test performed

```bash
POST https://api.xiaomimimo.com/anthropic/v1/messages
Headers:
  x-api-key: <ANTHROPIC_AUTH_TOKEN from ~/.claude/settings.json>
  anthropic-version: 2023-06-01
Body:
  {"model":"mimo-v2.5-pro","max_tokens":10,"messages":[{"role":"user","content":"hi"}]}
```

Result:
- **HTTP 200**
- Response body started with `{"id":"...","type":"message","role":"assistant","model":"mimo-v2.5-pro",...}`

The same key also returns 200 on `https://api.xiaomimimo.com/v1/chat/completions`, confirming `/v1` is OpenAI-protocol and `/anthropic` is the Anthropic-protocol path that cc needs.

### 2.4 Conclusion

**No — do not use `ANTHROPIC_API_KEY` + `api.xiaomimimo.com/v1` for Claude Code.**
Use:
```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.xiaomimimo.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "<MiMo sk-... key>",
    "ANTHROPIC_MODEL": "mimo-v2.5-pro",
    "CLAUDE_CODE_SUBAGENT_MODEL": "mimo-v2.5-pro"
  }
}
```

---

## 3. Live configuration files — current state

### 3.1 `~/.claude/settings.json` ✅ CORRECT

```text
line 3:    "ANTHROPIC_BASE_URL": "https://api.xiaomimimo.com/anthropic",
line 4:    "ANTHROPIC_AUTH_TOKEN": "sk-cx2ce2l60io8ucbb40rrhewno97cd60ycuifr27i6i4gus0x",
line 5:    "ANTHROPIC_MODEL": "mimo-v2.5-pro",
line 6:    "CLAUDE_CODE_SUBAGENT_MODEL": "mimo-v2.5-pro",
```

No update needed.

### 3.2 `~/.zshrc` ✅ CORRECT

```text
line 5:  export ANTHROPIC_MODEL=mimo-v2.5-pro
line 6:  export CLAUDE_CODE_SUBAGENT_MODEL=mimo-v2.5-pro
line 7:  export ANTHROPIC_BASE_URL=https://api.xiaomimimo.com/anthropic
line 10: export MIMO_API_KEY=sk-cx2ce2l60io8ucbb40rrhewno97cd60ycuifr27i6i4gus0x
line 11: export ANTHROPIC_AUTH_TOKEN=$MIMO_API_KEY
line 12: # export ANTHROPIC_API_KEY=$MIMO_API_KEY  # DEPRECATED — use ANTHROPIC_AUTH_TOKEN for Anthropic protocol
```

No update needed. The commented-out `ANTHROPIC_API_KEY` line is fine as a reminder.

### 3.3 `~/.claude/settings.json.bak` — DeepSeek backup

```text
line 3: "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
line 4: "ANTHROPIC_AUTH_TOKEN": "[REDACTED_DEEPSEEK_KEY]",
line 5: "ANTHROPIC_MODEL": "deepseek-v4-pro",
```

This is a valid rollback snapshot to DeepSeek. **No change required** unless the backup policy is to keep it synchronized with the current MiMo config.

---

## 4. Files and lines that need updating

### 4.1 Hermes skill docs (live source under `~/.hermes/profiles/technical/skills/`)

These documents currently tell future agents to use the wrong endpoint, the wrong auth variable, or the obsolete `token-plan-cn` gateway for cc.

| File | Line(s) | Current text / issue | Recommended update |
|---|---|---|---|
| `autonomous-ai-agents/claude-code/SKILL.md` | 27 | "MiMo (`token-plan-cn.xiaomimimo.com`, `mimo-v2.5-pro`)" | Replace with `https://api.xiaomimimo.com/anthropic` or note both standard and token-plan endpoints. |
| `autonomous-ai-agents/claude-code/SKILL.md` | 32 | `ANTHROPIC_BASE_URL="https://token-plan-cn.xiaomimimo.com"` | Add `/anthropic` suffix. If documenting current standard, use `https://api.xiaomimimo.com/anthropic`. |
| `autonomous-ai-agents/claude-code/SKILL.md` | 33 | `ANTHROPIC_AUTH_TOKEN=***` | Keep var name, but ensure the endpoint above is `/anthropic`. |
| `autonomous-ai-agents/claude-code/SKILL.md` | 773 | Conflict note references `ANTHROPIC_AUTH_TOKEN` and MiMo `sk-cx2ce...` key. | Update to say standard endpoint requires `ANTHROPIC_AUTH_TOKEN`; `ANTHROPIC_API_KEY` should not be set. |
| `autonomous-ai-agents/claude-code/references/cc-mimo-backend.md` | 25-26 | `ANTHROPIC_BASE_URL="https://token-plan-cn.xiaomimimo.com"` + `ANTHROPIC_AUTH_TOKEN=***` | Add `/anthropic` to the base URL; or switch the whole section to `https://api.xiaomimimo.com/anthropic`. |
| `autonomous-ai-agents/claude-code/references/cc-mimo-backend.md` | 37 | "cc and MAGI Myrrh share the same token-plan-cn endpoint" | Update to reflect current routing (standard MiMo API, not token-plan-cn). |
| `autonomous-ai-agents/claude-code/references/third-party-providers.md` | 60-67 | MiMo block uses `https://api.xiaomimimo.com` (no `/anthropic`) and model `mimo-v2-pro` | Change endpoint to `https://api.xiaomimimo.com/anthropic` and model to `mimo-v2.5-pro`. |
| `autonomous-ai-agents/claude-code/references/cc-auth-conflict.md` | 29 | Example uses `https://token-plan-cn.xiaomimimo.com/anthropic` + `ANTHROPIC_API_KEY` | Align with official docs: `https://api.xiaomimimo.com/anthropic` + `ANTHROPIC_AUTH_TOKEN`. |
| `autonomous-ai-agents/claude-code/references/cc-auth-conflict.md` | 56 | Historical note says Gold + Myrrh fixed by renaming AUTH_TOKEN → API_KEY. | Add a correction: the fix should have been the reverse — keep `ANTHROPIC_AUTH_TOKEN` and remove `ANTHROPIC_API_KEY`. |
| `multi-agent-debate/references/claude-code-provider-switching.md` | 23-24 | `https://api.xiaomimimo.com/v1` + `ANTHROPIC_API_KEY`; claims token-plan is deprecated | **Critical fix:** change to `https://api.xiaomimimo.com/anthropic` + `ANTHROPIC_AUTH_TOKEN`. |
| `multi-agent-debate/references/quinte-agent-provider-config.md` | 9 | Table says cc key field is `env.ANTHROPIC_AUTH_TOKEN` — correct, but context is token-plan. | Add a note that standard pay-as-you-go uses the same var with `https://api.xiaomimimo.com/anthropic`. |
| `multi-agent-debate/references/quinte-agent-provider-config.md` | 17-18 | Lists token-plan endpoints only. | Add standard endpoint row: `https://api.xiaomimimo.com/anthropic` / `https://api.xiaomimimo.com/v1`. |
| `multi-agent-debate/references/quinte-agent-provider-config.md` | 21-27 | cc config example is token-plan only. | Add a standard-API example or switch the canonical example to `api.xiaomimimo.com/anthropic` + `sk-...`. |
| `multi-agent-debate/references/mimo-agent-routing.md` | 8 | Routing table says cc endpoint is `token-plan-cn.../anthropic` with `tp-...` | Update cc row to current standard `api.xiaomimimo.com/anthropic` + `sk-...`. |
| `multi-agent-debate/references/mimo-agent-routing.md` | 21-22 | Example config uses token-plan endpoint + `tp-...` | Update to standard endpoint and `sk-...` key. |
| `multi-agent-debate/references/cc-python-wrapper.md` | 24-25 | `ANTHROPIC_BASE_URL = 'https://token-plan-cn.xiaomimimo.com'` + `ANTHROPIC_AUTH_TOKEN = key` | Add `/anthropic`; or use `https://api.xiaomimimo.com/anthropic` if documenting current standard. |
| `multi-agent-debate/references/model-dispatch-strategies.md` | 35-36 | Python wrapper uses `https://token-plan-cn.xiaomimimo.com` | Same as above. |
| `multi-agent-debate/references/quad-key-rotation.md` | 115 | Lists `~/.claude/settings.json (ANTHROPIC_AUTH_TOKEN)` as one of 8 locations. | No variable change needed, but the surrounding instructions should mention `/anthropic` endpoint. |
| `multi-agent-debate/references/iron-triangle-key-rotation.md` | 115 | Same as above. | Same as above. |
| `autonomous-ai-agents/codewhale/references/hermes-env-scrubbing.md` | 97 | "Update Claude Code: edit `~/.claude/settings.json` → `ANTHROPIC_AUTH_TOKEN`" | Add that the endpoint must be `/anthropic`, not `/v1`. |
| `autonomous-ai-agents/codewhale/references/credential-rotation.md` | 10 | Table lists `env.ANTHROPIC_AUTH_TOKEN` for Claude Code. | Add endpoint column or note `/anthropic`. |
| `devops/batch-llm-workloads/SKILL.md` | 136, 200 | Mentions `token-plan-cn` rate limits and model. | If these batch scripts are now targeting the standard API, update endpoint references; otherwise keep as token-plan documentation. |
| `devops/batch-llm-workloads/references/mimo-api-patterns.md` | 1, 5 | Title/endpoint say `token-plan-cn.xiaomimimo.com/v1`. | Clarify whether this is token-plan-specific or rename to MiMo API patterns with `api.xiaomimimo.com/v1`. |
| `autonomous-ai-agents/mimo-code/SKILL.md` | 12, 40, 45, 67, 160, 181-184, 187-189, 202, 205-206 | Many `token-plan-cn` references. | These are accurate for token-plan users. Add a section distinguishing token-plan vs. standard pay-as-you-go `api.xiaomimimo.com/anthropic` for Claude Code. |

### 4.2 Public core-rules repos (mirrors of the Hermes skills)

The same drift exists in the committed / backup copies under `~/Public/`. They should be updated in lockstep with the live Hermes skills.

| Repo path | Files to mirror-update |
|---|---|
| `Public/hermes-core-rules-mac-x86/skills/autonomous-ai-agents/claude-code/SKILL.md` | Lines referencing `token-plan-cn` and the MiMo dispatch snippet. |
| `Public/hermes-core-rules-mac-x86/skills/autonomous-ai-agents/claude-code/references/third-party-providers.md` | MiMo endpoint + model name. |
| `Public/hermes-core-rules-mac-x86/skills/autonomous-ai-agents/claude-code/references/deepseek-pitfalls.md` | Historical `ANTHROPIC_AUTH_TOKEN` for DeepSeek — keep if historical, update only if presenting as current. |
| `Public/hermes-core-rules-mac-x86/skills/autonomous-ai-agents/claude-code/references/cross-provider-limits.md` | Generic mention — likely OK. |
| `Public/hermes-core-rules-mac-x86/skills/autonomous-ai-agents/codewhale/references/hermes-env-scrubbing.md` | Add `/anthropic` note. |
| `Public/hermes-core-rules-mac-x86/skills/autonomous-ai-agents/codewhale/references/credential-rotation.md` | Add endpoint note. |
| `Public/hermes-core-rules-mac-x86/skills/multi-agent-debate/references/quad-key-rotation.md` | Add endpoint note. |
| `Public/hermes-core-rules-mac-x86/skills/multi-agent-debate/references/iron-triangle-key-rotation.md` | Add endpoint note. |
| `Public/hermes-core-rules-mac-x86/skills/multi-agent-debate/references/cc-cross-provider-parallelism.md` | Generic mention — likely OK. |
| `Public/hermes-core-rules-mac-x86/skills/devops/hermes-maintenance/references/deepseek-key-rotation.md` | Historical DeepSeek instructions — OK as history. |
| `Public/hermes-core-rules-win/skills/...` | Same set as mac-x86 above. |

### 4.3 Helper scripts / code

| File | Line(s) | Issue | Recommended update |
|---|---|---|---|
| `Public/QUINTE/debates/2026-06-20/magi-model-leak/run_cc.py` | 5-6 | Uses `https://token-plan-cn.xiaomimimo.com` (no `/anthropic`) + `ANTHROPIC_AUTH_TOKEN`. | Change to `https://api.xiaomimimo.com/anthropic` (or add `/anthropic`). |
| `Public/MAGI/debates/2026-06-20/magi-model-leak/run_cc.py` | 5-6 | Same as above. | Same as above. |
| `Public/DEVELOPMENT/quinte-t1/llm_client.py` | 4, 32, 37 | Defaults/fallbacks to `https://token-plan-cn.xiaomimimo.com/v1`. | If the project now uses the standard OpenAI-compatible endpoint, change defaults to `https://api.xiaomimimo.com/v1`. |
| `Public/DEVELOPMENT/quinte-t1-v2/llm_client.py` | 4, 32, 37 | Same as above. | Same as above. |
| `Public/DEVELOPMENT/READ ONLY/3.模型设计/工具配置/claude-code-macos-setup-for-win.md` | 103, 151 | Setup example uses `ANTHROPIC_AUTH_TOKEN` with placeholder key. | Add the correct `/anthropic` endpoint and note not to use `/v1`. |
| `Public/DEVELOPMENT/READ ONLY/3.模型设计/工具配置/claude-code-macos-setup-for-win copy.md` | 103, 151 | Same as above. | Same as above. |

### 4.4 `.claude` context — logs, backups, paste-cache, project JSONLs

These files contain references but are **transient/cache/historical**. They are listed because the user asked to search cc context, but in most cases they should **not** be hand-edited.

| File / pattern | Count | Notes |
|---|---|---|
| `.claude/settings.json` | 1 | Live config — already correct. |
| `.claude/settings.json.bak` | 1 | DeepSeek rollback snapshot — keep as-is. |
| `.claude/history.jsonl` | 2 | Historical chat/paste references to `token-plan-cn`. No edit needed. |
| `.claude/cache/changelog.md` | 5 | Official Claude Code changelog mentions both `ANTHROPIC_AUTH_TOKEN` and `ANTHROPIC_API_KEY`. Do not edit. |
| `.claude/paste-cache/*.txt` | 32 | Cached pasted text containing old configs and discussions. No edit needed; clear cache if desired. |
| `.claude/file-history/*` | ~30 | Versioned file backups containing old `settings.json` states. No edit needed; they are backups. |
| `.claude/projects/*.jsonl` and `tool-results/*.txt` | ~200+ | Session transcripts. No edit needed. Some contain real `tp-` / `sk-` keys; consider rotating keys if concerned, but do not edit logs. |
| `.claude/plugins/marketplaces/claude-plugins-official/plugins/security-guidance/hooks/*.py` | 2 | Plugin source that scans for `ANTHROPIC_AUTH_TOKEN` / `ANTHROPIC_API_KEY`. Do not edit. |

### 4.5 MAGI / QUINTE debate and audit logs

All debate files under `~/Public/MAGI/debates/` and `~/Public/QUINTE/debates/` are **historical transcripts**. They record what was said and done at the time. Editing them would destroy the audit trail.

Notable files (no update required):
- `Public/MAGI/debates/2026-06-24/cc-switch-mimo/gold.md`
- `Public/MAGI/debates/2026-06-24/cc-switch-mimo/auth-fix2-myrrh.md`
- `Public/MAGI/debates/2026-06-24/cc-switch-mimo/anthropic-fix.md`
- `Public/MAGI/debates/2026-06-24/cc-switch-mimo/full-gold.md`
- `Public/MAGI/debates/2026-06-20/magi-dispatch-integrity/fr_fullscan.md`
- `Public/MAGI/debates/2026-06-20/magi-model-leak/fr_round1.md`
- `Public/QUINTE/debates/2026-06-13/Mimo-API连通性检查-20260613.md`
- `Public/QUINTE/debates/2026-06-20/provider-switch-quinte/*.md`
- `Public/QUINTE/debates/2026-06-20/meta-quinte/*.md`
- `Public/MAGI/audit/model-name-leak-scan.md`

If any of these logs contain **real, unredacted API keys**, the appropriate action is key rotation, not log redaction.

---

## 5. Reference inventory by root

### 5.1 `~/.hermes/` — 78 matching lines across 30 files

Key files (actionable) are listed in §4.1. Additional occurrences are in:
- `.hermes/models_dev_cache.json` (3) — generated model cache; no update.
- `.hermes/hermes-agent/tests/hermes_cli/test_web_server.py` (2), `test_xiaomi_provider.py` (1), `test_custom_provider_session_persistence.py` (1) — test fixtures referencing `token-plan-cn`; update only if the test is meant to cover the standard endpoint.

### 5.2 `~/Public/` — ~260 matching lines across ~70 files

Most are in `MAGI/debates/`, `QUINTE/debates/`, and audit logs (historical). The actionable subset is in §4.2 and §4.3.

### 5.3 `~/.claude/` — ~700+ matching lines across ~150 files

Almost all are session logs, backups, paste-cache, and tool results. Only `settings.json` and `settings.json.bak` are configuration files. See §4.4.

### 5.4 `~/.zshrc` — 2 matching lines

Both are correct as of the latest edit (line 11 `ANTHROPIC_AUTH_TOKEN`, line 12 commented-out `ANTHROPIC_API_KEY`).

---

## 6. Recommended next steps

1. **Fix the most dangerous doc first:** `~/.hermes/profiles/technical/skills/multi-agent-debate/references/claude-code-provider-switching.md` — it explicitly instructs `api.xiaomimimo.com/v1` + `ANTHROPIC_API_KEY`, which will break cc.
2. **Align all cc MiMo snippets:** Every cc dispatch example using `token-plan-cn.xiaomimimo.com` without `/anthropic` should add the suffix or switch to `api.xiaomimimo.com/anthropic`.
3. **Mirror updates** into `Public/hermes-core-rules-mac-x86/` and `Public/hermes-core-rules-win/` so the committed core rules match the live Hermes skills.
4. **Update helper scripts:** `run_cc.py` (both MAGI and QUINTE copies) and the `llm_client.py` default endpoints.
5. **Leave historical logs alone.** If any contain live keys, rotate the keys instead.
6. **Verify after editing:** Run `claude doctor` or a direct `/anthropic/v1/messages` curl with `ANTHROPIC_AUTH_TOKEN` to confirm cc still works.

---

## 7. Quick canonical snippet

Use this as the single source of truth for Claude Code + MiMo standard API:

```json
{
  "env": {
    "ANTHROPIC_BASE_URL": "https://api.xiaomimimo.com/anthropic",
    "ANTHROPIC_AUTH_TOKEN": "<MiMo sk-... key>",
    "ANTHROPIC_MODEL": "mimo-v2.5-pro",
    "CLAUDE_CODE_SUBAGENT_MODEL": "mimo-v2.5-pro"
  },
  "model": "mimo-v2.5-pro"
}
```

And in `~/.zshrc`:

```zsh
export ANTHROPIC_MODEL=mimo-v2.5-pro
export CLAUDE_CODE_SUBAGENT_MODEL=mimo-v2.5-pro
export ANTHROPIC_BASE_URL=https://api.xiaomimimo.com/anthropic
export MIMO_API_KEY=<sk-...>
export ANTHROPIC_AUTH_TOKEN=$MIMO_API_KEY
# Do NOT set ANTHROPIC_API_KEY for MiMo — cc will warn about the conflict.
```

---

*End of survey.*
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                       We have written report. Need respond to user summarizing. Also maybe mention the live config is now correct and verification. Provide file path. Ensure same language as user (English). Keep concise.

• Done. I searched `~/.hermes/`, `~/Public/`, `~/.claude/`, and `~/.zshrc`, read the live configs and key skill files, and wrote the full survey report to:

  **`/Users/ericstone/Public/MAGI/debates/2026-06-24/cc-switch-mimo/full-fr.md`**

  Key findings:

  - **Live cc config is already correct** as of this check:
    - `~/.claude/settings.json` uses `ANTHROPIC_BASE_URL=https://api.xiaomimimo.com/anthropic` + `ANTHROPIC_AUTH_TOKEN`
    - `~/.zshrc` mirrors that
  - **Verification:** I tested `POST https://api.xiaomimimo.com/anthropic/v1/messages` with the live `ANTHROPIC_AUTH_TOKEN` — got **HTTP 200** and a valid `mimo-v2.5-pro` response.
  - **Answer to your question:** `ANTHROPIC_API_KEY` + `api.xiaomimimo.com/v1` is **not** the correct way for cc to auth with MiMo. Use `ANTHROPIC_AUTH_TOKEN` with `https://api.xiaomimimo.com/anthropic`. The `/v1` path is OpenAI-compatible; cc speaks Anthropic protocol.
  - **Most remaining work is documentation drift:** several Hermes skill files and reference docs still describe `token-plan-cn` or the wrong `api.xiaomimimo.com/v1` + `ANTHROPIC_API_KEY` combo. The report lists every actionable file/line.
  - `.claude` logs/backups and debate audit logs contain many references but are historical/cache; they generally should not be edited (key rotation is the right fix if any real keys leaked).

To resume this session: kimi -r session_7cb9f6e5-4eef-4ea4-97d2-fcb3dbd2a2ab
