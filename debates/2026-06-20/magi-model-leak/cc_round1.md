Here's the complete picture:

---

## Core Spec Docs — leaks confirmed (you found all 3)

| File | Line | Leaked Names |
|------|------|-------------|
| `README.md` | 73 | `grok-build`, `kimi K2.7`, `mimo-v2.5-pro` |
| `specs/theoretical-foundation.md` | 9 | `DeepSeek v4-pro`, `mimo-v2.5`, `kimi` |
| `specs/theoretical-foundation.md` | 21 | `DS v4-pro`, `mimo-v2.5`, `kimi` |

**Clean:** `specs/PROTOCOL.md` ✅, `ontology/magi-ontology.md` ✅, `theology.md` ✅, `examples/code-review.md` ✅

---

## debates/ MAGI-definition files — 4 additional leak sites

These aren't ephemeral debate transcripts — they read like spec-level architecture docs:

| File | Lines | Leaked Names |
|------|-------|-------------|
| `debates/.../MAGI-CONSTRAINTS.md` | 10, 13, 63 | `mimo-v2.5-pro`, `mimo`, `DeepSeek` |
| `debates/.../MAGI-DEFINITION.md` | 28 | `DeepSeek`, `mimo` |
| `debates/.../MAGI-ECOSYSTEM.md` | 19, 21, 70, 113, 117 | `DeepSeek`, `mimo` |
| `debates/.../MAGI-INVOCATION.md` | 87, 88, 91, 96, 101, 103 | `mimo`, `mimo-v2.5-pro`, `DeepSeek` |

That's **7 total files** with leaks, not 1. The debates/ ones are the sneaky ones — they're dated working docs that look informal but contain architectural constraints and definitions that someone would copy-paste into a clean spec.

**No leaks found** for `Claude`, `GPT`, `Gemini`, `Llama`, `Qwen`, `Mistral`, or other major brand names — the leaks are all from the original MAGI reference implementation (grok/kimi/mimo/DeepSeek).
