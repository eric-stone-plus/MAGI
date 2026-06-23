I'll read SOUL.md and SKILL.md and compare them against the v3.4 feature list you gave.
Searching both files for each v3.4 feature by name.
## v3.4 feature audit: SOUL.md + SKILL.md

| # | Feature | SOUL.md | SKILL.md | Status |
|---|---------|---------|----------|--------|
| 1 | JSON sidecar (verdict/confidence/reasoning_chain/evidence_citations) | ❌ | ❌ | **Missing** — only unrelated OCR `--sidecar` and cc `stream-json` mention |
| 2 | Evidence Validation Gate (Myrrh → file:line; fake → 0.5×) | ❌ | ❌ | **Missing** — Myrrh labeled "verification" in dispatch comment only |
| 3 | Anonymous R2 (Participant A/B/C/D/E) | ❌ | ✅ L45 | **SKILL only** |
| 4 | Mind-change tracking (`CHANGED: [old] BECAUSE [evidence]`) | ❌ | ⚠️ L45 | **Partial** — concept named, format not specified |
| 5 | 6-tier errors (auth \| rate_limit \| timeout \| interrupted_recoverable \| deprecated \| unknown) | ❌ | ❌ | **Missing** |
| 6 | rx quality gate (<1500 chars + `<tool_call>` → MAGI substitute) | ❌ | ⚠️ L141–142 | **Partial** — rx `tool_calls` symptom + Gold substitute, no char threshold or formal gate |
| 7 | Agent→MAGI Substitution Table (equal weight) | ⚠️ L136–144 | ⚠️ L35–36, L135–136 | **Partial** — generic "dispatch MAGI substitute" + KANSA B fallback matrix (R3, not R1/R2 equal-weight table) |
| 8 | Grok interrupt recovery (exit 143 → `--resume`) | ❌ | ❌ | **Missing** |
| 9 | `magi_dispatch.py` v1 | ❌ | ❌ (anti-script L57) | **Missing** — SKILL explicitly forbids script wrappers |
| 10 | 憲門 Kennōmon (no solo README/specs/ontology edits) | ⚠️ L67 | ❌ | **Partial** — "Architecture decisions mandate QUINTE" without 憲門 name or file-scope |
| 11 | Romaji-only body convention | ❌ | ❌ | **Missing** — SOUL bans Simplified Chinese + loanwords, not romaji-only bodies |

**Already well-covered (related but not on your list):** MAGI iron law, process independence, thermal gate, DEGRADED abolition, KANSA matrix, firepower standard, rx run-mode limitation.

---

## What's actually in the files

**Fully present (1):** Anonymous R2 in SKILL.

**Partially present (4):** Mind-change tracking, rx/tool_calls handling, agent→MAGI substitution (no equal-weight table), architecture solo-edit rule (no 憲門).

**Absent (6):** JSON sidecar, Evidence Validation Gate, 6-tier errors, formal rx quality gate, Grok `--resume`, romaji-only. `magi_dispatch.py` is absent and conflicts with current process-separation rule.

---

## Minimum to add

Prioritized by constitutional vs operational impact:

### BLOCKER — SOUL.md (~8 lines)

Add a **憲門 Kennōmon** gate (named, scoped):

```markdown
## 憲門 Kennōmon · Architecture gate (mandatory)
hm must not solo-modify core architecture files in any public repo:
README*, specs/**, ontology/**. Full QUINTE (R1+R2+R3) required before patch.
Violations = protocol breach. See HIGHBALL specs/PROTOCOL.md.
```

SOUL L67 is close but not sufficient — it lacks the gate name, file list, and HIGHBALL linkage.

### HIGH — both files (~25 lines total)

**SOUL** — two one-liner gates after MAGI iron law or in 證門:
- MAGI outputs must append JSON sidecar (`verdict`, `confidence`, `reasoning_chain`, `evidence_citations`).
- Post-convergence: Myrrh validates citations; unresolvable → 0.5× weight.

**SKILL** — extend MAGI dispatch + workflow:
- Sidecar schema + example block after each MAGI output file.
- Myrrh prompt line: verify every `file:line` in sidecar `evidence_citations`.
- R2: require `CHANGED: [old] BECAUSE [evidence from Participant X]` (tighten L45).
- Agent→MAGI substitution table with **equal weight** (cc→Gold, cw→Fr, omp→Myrrh, rx→Gold, etc.) — distinct from SOUL's KANSA B matrix.

### MEDIUM — SKILL Pitfalls (~12 lines)

- **6-tier error taxonomy** with per-tier action (retry, shrink prompt, `--resume`, substitute, escalate).
- **rx quality gate**: if output `<1500` chars OR contains `<tool_call>` → dispatch MAGI substitute immediately (formalize what L141–142 hints at).

### LOW — defer unless you want full v3.4 parity

- Grok exit 143 → `grok --resume` (one Pitfalls bullet).
- Romaji-only body convention in SOUL Four-Repo section.
- **`magi_dispatch.py` v1** — reconcile with L57 "Never wrap CLI calls in scripts" first; either drop from v3.4 target or amend process-separation rule.

---

## Smallest closing set

If you want the **minimum diff that fixes real protocol holes**:

| File | Add |
|------|-----|
| **SOUL** | 憲門 gate + JSON sidecar requirement + Evidence Validation Gate |
| **SKILL** | Sidecar format in dispatch + Myrrh citation step + substitution table + `CHANGED:` format + 6-tier errors + rx quality gate |

That closes **9 of 11** gaps. Defer Grok `--resume`, romaji-only, and `magi_dispatch.py` unless you explicitly want full spec parity (and resolve the script-wrapper conflict for the last one).

**Verdict:** FAIL on v3.4 constitution alignment — 6 fully missing, 4 partial, 1 present only in SKILL. 憲門 is the highest-risk gap because SOUL still allows interpreting L67 as "run QUINTE on architecture" without blocking solo edits to `specs/` and `ontology/`.
