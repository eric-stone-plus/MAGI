• Let me start by reading the ~/.zshrc file to find the exact line.I found the line. Line 6 contains exactly `export CLAUDE_CODE_SUBAGENT_MODEL=mimo-v2.5-pro`.

  Now I need to write a one-liner command that safely replaces it with `export CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514`.

  Requirements:
  1. Only change that specific line
  2. Leave all other lines intact
  3. Work without human interaction

  I'll use `sed -i ''` which is the macOS in-place edit syntax. The pattern should match the exact line and replace it.

  Command:
  ```bash
  sed -i '' 's/^export CLAUDE_CODE_SUBAGENT_MODEL=mimo-v2\.5-pro$/export CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514/' ~/.zshrc
  ```

  This uses `^` and `$` anchors to ensure it only matches the exact line, and escapes the `.` characters in the version string.

  Then I need to verify it works by checking the file.6:export CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514
The command worked and verified. Only line 6 was changed. Let me give the user the exact command and confirmation.

• The exact one-liner is:

  ```bash
  sed -i '' 's/^export CLAUDE_CODE_SUBAGENT_MODEL=mimo-v2\.5-pro$/export CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514/' ~/.zshrc
  ```

  **Verified:** `~/.zshrc` now contains only the updated line:

  ```text
  6:export CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514
  ```

  It matched the full exact line with `^...$` anchors, escaped the literal dots, and left all 39 other lines untouched.

To resume this session: kimi -r session_ab527c2d-5a5e-426d-bd94-d50660563b1d
