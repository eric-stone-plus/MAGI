error: unexpected argument 'TASK: Verify these agent dispatch claims against actual configs. Read:
1. ~/.hermes/profiles/technical/skills/multi-agent-debate/scripts/cc_dispatch.py — does it call --effort xhigh? Is CLAUDE_CODE_SUBAGENT_MODEL set?
2. ~/.claude/settings.json — is effortLevel xhigh? ultracode true?
3. ~/.hermes/profiles/technical/skills/multi-agent-debate/SKILL.md — cw dispatch section, rx dispatch section
4. ~/.codewhale/config.toml — is the key correct?
5. ~/.hermes/profiles/technical/memories/MEMORY.md — model economy rules

CLAIMS TO VERIFY:
- cc: claude -p --effort xhigh, CLAUDE_CODE_SUBAGENT_MODEL locks pro
- cw: R1=R1: --auto with 'no execute/modify, produce analysis', R2: 'Do NOT use tool calls'
- Gold: grok build default
- Fr: kimi -p, file explorer
- Myrrh: mimo run --dangerously-skip-permissions
- hm: DS v4-pro, must NOT solo implement
- rx: reasonix run, embed content no paths, <1500B or tool_call -> discard, Gold substitute
- All MAGI models are 'free' (grok annual, kimi subscription, mimo 39/month) vs DS pay-per-use

Flag any claim that does NOT match actual config/files. Output to /Users/ericstone/Public/QUINTE/debates/2026-06-23/agent-dispatch-audit/gold_audit.md' found

Usage: grok [OPTIONS] [PROMPT] [COMMAND]

For more information, try '--help'.
