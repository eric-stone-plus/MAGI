TASK: MAGI final audit. Contradictions, gaps, ambiguity, deployability.

**Auditor**: cw (systems/accuracy perspective)
**Sources audited** (four canonical sources with exact paths):
1. SOUL.md (core-rules): `/Users/ericstone/Public/hermes-core-rules-mac-x86/SOUL.md` L35, L102–129
2. MEMORY.md (technical profile): `/Users/ericstone/.hermes/profiles/technical/memories/MEMORY.md` L23–27
3. MAGI SKILL.md: `/Users/ericstone/.hermes/profiles/technical/skills/multi-agent-debate/magi/SKILL.md` (858 lines)
4. MAGI README.md: `/Users/ericstone/Public/MAGI/README.md` (204 lines)

**Supplementary source examined**:
- SOUL.md (technical profile): `/Users/ericstone/.hermes/profiles/technical/SOUL.md` L34, L114–122 — contains divergent MAGI description
- MEMORY.md (core-rules): `/Users/ericstone/Public/hermes-core-rules-mac-x86/memories/MEMORY.md` — contains zero MAGI content
- MAGI PROTOCOL.md: `/Users/ericstone/Public/MAGI/specs/PROTOCOL.md` — abstract spec (model-agnostic, correct)

---

## 1. CONTRADICTIONS

### C1. SOUL.md Split Personality: v1.2 vs v2.0 Across Two Active Profiles [HIGH]

Two `SOUL.md` files live in active profiles with incompatible MAGI descriptions:

| File | Location | MAGI Version | Description |
|------|----------|-------------|-------------|
| Core-rules SOUL.md L35 | `Public/hermes-core-rules-mac-x86/SOUL.md` | **v2.0** | OCR校验协议 v2.0 — Gold-dominant pipeline |
| Technical profile SOUL.md L34 | `.hermes/profiles/technical/SOUL.md` | **v1.2** | 辩证螺旋协议 v1.2 — 5阶段 (dialectical spiral) |

The technical profile SOUL.md (the profile this session runs under) still describes MAGI as a v1.2 dialectical spiral protocol with 5 phases. Its OCR section (L114–122) has a brief v2.0 note but **lacks the entire Gold tiered pipeline** (mimo→kimi→DS text tier, cost model, calibration requirements, circuit breaker) present in the core-rules version (L102–129). An agent loading either profile gets a different architecture description. This is a direct operational hazard — the 四 repo section (mandatory cognition) actively misinforms agents about what MAGI is.

### C2. Pipeline Topology: Pre-OCR Gate vs Post-OCR Gate [MEDIUM]

| Source | Gate placement | Criteria | Post-OCR gate |
|--------|---------------|----------|---------------|
| SOUL.md (core-rules) L115 | **Post-OCR** | DPI<150/contrast/skew>15° after Tesseract | None separate |
| SKILL.md L46 | **Pre-OCR** | DPI<150/contrast/skew>15° before Tesseract | OCR mean confidence <60% (L52) |
| README.md L164 | **Pre-OCR** | DPI<150/low contrast/skew>15° before OCR | None separate |

Two different pipeline topologies exist. In SOUL.md, Tesseract ALWAYS runs on scanned documents — the gate decides whether to use mimo or kimi on Tesseract's output. In SKILL.md/README.md, documents that fail the pre-OCR gate never reach Tesseract. These produce different behavior: SOUL.md's approach means even poor-quality scans get OCR'd (producing bad text that kimi must correct), while SKILL.md's approach skips OCR entirely and goes straight to kimi. The SKILL.md approach is more token-efficient but SOUL.md hasn't been updated.

### C3. MAGI Rules Absent from Core-Rules MEMORY.md [MEDIUM]

The evidence labels MEMORY.md as "(core-rules)" and quotes MAGI operational rules (田忌赛马, model assignments). However, the actual core-rules repo MEMORY.md (`Public/hermes-core-rules-mac-x86/memories/MEMORY.md`) contains **zero MAGI content** — it's entirely shipping/logistics/shell rules. The MAGI content resides only in the technical profile MEMORY.md (`.hermes/profiles/technical/memories/MEMORY.md` L23–27). This means:
- The canonical core-rules repo has no MAGI deployment instructions
- Anyone cloning `hermes-core-rules-mac-x86` gets no MAGI guidance
- The label "MEMORY.md (core-rules)" in evidence is factually wrong

