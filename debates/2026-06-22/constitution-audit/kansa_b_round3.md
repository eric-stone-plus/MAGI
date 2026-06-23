# KANSA B · R3 Dual-Audit — Constitution Fix Prioritization

**Auditor**: KANSA B (protocol / strategy lane — rx persona)  
**Date**: 2026-06-22  
**Scope**: SOUL.md · USER.md · MEMORY.md · POSTMORTEM.md  
**Inputs**: R1 reports (Gold, Fr, Myrrh, cc, omp, hm, cw), R2 cross-exam (hm, rx), `r1_context.md`, `r2_brief.md`  
**Question**: What is the **minimal safe fix set**? What **must** be fixed now vs can wait?

---

## R3 Verdict

**FAIL → CONDITIONAL PASS after 4-patch minimum.**

The constitution is **not safe to trust** until four operational contradictions are resolved. Everything else is hygiene — important, but not blocking the next QUINTE or file edit.

R1 consensus: all parties FAIL. R2 (hm + rx) validated the two Gold blockers and the KANSA fallback mismatch. This R3 ruling **narrows** the remediation to the smallest edit surface that restores a single coherent dispatch graph.

---

## Minimal Safe Fix Set (4 patches)

These four edits are **sufficient** to unblock constitutional trust. No file moves, no dedup pass, no POSTMORTEM refresh required for safety.

### Patch 1 — MAGI quorum (BLOCKER)

**Problem**: SOUL permits solo doctor; MEMORY and MAGI specs require all three.

| Source | Line | Text |
|--------|------|------|
| SOUL | L33 | `MAGI (Gold/Fr/Myrrh) 至少一人必须已就位` |
| SOUL | L83 | `MAGI (Gold/Fr/Myrrh) 必须至少一人已在场` |
| MEMORY | L31 | `MAGI = grok+kimi+mimo 全发缺一不可` |
| SOUL | L46 | `二进制收敛门(≥2/3)` — logically requires all 3 to run |

**Root cause**: L33/L83 are drafting residue from pre–MAGI-in-R1 era. MEMORY and specs v3.4 state the current rule.

**Minimal fix** (SOUL only — 2 lines):

```
L33: 至少一人 → 全发缺一不可（Gold/Fr/Myrrh 三模型均须派遣）
L83: 必须至少一人已在场 → 三模型全发缺一不可，须完成审查后方可修改
```

MEMORY L31 is already correct. Do not weaken it.

**Risk if unfixed**: Agent following SOUL dispatches Gold-only before file edits → protocol violation per MEMORY and MAGI convergence gate. This directly caused the 2026-06-20 iron-law incidents.

---

### Patch 2 — Thermal gate vs no-light-QUINTE (BLOCKER)

**Problem**: SOUL contradicts itself — absolutism at L93–95 vs Netsumon reduced R1 at L123–126.

| Source | Line | Conflict |
|--------|------|----------|
| SOUL | L95 | `无"轻量 QUINTE"、无"快速 QUINTE"、无"简化 QUINTE"` |
| SOUL | L123–126 | Phase 1: `R1: hm + MAGI Gold 仅` … `轻量 MAGI vote` |

**Root cause**: Netsumon gate added 2026-06-21; L93–95 absolutism not updated with scoped exception.

**Minimal fix** (SOUL only — 1 line append + 1 cross-ref):

```
L95: append — （**熱門 Netsumon Phase 1 除外** — 见 L112–128）
L93: prepend one clause — 默认全量；熱門分流时按 Netsumon Phase 0/1 执行。
```

Do **not** delete Netsumon. Thermal gate is operationally correct on Intel i9 MBP. Delete the exception and you get heat-induced session death.

**Risk if unfixed**: Agent either (a) refuses life-saving thermal kill path and runs full QUINTE into throttling, or (b) runs reduced R1 and self-reports protocol violation against L95.

---

### Patch 3 — KANSA B fallback matrix (BLOCKER)

**Problem**: MEMORY shorthand contradicts SOUL authoritative matrix on all three agent-fail paths.

