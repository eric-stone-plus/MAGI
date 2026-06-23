# Myrrh — Mac Constitution Verification

> mimo-v2.5-pro | 2026-06-23

## Files Read

| File | Expected Path | Actual Path | Status |
|------|--------------|-------------|--------|
| SOUL.md | `~/.hermes/profiles/technical/SOUL.md` | same | ✓ 56 lines |
| USER.md | `~/.hermes/memories/USER.md` | `~/.hermes/profiles/technical/memories/USER.md` | ✗ path wrong |
| MEMORY.md | `~/.hermes/memories/MEMORY.md` | `~/.hermes/profiles/technical/memories/MEMORY.md` | ✗ path wrong |
| POSTMORTEM.md | `~/.hermes/memories/POSTMORTEM.md` | `~/.hermes/profiles/technical/memories/POSTMORTEM.md` | ✗ path wrong |
| multi-agent-debate/SKILL.md | `~/.hermes/skills/multi-agent-debate/SKILL.md` | `~/.hermes/profiles/technical/skills/multi-agent-debate/SKILL.md` | ✗ path wrong |
| magi/SKILL.md | `~/.hermes/skills/magi/SKILL.md` | `~/.hermes/profiles/technical/skills/magi/SKILL.md` | ✗ path wrong |

**Finding**: All six paths in the user prompt omit `profiles/technical/`. This caused Gold and Fr (and my first pass) to fail on 5 of 6 files. SOUL.md was the only file at its expected location.

## Cross-Reference: Gold vs Fr

Both Gold and Fr failed to read 5 of 6 files. Neither produced substantive analysis — Gold's output is 15 lines (all errors), Fr's output is a single line of internal reasoning about path resolution. **No cross-referenceable findings exist from either peer.** This Myrrh report is the sole substantive output.

## Grep Audit Results

### 1. `grok` (171 matches across `~/.hermes/profiles/technical/`)

**Constitutional files (SOUL/USER/MEMORY)**: All correctly reference `Gold = opencode/GLM-5.2`. No stale grok-as-Gold mapping.

**CRITICAL — multi-agent-debate/SKILL.md** (the QUINTE protocol document, 302 lines):
- L14: `MAGI is cheap (grok包年 + kimi包月 + mimo按量)` — stale. grok kicked out 2026-06-23. Current: opencode (按量中转).
- L26: `MAGI(grok+kimi+mimo, >=2/3 gate)` — stale architecture diagram.
- L42: `MAGI Gold | grok | ... grok -p "..." --always-approve` — stale. Should be `opencode run --dangerously-skip-permissions`.
- L68: `Gold (grok) | Design the fix` — stale.
- L112-116: Entire `# Gold (grok)` dispatch block — stale.
- L208-210: Grok-specific invocation pitfalls (conversational tone, equals sign) — stale operational guidance.

**MAGI SKILL.md**: Correctly updated. `Gold | opencode run --dangerously-skip-permissions` at L32. `grok踢出2026-06-23(连续5次0B)` annotation present.

**Status**: SKILL.md v3.4 is 2 versions behind MAGI v3.5 on the Gold model mapping. This is the single largest remaining inconsistency.

### 2. `grok build` / `grok-build` (38 / 33 matches)