### C4. Version Number Inconsistency [MEDIUM]

| Source | Version stated |
|--------|---------------|
| Technical profile SOUL.md L34 | v1.2 |
| Technical profile SOUL.md L120 | v2.0 |
| Core-rules SOUL.md L35 | v2.0 |
| Technical profile MEMORY.md L23 | v2.0 |
| SKILL.md header (L4) | **v2.1** |
| SKILL.md L36 | v2.0 |
| README.md badge (L15) | Protocol v2.0 |
| PROTOCOL.md §1 | v2.0 |

Four distinct version identifiers (v1.2, v2.0, v2.1) appear across sources. SOUL.md alone contains two. SKILL.md header says v2.1, body says v2.0. No single source of truth for version.

### C5. "Three Model" Count Inconsistency [LOW]

SKILL.md L115: "Three Gifts = three models: mimo-v2.5 + mimo-v2.5-pro + DS v4-pro. kimi is surgical fallback only." → **3 runtime models + 1 fallback = 4 total models**.

Technical MEMORY.md L27: "三模型全火力不降级: mimo-v2.5主力 + kimi + DS v4-pro" → **3 models including kimi**.

The system actually routes to 4 distinct models at runtime. Different sources count 3 vs 4. Affects capacity planning and cost modeling.

---

## 2. GAPS

### G1. Technical Profile SOUL.md Missing Gold Pipeline [HIGH]

The SOUL.md loaded by the active technical profile (`.hermes/profiles/technical/SOUL.md`) has only a 2-line MAGI summary at L120–121:
> "MAGI v2.0 (2026-06-17) — OCR 校验层，QUINTE 的视觉输入。扫描件或无文本层 PDF：Tesseract → MAGI (Gold/kimi 看原图校验 → Fr+Myrrh 语义+对抗) → 置信度拓扑 → QUINTE。"

Missing entirely: tiered pipeline (text-layer path vs scanned path), DS text tier, batch kimi escalation, cost model, calibration requirements (50-200 docs, ≥95%), circuit breaker. The full pipeline only exists in core-rules SOUL.md. This is the active profile's SOUL — an agent loading this profile has an incomplete architecture.

### G2. `calibrated_threshold` Undefined — Pipeline Inoperable [HIGH]

SKILL.md L731: "mimo confidence < calibrated_threshold (TBD from benchmark, NOT 0.7)."
SOUL.md L127: "置信度阈值从数据导出，非 0.7 拍脑袋。"

This parameter gates ALL kimi escalation. Without it, the system cannot decide when to invoke the most expensive model. Neither source specifies: calibration benchmark design, derivation methodology, who performs calibration, or what value to use pre-calibration. The pipeline is structurally inoperable without this value.

### G3. Pre-Deployment Calibration Not Executed [HIGH]

SKILL.md L735 Pitfall 0a-iii(1): QUINTE 4/4 blocking condition — "Calibrate mimo-v2.5 on 50-200 labeled shipping docs before deploy. Must achieve ≥95% precision at chosen threshold." This has not been performed. The pipeline fails its own deployment gate.

### G4. No kimi Failure Handling [HIGH]

Only mimo has a circuit breaker (mimo故障→all-kimi). No failure handling specified for:
- kimi API down during escalation → pipeline halts with no recovery
- kimi rate-limited on batch call → no retry strategy
- kimi returns garbled/incomplete output → no validation or fallback
- kimi timeout on large composite call → no split/retry logic

### G5. No DS v4-pro Failure Handling [HIGH]

DS v4-pro serves three roles: text-tier verify (text-layer PDFs), text-only field verify (low-confidence text fields), and Myrrh (adversarial audit). No circuit breaker or fallback for any DS failure. If DS is down, the text-layer PDF path, the text-only field escalation path, and Myrrh all halt simultaneously. This is a single-point-of-failure for 3 of 6 pipeline branches.

### G6. QUINTE Blocking Condition #5 Unresolved [MEDIUM]

SKILL.md L735 Pitfall 0a-iii(5): "Resolve whether mimo receives raw image + OCR text or text-only." Listed as QUINTE 4/4 blocking condition but remains unresolved across all four sources. The pipeline architecture is undefined at a fundamental input level — does Gold see the original image or only OCR text? This changes the entire visual verification premise.

