**6-repo cross-consistency audit complete.** Findings written to [](/Users/ericstone/Public/MAGI/audit/6-repo-cross-consistency-audit.md) (215 lines, exhaustive with file:line citations).

### High-level summary of inconsistencies (all checked against reads/greps/diffs of constitutional files: SOUL.md, memories/{MEMORY,USER,POSTMORTEM}.md, specs/PROTOCOL.md, GATES.md, key SKILLs/README/SETUP, etc.):

**1. Mac live profile (~/.hermes/profiles/technical/) vs Mac mirror (~/Public/hermes-core-rules-mac-x86/) — NOT identical (CRITICAL drift).**
- SOUL.md diffs (constitutional files list L3; Shōmon extra drift text L30 mirror; missing "Agent patience" section + 600s caps L40+ mirror; Netsumon zombie check L48 mirror; other wording in Iron Law/Agent Dispatch/Netsumon/Accountability).
- memories/MEMORY.md diffs (audit dir phrasing, document norms L39, QUINTE archive paths L43, MAGI highest-permission § L49).
- memories/USER.md diffs (live Chinese-mixed/short + trailing 2026-06-23 Win note vs mirror English detailed; QUINTE v3.4 model phrasing).
- README.md major drift (mirror has fuller ecosystem table + updated Key Decisions with 2026-06-22 items; live older).
- SETUP.md: identical. Shared skills (e.g. ocr-and-documents): mostly match on key facts. (Profile has expected extra runtime dirs.)
- Mirror often looks newer on recent additions (patience, zombie checks, precise paths).

**2. Win Gold = apiyi GPT-4o-mini (company firewall blocks grok) — consistent in core, not across all files.**
- SOUL.md (L13,22,39), MEMORY.md (L37), USER.md (L1): correct ("Gold=apiyi GPT-4o-mini ... grok blocked..."; heterogeneity restored).
- Stale in Win:
  - skills/multi-agent-debate/SKILL.md:133 ("| MAGI Gold | grok→kimi on Win |"), :140 ("MAGI Gold (grok)"), :143 (rx row), plus later correct comment/dispatch at L261-264.
  - skills/multi-agent-debate/magi/SKILL.md:3 ("v1.2 ... Gold→grok ..."), :45.
  - skills/software-development/flow-orchestration/R2_OPERATIONAL_CROSS.md:5 ("Gold (grok→kimi)").
- Per Win POSTMORTEM: "Win Gold=apiyi GPT-4o-mini is canonical."

**3. All constitutions use 5 gates (Amamon, Kyōmon/Kyomon, Shōmon/Shomon, Kan'nukimon, Kennōmon/Kennomon) — confirmed in current text.**
- RASHOMON/GATES.md: "The Five Gates", explicit 1-5 + execution flow.
- QUINTE/specs/PROTOCOL.md: "Phase -1: Five Gates", "The Five Gates" §6 + table (5 rows), L89/L348.
- Mac (live+mirror) + Win SOULs: "Gate Precedence" lists exactly 5 (with/without diacritics).
- "Five constitutional files" phrasing consistent.
- **Stale "4 gates"/"four gates"/"Four Gates" (non-history, needs update)**: QUINTE/ontology/quinte-ontology.md:34/45; QUINTE/specs/theoretical-foundation.md:66/110; RASHOMON/REFINED-BRUTE-FORCE.md:29/61; RASHOMON/references/mathematical-foundations.md:57; ~10+ skills/*/*/references/ (quinte-conceptual-taxonomy, gates-taxonomy, kengen-*, platform-*, rashomon-diagram, highball-*, cross-audit notes, chinese-cleanup, etc.) still use 4-gate language or "four-gate defense-in-depth" (first 4 + separate Kennomon sometimes). QUINTE PROTOCOL history (old v2.x) exempt.

**4. QUINTE + MAGI both tagged v3.4 — yes.**
- Headers + v3.4 sections (JSON sidecar, error classification, MAGI Mode A/B, cross-repo, substitution, etc.) + "Synced with ..." notes. Mirror/Win SOULs + SKILLs declare v3.4.

**5. MAGI spec says "sidecar" (not "sidecard") — yes.**
- MAGI/specs/PROTOCOL.md: "JSON Sidecar & Evidence Validation (v3.4)"; QUINTE/specs/PROTOCOL.md multiple "JSON sidecar"/"sidecar". Only in historical Win POSTMORTEM L258 (allowed).

**6. Leftover grok-unreachable / Gold-equals-kimi (non-POSTMORTEM) — none exact; variants flagged.**
- No literal "grok-unreachable" or "Gold-equals-kimi" outside POSTMORTEM (historical entries there OK).
- Variants (non-POSTMORTEM): Win SKILL tables (above); live profile skills/multi-agent-debate/references/{cross-platform-constitution-audit.md:18, constitution-cross-audit.md:52, cross-platform-alignment-methodology.md:59/66} ("Gold=kimi (grok unreachable)", "Win grok unreachable → Gold=kimi"). Some audit logs border historical. Clean in core constitutions.

**7. PaddleOCR 2.10.0 primary OCR everywhere — mostly (Win USER incomplete).**
- Mac (USER L7, MEMORY L35, POSTMORTEM L110+, ocr-and-documents/SKILL + refs, shipping/*, multi-agent SKILL): consistent "PaddleOCR 2.10.0/PP-OCRv4 (primary)" + Intel lock + PP-Structure.
- Win: SOUL L58 ("PaddleOCR 2.10.0/PP-OCRv4 (primary)"); POSTMORTEM notes adoption + Tesseract English fallback only. **USER.md:7** only says "PaddleOCR (Chinese/mixed), Tesseract (English fallback)" — missing version/primary qualifier.

**Other notes**:
- RASHOMON GATES.md + QUINTE §6 align on 5 gates + v3.4.
- Mac live profile SOUL shorter/older vs mirror (constitutional list, recent sections).
- General: 5 constitutional files, process independence, MAGI before mods, etc. consistent where current.
- No other major version or mapping contradictions in core files.

Report includes full per-section evidence + recommendations (sync Mac from mirror; fix Win SKILL tables; update 4-gate language in ontology/theory/refs; patch Win USER OCR line). All via direct reads + targeted searches/diffs. Let me know if you want a follow-up QUINTE on the fixes or more files.
