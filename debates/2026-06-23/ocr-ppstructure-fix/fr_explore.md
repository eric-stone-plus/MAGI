# Fr File Exploration — OCR / PPStructure / Tesseract Stragglers

**Scope:**
- `~/.hermes/profiles/technical/`
- `~/Public/hermes-core-rules-mac-x86/`

**Snapshot:** 2026-06-23, during the QUINTE OCR/PPStructure audit.  
**Note:** The mac-x86 repo working tree already has *uncommitted* fixes on four files (`invocation-mac-intel-x86.md`, `SKILL.md`, `paddleocr-deployment.md`, `setup_paddleocr_mac.sh`). Those corrections move `table/layout/formula` from `PaddleOCR()` to `PPStructure()`. This report reflects the files **as they exist right now**.

**Legend:**
- **A** — `table=True` / `layout=True` / `formula=True` passed to `PaddleOCR()` (no-op; belongs on `PPStructure`).
- **B** — Reference to `PPStructure`.
- **C** — Inline `PaddleOCR()` constructor that violates the Platform Router ("load exactly one invocation ref; never inline a constructor").
- **D** — Old `tesseract` / `ocrmypdf` straggler still present after 2026-06-23 removal.

---

## 1. `table=True` / `layout=True` / `formula=True` on `PaddleOCR()` constructor (A)

### `~/.hermes/profiles/technical/`

| File | Line(s) | Snippet / what’s wrong |
|------|---------|------------------------|
| `skills/productivity/ocr-and-documents/SKILL.md` | 146 | `_ocr = PaddleOCR(lang='ch', use_angle_cls=True, enable_mkldnn=False, table=True, layout=True, formula=True, show_log=False)` — batch template inlines the no-op flags on `PaddleOCR`. |
| `skills/productivity/ocr-and-documents/references/paddleocr-deployment.md` | 75 | API table lists `PaddleOCR(..., table=True, layout=True, formula=True)` as the 2.10.0 API. |
| `skills/productivity/ocr-and-documents/references/paddleocr-deployment.md` | 80 | Bullet still describes `PaddleOCR(..., table=True, layout=True, formula=True, show_log=False)` and claims the flags enable PPStructure models. |
| `skills/productivity/ocr-and-documents/references/invocation-mac-intel-x86.md` | 25, 26, 27 | Full Constructor block passes `table=True`, `layout=True`, `formula=True` to `PaddleOCR()`. |
| `skills/productivity/ocr-and-documents/references/invocation-mac-intel-x86.md` | 44 | Singleton pattern passes `table=True, layout=True, formula=True, show_log=False` to `PaddleOCR()`. |
| `memories/POSTMORTEM.md` | 114 | Records the 2026-06-23 fix and claims `table=True, layout=True, formula=True` (on PaddleOCR) "enable cached models". Now incorrect. |
| `memories/MEMORY.md` | 39 | Operational memory: "Agent invocation: use_angle_cls=True, enable_mkldnn=False, table/layout/formula=True. Singleton pattern." Still implies these are `PaddleOCR` flags. |
| `memories/MEMORY.md` | 19 | Notes "table=True实际no-op" — correctly identifies the bug, but still references the anti-pattern. |
| `skills/magi/SKILL.md` | 43 | Cites `table=True` on `PaddleOCR()` as a no-op example. |

### `~/Public/hermes-core-rules-mac-x86/`

| File | Line(s) | Snippet / what’s wrong |
|------|---------|------------------------|
| `memories/POSTMORTEM.md` | 114 | Same outdated postmortem record as technical profile. |
| `memories/MEMORY.md` | 41 | Same outdated operational memory as technical profile. |

> In the mac-x86 working tree, the operational code files (`SKILL.md`, `invocation-mac-intel-x86.md`, `paddleocr-deployment.md`, `setup_paddleocr_mac.sh`) have already been edited so that `table/layout/formula` now appear only on `PPStructure()`. Those corrected lines are listed in section 2 below.

---

## 2. `PPStructure` references (B)

### `~/.hermes/profiles/technical/`

| File | Line(s) | Snippet / what’s wrong |
|------|---------|------------------------|
| `skills/productivity/ocr-and-documents/references/paddleocr-deployment.md` | 74 | Table row mentions PPStructure models (SLANet/picodet/LaTeX-OCR) but still couples them to `PaddleOCR()`. |
| `skills/productivity/ocr-and-documents/references/paddleocr-deployment.md` | 80 | Bullet mentions PPStructure models while documenting the wrong `PaddleOCR()` constructor. |
| `skills/productivity/ocr-and-documents/references/paddleocr-deployment.md` | 86 | Model cache line `~/.paddleocr/whl/{det,rec,cls,table,layout,formula}/` references PPStructure model directories. |
| `skills/productivity/ocr-and-documents/references/invocation-mac-intel-x86.md` | 82 | Failure-mode row: "No PPStructure output | table/layout/formula not set | Add all three to constructor" — direction is right but does not clarify that the constructor must be `PPStructure`, not `PaddleOCR`. |
| `skills/productivity/ocr-and-documents/SKILL.md` | 98 | Capabilities line says "table structure → HTML, layout detection (10 categories), formula → LaTeX" under the PaddleOCR tier without splitting out `PPStructure`. |
| `memories/POSTMORTEM.md` | 110 | Mentions "table/LaTeX layout via PP-StructureV2" being underutilized. |