### G7. Merge Consistency Gate Undefined [MEDIUM]

SOUL.md L122 pipeline: "merge 一致性校验" after batch kimi call.
SKILL.md L64 pipeline: "merge consistency gate → Fr+Myrrh."

What does this gate check? consistency between kimi output and mimo output? between multiple kimi field extractions? internal consistency of kimi's composite response? No source defines the check, pass/fail criteria, or failure action.

### G8. Convergence Gate Aggregation Underspecified [MEDIUM]

SKILL.md L187: "Composite per segment: visual(0.4) + semantic(0.3) + adversarial_risk(0.3). Overall ≥0.7, no CRITICAL → pass."

Per-segment composite is defined, but how per-segment scores aggregate to "Overall" is not specified. Simple mean? Weighted by segment importance? Minimum threshold per segment? Harmonic mean? Different aggregation functions produce different pass/fail outcomes.

### G9. mimo-v2.5 Confidence Score Semantics Undefined [MEDIUM]

The entire Gold tiered pipeline depends on mimo-v2.5 emitting per-field confidence scores (SKILL.md L56, README.md L169). However:
- mimo-v2.5 does not natively emit structured confidence scores
- No prompt engineering specification for confidence extraction
- No score scale definition (0-1? ordinal?)
- No calibration methodology between raw output and the threshold
- No validation that model-emitted "confidence" correlates with actual accuracy

This is the lynchpin of the entire escalation logic and it's unspecified.

### G10. Batch Kimi Escalation Format Underspecified [MEDIUM]

SKILL.md L134–150 shows a sketch kimi command but lacks:
- Maximum regions per composite call (what if 50+ ambiguous fields?)
- Region packaging format (base64 inline? file references? cropped image data?)
- Output parsing schema for stream-json
- Error handling for partial kimi output
- Validation that kimi addressed all submitted regions
- What to do if kimi's output doesn't parse as valid JSON

### G11. No End-to-End Accuracy Target [MEDIUM]

Component-level targets exist: Tesseract ~92% Chinese, mimo ≥95% precision, convergence ≥0.7. But no end-to-end accuracy target for the complete MAGI→QUINTE pipeline. What is the acceptable error rate for final verified text? Without this, there's no way to validate the system as a whole.

### G12. Text-Layer PDF Path Has No Gold Verification [MEDIUM]

SOUL.md L112: "文本层 PDF → zlib 提取 → DS verify → Fr+Myrrh → QUINTE." Text-layer PDFs bypass Gold (mimo-v2.5) entirely. If the text layer is corrupted, truncated, or contains encoding errors, DS verify may miss them. No Gold cross-check for text-layer documents. The pipeline trusts zlib extraction implicitly after a single DS pass.

### G13. No Pre-Flight Dependency Check [MEDIUM]

Pipeline depends on: qpdf, Tesseract 5.5.2, Python zlib, sips (macOS), mimo API, kimi CLI, DeepSeek API. No source defines a startup health check to verify all dependencies before processing. Mid-pipeline failures from missing dependencies have no recovery path.

### G14. Output Path Violates MEMORY.md Prohibition [MEDIUM]

SKILL.md L195 specifies output to `/tmp/magi-audit/<topic-slug>/`. Technical profile MEMORY.md L19 prohibits: "NEVER write output files... to /tmp or /private/tmp. These are ephemeral on macOS (cleared on reboot/system cleanup)." Intermediate audit artifacts lost on reboot — breaks crash recovery and audit trails.

---

## 3. AMBIGUITY

### A1. "逐字段" (per-field) — Selection vs Call Granularity [MEDIUM]

SOUL.md L109: "逐字段，非逐文档" — per-field, not per-document.
SOUL.md L126: "仅在 mimo 看不清且需要视觉推理时逐字段上场" — appears per-field only when needed.

SKILL.md uses batch per-document escalation (L111, L133–150). The Chinese "逐字段" is ambiguous between:
- (a) **Field selection**: kimi is invoked only for specific fields, not the whole document (consistent with batch)
- (b) **API call granularity**: each field gets its own kimi call (contradicts batch)

Without disambiguation, "逐字段" in SOUL.md could be read as supporting per-field API calls, contradicting SKILL.md's batch approach.

### A2. kimi Model Identity: Andante vs K2.7 Code [LOW]

