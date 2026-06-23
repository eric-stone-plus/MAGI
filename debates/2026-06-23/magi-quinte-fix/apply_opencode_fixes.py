#!/usr/bin/env python3
"""Apply the ten opencode-review fixes to QUINTE/MAGI specs."""
from pathlib import Path

QUINTE = Path('/Users/ericstone/Public/QUINTE')
MAGI = Path('/Users/ericstone/Public/MAGI')

# ---------------------------------------------------------------------------
# QUINTE/specs/PROTOCOL.md (from current HEAD)
# ---------------------------------------------------------------------------
proto = QUINTE / 'specs' / 'PROTOCOL.md'
text = proto.read_text()

# 1/5 Convergence gate: mechanical wording, not "adjudicate"
text = text.replace(
    '**hm separation from MAGI convergence during R1**: hm retains veto over Phase outputs but does NOT adjudicate MAGI\'s internal convergence gate during R1 Mode B. MAGI delegates self-converge (≥2/3 gate).',
    '**hm separation from MAGI convergence during R1**: hm retains veto over Phase outputs but applies mechanical binary gate only to MAGI\'s internal convergence during R1 Mode B. MAGI delegates self-converge (≥2/3 gate).'
)

# 5/5 Mode A/B + anytime deployment
text = text.replace(
    '### 1.4 MAGI v3.4: Dual-Mode Operation\n\nMAGI operates in two mutually exclusive modes:\n\n**Mode A — Pre-Verification (standalone)**: For questions where hm\'s confidence is insufficient, MAGI provides rapid pre-verification before escalating to full QUINTE debate:\n\n```\nhm uncertain → MAGI (3 heterogeneous models in parallel)\n                 ├─ ≥2/3 converge → answer with confidence annotation\n                 └─ diverge → escalate to QUINTE\n```\n\n**Mode B — R1 Participant (embedded)**: During QUINTE execution, MAGI enters R1 as one collective element with internal convergence gate ACTIVE. Three heterogeneous models converge internally (≥2/3) → single converged output, single vote. MAGI does not participate in R2; its R1 output is cross-examined by rx. Mode A and Mode B are mutually exclusive per session.\n\nMAGI uses three heterogeneous base models in parallel. It is hm-triggered, not user-triggered. See [MAGI v3.4 spec](https://github.com/eric-stone-plus/MAGI/blob/main/specs/PROTOCOL.md).',
    '### 1.4 MAGI v3.4: Deployment Modes\n\nMAGI operates in two primary modes (Mode A standalone, Mode B embedded), plus an anytime independent deployment (MAGI v3.1+). Mode A and Mode B are mutually exclusive in the same session; either, or the independent anytime deployment, may be invoked at any time.\n\n**Mode A — Pre-Verification (standalone)**: For questions where hm\'s self-assessment is insufficient, MAGI provides rapid pre-verification before escalating to full QUINTE debate:\n\n```\nhm uncertain → MAGI (3 heterogeneous models in parallel)\n                 ├─ ≥2/3 converge → answer with [MAGI N/3] convergence annotation\n                 └─ diverge → escalate to QUINTE\n```\n\n**Mode B — R1 Participant (embedded)**: During QUINTE execution, MAGI enters R1 as one collective element with internal convergence gate ACTIVE. Three heterogeneous models converge internally (≥2/3) → single converged output, single vote. MAGI does not participate in R2; its R1 output is cross-examined by rx.\n\n**Anytime / Independent (v3.1+)**: MAGI doctors may be dispatched independently or collectively at any QUINTE phase, or outside it, for on-demand analysis, agent fallback, filesystem exploration, or second opinion.\n\nMAGI uses three heterogeneous base models in parallel. It is hm-triggered, not user-triggered. See [MAGI v3.4 spec](../../MAGI/specs/PROTOCOL.md).'
)

