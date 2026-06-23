# Six-Repo Cross-Consistency Audit Report

**Date:** 2026-06-23
**Scope:** Mac profile (`~/.hermes/profiles/technical`), Mac mirror (`~/Public/hermes-core-rules-mac-x86`), Win (`~/Public/hermes-core-rules-win`), RASHOMON, QUINTE, MAGI.

## Executive Summary

| Category | Findings |
|----------|----------|
| Mac profile vs Mac mirror identity | **3 of 4 files differ** (SOUL.md, USER.md, MEMORY.md). POSTMORTEM.md is identical. |
| Win Gold mapping consistency | **3 stale references** to grok/Gold→kimi in Win `MEMORY.md`. |
| QUINTE vs RASHOMON gate cardinality | **Canonical specs agree on 5 gates**, but stale "Four Gates" text survives in QUINTE ontology, RASHOMON essays/references, and Hermes reference docs. |
| MAGI typo-free | **No `sidecard` typo** found; MAGI cross-refs resolve; no typos detected in MAGI specs. |
| Stale-term scan (core + references) | `grok build` in Mac MEMORY; `Tesseract` in Win config/skills and Mac references; `Gold=kimi` / `grok unreachable` in Mac profile references. |

---

## 1. Mac Profile vs Mac Mirror (should be identical)

`POSTMORTEM.md` is byte-identical. The other three constitutional files are out of sync.

### 1.1 `SOUL.md`

| Location | Profile actual | Mirror actual | Expected fix |
|----------|----------------|---------------|--------------|
| `~/.hermes/profiles/technical/SOUL.md:3` | `Constitutional files: SOUL · USER · MEMORY · SKILL · POSTMORTEM.` | `Constitutional files: SOUL.md · memories/USER.md · memories/MEMORY.md · skills/multi-agent-debate/SKILL.md · memories/POSTMORTEM.md.` | Use the explicit path form from the mirror. |
| `~/.hermes/profiles/technical/SOUL.md:30` | Ends with `Sub-issues may open nested full QUINTE.` | Adds: `If agent drift is caused by unclear prompt → fix prompt and re-dispatch; do NOT use MAGI as substitute for a bad prompt.` | Add the anti-substitution sentence from the mirror. |
| `~/.hermes/profiles/technical/SOUL.md:40` | No `Agent patience` bullet after `rx quality gate`. | Adds full `Agent patience` bullet (600s hard cap, per-agent ceilings). | Add the `Agent patience` bullet from the mirror. |
| `~/.hermes/profiles/technical/SOUL.md:48` | Ends Netsumon section with `...Netsumon Phase 1 lightweight path).` | Adds: `**Before killing any agent**: verify zombie status — check uptime >600s AND ... Slow ≠ stalled.` | Add the zombie-check sentence from the mirror. |

### 1.2 `memories/USER.md`