| Failure | SOUL L150–156 | MEMORY L29 | Match |
|---------|---------------|------------|-------|
| cc | → MAGI **Gold** | → **Myrrh** | **NO** |
| cw | → MAGI **Myrrh** → Fr | → **Fr** | **NO** (order) |
| omp | → MAGI **Myrrh** | → **Gold** | **NO** |

**Root cause**: MEMORY L29 is stale compression of pre-2026-06-21 matrix. SOUL matrix is dated, structured, auditable.

**Minimal fix** (MEMORY only — 1 line replace):

```
L29 OLD: agent fail→MAGI sub(cc→Myrrh/cw→Fr/omp→Gold)
L29 NEW: agent fail→见 SOUL KANSA B fallback matrix (L150–156); DEGRADED废止
```

Also trim L31 duplicate `agent fail→Myrrh fallback` — it reintroduces the wrong default. Replace with `→见 SOUL L148–156`.

**Risk if unfixed**: Timeout on cc R3 → wrong MAGI model (Myrrh instead of Gold) → contract/legal review by wrong specialist.

---

### Patch 4 — Version pins (HIGH → bundle with above)

**Problem**: SOUL carries stale inline versions; USER and specs say v3.4.

| Entity | SOUL | USER / specs |
|--------|------|--------------|
| QUINTE | L44 `v3.3`, L79/L85 `v3.3+` | L1 `v3.4`, specs/PROTOCOL.md `v3.4` |
| MAGI | L46 `v3.0` | specs/PROTOCOL.md `v3.4` |

MEMORY L33: `四repo specs是版本号唯一权威源` — SOUL inline pins violate this meta-rule.

**Minimal fix** (SOUL only — 4 substitutions):

```
L44:  v3.3 → v3.4
L46:  v3.0 → v3.4
L79:  v3.3+ → v3.4+
L85:  v3.3+ → v3.4+
```

Optional hardening (not required for safety): add `版本以 specs/PROTOCOL.md 为准` beside each pin, or remove inline versions entirely.

**Risk if unfixed**: Lower than Patches 1–3 — agents already load USER v3.4 and live specs. Stale SOUL pins cause **documentation distrust**, not wrong dispatch. Still cheap to fix; include in the same commit.

---

## Fix Now vs Can Wait

### Fix now (before next constitution edit or QUINTE)

| # | Item | Severity | Files | Lines | Why now |
|---|------|----------|-------|-------|---------|
| 1 | MAGI quorum | **BLOCKER** | SOUL | L33, L83 | Wrong dispatch graph — solo doctor vs all-three |
| 2 | Thermal exception clause | **BLOCKER** | SOUL | L93, L95 | Self-contradicting supreme law |
| 3 | KANSA fallback unification | **BLOCKER** | MEMORY | L29, L31 | Wrong MAGI on agent timeout |
| 4 | QUINTE/MAGI version sync | **HIGH** | SOUL | L44, L46, L79, L85 | Trivial; completes trust restore |

**Estimated edit surface**: ~10 lines across 2 files. One commit. Re-QUINTE cross-audit recommended per SOUL L99 but not required for *safety* if patches are verbatim as above.

---

### Can wait (post-unblock hygiene)