# 4/5 MAGI timeout exemption
text = text.replace(
    '**Discipline**: R1 all launch in parallel. Timeout 120s → kill + shrink prompt + retry. Three consecutive failures → escalate. **Never skip an agent**.',
    '**Discipline**: R1 per-agent timeout 120s (MAGI excepted — see §4.5 convergence-gate budget 180s) → kill + shrink prompt + retry. Three consecutive failures → escalate. **Never skip an agent**.'
)

# 2/5 R2 = 5 agents, thresholds 3/5 / 2/5 / 1/5
text = text.replace(
    'For each disputed claim, 3 refutation agents cross-review:\n- **Cross-model requirement**: at least 1 refuter uses a different provider/model\n- ≥2/3 refute → claim discarded\n- 1/3 refute → claim retained, marked "contested"\n- 0/3 refute → claim confirmed',
    'For each disputed claim, all five R2 agents cross-review:\n- **Cross-model requirement**: at least 2/5 refuters use a different provider/model\n- ≥3/5 refute → claim discarded\n- 2/5 refute → claim retained, marked "contested"\n- ≤1/5 refute → claim confirmed'
)

# 2/5 Invariant #4 floor
text = text.replace(
    '4. **Cross-model diversity in R2 (Invariant).** At least 1/3 R2 refuters MUST use a different provider/model.',
    '4. **Cross-model diversity in R2 (Invariant).** At least 2/5 R2 refuters MUST use a different provider/model.'
)

# 7/5 BANNIN downgrade — invariant
text = text.replace(
    '6. **Push gate.** Any push (code, config, docs) requires prior QUINTE (R1+R2+R3). No exceptions.',
    '6. **Push gate (target).** Any push (code, config, docs) should be preceded by prior QUINTE (R1+R2+R3). Enforcement pending BANNIN implementation; interim enforcement via KENGEN git hook. No "no exceptions" claim until BANNIN ships.'
)

# 7/5 BANNIN downgrade — Kennōmon gate table
text = text.replace(
    '| **憲門** Kennōmon | Architecture drift | `write_file`/`patch`/`terminal(commit)` on public repos | BANNIN-enforced pre-write check: QUINTE verdict trail required. Defined in HIGHBALL `specs/kennomon-architecture-gate.md` (ratified 2026-06-19) |',
    '| **憲門** Kennōmon | Architecture drift | `write_file`/`patch`/`terminal(commit)` on public repos | BANNIN (specification-only) pre-write check: QUINTE verdict trail required. Interim enforcement via KENGEN git hook until BANNIN ships. Defined in HIGHBALL `specs/kennomon-architecture-gate.md` (ratified 2026-06-19) |'
)
proto.write_text(text)