| Location | Profile actual | Mirror actual | Expected fix |
|----------|----------------|---------------|--------------|
| `~/.hermes/profiles/technical/memories/USER.md:1` | Chinese shorthand: `Hermes:不碰default/codesign/keychain。Provider切换用--provider/--model或isolated profile(用完rm -rf)。DS v4-pro max(hm/omp/cw/rx), cc=DS v4-pro(...)。flash禁止。compression 85%→80%+提醒切session。MAGI三模:Gold=grok -p --always-approve,Fr=kimi,Myrrh=mimo。delegate_task禁用于QUINTE/MAGI。hm禁solo架构决策。cc key:env→~/.codewhale/config。` | English: `Hermes config: never touch default/codesign/keychain. Provider switch via --provider/--model or isolated profile (rm -rf after use). DS v4-pro max (hm/omp/cw/rx), cc=DeepSeek v4-pro (via Anthropic-compat, claude-opus-4→v4-pro, effort=xhigh+ultracode, 三重锁防flash), flash forbidden. compression 85%→80%+ remind to switch session. Install from original sources. QUINTE v3.4: MAGI three-model (grok-build/kimi K2.7/mimo-v2.5-pro) embedded R1 Mode B. delegate_task banned in QUINTE/MAGI domain. R2 embed content, no /tmp paths. cc plain text only, no stream-json. hm forbidden from solo architecture decisions. cc_dispatch.py key: env→~/.codewhale/config fallback.` | Harmonize on English expanded form, **but replace mirror's stale `grok-build` with `grok -p --always-approve`**. |
| `~/.hermes/profiles/technical/memories/USER.md:5` | `Reports: .md+.html双版,文件放真实位置(~/Downloads/DEVELOPMENT/等)非/tmp。禁架构图/ASCII图(宪法文件+对话输出均适用)。Tone professional restrained。` | `Reports: produce .md + .html dual versions (md charts + HTML visualization). Tone professional, restrained. Output files must go to real locations (e.g. ~/Downloads/DEVELOPMENT/), never /tmp sandbox only — user explicitly corrected: "archive to real location, not sandbox."` | Use the expanded English version from the mirror. |
| `~/.hermes/profiles/technical/memories/USER.md:9` | Extra line: `2026-06-23明确：不要画架构图(ASCII/框图均免)。直接陈述。全修走MAGI三模不要hm solo。Win Gold=apiyi GPT-4o-mini(grok被公司防火墙阻)。` | File ends at line 7. | Remove Win-specific / duplicate directive from Mac `USER.md`; keep only Mac-relevant text. |

### 1.3 `memories/MEMORY.md`

| Location | Profile actual | Mirror actual | Expected fix |
|----------|----------------|---------------|--------------|
| `~/.hermes/profiles/technical/memories/MEMORY.md:33` | `审计目录勿早清:等通知收齐再rm -rf。mirror用force push。process list+therm确认无残留。行号引用脆弱→用section名。` | `审计目录勿早清: 等所有agent通知收齐、输出已读后再rm -rf。丢输出=浪费算力。hermes-core-rules-mac-x86是备份镜像repo，force push覆盖远程正确。火力全开后跑process list+therm确认无残留。USER=机器配置+状态，非个人隐私。宪法行号引用脆弱，偏好section名称。` | Adopt the mirror's expanded wording. |
| `~/.hermes/profiles/technical/memories/MEMORY.md:39` | `文档规范：全部md文档禁止ASCII架构图/流程图——容易读取错误(2026-06-23用户纠正)。宪法文件同样禁止。字体字号统一。` | `文档规范：宪法文件(SOUL/USER/SKILL/MEMORY/POSTMORTEM)禁止架构图/ASCII图——歧义+格式错乱。所有md文档字体字号统一。` | Adopt the mirror's explicit file list and rationale. |
| `~/.hermes/profiles/technical/memories/MEMORY.md:43` | `QUINTE archive: ~/Public/QUINTE/debates/YYYY-MM-DD/<topic>/, no /tmp, mkdir -p before dispatch.` | `QUINTE debate archives: /Users/ericstone/Public/QUINTE/debates/YYYY-MM-DD/<topic-slug>/. Never use /tmp/quinte-audit/. Directory must exist before agent dispatch (shell redirect fails silently otherwise).` | Adopt the mirror's expanded archive rule. |
| `~/.hermes/profiles/technical/memories/MEMORY.md:49` | `MAGI最高权限:sed/write_file/rm免请示。MAGI=手(执行),QUINTE=嘴(裁决)。三模:Gold(grok包年→架构)+Fr(kimi包月→勘察)+Myrrh(mimo按量→验证)。Win Gold=apiyi GPT-4o-mini。RASHOMON/HIGHBALL不设版本号。cc effort:xhigh+ultracode=DeepSeek天花板。` | `MAGI最高权限: sed/write_file/rm直接执行不请示。QUINTE=嘴(裁决辩论),MAGI=手(执行实现)。MAGI三模:Gold(grok包年)架构+Fr(kimi包月)勘察+Myrrh(mimo按量)验证执行。Win Gold=apiyi GPT-4o-mini(公司防火墙阻grok)。RASHOMON/HIGHBALL不设版本号(哲学/架构,非产品)。cc effort: xhigh+ultracode=DeepSeek天花板(max=UI假象)。` | Adopt the mirror's refined wording (but see §5.1 for `grok build` cleanup). |

