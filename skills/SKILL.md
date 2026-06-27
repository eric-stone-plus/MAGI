---
name: magi
description: "MAGI v1.7 — Lightweight heterogeneous pre-verification layer. Three base models (kimi/mimo/rx) in parallel with binary convergence gate (>=2/3). Standalone — fully decoupled from QUINTE. hm's self-doubt resolution layer."
spec: "https://github.com/eric-stone-plus/MAGI/blob/master/specs/PROTOCOL.md"
version: "1.7"
triggers:
  - "magi"
---

# MAGI — Heterogeneous Pre-Verification Protocol v1.7

## Architecture

hm dispatches three doctors in parallel: Gold (kimi), Frankincense (mimo), Myrrh (rx). Each answers independently. Output converges through a binary gate: >=2/3 agreement -> [MAGI N/3] verdict; <=1/3 -> escalate to QUINTE.

## Standalone Operation

MAGI is fully decoupled from QUINTE. hm is uncertain about a claim, decision, or analysis -> dispatches MAGI three doctors in parallel for independent verification. Each doctor answers the same question with their own model and perspective. Convergence gate: >=2/3 agreement -> accepted. <=1/3 -> escalate to full QUINTE.

## Three Doctors

| Doctor | Model | Role | Dispatch |
|--------|-------|------|----------|
| Gold | kimi | External perspective, deep analysis | `kimi -p "prompt"` |
| Frankincense (Fr) | mimo | File system exploration, thorough scanning | `mimo run --dangerously-skip-permissions "prompt"` |
| Myrrh | rx (deepseek-v4-pro) | Verification, catch what others miss | `rx -p "prompt" --effort max` |

## Dispatch Strategies

Per-model optimal prompt style determined empirically:

- **Gold (kimi)**: Deep reasoning, external perspective. Structured prompts with clear constraints.
- **Fr (mimo)**: File explorer mode. Give file paths to explore, not open-ended questions. Prevents tool-search mode.
- **Myrrh (rx)**: Verification mode. Uses deepseek-v4-pro with `--effort max`. "Work from the provided context, not memory search. Be thorough, catch what others miss."

## Convergence Gate

- >=2/3 doctors agree -> `[MAGI N/3]` — verdict accepted
- <=1/3 agree -> MAGI divergence — escalate to QUINTE
- Single delegate failure does not block others — retry independently (max 3 attempts)
- 3x all-delegate failure -> `[MAGI hm-solo]` — hm produces substitute analysis

## Failure Recovery

| Failure | Doctor | Recovery |
|---------|--------|----------|
| Timeout | Fr | Shrink prompt <=500 chars, retry; still fails -> `[MAGI Fr-unavailable]` |
| Empty output | Myrrh | Check key validity, retry; still fails -> `[MAGI Myrrh-unavailable]` |
| Any delegate 0 bytes | Any | Classify error (6-tier: auth/rate_limit/timeout/interrupted_recoverable/deprecated/unknown) -> apply tier-specific recovery |

## Dispatch Command Reference

```bash
# Gold (kimi) — deep reasoning, external perspective
kimi -p "Full analysis of <topic>. Be thorough." > /tmp/magi_gold.md 2>&1

# Frankincense (mimo) — file explorer, give paths
mimo run --dangerously-skip-permissions "Read /path/to/files. Check for <issue>. Report findings." > /tmp/magi_fr.md 2>&1

# Myrrh (rx) — verification, deepseek-v4-pro, max effort
rx -p "Work from the provided context. Exhaustive verification." --effort max > /tmp/magi_myrrh.md 2>&1

# NEVER delegate_task — routes through parent provider, breaks model heterogeneity
```

## Invocation Rules

- MAGI is triggered autonomously by hm — not by user command
- Three doctors always dispatched together — each model has unique blind spots
- File modification gate: hm must output `[MAGI CHECK]` before any patch/write_file

## Integration

MAGI operates standalone as hm's pre-verification layer. On divergence, escalates to QUINTE for full multi-agent debate.

When invoked by QUINTE, MAGI is R3 KANSA B only. It must never be dispatched as a R1/R2 debate party or as a fallback for failed QUINTE parties.

See [QUINTE spec](https://github.com/eric-stone-plus/QUINTE/blob/master/specs/PROTOCOL.md) for escalation protocol.
