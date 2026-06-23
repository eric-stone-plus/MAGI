**Claims from the specified headers (first lines + version annotation):**

1. `~/Public/QUINTE/specs/PROTOCOL.md`: **v3.4**  
   Header: `# QUINTE Protocol Specification v3.4 · Hermes Agent`  
   Followed by `**v3.4 (2026-06-20)**: MAGI ecosystem adoption... Synced with MAGI v3.4.`

2. `~/Public/MAGI/specs/PROTOCOL.md`: **v3.4**  
   Header: `# MAGI v3.4 — Protocol Specification · Hermes Agent`  
   Followed by `**v3.4 (2026-06-20)**: Synced with QUINTE v3.4...`

3. `~/Public/RASHOMON/specs/theoretical-foundation.md`: **1.0**  
   Header: `# RASHOMON Theoretical Foundation`  
   `> **Version**: 1.0 (2026-06-18)`  
   (Parent audit note: QUINTE v3.4)

4. `~/Public/HIGHBALL/specs/theoretical-foundation.md`: **2.0**  
   Header: `# HIGHBALL Theoretical Foundation`  
   `> **Version**: 2.0 (2026-06-18) — Upgraded with formal verification and access control anchors`  
   (Parent audit note: QUINTE v3.4)

**RASHOMON and HIGHBALL specs/PROTOCOL.md status:** Neither has `specs/PROTOCOL.md` (confirmed via `ls`, `git ls-tree`, and history checks). No such file exists in the current tree or in the relevant tag trees. RASHOMON `specs/` contains `theoretical-foundation.md`, `adversarial-defense.md`, `drift-detection.md`, `parallel-topology.md`. HIGHBALL `specs/` contains `theoretical-foundation.md` + several other constraint/audit docs (e.g., `rubicon-aps.md`, `kennomon-architecture-gate.md`).

**Current git state snapshot (as of latest checks):**

- **QUINTE**: Tags `v3.0.1`, `v3.1`, `v3.4`. `git describe --tags --always` → `v3.4`. HEAD `7446f92` "Sync: lean QUINTE skill v3.4".
- **MAGI**: Tag `v3.4`. `git describe` → `v3.4`. HEAD `482349a` "MAGI skill: remove ASCII diagram, pure text architecture".
- **RASHOMON**: Tags `v1.1.0`, `v1.2.0` (both tagged 2026-06-10). `git describe` → `v1.2.0-48-gc477b7a`. HEAD `c477b7a` "v3.4: strip kanji...".
- **HIGHBALL**: No tags. `git describe` → `3a7b945`. HEAD `3a7b945` "v3.4: strip kanji...".

**v3.4 tag details (recent, 2026-06-23):**
- QUINTE `v3.4`: tag msg "v3.4: MAGI ecosystem adoption, 5-gate sync, cross-repo consistency". Points to commit whose msg includes "v3.4". File header at tag: v3.4 (matches).
- MAGI `v3.4`: tag msg "v3.4: Synced with QUINTE v3.4, dual-mode operation, JSON sidecar". Points to the "remove ASCII" commit. File header at tag: v3.4 (matches).

**All mismatches between claimed version (md header), git tag, and commit message:**

**QUINTE:**
- Current claimed v3.4 + v3.4 tag + tag msg + tagged commit msg ("... v3.4") are aligned.
- Older tags (`v3.0.1`, `v3.1`, messages referencing v3.1 trim etc.) predate the v3.4 content and the `specs/` restructure (current `specs/PROTOCOL.md` path did not exist in those tag trees; rename noted in history around 2026-06-17).
- No other header/tag/commit version mismatches at tip.

**MAGI:**
- Claimed v3.4 matches the `v3.4` tag name and tag message ("v3.4: Synced with QUINTE v3.4...").
- **Mismatch**: The commit *tagged* `v3.4` is `482349a` with message "MAGI skill: remove ASCII diagram, pure text architecture" (no version mention). The substantive v3.4 protocol changes (including body updates to the header) were in the prior commit `197e390` ("MAGI skill: v3.4 protocol, three-doctor architecture, dual-mode"). Multiple earlier commits carry "v3.4:" labels (e.g., cross-repo refs, JSON sidecar, error classification). Tag was applied to a later cleanup commit.
- No older tags. HEAD commit message does not match the version/tag.

**RASHOMON:**
- Claimed **1.0 (2026-06-18)** in `theoretical-foundation.md`.
- Git tags: **v1.1.0** and **v1.2.0** (both 2026-06-10, tag messages simply "v1.x — 2026-06-10"). Latest tag points to commit `1d342c1` "Remove Simplified Chinese; English primary + Japanese terminology".
- **Mismatches**:
  - Claimed 1.0 does not match any git tag (no v1.0 tag; existing tags are v1.1/v1.2 and predate the file).
  - `specs/theoretical-foundation.md` did not exist in the v1.1.0 or v1.2.0 trees (git show fails with "path ... not in 'v1.2.0'").
  - File introduced later in `aa8d213` ("theoretical-foundation.md: BFT + MAD-Spear + drift detection anchors"). Header has stayed at 1.0 since introduction.
  - Post-creation commits on the file use "v3.4:" labels (e.g., `a9b873e` "v3.4: PHENOMENOLOGY version refs, theoretical-foundation duplicate § fix", `e5e7f4a` "v3.4: cross-repo version references updated", plus others for kanji/romaji, parent audit refs v3.2→v3.3, etc.). HEAD is labeled v3.4.
  - Tags predate the 2026-06-18 header date by ~8 days.
- No `specs/PROTOCOL.md` (or any PROTOCOL.md) ever present.

**HIGHBALL:**
- Claimed **2.0 (2026-06-18)** in `theoretical-foundation.md`.
- Git tags: **none**.
- **Mismatches**:
  - No git tags exist to match (or contradict) the claimed 2.0.
  - Commit messages reference higher versions that were never reflected in the file header: `2c18a7b` "v2.2: VeriGuard→VerAct...", `05eca8b` "v2.1: VeriGuard venue corrected...". At those commits (and currently) the header is still exactly `**Version**: 2.0 (2026-06-18)...`.
  - `625641d` did set "v2.0: upgraded".
  - Current/last commits touching the file use "v3.4:" (HEAD: "v3.4: strip kanji from body text...", plus multiple "v3.4: cross-repo version references updated", "v3.4: remove stale...", parent audit updates, etc.).
  - HEAD commit message uses v3.4 label.
- No `specs/PROTOCOL.md` (or any PROTOCOL.md) ever present.

**Additional cross-repo notes:**
- RASHOMON and HIGHBALL theoretical docs explicitly note "Parent audit: QUINTE v3.4" while carrying their own 1.0/2.0 versions and having no (or mismatched) tags.
- Multiple commits across RASHOMON/HIGHBALL (and QUINTE/MAGI) are titled "v3.4: cross-repo version references updated".
- QUINTE maintains separate versioning: `specs/PROTOCOL.md` = v3.4 while its own `specs/theoretical-foundation.md` = 1.0 (2026-06-18). Not directly asked but visible in structure.
- Older tags in QUINTE/RASHOMON generally predate file renames (`spec/` → `specs/`) and the current header dates/content.

All extractions used the live file headers (not tags or messages). Git data from `git tag`, `git describe`, `git for-each-ref`, `git log`, `git show <tag>:<path>`, and file history. State reflects latest tool results (including recent 2026-06-23 v3.4 tags on QUINTE/MAGI).