Found in operational references (thermal-triage, thermal-rescue, stale-doc-audit, grok-build/SKILL.md, macos-maintenance). These are **process-signature references** for kill/cleanup commands (`pgrep -f 'grok-build'`). The `grok-build` SKILL.md itself at `~/.[0m
[0m← [0mWrite ../MAGI/debates/2026-06-23/mac-rules-audit/myrrh_mac.md
Wrote file successfully.
[0m
Done. Written to `/Users/ericstone/Public/MAGI/debates/2026-06-23/mac-rules-audit/myrrh_mac.md`.

**Summary of findings:**

- **Verdict: FAIL** (confidence 0.92)
- **1 BLOCKER**: `multi-agent-debate/SKILL.md` v3.4 still maps Gold→grok in 15+ locations — 2 versions behind MAGI v3.5 which correctly uses opencode/GLM-5.2. This is the authoritative QUINTE dispatch doc; agents reading it will dispatch the wrong Gold model.
- **2 HIGHs**: `/tmp/quinte-audit/` persists in 49 reference docs despite archive-path correction; public repos still say "4 gates" (SOUL has 5).
- **4 MEDIUMs**: grok-build SKILL.md still installed without deprecation; 2 reference docs still treat Tesseract as available.
- **Path issue confirmed**: 5 of 6 requested paths omit `profiles/technical/`, which caused Gold and Fr to fail completely — no peer findings to cross-reference.
- **Mac constitutional files (SOUL/USER/MEMORY/MAGI SKILL) are internally consistent** on model mappings and gate count. The drift is in the debate SKILL.md and reference docs.
te-audit/` as working directory
- `cross-repo-audit-methodology.md`: `AUDIT_DIR="/tmp/quinte-audit/${TOPIC}"`
- `kimi-code-r1-participant.md`: Prompt templates reference `/tmp/quinte-audit/`
- `quinte-session-archive.md`, `quinte-archive-management.md`: Archive commands use `/tmp/quinte-audit/`
- Multiple cc/cw drift references, anti-drift patterns, recursive QUINTE patterns

**Assessment**: The constitutional rule (SKILL.md L159) and POSTMORTEM are correct. The reference docs are legacy operational patterns that predate the archive-path correction. These are **documentation debt**, not active violations — the dispatch commands in SKILL.md itself use `$AUDIT` variable correctly. But agent prompts reading these references may inherit the old path.

### 5. `Four Gate` / `four gate` (15 matches)

SOUL.md defines **5 gates**: Amamon, Kyōmon, Shōmon, Kan'nukimon, Kennōmon.

POSTMORTEM #13 (L122): "Public repos (RASHOMON GATES.md, QUINTE PROTOCOL Phase -1) still document 4 gates." This was flagged as a CRITICAL finding in the 2026-06-23 cross-repo audit.

`protocol-doc-design.md` L13: "Four Gates stay 雨門/鏡門/證門/閂門" — stale, missing Kan'nukimon and Kennōmon.

`chinese-cleanup-protocol.md` L15: `四道門→Four Gates` — stale sed pattern.

**Status**: Mac constitution (SOUL.md) correctly has 5 gates. The public repos and some reference docs still say 4. This was flagged in POSTMORTEM #13 but the fix is incomplete — public repo sync still needed.

### 6. `sidecard` — 0 matches (correct; term is `sidecard` does not exist)

`sidecar` (22 matches): All correctly refer to "JSON sidecar" (v3.4 feature). Consistent across SOUL, SKILL, POSTMORTEM, MAGI references. No issues.

### 7. `Tesseract` (11 matches)

POSTMORTEM #12: Tesseract removed (`brew uninstall`), PaddleOCR 2.10.0 adopted as sole engine.

**Residual non-historical references**:
- `ocr-and-documents/SKILL.md` L132: `Tesseract 5.5.2 | ❌ Removed 2026-06-23` — correctly annotated as removed.
- `ocr-cross-reference.md` L21: `可能有 OCR 误差（tesseract 局限）` — stale context, implies Tesseract still in use.
- `platform-compatibility-mirage.md` L42: `Tesseract 5.5.2（离线英文兜底）` — stale, still lists Tesseract as available.
- `cross-platform-profile.md` L65: mentions `brew install tesseract` as documentation example — acceptable (pedagogical context).

**Assessment**: 2 reference docs still treat Tesseract as available/functional. These need annotation or removal.

## Remaining Issues (Ranked)

