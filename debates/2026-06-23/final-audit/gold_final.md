**Gold verdict: rules + OCR + agent dispatch are largely correct/optimal in the live profile; repos have drift; a few cleanup items remain broken.**

I read the exact files you specified (plus workspace mirrors, SOUL.md, cross-repo-audit outputs, references, setup script, POSTMORTEM entries #12/#13, SKILL dispatch blocks, and key supporting docs). Also checked runtime (tesseract gone) + greps for Tesseract/Paddle/grok flags/locks/MAGI roles/v3.4.

### What verifies as correct + optimal (today's additions)

**1. OCR strategy (primary path)**
- Tesseract removed (confirmed: not in PATH, not via brew; only historical references in POSTMORTEM and the deprecation table).
- PaddleOCR 2.10.0 + PP-OCRv4 is sole primary engine for Intel Mac (paddlepaddle==3.0.0 ceiling; 3.x has no x86_64 wheel).
- PPStructure explicitly for tables/layout/formulas (with `table=True, layout=True, formula=True, cls_model_dir=...`).
- Correct invariants in [SKILL.md](/Users/ericstone/.hermes/profiles/technical/skills/productivity/ocr-and-documents/SKILL.md): `use_angle_cls=True` (mandatory), `enable_mkldnn=False` (mandatory), singleton, PyMuPDF rasterize first, zlib text layer before OCR, vision_analyze last.
- Decision tree, pitfalls, and batch template are precise.
- Reference [invocation-mac-intel-x86.md](/Users/ericstone/.hermes/profiles/technical/skills/productivity/ocr-and-documents/references/invocation-mac-intel-x86.md) correctly separates `PaddleOCR` (line) vs `PPStructure` (structure) and calls out the exact no-op bug (table= on wrong class).
- Setup script [setup_paddleocr_mac.sh](/Users/ericstone/Public/hermes-core-rules-mac-x86/scripts/setup_paddleocr_mac.sh) pins versions + verifies both engines with the right flags.
- USER/MEMORY/POSTMORTEM updated (USER L7, MEMORY L35/L39, POSTMORTEM #12 with cache-inspection root cause).

**2. Agent dispatch**
- cc=DeepSeek v4-pro (Anthropic-compat `claude-opus-4-20250514` → deepseek-v4-pro), `--effort xhigh`, triple anti-flash lock documented (zshrc + settings.json + cc_dispatch.py/script; CLAUDE_CODE_SUBAGENT_MODEL=claude-opus-4-20250514; reference cc-deepseek-switch-2026-06-23.md has the table + 2026-06-23 flash incident RCA).
- cw R1/R2 constraints explicit (R1: "READ ONLY... Do not execute... Produce analysis"; R2: "Do NOT use tool calls. Reason from the embedded R1 summaries"; pitfalls section details the three failure modes + detection + MAGI Fr substitute).
- Gold = `grok -p "..." --always-approve` (headless; table in live SKILL.md:42 explicitly calls out `grok build` as TUI-only, not for background). References also carry `--always-approve` examples.
- MAGI upgraded to code engine (R0 section in SKILL: post-QUINTE impl must use MAGI not hm solo; Gold=architect, Fr=explorer/file audit, Myrrh=verifier/runtime; exact PaddleOCR `table=True` no-op example as rationale).
- Firepower, process independence (independent terminal background), archive `~/Public/QUINTE/debates/...`, mkdir-before-dispatch, rx quality gate, JSON sidecar, substitution table, KANSA, Netsumon, KENGEN all present and consistent with SOUL.
- Cross-repo audit (POSTMORTEM #13 + ~/Public/QUINTE/debates/2026-06-23/cross-repo-audit/ with fr/gold/myrrh outputs): 9 findings described (HIGHBALL PROTOCOL missing is the standout CRITICAL; Win Gold=apiyi GPT-4o-mini for heterogeneity; model economy, gate sync, etc.). QUINTE+MAGI v3.4 tagged (v3.4-tag-fix.json + SKILL frontmatter + POSTMORTEM).

**3. Constitution 5 files (live ~/.hermes)**
- SOUL.md, memories/{USER,MEMORY,POSTMORTEM}.md, skills/multi-agent-debate/SKILL.md all carry the session changes (OCR #12, MAGI cross-repo #13, R0 code engine, dispatch rules, KENGEN 4x self-push note, v3.4-era content).
- Protocol selection table (MAGI default for ops, QUINTE for high-stakes) is new and present.
- Cross-audit dir and debate outputs exist for 2026-06-23.

### What's still broken (or not optimal)

**Repo / source-of-truth drift (biggest issue)**
- hermes-core-rules-mac-x86 (the rules mirror/source) is **not** in sync with the live ~/.hermes profile you edited today.
  - memories/USER.md (workspace): still opens with old "cc=MiMo v2.5-pro".
  - skills/multi-agent-debate/SKILL.md (workspace): dispatch table + bash examples still list `grok build` as primary for Gold/MAGI; some cc key sources and effort notes lag; cw constraints present but not identical.
  - memories/POSTMORTEM.md (workspace): cuts off before full #13 cross-repo + key learnings.
  - cross-repo-audit.json (workspace root): old 2026-06-22 version with ~5 contradictions, not the 9-finding MAGI audit.
- Live profile is the running truth; the source repo (intended for force-push mirror + cross-platform) lags. Syncing from source regresses rules. (hermes-core-rules-mac-x86 is explicitly "backup mirror" in docs, but it should still be authoritative for the 5 constitution files.)

**OCR strategy incomplete**
- Core ocr-and-documents + setup + refs are excellent.
- Domain skills still prescribe old Tesseract:
  - shipping/demurrage-verification/SKILL.md (line ~50): "扫描件用 Tesseract 400 DPI..."
  - devops/demurrage-monthly/references/ocr-sof-time-extraction.md and SKILL notes.
- These should route through the new primary or be updated (historical comparisons OK; prescriptive use is not).

**Dispatch doc nit (live SKILL)**
- Table correctly says `grok -p "..." --always-approve`.
- Bash example block (SKILL.md:113): `grok -p="<prompt>" > ...` omits the flag (and some comments mix modes). References are better, but the canonical dispatch section is inconsistent.

**Other gaps**
- Audit report: actual outputs live in the QUINTE debate dir (good), but the repo's .json is stale and no consolidated final .md appears to have been committed back into hermes-core-rules-mac-x86.
- v3.4 string coverage across the exact 5 files is uneven (SKILL/POSTMORTEM heavy; SOUL/USER/MEMORY use sections or minimal tags — content is updated but explicit version markers not uniform).
- Quick env check: tesseract gone (good); ~/paddleocr-venv not present (USER.md assumes it; setup script creates it optionally; skills prefer uv/paddleocr-venv pattern). Not fatal.
- No visible full 5-file post-edit QUINTE re-audit log in the new debate dir (cross-repo used MAGI doctors; the constitution-drift rule calls for re-QUINTE after multi-file changes).

**Summary single line**: Live rules/OCR/MAGI-dispatch + today's 5 constitution updates are correct and follow the stated strategy; the source repo (hermes-core-rules-mac-x86) has drifted and domain skills have Tesseract holdovers. Fix the source sync + migrate the two shipping/devops references + add the missing `--always-approve` to the SKILL example, then re-force the mirror. Everything else in the specified files checks out.
