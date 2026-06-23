[2m2026-06-23T14:01:09.671175Z[0m [31mERROR[0m tool_error: tool_output_error [3msession_id[0m[2m=[0m019ef4c8-b11f-7691-a883-3c631e78e6c8 [3mtool_name[0m[2m=[0m"read_file" [3meffective_tool_name[0m[2m=[0m"read_file" [3mmodel_id[0m[2m=[0m"grok-build" [3merror_kind[0m[2m=[0m"tool_output_error"
[2m2026-06-23T14:03:28.657448Z[0m [31mERROR[0m tool_error: tool_output_error [3msession_id[0m[2m=[0m019ef4c8-b11f-7691-a883-3c631e78e6c8 [3mtool_name[0m[2m=[0m"read_file" [3meffective_tool_name[0m[2m=[0m"read_file" [3mmodel_id[0m[2m=[0m"grok-build" [3merror_kind[0m[2m=[0m"tool_output_error"
**Append a later override is the safest.**

### Why among the three options

| Option | Preserves rest of file intact? | Risk of mangling syntax/other lines | Race / partial-write exposure for sourcing shells | Idempotent & predictable | Verdict |
|--------|-------------------------------|-------------------------------------|---------------------------------------------------|---------------------------|---------|
| (1) `sed -i ''` | No (rewrites the matched line) | Medium (regex, macOS `sed -i ''` footgun, silent no-op if whitespace/quotes differ) | Full rewrite | Only if pattern always matches | Acceptable (project precedent for keys) but not safest |
| (2) python3 inline | No (full read-modify-write) | Low (if done carefully) | Full rewrite | Easy to make | Good when you want a clean single line |
| (3) append override | **Yes** (literally untouched) | **None** | Append only (safest) | Trivially | **Safest** |

### Key constraints mapped to reality

- **"Preserve the rest of zshrc intact"**: Only append satisfies this strictly. sed/python change bytes that are already there.
- **Sourced by new shells, must not break existing sessions**: None of the three affect *already-running* shells (they already executed the `export` at start). New shells just re-source the file. Append cannot introduce a syntax error that would break a new shell.
- **Automated, no manual edit**: Append is one line and extremely hard to get wrong.
- **Current reality in this workspace**: The line is already `claude-opus-4-20250514`. The `mimo-v2.5-pro` you see at runtime is a *stale inherited env* from the current shell/session start (or from `~/.claude/settings.json` top-level model field). Changing the file only affects future shells.

### Recommended implementation (append)

```bash
# Safe, non-destructive
echo 'export CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514' >> ~/.zshrc

# Optional hygiene: document why the duplicate exists
# echo '# CLAUDE_CODE_SUBAGENT_MODEL override (ensures pro-tier subagents; last export wins)' >> ~/.zshrc
```

Then verify only new shells:
```bash
zsh -c 'source ~/.zshrc; echo $CLAUDE_CODE_SUBAGENT_MODEL'
```

### When you would choose differently (architecture notes)

- **Choose Python (2)** when you want a single canonical line and will do the work to make it robust:
  - Always backup first: `cp ~/.zshrc ~/.zshrc.bak.$(date +%s)`
  - Prefer temp file in same dir + `os.replace()` (atomic on POSIX) over direct `open(..., 'w')`
  - Run `zsh -n ~/.zshrc` after
  - Handle "line missing" vs "line present" cases explicitly

- **sed** only when you already have a proven exact pattern (see the DEEPSEEK_API_KEY cases in quad-key-rotation.md and iron-triangle-key-rotation.md) and you accept the maintenance burden of macOS vs GNU syntax.

- **Better long-term pattern** (beyond the three options): Source an overrides file at the very end of `.zshrc`:
  ```zsh
  [[ -f ~/.zshrc.local ]] && source ~/.zshrc.local
  ```
  Then your automation only ever appends/writes the override to the `.local` file. This keeps the main `.zshrc` completely untouched forever.

Append wins on the explicit requirements you gave. It is the lowest-regret, zero-mutilation choice for a file that is sourced into many shells.
