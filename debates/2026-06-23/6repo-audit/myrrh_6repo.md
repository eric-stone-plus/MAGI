# Myrrh 6-Repo Cross-Consistency Audit — 2026-06-23

> **Auditor**: Myrrh (mimo-v2.5-pro)  
> **Scope**: Mac profile (~/.hermes/profiles/technical/) · Mac mirror (~/Public/hermes-core-rules-mac-x86/) · Win (~/Public/hermes-core-rules-win/) · RASHOMON (~/Public/RASHOMON/) · QUINTE (~/Public/QUINTE/) · MAGI (~/Public/MAGI/)  
> **Method**: Read all 16 key files + targeted grep for 7 stale-term patterns  

---

## §0 · Gold and Fr Cross-Reference

### Gold (grok) — Status: EMPTY
`gold_6repo.md` produced 0 bytes. Gold agent either failed to dispatch or produced no output. **Cannot cross-reference — Gold gaps are total.**

### Fr (kimi) — Status: PARTIAL
`fr_6repo.md` contains 123 lines of internal agent reasoning (thinking trace). No structured report was produced. Fr identified several discrepancies in its reasoning trace but never compiled a final deliverable:
- Mac profile vs Mac mirror: SOUL.md divergent (mirror has "Agent patience" + "Before killing any agent" paragraphs absent from profile)
- Mac profile USER.md Chinese-compact (9 lines) vs mirror English-expanded (7 lines)
- Mac profile MEMORY.md L33 and L35 differ from mirror
- Win Gold=apiyi GPT-4o-mini consistent across Win files
- RASHOMON GATES.md has 5 gates (matches QUINTE)

### Gap Analysis
| Item | Gold | Fr | Myrrh |
|------|------|-----|-------|
| Mac profile ≠ mirror | — | Found (partial) | Confirmed (detailed below) |
| Win Gold mapping | — | Noted | Confirmed |
| Gate cardinality | — | Noted 5 | Confirmed 5 |
| Verification greps | — | Not executed | Executed (see §1) |
| Structured report | No | No | Yes (this file) |

**Gap**: Neither Gold nor Fr produced usable structured output. Myrrh audit is the sole complete deliverable.

---

## §1 · Verification Grep Results

### 1.1 `Gold=kimi` outside POSTMORTEM historical entries

| Repo | Matches | Location | Verdict |
|------|---------|----------|---------|
| Mac profile | 0 | — | CLEAN |
| Mac mirror | 0 | — | CLEAN |
| Win | 0 (active) | POSTMORTEM #13 has historical "Win Gold=kimi→apiyi GPT-4o-mini" — acceptable as fix history | CLEAN |
| RASHOMON | 0 | — | CLEAN |
| QUINTE | 0 | — | CLEAN |
| MAGI | 0 (active) | audit/ files have historical refs only | CLEAN |

**Verdict**: CLEAN. No stale Gold=kimi in active constitutional files.

### 1.2 `grok unreachable` outside debate archives

| Repo | Matches | Verdict |
|------|---------|---------|
| All six repos | 0 | CLEAN |

**Verdict**: CLEAN. No occurrences found.

### 1.3 `sidecard` anywhere

| Repo | Matches | Verdict |
|------|---------|---------|
| All six repos | 0 | CLEAN |

