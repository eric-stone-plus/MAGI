# 6-Repo Cross-Consistency Audit — 2026-06-23 (Gold)

**Scope**: 
1. ~/.hermes/profiles/technical/ (Mac live profile)
2. ~/Public/hermes-core-rules-mac-x86/ (Mac backup mirror)
3. ~/Public/hermes-core-rules-win/ (Win repo)
4. ~/Public/RASHOMON/ (esp. GATES.md)
5. ~/Public/QUINTE/specs/PROTOCOL.md
6. ~/Public/MAGI/specs/PROTOCOL.md

**Key facts verified**:
- Win Gold = apiyi GPT-4o-mini (firewall blocks grok)
- All constitutions use 5 gates: Amamon, Kyōmon/Kyomon, Shōmon/Shomon, Kan'nukimon, Kennōmon/Kennomon
- QUINTE + MAGI both v3.4
- PaddleOCR 2.10.0/PP-OCRv4 primary OCR everywhere (with Win Tesseract English fallback)

**Output**: Inconsistencies listed with file:line (or section). All non-POSTMORTEM references to legacy "grok-unreachable"/"Gold=kimi" flagged. "sidecard" checked. Mac profile vs mirror diffed for identity.

---

## 1. Mac Live Profile vs Mac Mirror — NOT IDENTICAL (CRITICAL)

Core constitutional files diverge. Mirror appears more current in places; live profile lags or has slimmed/older variants.

### 1.1 SOUL.md
- [~/.hermes/profiles/technical/SOUL.md:3](/Users/ericstone/.hermes/profiles/technical/SOUL.md): "Constitutional files: SOUL · USER · MEMORY · SKILL · POSTMORTEM."
- [/Users/ericstone/Public/hermes-core-rules-mac-x86/SOUL.md:3](/Users/ericstone/Public/hermes-core-rules-mac-x86/SOUL.md): "Constitutional files: SOUL.md · memories/USER.md · memories/MEMORY.md · skills/multi-agent-debate/SKILL.md · memories/POSTMORTEM.md."
- [live:29](/Users/ericstone/.hermes/profiles/technical/SOUL.md) vs [mirror:30](/Users/ericstone/Public/hermes-core-rules-mac-x86/SOUL.md): Shōmon text — mirror adds "If agent drift is caused by unclear prompt → fix prompt and re-dispatch; do NOT use MAGI as substitute for a bad prompt."
- [live missing entire section](/Users/ericstone/.hermes/profiles/technical/SOUL.md) vs [mirror:40-41](/Users/ericstone/Public/hermes-core-rules-mac-x86/SOUL.md): "**Agent patience** — Long think time..." (600s hard cap details).
- [live:46](/Users/ericstone/.hermes/profiles/technical/SOUL.md) vs [mirror:48](/Users/ericstone/Public/hermes-core-rules-mac-x86/SOUL.md): Netsumon — mirror adds zombie verification: "Before killing any agent: verify uptime >600s AND (file output empty/nonexistent OR file mtime >600s ago)."
- Additional wording diffs in KENGEN, accountability, Iron Law preamble.

### 1.2 memories/MEMORY.md
Multiple § differences:
- [live ~33](/Users/ericstone/.hermes/profiles/technical/memories/MEMORY.md) vs [mirror](/Users/ericstone/Public/hermes-core-rules-mac-x86/memories/MEMORY.md): "审计目录勿早清:等通知收齐再rm -rf。" vs longer "等所有agent通知收齐、输出已读后再rm -rf。... USER=机器配置+状态，非个人隐私。"
- [live:39](/Users/ericstone/.hermes/profiles/technical/memories/MEMORY.md) vs mirror: document norm text differs ("全部md文档禁止ASCII..." vs "宪法文件(SOUL/USER/SKILL/MEMORY/POSTMORTEM)禁止...").
- [live:43](/Users/ericstone/.hermes/profiles/technical/memories/MEMORY.md) vs mirror: QUINTE archive path wording and example differ (short vs full /Users/... + "Never use /tmp/quinte-audit/").
- [live:49](/Users/ericstone/.hermes/profiles/technical/memories/MEMORY.md) vs mirror: "MAGI最高权限:sed/write_file/rm免请示。" vs "MAGI最高权限: sed/write_file/rm直接执行不请示。QUINTE=嘴(裁决辩论),MAGI=手(执行实现)。" + " (公司防火墙阻grok)" addition in mirror.