SOUL.md L125: "kimi (Andante ¥49/月)"
Technical MEMORY.md L25: "kimi (K2.7 Code)"
SKILL.md L111: "kimi — Andante ¥49/月"
README.md L15: "kimi" (no qualifier)

Are Andante and K2.7 Code the same model? Different product lines of the same provider? No source clarifies. Operators provisioning API access need a canonical identifier.

### A3. Text-Layer Detection Method Undefined [LOW]

All sources branch on "Text layer?" but none specify the detection method. Is it `qpdf --show-npages` with text extraction? `pdftotext` byte count threshold? Mixed documents (some pages text, some scanned) are not addressed — does the pipeline fork per-page or per-document?

### A4. Frankincense "Semantic Classification" Categories Inconsistent [LOW]

README.md L78-83 lists Frankincense categories as: COSMETIC / LEXICAL / SEMANTIC / STRUCTURAL / QUINTE_CRITICAL.
SKILL.md L106 describes Frankincense as "semantic classification" with core question "Does the error change meaning?" — implying a simpler binary/ordinal classification than the 5-category taxonomy in README.md.
Neither SOUL.md nor MEMORY.md define Frankincense's classification output format.

### A5. Convergence Gate Weights Without Justification [LOW]

SKILL.md L187: "visual(0.4) + semantic(0.3) + adversarial_risk(0.3)." These weights appear with zero empirical or theoretical justification across all four sources. Are they derived from calibration data? Judgment-based? If calibration determines the confidence threshold, shouldn't it also determine the convergence weights?

### A6. "thinking wastes 80%" — Assertion Without Source [LOW]

MEMORY.md (technical) L24 and SKILL.md L731: "thinking wastes 80% of tokens with no accuracy gain." No benchmark, measurement, or citation. The MAGI skill references a SOF test (L150: "50K tokens → ~3K + 0-8K") which shows token savings but doesn't validate the 80% figure or the "no accuracy gain" claim. This is an unverified assertion used as architectural justification.

### A7. Tesseract-v2 "Alternative Parameters" Undefined [LOW]

SKILL.md L78: "For every Gold correction, run Tesseract with alternative parameters." What alternative parameters? Different PSM mode? Different language packs? Different preprocessing? The cross-check procedure is described as architectural but has zero operational specification.

---

## 4. DEPLOYABILITY

### D1. BLOCKED: Pre-Deployment Calibration Not Complete [CRITICAL]

QUINTE 4/4 blocking condition (SKILL.md Pitfall 0a-iii(1)): "Calibrate mimo-v2.5 on 50-200 labeled shipping docs before deploy. Must achieve ≥95% precision at chosen threshold." This calibration has not been performed. The pipeline cannot be deployed until calibration is complete and the ≥95% bar is met.

### D2. BLOCKED: `calibrated_threshold` Undefined [CRITICAL]

The parameter that gates all kimi escalation is undefined. Without it, the system cannot decide when to invoke the most expensive model. This is a hard deployment blocker — the pipeline's core routing logic is inoperable.

### D3. Active Profile SOUL.md Describes Wrong Architecture [HIGH]

The technical profile SOUL.md (active session) describes MAGI as v1.2 dialectical spiral (L34) with no Gold tiered pipeline. An agent loading this profile gets an obsolete architecture. The v2.0 Gold pipeline only exists in the core-rules SOUL.md. A deployer working from the active profile would build the wrong system.

### D4. Single-Point-of-Failure: DS v4-pro in 3 Roles [HIGH]

DS v4-pro is the sole model for: text-layer verify, text-only field verify, and Myrrh adversarial audit. If DS is down, three pipeline branches fail simultaneously. Only mimo has a circuit breaker — DS has none.

### D5. Five External Service Dependencies With No SLA [HIGH]

| Service | Pipeline role | Failure recovery |
|---------|--------------|-----------------|
| qpdf (local) | PDF decrypt/split | None |
| Tesseract 5.5.2 (local) | OCR engine | None |
| mimo API | Gold primary + Frankincense | Circuit breaker→all-kimi (underspecified) |
| kimi CLI | Gold fallback | None |
| DeepSeek API | Text tier + Myrrh | None |