# ---------------------------------------------------------------------------
# QUINTE/README.md
# ---------------------------------------------------------------------------
readme = QUINTE / 'README.md'
text = readme.read_text()
text = text.replace(
    'Single-model AI hits a confidence ceiling.',
    'Single-model AI hits a reliability ceiling.'
)
text = text.replace(
    'See [RASHOMON](https://github.com/eric-stone-plus/RASHOMON) for the full design philosophy and [HIGHBALL](https://github.com/eric-stone-plus/HIGHBALL) for the constraint layer (KANSA KANSA verdict audit + KENGEN KENGEN authorization perimeter).',
    'See [RASHOMON](../RASHOMON) for the full design philosophy and [HIGHBALL](../HIGHBALL) for the constraint layer (KANSA KANSA verdict audit + KENGEN KENGEN authorization perimeter).'
)
text = text.replace(
    "Operations are gated by [HIGHBALL](https://github.com/eric-stone-plus/HIGHBALL)'s KENGEN (KENGEN) authorization perimeter with BANNIN (BANNIN) as the session-level guard. No irreversible external write proceeds without explicit user authorization.",
    "Operations are gated by [HIGHBALL](../HIGHBALL)'s KENGEN (KENGEN) authorization perimeter with BANNIN (BANNIN, specification-only) as the session-level guard. Interim enforcement: KENGEN git hook checks for a QUINTE verdict trail before pushes until BANNIN ships. No irreversible external write proceeds without explicit user authorization."
)
text = text.replace(
    'MAGI continues its standalone pre-verification role (Mode A): when hm is uncertain, three heterogeneous models converge or diverge before escalating to full QUINTE debate. Mode A and Mode B are mutually exclusive. See [MAGI v3.4 spec](https://github.com/eric-stone-plus/MAGI/blob/main/specs/PROTOCOL.md).',
    'MAGI continues its standalone pre-verification role (Mode A): when hm is uncertain, three heterogeneous models converge or diverge before escalating to full QUINTE debate. Mode A and Mode B are mutually exclusive in the same session; either, or the independent anytime deployment (MAGI v3.1+), may be invoked at any time. See [MAGI v3.4 spec](../MAGI/specs/PROTOCOL.md).'
)
text = text.replace(
    'It is not implementation-agnostic — it depends on Hermes-specific primitives (delegate_task, memory, skill persistence, cron, session_search) to enforce its invariants.',
    'It is not implementation-agnostic — it depends on Hermes-specific primitives (terminal for heterogeneous agent dispatch, delegate_task for internal sub-agents, memory, skill persistence, cron, session_search) to enforce its invariants.'
)
readme.write_text(text)

# ---------------------------------------------------------------------------
# MAGI/specs/PROTOCOL.md
# ---------------------------------------------------------------------------
mproto = MAGI / 'specs' / 'PROTOCOL.md'
text = mproto.read_text()
text = text.replace(
    '### 2.1a Dual-Mode Operation (v3.4+)\n\nMAGI operates in two mutually exclusive modes:\n\n- **Mode A — Standalone Pre-Verification**: hm uncertain → MAGI → ≥2/3 converge (answer) or diverge (escalate to QUINTE).\n- **Mode B — QUINTE R1 Participant**: During QUINTE v3.4+ execution, MAGI enters R1 as one collective element. Internal convergence gate is ACTIVE — three delegates converge (≥2/3) into one output with one vote. Delegates do not participate in R2. Mode A and Mode B cannot both be active in the same session. See [QUINTE v3.4 spec](https://github.com/eric-stone-plus/QUINTE/blob/master/specs/PROTOCOL.md).',
    '### 2.1a Deployment Modes (v3.4+)\n\nMAGI operates in two primary mutually exclusive modes, plus an anytime independent deployment (MAGI v3.1+):\n\n- **Mode A — Standalone Pre-Verification**: hm uncertain → MAGI → ≥2/3 converge (answer) or diverge (escalate to QUINTE).\n- **Mode B — QUINTE R1 Participant**: During QUINTE v3.4+ execution, MAGI enters R1 as one collective element. Internal convergence gate is ACTIVE — three delegates converge (≥2/3) into one output with one vote. Delegates do not participate in R2. Mode A and Mode B cannot both be active in the same session.\n- **Anytime / Independent (v3.1+)**: MAGI doctors may be dispatched independently or collectively at any QUINTE phase, or outside it, for on-demand analysis, agent fallback, filesystem exploration, or second opinion. Mode A and Mode B remain but are non-exhaustive.\n\nSee [QUINTE v3.4 spec](../../QUINTE/specs/PROTOCOL.md).'
)
text = text.replace(
    '### 2.4 Convergence Gate\n\nhm reads all three outputs. Binary decision:\n\n| Condition | Outcome | Action |\n|-----------|---------|--------|\n| ≥2/3 agree | **Converge** | hm adopts answer. Annotates: `[MAGI 2/3]` or `[MAGI 3/3]`. |\n| ≤1/3 agree | **Diverge** | Escalate to QUINTE. Disagreement pattern recorded for KOZO. |\n\nNo weighted voting. No confidence score. Binary gate.',
    '### 2.4 Convergence Gate\n\nhm applies the mechanical binary gate to the three delegate outputs:\n\n| Condition | Outcome | Action |\n|-----------|---------|--------|\n| ≥2/3 agree | **Converge** | Answer is mechanically adopted. Annotates: `[MAGI 2/3]` or `[MAGI 3/3]`. |\n| ≤1/3 agree | **Diverge** | Escalate to QUINTE. Disagreement pattern recorded for KOZO (構造, HIGHBALL attention-quality measurement layer; see [HIGHBALL spec](../../HIGHBALL/README.md#kozo--attention-quality--cross-detection-sensitivity)). |\n\nNo weighted voting. No confidence score. Binary gate.'
)
mproto.write_text(text)