### `~/Public/hermes-core-rules-mac-x86/`

| File | Line(s) | Snippet / status |
|------|---------|------------------|
| `skills/productivity/ocr-and-documents/references/paddleocr-deployment.md` | 49, 52, 54, 82, 83, 89, 95 | Corrected to use `PPStructure(..., table=True, layout=True, formula=True)` and document the split. |
| `skills/productivity/ocr-and-documents/references/invocation-mac-intel-x86.md` | 23, 25, 54, 58, 64, 68–71, 94, 100, 120, 154, 155 | Corrected `PPStructure` usage with `cls_model_dir` and routing rule. |
| `skills/productivity/ocr-and-documents/SKILL.md` | 28, 74, 101, 158, 160 | Corrected batch template introduces `get_structure()` returning `PPStructure(...)`. |

---

## 3. Inline `PaddleOCR()` constructors violating the Platform Router (C)

> Router rule (from `ocr-and-documents/SKILL.md`): "Load exactly ONE ref. Never inline a constructor — deltas-only refs prevent cross-platform copy-paste bugs."

### `~/.hermes/profiles/technical/`

| File | Line(s) | Snippet / what’s wrong |
|------|---------|------------------------|
| `skills/productivity/ocr-and-documents/SKILL.md` | 138, 142–147 | **Batch template** imports `PaddleOCR` directly and inlines the constructor in `get_ocr()`, hard-coding `enable_mkldnn=False` and the no-op `table/layout/formula` flags instead of loading the platform invocation ref. |
| `skills/productivity/ocr-and-documents/references/paddleocr-deployment.md` | 50 | Verify one-liner: `python3 -c "from paddleocr import PaddleOCR; ocr = PaddleOCR(lang='ch'); print('OK')"` — uses the wrong class, omits mandatory invariants (`use_angle_cls`, `enable_mkldnn`), and ignores the router. |

### `~/Public/hermes-core-rules-mac-x86/`

| File | Line(s) | Snippet / what’s wrong |
|------|---------|------------------------|
| `skills/productivity/ocr-and-documents/SKILL.md` | 141, 150–151, 158–160 | Batch template has a comment saying "Load platform ref for get_ocr() / get_structure() constructors — do NOT inline kwargs here", but still hard-codes `PaddleOCR(...)` and `PPStructure(...)` inline in the template. The router wants constructors to live in the platform ref and be imported/loaded, not duplicated. |
| `skills/productivity/ocr-and-documents/references/paddleocr-deployment.md` | 53 | Verify block inlines `PaddleOCR(lang='ch', use_angle_cls=True, enable_mkldnn=False, show_log=False)` (line-OK for a reference doc, but still a non-router inline example). |
| `scripts/setup_paddleocr_mac.sh` | 39–55 | Setup script inlines both `PaddleOCR(...)` and `PPStructure(...)` constructors. It is a setup script, not a batch template, but it still hard-codes platform deltas instead of loading the invocation ref. |

---

## 4. Old `tesseract` / `ocrmypdf` stragglers (D)

> Tesseract was removed 2026-06-23; `ocrmypdf` is orphaned because it depends on Tesseract. References below are still live in skill logic or recent examples.

### `~/.hermes/profiles/technical/`