Only mimo has any failure handling (and it's underspecified). The pipeline has 5 dependencies and protects against failure of 1.

### D6. Three Credential Systems With No Health Check [MEDIUM]

- mimo: `~/.local/share/mimocode/auth.json` (x25519 ECDH + OAuth)
- kimi: `~/.kimi-code/bin/kimi` CLI + env vars
- DeepSeek: Hermes provider config

No unified credential management. No pre-flight credential health check. Credential rotation requires touching three separate systems. Known edge case documented at SKILL.md L786: mimo credential pool path ≠ main session path → 401 even when session is healthy.

### D7. Output Path to /tmp — Ephemeral on macOS [MEDIUM]

SKILL.md L195: `/tmp/magi-audit/<topic-slug>/`. MEMORY.md L19: NEVER write to /tmp. Outputs lost on reboot. Violates crash recovery and audit trail requirements.

### D8. Volume Gate Not Operationalized [MEDIUM]

SKILL.md L735 Pitfall 0a-iii(6): "<8 docs/week → all-kimi (¥39/mo not justified)." Missing: measurement mechanism, lookback window, transition trigger (auto/manual), recovery condition (when to switch back). Without operationalization, this gate is a policy statement, not a deployable rule.

### D9. No Dry-Run / Test Mode [LOW]

No source describes a way to validate the pipeline without calling paid APIs. Operators cannot test routing logic, confidence thresholds, or circuit breaker behavior without incurring costs. Given that all three models are user-paid resources, this is a cost risk.

### D10. QUINTE Blocking Condition #5 Unresolved [LOW]

"Resolve whether mimo receives raw image + OCR text or text-only" — this QUINTE 4/4 blocking condition remains open. It's one of 6 deployment blockers and it's still unresolved.

---

## Summary

| Category | Count | CRITICAL | HIGH | MEDIUM | LOW |
|----------|-------|----------|------|--------|-----|
| Contradictions | 5 | 0 | 1 (C1) | 3 (C2, C3, C4) | 1 (C5) |
| Gaps | 14 | 0 | 3 (G1, G2, G3) | 9 (G4–G8, G10–G14) | 2 (G9) — wait, recheck... |

Let me recount:

**Contradictions**: 5 total — C1[HIGH], C2[MED], C3[MED], C4[MED], C5[LOW]
**Gaps**: 14 total — G1[HIGH], G2[HIGH], G3[HIGH], G4[HIGH], G5[HIGH], G6[MED], G7[MED], G8[MED], G9[MED], G10[MED], G11[MED], G12[MED], G13[MED], G14[MED]
**Ambiguity**: 7 total — A1[MED], A2[LOW], A3[LOW], A4[LOW], A5[LOW], A6[LOW], A7[LOW]
**Deployability**: 10 total — D1[CRIT], D2[CRIT], D3[HIGH], D4[HIGH], D5[HIGH], D6[MED], D7[MED], D8[MED], D9[LOW], D10[LOW]

| Category | Count | CRITICAL | HIGH | MEDIUM | LOW |
|----------|-------|----------|------|--------|-----|
| Contradictions | 5 | 0 | 1 | 3 | 1 |
| Gaps | 14 | 0 | 5 | 9 | 0 |
| Ambiguity | 7 | 0 | 0 | 1 | 6 |
| Deployability | 10 | 2 | 3 | 3 | 2 |

**Deployment verdict: NOT DEPLOYABLE.** Two CRITICAL blocking conditions prevent deployment: (1) pre-deployment calibration on 50–200 labeled documents not performed, (2) `calibrated_threshold` value undefined. Until these are resolved, the pipeline's core routing logic cannot function.

**Top 5 actions before deploy:**
1. Complete mimo-v2.5 calibration on 50–200 labeled shipping docs → derive `calibrated_threshold` → publish value
2. Update technical profile SOUL.md L34 from v1.2 to v2.0 with full Gold tiered pipeline
3. Define failure handling for kimi, DS v4-pro, and Frankincense (circuit breakers, retry, degraded modes)
4. Define merge consistency gate and convergence aggregation methodology
5. Specify mimo confidence score extraction (prompt engineering, calibration, validation)

**Architecture quality assessment (cv):** The four sources have converged on the core design (Gold-dominant, three-model, batch kimi escalation) and previous contradictions (per-field vs batch, 0.7 threshold, mimo cost) have been resolved. However, the system has two hard deployment blockers and the active SOUL.md still describes the wrong architecture. The design is logically coherent but not yet operationally complete.