### 1.3 memories/USER.md
- [live:1](/Users/ericstone/.hermes/profiles/technical/memories/USER.md): Chinese-mixed short version ending with "2026-06-23明确：... Win Gold=apiyi GPT-4o-mini(grok被公司防火墙阻)。"
- [mirror:1-8](/Users/ericstone/Public/hermes-core-rules-mac-x86/memories/USER.md): English detailed, "QUINTE v3.4: MAGI three-model (grok-build/kimi K2.7/mimo-v2.5-pro)...", no trailing 2026-06-23 Win note.
- Mac hardware/PaddleOCR line matches, but overall text and QUINTE model phrasing differ.

### 1.4 README.md
- Major structural + content drift. Mirror has expanded "Ecosystem" table (RASHOMON/QUINTE/HIGHBALL/MAGI with v3.4 refs), longer "Key Decisions" table (includes 2026-06-22 v3.4 alignment, Agent patience, constitutional cross-audit entries), updated structure notes.
- [live ~2011-06-11 timestamp older](/Users/ericstone/.hermes/profiles/technical/README.md) vs [mirror 2026-06-22](/Users/ericstone/Public/hermes-core-rules-mac-x86/README.md).

### 1.5 Other
- SETUP.md: identical (no diff).
- Shared skills (e.g. productivity/ocr-and-documents/SKILL.md): content matches on PaddleOCR 2.10.0.
- multi-agent-debate/SKILL.md (Mac mirror vs live profile): both describe Gold=grok for Mac; minor description drift on dispatch/JSON sidecar/patience rules.
- Profile contains large runtime dirs (pastes/, sessions/, cache/, logs/, lsp/) absent from mirror (expected). Constitutional content should match exactly.