| File | Line(s) | Snippet / what’s wrong |
|------|---------|------------------------|
| `skills/devops/demurrage-monthly/SKILL.md` | 219 | Operational PDF pipeline: `qpdf decrypt → python3 zlib 直读（优先）→ ocrmypdf --sidecar 兜底`. `ocrmypdf` fallback is now orphaned. |
| `skills/devops/demurrage-monthly/SKILL.md` | 254 | "...不要 OCR 扫描 PDF。.doc 提取准确率 100% vs Tesseract OCR ~92%." Still cites Tesseract as a live OCR alternative. |
| `skills/devops/demurrage-monthly/references/ocr-sof-time-extraction.md` | 9 | "OCR: Tesseract 5.5.2 (brew) with chi_sim+chi_tra+eng" — entire reference path is based on the removed engine. |
| `skills/shipping/demurrage-verification/SKILL.md` | 50 | "扫描件用 Tesseract 400 DPI, `--psm 6`, `-l eng`" — direct Tesseract instruction. |
| `skills/shipping/vessel-nomination-vetting/references/peace-gem-hp214-case-study.md` | 47 | "OCR 新方法：qpdf decrypt → python3 zlib 直读文本层（90%证书适用）→ ocrmypdf --sidecar 兜底" — orphaned fallback. |
| `skills/business-intelligence/research-intelligence/SKILL.md` | 53 | "兜底：ocrmypdf --sidecar（扫描件）" — orphaned fallback in a batch PDF pipeline. |
| `skills/multi-agent-debate/references/ocr-cross-reference.md` | 21 | "Grok ... 可能有 OCR 误差（tesseract 局限）" — still names Tesseract as the OCR backend. |
| `skills/multi-agent-debate/references/platform-compatibility-mirage.md` | 42 | Recommends "Tesseract 5.5.2（离线英文兜底）" as an offline English fallback. |
| `skills/productivity/ocr-and-documents/SKILL.md` | 129, 130 | Deprecated-tools table marks Tesseract and ocrmypdf correctly as ❌ Removed / ❌ Orphaned. These rows are accurate reference, not stragglers to remove. |
| `skills/multi-agent-debate/references/cross-platform-profile.md` | 65 | Mentions `brew install tesseract` as a documentation example; policy note says not to remove platform-specific examples. Not an active instruction. |
| `skills/multi-agent-debate/references/cc-cw-drift-2026-06-07-pm.md` | 12 | Historical audit snippet: "SOUL.md OCR: Tesseract only (Flash removed)". Historical record only. |
| `skills/multi-agent-debate/references/kengen-violation-2026-06-23.md` | 7 | "Post-Tesseract removal SYNC push". Historical record only. |
| `memories/POSTMORTEM.md` | 55, 57, 108, 110, 114 | Historical postmortem references to Tesseract removal. Expected in an archive. |
| `memories/MEMORY.md` | 39 | Notes "Tesseract removed 2026-06-23". Accurate status note. |

### `~/Public/hermes-core-rules-mac-x86/`

| File | Line(s) | Snippet / what’s wrong |
|------|---------|------------------------|
| `skills/devops/demurrage-monthly/SKILL.md` | 219, 254 | Same `ocrmypdf --sidecar` fallback and Tesseract comparison as technical profile. |
| `skills/devops/demurrage-monthly/references/ocr-sof-time-extraction.md` | 9 | Same Tesseract 5.5.2 OCR path. |
| `skills/shipping/demurrage-verification/SKILL.md` | 50 | Same Tesseract scanning instruction. |
| `skills/shipping/vessel-nomination-vetting/references/peace-gem-hp214-case-study.md` | 47 | Same `ocrmypdf --sidecar` fallback. |
| `skills/multi-agent-debate/references/platform-compatibility-mirage.md` | 42 | Same Tesseract fallback recommendation. |
| `skills/multi-agent-debate/references/ocr-cross-reference.md` | 21 | Same Tesseract limitation note. |
| `skills/multi-agent-debate/references/cross-platform-profile.md` | 65 | Same documentation policy note. |
| `skills/multi-agent-debate/references/cc-cw-drift-2026-06-07-pm.md` | 12 | Same historical audit mention. |
| `skills/productivity/ocr-and-documents/SKILL.md` | 132, 133 | Deprecated-tools table (accurate). |
| `memories/POSTMORTEM.md` | 55, 57, 108, 110, 114 | Historical postmortem references. |
| `memories/MEMORY.md` | 41 | Status note that Tesseract was removed. |

---

## 5. Meta / non-source references

| File | Line(s) | Note |
|------|---------|------|
| `~/.hermes/profiles/technical/processes.json` | 4 | This file contains the QUINTE process command that launched the present exploration. It quotes the search criteria (`table=True`, `layout=True`, `formula=True`, etc.) and is therefore a self-referential match. It is not a skill/source file and needs no fix. |

---

## Summary

- **Category A (wrong constructor flags):** 9 hits in the technical profile; only the two memory files still carry the outdated record in the mac-x86 repo (the operational code files have been corrected in the working tree).
- **Category B (`PPStructure`):** References in both repos; mac-x86 working tree now uses `PPStructure` correctly, while the technical profile still conflates PPStructure flags with `PaddleOCR()`.
- **Category C (router violations):** The biggest remaining violation is the **batch template in `ocr-and-documents/SKILL.md`** in both repos, which still hard-codes constructors. The mac-x86 verify one-liner and setup script also inline constructors.
- **Category D (tesseract/ocrmypdf stragglers):** Multiple active skill files still name Tesseract/`ocrmypdf` as fallbacks or examples, especially in `demurrage-monthly`, `demurrage-verification`, `vessel-nomination-vetting`, `research-intelligence`, and the multi-agent-debate references.