| # | Item | Severity | Rationale |
|---|------|----------|-----------|
| 5 | SOUL L35 push-mandatory vs L142 push-consent | HIGH | Ambiguous on backup repo only; no wrong-model risk. Clarify `hermes-core-rules-mac-x86` exempt or change to `propose push`. |
| 6 | SOUL internal MAGI duplicate (L27–37 vs L83) | MEDIUM | Redundant, not contradictory once L83 quorum fixed. L83 → `详见 ⛔⛔ 鉄律`. |
| 7 | Push rules in 3 files | MEDIUM | MEMORY ⊆ SOUL. Dedup after blockers. |
| 8 | Mac hardware duplicate (USER L7 = MEMORY L37) | LOW | Delete MEMORY L37. |
| 9 | USER L1 kitchen-sink split | MEDIUM | Structural; no operational contradiction. |
| 10 | POSTMORTEM stale (frozen 2026-06-17) | MEDIUM | Missing 9 incidents; rules already codified in SOUL. Log when convenient. |
| 11 | delegate_task concurrency cap (MEMORY L17 `up to 3`) | MEDIUM | MEMORY adds cap SOUL lacks. Add to SOUL or strike from MEMORY. |
| 12 | cc `claude` vs `cc` CLI (MEMORY L33) | LOW | **Resolved in R2** — MiMo model (SOUL/USER) + `claude` CLI invocation (MEMORY) are compatible. Wording clarify only. |
| 13 | OCR block in SOUL (L172–198) | LOW | Wrong container; not a contradiction. Move to SKILL later. |
| 14 | Archive path three-tier confusion | LOW | Workflow stages, not conflict. |
| 15 | Force push scope (SOUL universal vs POSTMORTEM scoped) | LOW | SOUL stricter = safer. |
| 16 | SKILL.md absent from audit set | STRUCTURAL | Fifth constitution file; audit separately. |
| 17 | No conflict-resolution hierarchy declared | MEDIUM | Implicit: SOUL > MEMORY > USER for protocol. Codify in SOUL preamble when convenient. |

---

## R3 Merge with hm (KANSA A)

| Finding | hm R2 | rx R2 | KANSA B R3 |
|---------|-------|-------|------------|
| MAGI quorum | Fix SOUL → 全发 | Fix now | **Agree — Patch 1** |
| Thermal exception | Add Netsumon carve-out | Fix now | **Agree — Patch 2** |
| KANSA fallback | SOUL authoritative | Fix now | **Agree — Patch 3** |
| QUINTE v3.3→v3.4 | Fix SOUL | Can wait* | **Bundle — Patch 4** (*rx: escalate if v3.4 not backward-compatible; hm confirms specs say v3.4*) |
| MAGI v3.0→v3.4 | Fix SOUL | Fix now | **Bundle — Patch 4** |
| cc MiMo vs Claude | Non-conflict | — | **No patch needed** |

**Consensus**: 4/4 on blockers. rx originally rated QUINTE version as watch-item; KANSA B upgrades it to bundle-with-blockers because edits are zero-risk one-liners in the same file already being patched.

---

## What we explicitly do NOT fix in the minimal set

- **No dedup pass** — duplication does not cause wrong behavior once quorum and fallback are aligned.
- **No POSTMORTEM refresh** — incidents are archival; live rules live in SOUL.
- **No USER.md edits** — USER already says v3.4; it is not the source of the contradictions.
- **No MEMORY quorum change** — MEMORY is correct; SOUL is wrong.
- **No Netsumon deletion** — thermal gate stays; only the absolutism clause gets an exception pointer.

---

## Post-patch verification checklist

After applying Patches 1–4, grep-verify:

```bash
# Quorum — SOUL must not contain 至少一人 in MAGI context
grep -n '至少一人' SOUL.md  # expect: 0 hits in MAGI sections

# Thermal — L95 must reference Netsumon
grep -n '熱門\|Netsumon' SOUL.md | grep -E '9[35]|11[2-9]'

# Fallback — MEMORY must point to SOUL matrix
grep -n 'L150' MEMORY.md  # expect: L29 or L31 reference

# Versions — SOUL QUINTE/MAGI pins
grep -n 'v3\.[034]' SOUL.md  # expect: v3.4 only, no v3.3 or v3.0
```

---

## Bottom line

**Minimal safe fix set = 4 patches, ~10 lines, 2 files (SOUL + MEMORY).**

| Priority | Patches |
|----------|---------|
| **Now** | 1 MAGI quorum · 2 Thermal carve-out · 3 KANSA fallback pointer · 4 Version sync |
| **Later** | Dedup, USER split, POSTMORTEM catch-up, hierarchy declaration, SKILL audit |

Until Patches 1–3 land, any agent loading all four constitution files receives **contradictory dispatch orders**. That is not a formatting problem — it is an operational safety failure. Patch 4 is cheap insurance in the same commit.

**R3 disposition**: BLOCKED → release after Patches 1–4 applied and grep checklist passes.

---

*KANSA B · protocol lane · R3 dual-audit complete*