**Verdict**: CLEAN. The typo "sidecard" has been fully corrected to "sidecar" across all repos. (Win POSTMORTEM #13 records this fix.)

### 1.4 `Four Gate` in QUINTE/RASHOMON specs

| Repo | Matches | Verdict |
|------|---------|---------|
| QUINTE | 0 | CLEAN |
| RASHOMON | 0 | CLEAN |

**Verdict**: CLEAN. All references correctly use "Five Gates" or "五つの門".

### 1.5 `/tmp/quinte-audit` in QUINTE/MAGI specs

| Repo | Matches | Location | Verdict |
|------|---------|----------|---------|
| QUINTE specs | 0 | — | CLEAN |
| MAGI specs | 0 | — | CLEAN |

**Constitution files (outside specs)**:
| File | Line | Text | Verdict |
|------|------|------|---------|
| Mac profile SOUL.md | L53 | "Session isolation — Each QUINTE uses `/tmp/quinte-audit/<topic-slug>/`" | **STALE** |
| Mac mirror SOUL.md | L53 | Same | **STALE** |
| Win SOUL.md | L53 | Same (Win path variant) | **STALE** |

**Note**: MEMORY.md (all three repos) correctly specifies `~/Public/QUINTE/debates/YYYY-MM-DD/<topic>/` as the archive path. The `/tmp/quinte-audit` path in SOUL.md L53 is a pre-fix residual from POSTMORTEM #1 (Win) incident. SOUL.md Accountability section was never updated after the archive path migration.

**Verdict**: **3 STALE references** in SOUL.md L53 (Mac profile, Mac mirror, Win). Specs are clean.

### 1.6 `Tesseract` outside ocr-and-documents/Deprecated/historical references

| Repo | File | Line | Context | Verdict |
|------|------|------|---------|---------|
| Mac profile | POSTMORTEM #6 | L53-59 | Historical OCR strategy | Historical ✓ |
| Mac profile | POSTMORTEM #12 | L108-116 | Tesseract→PaddleOCR migration | Historical ✓ |
| Mac mirror | POSTMORTEM #6, #12 | Same | Same | Historical ✓ |
| Win | USER.md L7 | "OCR: PaddleOCR (Chinese/mixed), Tesseract (English fallback)" | **ACTIVE — Win-only policy** |
| Win | SOUL.md L58 | "OCR: PaddleOCR 2.10.0/PP-OCRv4 (primary)" | ACTIVE — primary spec |
| Win | POSTMORTEM #12 | L242-250 | Win Tesseract retention rationale | Historical ✓ |
| RASHOMON | 0 | — | CLEAN |
| QUINTE | 0 | — | CLEAN |
| MAGI | audit/ directory | 94+ matches | Historical debate logs |

**Analysis**: Win USER.md L7 lists Tesseract as English fallback. This is **intentional** per Win POSTMORTEM #12 — PaddleOCR 3.x unavailable on Win x86_64 without GPU, Tesseract retained as English-only fallback. Mac removed Tesseract entirely (POSTMORTEM #12). This is a **platform divergence**, not a stale reference.

**Verdict**: CLEAN with caveat. Win Tesseract English fallback is intentional platform policy, not drift. All other Tesseract references are historical.

### 1.7 `grok build` in dispatch commands (not annotations)

| Repo | File | Line | Context | Verdict |
|------|------|------|---------|---------|
| Mac profile | MEMORY.md L35 | "MAGI:Gold(grok build)+Fr(kimi)+Myrrh(mimo API)" | **Annotation** — model mapping note |
| Mac profile | MEMORY.md L23 | "grok最强(工业,默认grok build,包年无限)" | **Annotation** — economic note |
| Mac mirror | MEMORY.md L35, L23 | Same | Annotation |
| Mac mirror | POSTMORTEM #7 | "grok-build/K2.7 模式匹配遗漏" | Historical |
| Win | 0 | — | Win uses apiyi, no grok references |
| RASHOMON | 0 | — | CLEAN |
| QUINTE | 0 | — | CLEAN |
| MAGI | 0 | — | CLEAN |

**Analysis**: "grok build" appears in Mac MEMORY.md as model-mapping annotations, not as dispatch commands. The actual dispatch command in Mac SOUL.md is `grok -p --always-approve` (headless mode). No stale `grok build` in dispatch command positions.

**Verdict**: CLEAN. All "grok build" references are annotations/context, not dispatch commands.

---

## §2 · Structural Consistency (from file reads)

### 2.1 Mac profile vs Mac mirror

**SOUL.md**: Mirror is 56 lines (has "Agent patience" L40 + "Before killing any agent" zombie-check L48). Profile is 55 lines (missing both). **DIVERGENT.**

**USER.md**: Profile is 9 lines (Chinese-compact, has L9 "2026-06-23明确：不要画架构图"). Mirror is 7 lines (English-expanded, no L9). **DIVERGENT.**

**MEMORY.md**: Profile L33 and L35 differ from mirror (mirror has expanded audit-directory rules and Mac hardware line). **DIVERGENT.**

**POSTMORTEM.md**: Both 138 lines, 13 entries. Content identical. **SYNCED.**

### 2.2 Gate Cardinality

| Source | Gate Count | Names |
|--------|-----------|-------|
| Mac profile SOUL.md | 5 | Amamon/Kyōmon/Shōmon/Kan'nukimon/Kennōmon |
| Mac mirror SOUL.md | 5 | Same |
| Win SOUL.md | 5 | Amamon/Kyomon/Shomon/Kan'nukimon/Kennomon |
| RASHOMON GATES.md | 5 | Same (full definitions) |
| QUINTE PROTOCOL §6 | 5 | Same (table format) |

**Verdict**: Gate cardinality is CONSISTENT across all repos. Five gates everywhere.

### 2.3 Win Gold Mapping

| File | Mapping |
|------|---------|
| Win SOUL.md L13 | "Gold=apiyi GPT-4o-mini, Fr=kimi, Myrrh=mimo" |
| Win SOUL.md L22 | "Gold=apiyi, Fr=kimi, Myrrh=mimo" |
| Win USER.md L1 | "Gold=apiyi GPT-4o-mini, Fr=kimi, Myrrh=mimo" |
| Win MEMORY.md L37 | "apiyi(Gold)+kimi(Fr)+mimo(Myrrh)" |
| Win POSTMORTEM #13 | "Win Gold=kimi→apiyi GPT-4o-mini (company firewall, heterogeneous restored)" |

**Verdict**: CONSISTENT. Win Gold=apiyi GPT-4o-mini across all active files.

### 2.4 Mac Gold Mapping

| File | Mapping |
|------|---------|
| Mac profile SOUL.md L9 | "Gold (grok) + Fr (kimi) + Myrrh (mimo)" |
| Mac profile MEMORY.md L45 | "Gold→grok -p --always-approve" |
| Mac mirror SOUL.md L9 | Same |
| Mac mirror MEMORY.md L45 | Same |

**Verdict**: CONSISTENT. Mac Gold=grok across all active files.

### 2.5 Magi/QUINTE Spec Consistency

- QUINTE PROTOCOL v3.4 (2026-06-20) ↔ MAGI PROTOCOL v3.4 (2026-06-20): Version numbers match, feature sets align (6-tier error classification, JSON sidecar, evidence validation, agent→MAGI substitution).
- Cross-references: QUINTE §1.4 references MAGI spec; MAGI §2.1a references QUINTE spec. Both link correctly.

**Verdict**: SYNCED.

---

## §3 · Verdict Summary

### CLEAN items (6/7 greps)
- [x] Gold=kimi outside POSTMORTEM: CLEAN
- [x] grok unreachable: CLEAN
- [x] sidecard: CLEAN
- [x] Four Gate in specs: CLEAN
- [x] Tesseract outside historical: CLEAN (Win English fallback is intentional)
- [x] grok build in dispatch: CLEAN (annotations only)

### ISSUES FOUND (4)

| # | Severity | Issue | Location | Fix |
|---|----------|-------|----------|-----|
| 1 | HIGH | Mac profile ≠ Mac mirror (SOUL.md missing "Agent patience" + zombie-check) | Mac profile SOUL.md L40, L48 | Sync profile from mirror or vice versa |
| 2 | HIGH | Mac profile ≠ Mac mirror (USER.md Chinese vs English, L9 absent from mirror) | Mac profile USER.md L9 | Reconcile — decide canonical language/format |
| 3 | MEDIUM | `/tmp/quinte-audit` stale in SOUL.md L53 (all 3 repos) | Mac profile, Mac mirror, Win SOUL.md L53 | Replace with `~/Public/QUINTE/debates/YYYY-MM-DD/<topic>/` |
| 4 | LOW | Mac profile MEMORY.md L33/L35 differ from mirror | Mac profile MEMORY.md | Sync or annotate divergence |

### Final Verdict: **NOT CLEAN** — 1 HIGH + 1 HIGH + 1 MEDIUM + 1 LOW

The ecosystem is structurally sound (gate cardinality, Gold mappings, spec versions all consistent). The remaining issues are Mac profile ↔ mirror synchronization failures and one stale `/tmp` path in SOUL.md Accountability section.

---

## §4 · Agent Output Quality

| Agent | Output | Quality |
|-------|--------|---------|
| Gold (grok) | 0 bytes — EMPTY | FAILED (dispatch failure or no output) |
| Fr (kimi) | 123 lines thinking trace — no structured report | PARTIAL (reasoning visible, deliverable absent) |
| Myrrh (mimo) | This report | COMPLETE |

**Assessment**: MAGI convergence gate cannot operate with 1/3 agents producing output. This audit is Myrrh-solo. Gold dispatch failure should be investigated (possible: grok session timeout, auth issue, or output redirect failure).

---

*Myrrh 6-Repo Audit — 2026-06-23 · sine ira et studio*