---

## 2. Win Gold Mapping Consistency

Canonical Win mapping (SOUL.md, USER.md, MEMORY.md:37) is `Gold = apiyi GPT-4o-mini` because grok is blocked by the company firewall. Stale remnants persist in `MEMORY.md`.

| File:line | Actual text | Expected fix |
|-----------|-------------|--------------|
| `~/Public/hermes-core-rules-win/memories/MEMORY.md:31` | `模型经济：kimi(token)+grok(年费)无限→代码/审计/grep往死里用。DS按量仅协调审查。mimo(¥39/月)辅助。` | Update to Win model economy: `apiyi GPT-4o-mini` (Gold) plus `kimi`/`mimo`; remove `grok(年费)无限` because grok is blocked on Win. |
| `~/Public/hermes-core-rules-win/memories/MEMORY.md:33` | `代码不用DS写(经济原因): kimi+grok+mimo三模并行→QUINTE取精→hm合。grok最强(工业),kimi中道,mimo最简。` | Replace `grok` with `apiyi GPT-4o-mini` for the Win three-model setup: `kimi+apiyi+mimo三模并行... apiyi最强(工业)...` |
| `~/Public/hermes-core-rules-win/memories/MEMORY.md:45` | `kimi工程判断最强—架构/结构/分类决策优先用kimi。Gold→kimi用对话式prompt。kimi输出16KB+。kimi=文件勘察(给路径)、mimo=验证、cc=人话+Python wrapper。` | Change `Gold→kimi` to `Gold→apiyi GPT-4o-mini` (or `Fr→kimi` for file exploration). Win Gold must not map to kimi. |

**Note:** `~/Public/hermes-core-rules-win/memories/POSTMORTEM.md:254-258` correctly records the historical `Win Gold=kimi→apiyi GPT-4o-mini` fix and is excluded as a POSTMORTEM historical entry.

---

## 3. QUINTE vs RASHOMON Gate Cardinality