| # | Severity | Issue | Location | Action |
|---|----------|-------|----------|--------|
| 1 | **BLOCKER** | SKILL.md v3.4 still maps Gold→grok (15+ references) | multi-agent-debate/SKILL.md L14,26,42,68,112-116,208-210 | Update all Gold references to opencode/GLM-5.2; remove grok-specific invocation pitfalls or move to historical section |
| 2 | **HIGH** | `/tmp/quinte-audit/` in 49 reference docs | Multiple references/ files | Bulk sed or annotate each as pre-archive-path-correction |
| 3 | **HIGH** | Public repos still say "4 gates" | RASHOMON GATES.md, QUINTE PROTOCOL Phase -1 (external) | Sync to 5 gates per SOUL.md; needs separate QUINTE |
| 4 | **MEDIUM** | `grok-build` SKILL.md still installed, no deprecation annotation | `~/.hermes/profiles/technical/skills/autonomous-ai-agents/grok-build/SKILL.md` | Add `⛔ DEPRECATED 2026-06-23` header or remove |
| 5 | **MEDIUM** | `platform-compatibility-mirage.md` lists Tesseract as available | references/ | Annotate as removed per POSTMORTEM #12 |
| 6 | **MEDIUM** | `ocr-cross-reference.md` references tesseract limitations | references/ | Update to PaddleOCR-only context |
| 7 | **LOW** | Constitutional file paths omit `profiles/technical/` | User's mental model / dispatch templates | Document canonical paths in SOUL.md or MEMORY.md |
| 8 | **LOW** | `protocol-doc-design.md` says "Four Gates" | references/ | Update to 5 gates |
| 9 | **LOW** | `chinese-cleanup-protocol.md` sed pattern says `四道門→Four Gates` | references/ | Update sed pattern |

## Gate Consistency Check

SOUL.md defines 5 gates in order:
1. Amamon (ambiguous intent)
2. Kyōmon (bidirectional verify)
3. Shōmon (full QUINTE before action)
4. Kan'nukimon (anti-drift)
5. Kennōmon (solo modification forbidden on README/specs/ontology)

multi-agent-debate/SKILL.md does not enumerate gates explicitly — defers to SOUL. No contradiction within Mac constitution itself. Contradiction is with external public repos (RASHOMON/QUINTE still at 4 gates).

## Model Mapping Consistency

| Document | Gold | Fr | Myrrh | Status |
|----------|------|----|-------|--------|
| SOUL.md | opencode/GLM-5.2 | kimi | mimo | ✓ |
| USER.md | opencode/GLM-5.2 | kimi | mimo | ✓ |
| MEMORY.md | opencode/GLM-5.2 | kimi | mimo | ✓ |
| magi/SKILL.md v3.5 | opencode/GLM-5.2 | kimi | mimo | ✓ |
| multi-agent-debate/SKILL.md v3.4 | **grok** | kimi | mimo | ✗ STALE |

## Verdict

Mac constitution (SOUL/USER/MEMORY/POSTMORTEM/MAGI SKILL) is internally consistent on model mappings and gate count. The **sole BLOCKER** is multi-agent-debate/SKILL.md v3.4 which still maps Gold→grok in 15+ locations — 2 versions behind MAGI v3.5. This document is the authoritative QUINTE dispatch reference; any agent reading it for MAGI dispatch will use the wrong Gold model.

**JSON sidecar**:
```json
{
  "verdict": "FAIL",
  "confidence": 0.92,
  "reasoning_chain": [
    "All 6 constitutional files read (5 required path correction)",
    "Gold and Fr both failed — no peer findings to cross-reference",
    "Grep audit: 7 search terms, 349 total matches",
    "BLOCKER: SKILL.md v3.4 Gold→grok (15+ refs) contradicts MAGI v3.5 Gold→opencode",
    "HIGH: /tmp/quinte-audit/ in 49 reference docs vs archive-path rule",
    "HIGH: Public repos still say 4 gates (external, needs separate QUINTE)",
    "Mac constitutional files (SOUL/USER/MEMORY/MAGI) internally consistent"
  ],
  "evidence_citations": [
    "multi-agent-debate/SKILL.md:42",
    "multi-agent-debate/SKILL.md:112-116",
    "magi/SKILL.md:32",
    "SOUL.md:9",
    "POSTMORTEM.md:122",
    "multi-agent-debate/SKILL.md:159"
  ]
}
```