**Recommendation**: Treat `hermes-core-rules-mac-x86` as source of truth. Sync profile constitutional files (SOUL, memories/*, README) from mirror, then re-verify.

---

## 2. Win Gold Mapping — apiyi GPT-4o-mini (mostly consistent, SKILLs stale)

Confirmed in core constitutional (SOUL, MEMORY, USER):
- [SOUL.md:13](/Users/ericstone/Public/hermes-core-rules-win/SOUL.md): "On this machine: Gold=apiyi GPT-4o-mini, Fr=kimi, Myrrh=mimo (grok blocked by company firewall)."
- [SOUL.md:22](/Users/ericstone/Public/hermes-core-rules-win/SOUL.md): "Gold=apiyi, Fr=kimi, Myrrh=mimo"
- [SOUL.md:39](/Users/ericstone/Public/hermes-core-rules-win/SOUL.md): "grok blocked by company firewall — Gold=apiyi GPT-4o-mini."
- [memories/MEMORY.md:37](/Users/ericstone/Public/hermes-core-rules-win/memories/MEMORY.md): "本机grok被公司防火墙阻→apiyi GPT-4o-mini补Gold位"
- [memories/USER.md:1](/Users/ericstone/Public/hermes-core-rules-win/memories/USER.md): "Gold=apiyi GPT-4o-mini, Fr=kimi, Myrrh=mimo; grok blocked by company firewall"

**Inconsistencies (stale grok refs in Win files)**:
- [skills/multi-agent-debate/SKILL.md:133](/Users/ericstone/Public/hermes-core-rules-win/skills/multi-agent-debate/SKILL.md): "| MAGI Gold | grok→kimi on Win | ..."
- [skills/multi-agent-debate/SKILL.md:140](/Users/ericstone/Public/hermes-core-rules-win/skills/multi-agent-debate/SKILL.md): "| cc | MAGI Gold (grok) | contract/legal review |"
- [skills/multi-agent-debate/SKILL.md:143](/Users/ericstone/Public/hermes-core-rules-win/skills/multi-agent-debate/SKILL.md): "| rx | MAGI Gold (grok) | protocol/strategy |"
- [skills/multi-agent-debate/SKILL.md:261-264](/Users/ericstone/Public/hermes-core-rules-win/skills/multi-agent-debate/SKILL.md): Correct comment + apiyi dispatch present, but table above not updated.
- [skills/multi-agent-debate/magi/SKILL.md:3](/Users/ericstone/Public/hermes-core-rules-win/skills/multi-agent-debate/magi/SKILL.md): "MAGI v1.2 — ... (Gold→grok, Fr→kimi, Myrrh→mimo) ..."
- [skills/multi-agent-debate/magi/SKILL.md:45](/Users/ericstone/Public/hermes-core-rules-win/skills/multi-agent-debate/magi/SKILL.md): "# Gold (grok) — conversational..."
- [skills/software-development/flow-orchestration/R2_OPERATIONAL_CROSS.md:5](/Users/ericstone/Public/hermes-core-rules-win/skills/software-development/flow-orchestration/R2_OPERATIONAL_CROSS.md): "**R1 Participants**: ... Gold (grok→kimi) ..."

**Rule from Win POSTMORTEM: "Win Gold=apiyi GPT-4o-mini is canonical."** SKILL files violate.

---

## 3. 5 Gates (not 4) — QUINTE/RASHOMON/Hermes Constitutions

**Confirmed current 5 gates** (all core):
- RASHOMON/GATES.md: "The Five Gates (五つの門)", lists Gate 1-5 (Amamon, Kyōmon, Shōmon, Kan'nukimon, Kennōmon). L1, L132 "Five gates".
- QUINTE/specs/PROTOCOL.md: "Phase -1: Five Gates", "The Five Gates", table L341-346 with 5 rows (雨門 Amamon ... 憲門 Kennōmon). "Five gates executed..." L89, L348.
- Mac SOULs (live + mirror): Gate Precedence lists 1-5 (Amamon, Kyōmon, Shōmon, Kan'nukimon, Kennōmon).
- Win SOUL: lists 1-5 (Amamon, Kyomon, Shomon, Kan'nukimon, Kennomon). "update all five constitutional files".
- All MEMORY/USER reference 5.

**Stale "4 gates" / "four gates" language (non-historical, must fix)**:
- [QUINTE/ontology/quinte-ontology.md:34](/Users/ericstone/Public/QUINTE/ontology/quinte-ontology.md): "| -1 | Four Gates | ..."
- [QUINTE/ontology/quinte-ontology.md:45](/Users/ericstone/Public/QUINTE/ontology/quinte-ontology.md): "### Gate (Four Gates)"
- [QUINTE/specs/theoretical-foundation.md:66](/Users/ericstone/Public/QUINTE/specs/theoretical-foundation.md): "QUINTE's 4-gate system..."
- [QUINTE/specs/theoretical-foundation.md:110](/Users/ericstone/Public/QUINTE/specs/theoretical-foundation.md): "QUINTE's combined mechanisms (5 agents + ... + 4 gates + ..."
- [RASHOMON/REFINED-BRUTE-FORCE.md:29](/Users/ericstone/Public/RASHOMON/REFINED-BRUTE-FORCE.md): "- Four Gates: targeted failure-mode defense..."
- [RASHOMON/REFINED-BRUTE-FORCE.md:61](/Users/ericstone/Public/RASHOMON/REFINED-BRUTE-FORCE.md): "the Four Gates, each targeting a specific failure mode"
- [RASHOMON/references/mathematical-foundations.md:57](/Users/ericstone/Public/RASHOMON/references/mathematical-foundations.md): "Four Gates' decision logic"
- Numerous skills/*/references/ (both Mac mirror + live profile + Win):
  - quinte-conceptual-taxonomy.md (multiple): "four-gate defense-in-depth", "Four gates"
  - gates-taxonomy.md (subagent-driven): "## The four gate types"
  - kengen-push-authorization.md, platform-agnostic-quinte.md: "four gates"
  - rashomon-diagram-design.md: "four gates stacked"
  - highball-constraint-layer/SKILL.md: "Independent of four gates"
  - cross-platform-*-audit.md (profile): old notes "Gates: 4 ... missing Kan'nukimon", "4? 5?"
  - chinese-cleanup-protocol.md: "四道門→Four Gates"
  - (and more in Win/Mac skills)

QUINTE PROTOCOL current text is correct (5). Supporting ontology/theory + reference docs lag. History sections (CHANGELOG, v2.x mentions) are exempt.

---

## 4. QUINTE + MAGI both v3.4 — YES

- [QUINTE/specs/PROTOCOL.md:1,5](/Users/ericstone/Public/QUINTE/specs/PROTOCOL.md): "QUINTE Protocol Specification v3.4", "> **v3.4 (2026-06-20)** ... Synced with MAGI v3.4."
- [MAGI/specs/PROTOCOL.md:1,5](/Users/ericstone/Public/MAGI/specs/PROTOCOL.md): "MAGI v3.4 — Protocol Specification", "> **v3.4 (2026-06-20)**: Synced with QUINTE v3.4."
- Version tables and "v3.4" in dispatch/JSON sidecar sections match.
- Win/Mar mirror SOULs + SKILLs declare "v3.4" and "QUINTE v3.4".

---

## 5. MAGI spec says "sidecar" not "sidecard" — YES (fixed)

- [MAGI/specs/PROTOCOL.md:74](/Users/ericstone/Public/MAGI/specs/PROTOCOL.md): "### 2.3 JSON Sidecar & Evidence Validation (v3.4)"
- [QUINTE/specs/PROTOCOL.md:98,107,144,332](/Users/ericstone/Public/QUINTE/specs/PROTOCOL.md): "JSON sidecar", "JSON Sidecar (v3.4)", "machine-readable sidecar"
- Only historical mention of "sidecard" is in [Win POSTMORTEM L258](/Users/ericstone/Public/hermes-core-rules-win/memories/POSTMORTEM.md) (allowed).

---

## 6. Leftover "grok-unreachable" / "Gold-equals-kimi" (non-POSTMORTEM)

No **exact** "grok-unreachable" or "Gold-equals-kimi" strings outside POSTMORTEM files.

**Variants in non-POSTMORTEM files (flag as stale)**:
- Win SKILL tables + magi/SKILL.md + R2_OPERATIONAL_CROSS.md (see §2).
- Live profile (Mac technical):
  - [skills/multi-agent-debate/references/cross-platform-constitution-audit.md:18](/Users/ericstone/.hermes/profiles/technical/skills/multi-agent-debate/references/cross-platform-constitution-audit.md): "Gold=kimi (grok unreachable)"
  - [skills/multi-agent-debate/references/constitution-cross-audit.md:52](/Users/ericstone/.hermes/profiles/technical/skills/multi-agent-debate/references/constitution-cross-audit.md): "Win=kimi (grok unreachable)"
  - [skills/multi-agent-debate/references/cross-platform-alignment-methodology.md:59,66](/Users/ericstone/.hermes/profiles/technical/skills/multi-agent-debate/references/cross-platform-alignment-methodology.md): "Win grok unreachable → Gold=kimi", "grok is unreachable"
- Some audit/model-name-leak-scan.md entries describe past routing (in MAGI/audit/ — borderline historical).
- Mac mirror has fewer (mostly cleaned in core, some references may have copies?).

**POSTMORTEM entries** (allowed per query): Mac/Win POSTMORTEM document the prior "Win Gold=kimi" incident + fix to apiyi. OK.

---

## 7. PaddleOCR 2.10.0 Primary Everywhere — Mostly

**Mac (live + mirror)**:
- [USER.md:7](/Users/ericstone/.hermes/profiles/technical/memories/USER.md) + mirror: "PaddleOCR 2.10.0/PP-OCRv4 (CPU only, ~/paddleocr-venv/)."
- [MEMORY.md:35](/Users/ericstone/.hermes/profiles/technical/memories/MEMORY.md) + mirror: "PaddleOCR 2.10(PP-OCRv4)..."
- POSTMORTEM detailed adoption (L110-116).
- skills/productivity/ocr-and-documents/SKILL.md + references/paddleocr-*.md: primary engine, 2.10.0 locked on Intel.
- shipping/demurrage-*, multi-agent-debate/SKILL.md, devops/.../ocr-sof-*: consistent.

**Win**:
- [SOUL.md:58](/Users/ericstone/Public/hermes-core-rules-win/SOUL.md): "OCR: PaddleOCR 2.10.0/PP-OCRv4 (primary)."
- POSTMORTEM: adoption notes, "PaddleOCR 2.10.0/PP-OCRv4 (primary). Tesseract retained as English-only fallback."
- [USER.md:7](/Users/ericstone/Public/hermes-core-rules-win/memories/USER.md): "OCR: PaddleOCR (Chinese/mixed), Tesseract (English fallback)." **Missing "2.10.0/PP-OCRv4" version + primary qualifier.**
- skills/ (setup_paddleocr_win.sh, ocr refs, demurrage): reference primary Paddle, some keep Tesseract note.

**Inconsistency**: Win USER.md incomplete vs SOUL/POSTMORTEM/Mac. Tesseract fallback is platform reality (not bug).

---

## 8. Other / Cross-Repo Notes

- RASHOMON/GATES.md: 5 gates, v3.4 refs, Kennōmon (BANNIN) as #5. Consistent with QUINTE §6.
- QUINTE PROTOCOL history correctly documents progression (2.0 four-gate → 3.3+ Kennōmon/5 gates). Current text is 5 gates.
- "Five constitutional files" phrasing consistent in Win/Mac SOUL/MEMORY (SOUL + 3 memories + multi-agent SKILL).
- Mac live profile SOUL still lists 5 gates but with older phrasing and missing recent sections (agent patience, Netsumon zombie check).
- No "grok-unreachable" exact outside allowed history.
- MAGI/QUINTE specs describe Gold generically as "grok" in tables (platform override lives in per-machine SOUL/USER/MEMORY — correct design).

---

## Summary of Inconsistencies (by severity)

**CRITICAL (Mac sync drift)**:
- SOUL, MEMORY, USER, README differ between live profile and mirror (multiple sections).

**HIGH (Win Gold not uniform)**:
- skills/multi-agent-debate/SKILL.md (table + substitution entries L133,140,143)
- skills/multi-agent-debate/magi/SKILL.md (v1.2 Gold→grok)
- skills/software-development/flow-orchestration/R2_OPERATIONAL_CROSS.md

**HIGH (5 gates language drift)**:
- QUINTE/ontology/quinte-ontology.md (L34,45)
- QUINTE/specs/theoretical-foundation.md (L66,110)
- RASHOMON/REFINED-BRUTE-FORCE.md (L29,61)
- RASHOMON/references/mathematical-foundations.md (L57)
- ~10+ skills/*/references/* (four-gate descriptions, taxonomy, diagrams)

**MEDIUM**:
- Win USER.md OCR line incomplete (no 2.10.0).
- Legacy phrasing in reference docs (grok unreachable variants) — update or label historical.
- Some Mac live profile skills/references contain old 4-gate / Gold=kimi audit notes.

**CLEAN**:
- No sidecard outside POSTMORTEM history.
- No exact grok-unreachable/Gold-equals-kimi outside POSTMORTEM.
- QUINTE/MAGI PROTOCOL.md current text: v3.4 + 5 gates + sidecar.
- Win core (SOUL/MEMORY/USER): Gold=apiyi consistent.
- PaddleOCR 2.10.0 primary cited everywhere (Win USER is only soft miss).
- RASHOMON GATES.md: correct 5 gates.

---

**Next actions recommended**:
1. Sync Mac profile constitutional files from hermes-core-rules-mac-x86 (or treat mirror as authoritative and update profile).
2. Update Win multi-agent-debate SKILL tables + magi/ subdir + R2 cross to apiyi (no grok).
3. Global replace/rewrite "four gates" / "4-gate" / "Four Gates" → "five gates" (5 gates) in ontology, theory, and reference docs (preserve historical sections).
4. Fix Win USER.md OCR line to match SOUL ("PaddleOCR 2.10.0/PP-OCRv4 (primary); Tesseract English fallback").
5. Re-run cross-audit after fixes; append to this or POSTMORTEM.

Report written by Gold per user request. All facts cross-checked via direct file reads + searches.