Both canonical gate specs now define **five gates** (Amamon, Kyōmon, Shōmon, Kan'nukimon, Kennōmon). Discrepancies are stale references that still say "Four Gates."

| File:line | Actual text | Expected fix |
|-----------|-------------|--------------|
| `~/Public/QUINTE/ontology/quinte-ontology.md:34` | `\| -1 \| Four Gates \| hm (parallel) \| 雨門·鏡門·證門·閂門 + cross-repo check (~5s) \|` | Rename to `Five Gates` and add `憲門 Kennōmon` to the list. |
| `~/Public/QUINTE/ontology/quinte-ontology.md:45` | `### Gate (Four Gates)` | Rename to `### Gate (Five Gates)`. |
| `~/Public/QUINTE/ontology/quinte-ontology.md:49-53` | Table lists only four gates (Amamon, Kyōmon, Shōmon, Kan'nukimon). | Add fifth row for `憲門 Kennōmon`. |
| `~/Public/RASHOMON/REFINED-BRUTE-FORCE.md:29` | `- Four Gates: targeted failure-mode defense, not "run more checks"` | Update to `Five Gates` and include `憲門 Kennōmon`. |
| `~/Public/RASHOMON/REFINED-BRUTE-FORCE.md:61` | `...the Four Gates, each targeting a specific failure mode...` | Update to `Five Gates`. |
| `~/Public/RASHOMON/references/mathematical-foundations.md:57` | `**QUINTE mapping**: Provides mathematical vocabulary for the Four Gates' decision logic:` | Update to `Five Gates'`. |

### Stale "four gates" references in Hermes skill/reference trees

These files are part of the six-repo search scope and still describe the pre-Kennōmon four-gate model.

| File:line | Actual text | Expected fix |
|-----------|-------------|--------------|
| `~/.hermes/profiles/technical/skills/software-development/subagent-driven-development/references/gates-taxonomy.md:7` | `## The four gate types` | Update to `five gate types` and add Kennōmon. |
| `~/.hermes/profiles/technical/skills/software-development/subagent-driven-development/references/gates-taxonomy.md:73` | `## Example — a review loop with all four gate types` | Update to `all five gate types`. |
| `~/.hermes/profiles/technical/skills/multi-agent-debate/references/quinte-conceptual-taxonomy.md:35` | `- **Four gates**: mnemonic architecture — creates clean namespace separate from CS vocabulary` | Update to `Five gates`. |
| `~/.hermes/profiles/technical/skills/multi-agent-debate/references/platform-agnostic-quinte.md:13` | `...the protocol itself (four gates, R1-R2-R3, anti-drift) runs on any platform.` | Update to `five gates`. |
| `~/.hermes/profiles/technical/skills/multi-agent-debate/references/kengen-push-authorization.md:3` | `Separate from the four gates — this is operational safety, not epistemology.` | Update to `five gates`. |
| `~/.hermes/profiles/technical/skills/multi-agent-debate/references/rashomon-diagram-design.md:22` | `Wide vertical boxes with ▼ arrows, four gates stacked:` | Update to `five gates stacked`. |
| `~/.hermes/profiles/technical/skills/creative/html-design-variants/templates/generator.py:93` | `<div class="card-title">Four Gates</div>` | Update to `Five Gates` and add Kennōmon card. |
| `~/.hermes/profiles/technical/skills/creative/html-design-variants/templates/generator.py:95` | `<div class="section-label">四道門 · THE FOUR GATES</div>...<h2 class="section-title">Every session passes through <em>four gates</em></h2>` | Update to `五道門 · THE FIVE GATES` and `five gates`. |
| `~/Public/hermes-core-rules-mac-x86/skills/software-development/subagent-driven-development/references/gates-taxonomy.md:7` | `## The four gate types` | Same as profile counterpart. |
| `~/Public/hermes-core-rules-mac-x86/skills/software-development/subagent-driven-development/references/gates-taxonomy.md:73` | `## Example — a review loop with all four gate types` | Same as profile counterpart. |
| `~/Public/hermes-core-rules-mac-x86/skills/multi-agent-debate/references/quinte-conceptual-taxonomy.md:35` | `- **Four gates**: ...` | Same as profile counterpart. |
| `~/Public/hermes-core-rules-mac-x86/skills/multi-agent-debate/references/platform-agnostic-quinte.md:13` | `...four gates...` | Same as profile counterpart. |
| `~/Public/hermes-core-rules-mac-x86/skills/multi-agent-debate/references/kengen-push-authorization.md:3` | `Separate from the four gates...` | Same as profile counterpart. |
| `~/Public/hermes-core-rules-mac-x86/skills/multi-agent-debate/references/rashomon-diagram-design.md:22` | `...four gates stacked:` | Same as profile counterpart. |
| `~/Public/hermes-core-rules-win/skills/software-development/subagent-driven-development/references/gates-taxonomy.md:7` | `## The four gate types` | Same fix. |
| `~/Public/hermes-core-rules-win/skills/software-development/subagent-driven-development/references/gates-taxonomy.md:73` | `## Example — a review loop with all four gate types` | Same fix. |
| `~/Public/hermes-core-rules-win/skills/multi-agent-debate/references/quinte-conceptual-taxonomy.md:35` | `- **Four gates**: ...` | Same fix. |
| `~/Public/hermes-core-rules-win/skills/multi-agent-debate/references/platform-agnostic-quinte.md:13` | `...four gates...` | Same fix. |
| `~/Public/hermes-core-rules-win/skills/multi-agent-debate/references/kengen-push-authorization.md:3` | `Separate from the four gates...` | Same fix. |
| `~/Public/hermes-core-rules-win/skills/multi-agent-debate/references/rashomon-diagram-design.md:22` | `...four gates stacked:` | Same fix. |

---

## 4. MAGI Typo Check

| Check | Result |
|-------|--------|
| `sidecard` typo in MAGI specs | **None found.** All occurrences use `sidecar`. |
| Cross-repo reference `../../RASHOMON/specs/theoretical-foundation.md` | **Resolves** — file exists. |
| Other obvious typos in `~/Public/MAGI/specs/PROTOCOL.md` and `~/Public/MAGI/specs/theoretical-foundation.md` | None detected. |

**Conclusion:** MAGI spec files are typo-free with respect to the target terms.

---

## 5. Stale-Term Scan Hits (non-historical)

### 5.1 `grok build` (outside annotations that warn it is the TUI)

| File:line | Actual text | Expected fix |
|-----------|-------------|--------------|
| `~/.hermes/profiles/technical/memories/MEMORY.md:23` | `...grok最强(工业,默认grok build,包年无限)。...` | Replace `grok build` with `grok -p --always-approve`. |
| `~/.hermes/profiles/technical/memories/MEMORY.md:35` | `MAGI:Gold(grok build)+Fr(kimi)+Myrrh(mimo API)。...` | Replace `Gold(grok build)` with `Gold(grok -p --always-approve)` or `Gold(grok)`. |
| `~/Public/hermes-core-rules-mac-x86/memories/MEMORY.md:23` | `...grok最强(工业,默认grok build,包年无限)。...` | Same as profile counterpart. |
| `~/Public/hermes-core-rules-mac-x86/memories/MEMORY.md:35` | `MAGI:Gold(grok build)+Fr(kimi)+Myrrh(mimo API)。...` | Same as profile counterpart. |
| `~/Public/hermes-core-rules-mac-x86/memories/USER.md:1` | `...MAGI three-model (grok-build/kimi K2.7/mimo-v2.5-pro)...` | Replace `grok-build` with `grok -p --always-approve` (or simply `grok`). |

**Not flagged:** `SKILL.md` dispatch tables that annotate `` `grok build`=TUI, NOT for background `` are explanatory annotations and are correct.

### 5.2 `Tesseract` outside Deprecated / OCR / Historical references

| File:line | Actual text | Expected fix |
|-----------|-------------|--------------|
| `~/Public/hermes-core-rules-win/memories/USER.md:7` | `OCR: PaddleOCR (Chinese/mixed), Tesseract (English fallback).` | Either remove Tesseract (adopt PaddleOCR-only, matching Mac) or explicitly annotate as `[DEPRECATED: Win-only English fallback]` and move fallback policy to the `ocr-and-documents` skill. |
| `~/Public/hermes-core-rules-win/SETUP.md:85` | `- **OCR**: PaddleOCR x86_64 (Chinese/mixed). Tesseract as English fallback via offline installer.` | Same as above. |
| `~/Public/hermes-core-rules-win/skills/devops/demurrage-monthly/SKILL.md:254` | `...若用 OCR 会遗漏 F-L 项。` (context compares `.doc` extraction to `Tesseract OCR ~92%`) | Update OCR reference to PaddleOCR and current accuracy baseline. |
| `~/Public/hermes-core-rules-win/skills/devops/demurrage-monthly/references/ocr-sof-time-extraction.md:9` | `1. **OCR**: Tesseract 5.5.2 (brew) with chi_sim+chi_tra+eng` | Migrate to PaddleOCR; archive this reference as historical if retained. |
| `~/Public/hermes-core-rules-win/skills/shipping/demurrage-verification/SKILL.md:50` | `- 扫描件用 Tesseract 400 DPI, --psm 6, -l eng` | Replace with PaddleOCR guidance. |
| `~/.hermes/profiles/technical/skills/multi-agent-debate/references/platform-compatibility-mirage.md:42` | `2. Tesseract 5.5.2（离线英文兜底）` | Mac removed Tesseract; delete or mark as historical. |
| `~/.hermes/profiles/technical/skills/multi-agent-debate/references/cc-cw-drift-2026-06-07-pm.md:12` | `SOUL.md OCR: Tesseract only (Flash removed).` | This is a June-7 audit snapshot; update to reflect current PaddleOCR-only policy or move to `references/historical/`. |
| `~/Public/hermes-core-rules-mac-x86/skills/multi-agent-debate/references/platform-compatibility-mirage.md:42` | `2. Tesseract 5.5.2（离线英文兜底）` | Same as profile counterpart. |
| `~/Public/hermes-core-rules-mac-x86/skills/multi-agent-debate/references/cc-cw-drift-2026-06-07-pm.md:12` | `SOUL.md OCR: Tesseract only (Flash removed).` | Same as profile counterpart. |

### 5.3 `Gold=kimi` / `Gold→kimi` / `grok unreachable` outside POSTMORTEM

| File:line | Actual text | Expected fix |
|-----------|-------------|--------------|
| `~/Public/hermes-core-rules-win/memories/MEMORY.md:45` | `Gold→kimi用对话式prompt。` | Change to `Gold→apiyi GPT-4o-mini用对话式prompt` (or route file-exploration tasks to `Fr→kimi`). |
| `~/.hermes/profiles/technical/skills/multi-agent-debate/references/cross-platform-constitution-audit.md:18` | `\| MAGI model mapping \| Gold→grok, Fr→kimi, Myrrh→mimo \| Gold=kimi (grok unreachable) \| Platform-dependent OK \|` | Update Win column to `Gold=apiyi GPT-4o-mini (grok blocked by company firewall)`. |
| `~/.hermes/profiles/technical/skills/multi-agent-debate/references/cross-platform-alignment-methodology.md:59` | `...Mac grok functional (vs Win grok unreachable → Gold=kimi).` | Update to `Win grok unreachable → Gold=apiyi GPT-4o-mini`. |
| `~/.hermes/profiles/technical/skills/multi-agent-debate/references/cross-platform-alignment-methodology.md:66` | `- **Check machine capabilities before overriding model mappings**: Win uses kimi for Gold because grok is unreachable.` | Update to `Win uses apiyi GPT-4o-mini for Gold because grok is unreachable`. |
| `~/.hermes/profiles/technical/skills/multi-agent-debate/references/cross-session-audit-staleness.md:13` | `...Win Gold=kimi (already changed to apiyi)...` | Mentions the issue as already-fixed; acceptable as audit log, but recommend archiving or updating to avoid stale-term hits. |

### 5.4 `sidecard`

**No occurrences found** in any of the six repos. MAGI and QUINTE specs use the correct spelling `sidecar`.

---

## 6. Excluded as Historical / Audit Logs

The following files mention stale terms but are explicitly version-history, POSTMORTEM, or audit-log material and were excluded from the discrepancy list above:

- `~/.hermes/profiles/technical/memories/POSTMORTEM.md` and `~/Public/hermes-core-rules-mac-x86/memories/POSTMORTEM.md` — Tesseract removal narrative and `Win Gold=kimi→apiyi` fix.
- `~/Public/hermes-core-rules-win/memories/POSTMORTEM.md` — same cross-platform historical entries.
- `~/Public/QUINTE/CHANGELOG.md:60` — version-history entry `Parallel Four Gates`.
- `~/Public/MAGI/audit/model-name-leak-scan.md` — extensive debate/audit log containing many `Tesseract`, `Gold→kimi`, and model-name mentions. Retained as historical audit evidence.

---

## 7. Recommended Action Order

1. **Win `MEMORY.md` Gold cleanup** (highest operational risk — wrong Gold mapping can break MAGI heterogeneity).
2. **Mac profile ↔ Mac mirror sync** so the four constitutional files are byte-identical; apply the `grok-build` fix while reconciling `USER.md`.
3. **QUINTE ontology** update to `Five Gates` to match QUINTE `specs/PROTOCOL.md` and RASHOMON `GATES.md`.
4. **RASHOMON essays/references** update to `Five Gates` or move to a `references/historical/` directory.
5. **Tesseract migration** in Win `USER.md`/`SETUP.md`/skills and Mac stale references.
6. **Reference doc sweep** for `Gold=kimi` and `Four Gates` leftovers.
