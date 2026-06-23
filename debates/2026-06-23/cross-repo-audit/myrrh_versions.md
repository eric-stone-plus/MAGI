[0m
> build · mimo-v2.5-pro
[0m
[0m$ [0mfor d in RASHOMON HIGHBALL QUINTE MAGI; do echo "=== $d ==="; git -C ~/Public/$d tag -l 2>&1; done
=== RASHOMON ===
v1.1.0
v1.2.0
=== HIGHBALL ===
=== QUINTE ===
v3.0.1
v3.1
=== MAGI ===
[0m
[0m$ [0mgrep -h 'version\|Version\|v3\.\|v1\.' ~/Public/QUINTE/specs/PROTOCOL.md ~/Public/MAGI/specs/PROTOCOL.md 2>/dev/null | head -10
# QUINTE Protocol Specification v3.4 · Hermes Agent
> **v3.4 (2026-06-20)**: MAGI ecosystem adoption — structured error classification, JSON sidecar with evidence validation, R2 pseudonyms + mind-change tracking, agent→MAGI substitution, Grok session recovery, cross-repo consistency. Synced with MAGI v3.4.
> **Scope**: QUINTE is a Hermes Agent protocol. It depends on Hermes-specific primitives (terminal for agent dispatch, memory+skill for cross-session invariant enforcement, cron for autonomous triggering, terminal for Phase 6 cross-match). delegate_task is explicitly forbidden for QUINTE/MAGI dispatch (breaks model heterogeneity). It improves factual completeness and oversight detection through redundant coverage, structured re-examination, and adversarial verification. Estimated improvement: ~20-50% over solo analysis (v3.4 baseline). It does not validate correctness of shared-model reasoning about novel situations where all agents share the same model's knowledge boundaries — cross-model diversity in R2 partially mitigates this.
v3.4 operates through a separation of powers: **Hermes coordinates execution** through terminal/background dispatch; **Claude Code, CodeWhale, omp, and MAGI participate** in debate rounds; **Hermes holds final arbiter authority** — the Tribune's *intercessio*, the power to block any phase.
**Agent Failure → MAGI Substitution (v3.4)**: Any R1/R2 agent producing 0 bytes triggers classified recovery per §4.8 — backoff/shrink/resume first, substitution only after retries are exhausted. Substitution table: cc→Myrrh, cw→Fr, omp→Gold, rx→any. Substitution output weighted equally.
**R2 Anonymous Review (v3.4)**: R2 agents are identified as "Participant A/B/C/D/E" — no agent names. Pseudonyms prevent brand-bias in cross-examination. R3 KANSA reveals the mapping for dual-consul verdict.
**R2 Mind-Change Tracking (v3.4)**: R2 prompt embeds agent's own R1 summary (≤300 chars). Agents MUST flag any position change caused by reviewing others' R1, using the format: "CHANGED: [old position] BECAUSE [evidence from agent X]". R3 weighs mind-changed views higher (persuasion = evidence strength).
### 1.4 MAGI v3.4: Dual-Mode Operation
MAGI uses three heterogeneous base models in parallel. It is hm-triggered, not user-triggered. See [MAGI v3.4 spec](https://github.com/eric-stone-plus/MAGI/blob/main/specs/PROTOCOL.md).
Four gates executed by hm in parallel (~5s). See §6 for gate definitions. Includes cross-repo consistency check (v3.4: website/ git sub-repo grep).
[0m
[0m$ [0mls ~/Public/RASHOMON/specs/PROTOCOL.md ~/Public/HIGHBALL/specs/PROTOCOL.md 2>&1
ls: /Users/ericstone/Public/HIGHBALL/specs/PROTOCOL.md: No such file or directory
ls: /Users/ericstone/Public/RASHOMON/specs/PROTOCOL.md: No such file or directory
[0m
[0m$ [0mgrep -h 'version\|Version' ~/Public/RASHOMON/README.md ~/Public/HIGHBALL/README.md 2>/dev/null | head -5
(no output)
[0m
[0m$ [0mgrep -ri 'version\|v1\.' ~/Public/RASHOMON/README.md ~/Public/RASHOMON/package.json ~/Public/RASHOMON/Cargo.toml ~/Public/RASHOMON/pyproject.toml 2>/dev/null | head -10
(no output)
[0m
[0m$ [0mgrep -ri 'version\|v1\.' ~/Public/HIGHBALL/README.md ~/Public/HIGHBALL/package.json ~/Public/HIGHBALL/Cargo.toml ~/Public/HIGHBALL/pyproject.toml 2>/dev/null | head -10
(no output)
[0m
[0m$ [0mgrep -ri 'version' ~/Public/MAGI/README.md 2>/dev/null | head -5
(no output)
[0m
[0m$ [0mls ~/Public/RASHOMON/README* ~/Public/HIGHBALL/README* 2>&1; echo "---"; head -20 ~/Public/RASHOMON/README.md 2>/dev/null; echo "==="; head -20 ~/Public/HIGHBALL/README.md 2>/dev/null
/Users/ericstone/Public/HIGHBALL/README.md
/Users/ericstone/Public/RASHOMON/README.md
---
# RASHOMON (羅生門)

> 芥川龍之介《藪の中》（1922）→ 黒澤明《羅生門》（1950）→ multi-perspective truth-seeking

**RASHOMON** is the philosophical foundation of the multi-agent debate ecosystem. It does not describe *how* agents debate — that is QUINTE's domain. It does not prescribe *which* agents debate — that is an operational concern. It asks the prior question: *why must perspectives confront each other, and what kind of truth emerges when they do?*

---

## The Rashomon Problem

Kurosawa's *Rashomon* (1950) presents four witnesses to the same event offering mutually contradictory testimonies. The woodcutter, the bandit, the wife, the samurai's ghost — each saw the event. Each account is internally coherent. The accounts cannot be reconciled.

Not because anyone is lying. Because each person sees only what their position allows them to see.

This is the exact problem facing any single-perspective system. One model, one training distribution, one set of RLHF alignments — one blind spot. The answer is not a better model. It is a *structure that forces perspectives to confront each other*.

---

## Cross-Detection: The Epistemological Core

===
# HIGHBALL (ハイボール)

> highball. The constraint layer for AI agent outputs — verdict audit, authorization perimeter, and attention quality measurement.

**HIGHBALL** is the third pillar of the QUINTE ecosystem. Where [RASHOMON](https://github.com/eric-stone-plus/RASHOMON) asks *why* multi-perspective truth-seeking is necessary and [QUINTE](https://github.com/eric-stone-plus/QUINTE) defines *how* to orchestrate cross-examination, HIGHBALL enforces three questions on every conclusion:

| Question | Component | Origin | Role |
|----------|-----------|--------|------|
| *Sound?* | **KANSA** | QUINTE Phase 6 / R3 | Independent second review of every verdict |
| *May I?* | **KENGEN** + **BANNIN** | HIGHBALL execution layer | Authorization perimeter — BANNIN session guard enforces silent block: no clarify, no negotiate |
| *Attentive? Effective?* | **KOZO** | HIGHBALL measurement layer | Attention compliance + cross-detection sensitivity |

## Architecture

```
RASHOMON (why) ──→ QUINTE+MAGI (how) ──→ conclusions
     │               │    │                  │
     │               │    └─ KANSA ─ R3 ─┤
     │               │                       │
     └── HIGHBALL ───┴─ KENGEN ─────────┤  (execution layer)
[0m
[0m$ [0mhead -5 ~/Public/MAGI/specs/PROTOCOL.md 2>/dev/null
# MAGI v3.4 — Protocol Specification · Hermes Agent

> **Lightweight heterogeneous pre-verification protocol. hm's self-doubt resolution layer.**
>
> **v3.4 (2026-06-20)**: Synced with QUINTE v3.4. MAGI ecosystem adoption complete: 6-tier error classification across all dispatch paths (magi_dispatch.py v1 unified wrapper for grok/kimi/mimo), Grok interrupt recovery (exit 143 → `--resume`/`grok export`), JSON sidecard with evidence validation gate (Myrrh), cross-repo consistency check (Fr/kimi), agent→MAGI substitution protocol. Three doctors dispatchable anytime — Mode A (pre-verification), Mode B (QUINTE R1 embedded), or independent.
[0m
Here's the verification result as a JSON sidecar:

```json
{
  "version_verification": {
    "timestamp": "2026-06-23T00:00:00Z",
    "repos": {
      "RASHOMON": {
        "git_tags": ["v1.1.0", "v1.2.0"],
        "latest_tag": "v1.2.0",
        "protocol_md": "NOT FOUND",
        "readme_version": "NONE (philosophical doc, no semver)"
      },
      "HIGHBALL": {
        "git_tags": [],
        "latest_tag": null,
        "protocol_md": "NOT FOUND",
        "readme_version": "NONE (no semver in README)"
      },
      "QUINTE": {
        "git_tags": ["v3.0.1", "v3.1"],
        "latest_tag": "v3.1",
        "protocol_md": {
          "file": "specs/PROTOCOL.md",
          "header_version": "v3.4",
          "dated": "2026-06-20"
        },
        "readme_version": null
      },
      "MAGI": {
        "git_tags": [],
        "latest_tag": null,
        "protocol_md": {
          "file": "specs/PROTOCOL.md",
          "header_version": "v3.4",
          "dated": "2026-06-20"
        },
        "readme_version": null
      }
    },
    "discrepancies": [
      "QUINTE: git tag v3.1 vs PROTOCOL.md v3.4 — protocol doc is ahead of latest tag",
      "MAGI: no git tags at all despite PROTOCOL.md claiming v3.4",
      "RASHOMON: no specs/PROTOCOL.md exists; version only from git tags (v1.2.0 latest)",
      "HIGHBALL: no git tags, no specs/PROTOCOL.md, no version markers anywhere"
    ]
  }
}
```

**Key findings:**
- **QUINTE**: Tag `v3.1` but PROTOCOL.md declares `v3.4` — doc ahead of tag by 3 minor versions
- **MAGI**: Zero tags despite `v3.4` in PROTOCOL.md
- **RASHOMON**: Tags `v1.1.0`/`v1.2.0` but no PROTOCOL.md or version in README
- **HIGHBALL**: No version markers anywhere