# ---------------------------------------------------------------------------
# QUINTE/specs/theoretical-foundation.md
# ---------------------------------------------------------------------------
tf = QUINTE / 'specs' / 'theoretical-foundation.md'
text = tf.read_text()
text = text.replace(
    '> **Version**: 1.0 (2026-06-18) — Initial, post-QUINTE audit',
    '> **Version**: v3.4 (2026-06-20) — Synced with QUINTE v3.4'
)
text = text.replace(
    'mandates that at least 1/3 R2 refuters use a different provider/model when available.',
    'mandates that at least 2/5 R2 refuters use a different provider/model when available.'
)
text = text.replace(
    '---\n\n## 5. Current Limitations\n\n1. **No QUINTE-specific empirical validation.**',
    '---\n\n## 5. v3.4 Feature Additions\n\nv3.4 introduced several mechanisms that extend the theoretical claims above. Their theoretical status is summarized here.\n\n### JSON sidecar + Evidence Validation Gate\nEach R1 agent now appends a structured JSON sidecar with `verdict`, `reasoning_chain`, and `evidence_citations`. Before Phase 2 weighs claims, hm verifies that every citation resolves to a real `file:line` or reproducible command output. Unresolved citations are tagged `[CITATION_UNVERIFIED]` and down-weighted 0.5×. This closes a trust boundary: self-reported metadata cannot inflate claim weight without external verification.\n\n### R2 Anonymous Review + Mind-Change Tracking\nR2 agents are presented as Participant A/B/C/D/E to suppress brand bias. After R3, KANSA reveals the pseudonym mapping. R2 prompts also embed each agent\'s own R1 summary; agents must flag any position change with cause and cited evidence. Mind-changed views are weighted higher on the theory that persuasion by cross-examination is a signal of evidence strength.\n\n### 6-Tier Error Classification + Agent→MAGI Substitution\nAll dispatch wrappers report structured errors (`auth`, `rate_limit`, `timeout`, `interrupted_recoverable`, `deprecated`, `unknown`) with tier-specific recovery (backoff, shrink, resume, skip). Failed core agents are substituted by MAGI doctors rather than blocking the pipeline. This cascades from lightweight recovery to heavier debate only when necessary.\n\n### Cross-Repo Consistency Check\nBefore edits to `scripts/`, `specs/`, or dispatch templates, hm greps across the root repo and the `website/` git sub-repo to detect stale duplicates. This prevents silent divergence between canonical and archived versions.\n\n**Theoretical status**: These additions are design hypotheses consistent with the pillars above, but they have not been empirically validated in controlled QUINTE-specific experiments.\n\n---\n\n## 6. Current Limitations\n\n1. **No QUINTE-specific empirical validation.**'
)
text = text.replace(
    '## 5. Minimum Evidence Requirements',
    '## 7. Minimum Evidence Requirements'
)
text = text.replace(
    '*Version 1.0 — 2026-06-18 — 5/5 QUINTE consensus (cc+cw+omp+rx+hm)*',
    '*Version v3.4 — 2026-06-20 — 5/5 QUINTE consensus (cc+cw+omp+rx+hm)*'
)
tf.write_text(text)

print('opencode fixes applied.')
