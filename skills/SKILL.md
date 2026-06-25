---
name: magi
description: "MAGI v1.6 — Lightweight heterogeneous pre-verification layer. Three base models (Gold=platform-specific/kimi/mimo) in parallel with binary convergence gate (>=2/3). Dual-mode: Mode A independent pre-verification / Mode B QUINTE cross-cutting audit layer. hm's self-doubt resolution layer."
spec: "https://github.com/eric-stone-plus/MAGI/blob/master/specs/PROTOCOL.md"
version: "3.4"
triggers:
  - "magi"
---

# MAGI — Heterogeneous Pre-Verification Protocol v1.6

## Architecture

hm dispatches three doctors in parallel: Gold (platform-specific — Win=apiyi codex/gpt-5.4, Mac=codex/codex/gpt-5.4), Frankincense (kimi), Myrrh (mimo). Each answers independently. Output converges through a binary gate: >=2/3 agreement -> [MAGI N/3] verdict; <=1/3 -> escalate to QUINTE.

## Dual-Mode Operation (v1.6)

### Mode A — Independent Pre-Verification

hm is uncertain about a claim, decision, or analysis -> dispatches MAGI three doctors in parallel for independent verification. Each doctor answers the same question with their own model and perspective. Convergence gate: >=2/3 agreement -> accepted. <=1/3 -> escalate to full QUINTE.

### Mode B — Cross-Cutting Audit Layer

During QUINTE execution, MAGI operates as cross-cutting audit layer alongside all phases. Internal convergence gate is ACTIVE — three delegates converge (>=2/3) into one output with one vote. MAGI delegates do not participate in R2. Mode A and Mode B cannot both be active in the same session.

## Three Doctors

| Doctor | Model | Role | Dispatch |
|--------|-------|------|----------|
| Gold | platform-specific (Win=apiyi codex/gpt-5.4, Mac=codex/codex/gpt-5.4) | External perspective, deep analysis | `apiyi -p "prompt"` (Win) / `codex -p "prompt"` (Mac) |
| Frankincense (Fr) | kimi | File system exploration, thorough scanning | `kimi -p "prompt"` (give file paths) |
| Myrrh | mimo | Verification, catch what others miss | `mimo run --dangerously-skip-permissions "prompt"` |

## Dispatch Strategies (2026-06-20 A/B Test)

Per-model optimal prompt style determined empirically:

- **Gold (platform-specific)**: Win=apiyi codex/gpt-5.4 (OpenAI backend, company firewall compatible); Mac=codex/codex/gpt-5.4. Conversational tone works well.
- **Fr (kimi)**: File explorer mode. Give file paths to explore, not open-ended questions. Prevents tool-search mode.
- **Myrrh (mimo)**: Verification mode. "Work from the provided context, not memory search. Be thorough, catch what others miss."

## Convergence Gate

- >=2/3 doctors agree -> `[MAGI N/3]` — verdict accepted
- <=1/3 agree -> MAGI divergence — escalate to QUINTE R2+
- Single delegate failure does not block others — retry independently (max 3 attempts)
- 3x all-delegate failure -> `[MAGI hm-solo]` — hm produces substitute analysis

## Failure Recovery

| Failure | Doctor | Recovery |
|---------|--------|----------|
| 400 (reasoningEffort) | Gold | Retry, verify no --effort/--reasoning-effort CLI flag |
| Timeout | Fr | Shrink prompt <=500 chars, retry; still fails -> `[MAGI Fr-unavailable]` |
| Empty output | Myrrh | Check tp- key validity, retry; still fails -> `[MAGI Myrrh-unavailable]` |
| Exit 143 (SIGTERM) | Gold (if grok) | `grok export <sessionId>` or `grok --resume` — interrupted_recoverable, not timeout. Not applicable to apiyi/codex. |

## Dispatch Command Reference

```bash
# Gold (Win=apiyi codex/gpt-5.4, Mac=codex/codex/gpt-5.4)
apiyi -p "Gold role: <prompt>" > D:/Download/MAGI/.../gold.md 2>&1    # Win
codex -p "Gold role: <prompt>" > ~/Downloads/MAGI/.../gold.md 2>&1     # Mac

# Frankincense (kimi) — file explorer, give paths
kimi -p "Read /path/to/files. Check for <issue>. Report findings." > D:/Download/MAGI/.../fr.md 2>&1

# Myrrh (mimo) — verification, from context
mimo run --dangerously-skip-permissions "Work from the provided context. Exhaustive analysis." > D:/Download/MAGI/.../myrrh.md 2>&1

# NEVER delegate_task — routes through parent provider, breaks model heterogeneity
```

## Invocation Rules

- MAGI is triggered autonomously by hm — not by user command
- Usable in any QUINTE phase: R1 audit, R2 audit, R3 advisory
- Three doctors always dispatched together — each model has unique blind spots
- File modification gate: hm must output `[MAGI CHECK]` before any patch/write_file

## Integration with QUINTE

MAGI serves as both the antechamber AND a senator in QUINTE:
- **Antechamber (Mode A)**: Resolves hm's self-doubt before entering full debate
- **Senator (Mode B)**: Operates alongside QUINTE as cross-cutting audit layer, advisory annotations

See [QUINTE v1.6 spec](https://github.com/eric-stone-plus/QUINTE/blob/master/specs/PROTOCOL.md) for full integration protocol.
