**Most likely root cause: #1 (zshrc export is stale/out-of-sync) combined with how CLAUDE_CODE_SUBAGENT_MODEL actually propagates to cc sub-processes.**

### Evidence from the repo (including today's verification data)

- `deepseek-cc-switch-verification.json` (timestamp 2026-06-23) explicitly shows the mismatch you are living:
  - `~/.claude/settings.json` "env" block: `CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514` (and same for ANTHROPIC_MODEL) → PASS.
  - Runtime shell: `echo $CLAUDE_CODE_SUBAGENT_MODEL` → `mimo-v2.5-pro`.
  - It notes the historical 58-flash incident was "fixed by adding CLAUDE_CODE_SUBAGENT_MODEL key", treats "mimo-v2.5-pro (pro)" as safe at the moment of the check (because they were in a MiMo phase or considered any *-pro safe), and records the top-level model field as mimo + a tp- MiMo token.

- Historical diagnosis (claude-code-subagent-flash.md + deepseek-pitfalls.md):
  - settings.json `env.*` values are injected **only into the main cc process**.
  - Sub-agents (`@agent`, WebSearch, WebFetch, internal Explore/Agent tool paths) are **real child OS processes**. They do **not** inherit the settings.json env block.
  - When the child reaches DeepSeek's `/anthropic` compat layer without a model name (or with sonnet/haiku/unknown), it defaults/maps to `deepseek-v4-flash`.
  - The original mitigation that actually worked was a shell-level `export` (sourced via `.zshrc`) so the parent cc process carries the var in its real `os.environ` / process env, which children inherit.

- Current practice (SKILL.md table + multi-agent-debate + verification) for DeepSeek:
  - Main + subagent use `claude-opus-4-20250514` (the string) so DeepSeek's mapper sees `claude-opus-*` → v4-pro.
  - Direct `deepseek-v4-pro` as the value is sometimes documented but the claude-opus alias is the one being used to also influence cc's internal tier selection for subagents.

- Invocation patterns that matter:
  - `HOME=/Users/ericstone script -q /dev/null claude -p ...` (the recommended non-bare wrapper).
  - Background `terminal(background=true)` dispatches (QUINTE/MAGI etc.).
  - `python3 scripts/cc_dispatch.py ...` (referenced everywhere, not present in this repo; described as reading keys from env + falling back to codewhale config, and using the opus name for DeepSeek compat).
  - These start from the current process env (which came from a shell that sourced `.zshrc`).

### Why the other modes are less likely (or secondary)

- **#2 (settings.json env.CLAUDE_CODE_SUBAGENT_MODEL missing)**: Verification says it is present. If you only edited it and didn't touch `.zshrc`, this isn't the active problem.
- **#3 (defaults to sonnet when unset)**: The var *is* set (to the wrong thing). If it were truly absent, you'd also see main-process effects or more consistent sonnet names.
- **#4 (some invocation path ignores env vars)**: Possible contributor (Hermes terminal subprocess filtering, a cc_dispatch.py that does `env=os.environ.copy()` without forcing the var, `script` PTY semantics, or non-login shells). But these paths still ultimately inherit from the launching shell's environment. If `.zshrc` is exporting `mimo-v2.5-pro`, they get the bad value.

### The mechanism that produces flash today

1. You (or a prior switch) put the correct `claude-opus-4-20250514` values + DeepSeek base URL/token in `~/.claude/settings.json`.
2. `.zshrc` (or a sourced env file) still has `export CLAUDE_CODE_SUBAGENT_MODEL=mimo-v2.5-pro` (or equivalent) from the MiMo era (or USER.md policy of "cc=MiMo").
3. `claude` (or cc_dispatch wrapper) is launched. The main process sees the shell env (mimo) + loads settings.json.
4. When cc forks a sub-agent child, the child process environment contains `CLAUDE_CODE_SUBAGENT_MODEL=mimo-v2.5-pro`.
5. The sub-request goes to the current `ANTHROPIC_BASE_URL` (DeepSeek) carrying a non-`claude-opus-*` model identifier → DeepSeek mapper → v4-flash.

Main conversation can still look correct (or use the settings value), while sub paths (and anything that goes through agent/Web* tools) produce flash traffic. Subagent model choice is not emitted in the local `~/.claude/projects/...` JSONL, so you only see it on the DeepSeek side.

### Recommended fix (in order)

1. **Fix the persistent source** (highest leverage):
   ```bash
   # In ~/.zshrc (and any sourced .env / profile files)
   export ANTHROPIC_MODEL=claude-opus-4-20250514
   export CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514
   # (Remove or guard any unconditional mimo-v2.5-pro for cc when DeepSeek backend is active)
   ```
   Then `source ~/.zshrc` (or new terminal/Hermes session).

2. **Keep settings.json in sync** (already done per verification, but double-check on every provider switch):
   ```json
   {
     "env": {
       "ANTHROPIC_BASE_URL": "https://api.deepseek.com/anthropic",
       "ANTHROPIC_AUTH_TOKEN": "sk-... (deepseek key)",
       "ANTHROPIC_MODEL": "claude-opus-4-20250514",
       "CLAUDE_CODE_SUBAGENT_MODEL": "claude-opus-4-20250514"
     },
     ...
   }
   ```

3. **Harden the actual launch sites** (defense in depth):
   - Prefix critical dispatches explicitly:
     ```bash
     CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514 \
     ANTHROPIC_MODEL=claude-opus-4-20250514 \
     HOME=/Users/ericstone script -q /dev/null claude -p ...
     ```
   - Update `cc_dispatch.py` (and the hermes-cc wrapper if it exists in ~/.hermes) to do `env = os.environ.copy(); env["CLAUDE_CODE_SUBAGENT_MODEL"] = "claude-opus-4-20250514"; ...` (and same for ANTHROPIC_MODEL) before the subprocess.
   - If using provider profiles, make the exports conditional or use wrapper functions that set the right pair for the active backend.

4. **Verification**:
   - After changes + full cc restart (new session), watch the DeepSeek console for 24h (the only reliable signal).
   - `echo $CLAUDE_CODE_SUBAGENT_MODEL` in the launching shell should show the opus name.
   - Re-run the checks that produced `deepseek-cc-switch-verification.json` after a restart.
   - Note the open #65863 bug: even with correct model names, some sub-agent/Web paths on DeepSeek can 400 for other reasons (thinking + reasoning_effort). Those may still surface as odd traffic.

5. **Operational hygiene**:
   - Provider switches (DeepSeek ↔ MiMo etc.) are a two-file atomic change: `~/.claude/settings.json` + `~/.zshrc` (plus any profile-specific copies).
   - USER.md currently says "cc=MiMo v2.5-pro" — if you are deliberately running cc on DeepSeek for a session/QUINTE, that policy line is the source of the stale export.

The settings.json-only "fix" was always partial because of the documented child-process inheritance behavior. The shell export (updated to the claude-opus alias) is what actually reaches the sub-agents. That's why you're seeing flash again after a switch.
