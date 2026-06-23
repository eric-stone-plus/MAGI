TASK: MAGI final audit. Contradictions, gaps, ambiguity, deployability.

# OMP R1 — Operations Perspective Audit

**Role**: omp (operations)  
**Scope**: MAGI architecture across four canonical sources  
**Sources audited**:
- SOUL.md (`~/.hermes/profiles/technical/SOUL.md`)
- MEMORY.md (`~/.hermes/profiles/technical/memories/MEMORY.md`)
- MAGI SKILL.md (`~/.hermes/profiles/technical/skills/multi-agent-debate/magi/SKILL.md`, 858 lines)
- MAGI README.md (`~/Public/MAGI/README.md`, public repo, 204 lines)

---

## 1. CONTRADICTIONS

### C1 · Gold Dispatch: kimi-primary vs mimo-primary (MEMORY.md internally, MEMORY vs SKILL)
**Severity: HIGH**

MEMORY.md L23 states:
> `Gold→kimi(-p one-shot batch)`

MEMORY.md L25–26 states:
> `MAGI Gold architecture: mimo-v2.5 primary (cheapest multimodal) → kimi surgical fallback per-field`

These two statements in the same file contradict each other. L23 describes kimi as the Gold dispatch target; L25–26 describes mimo-v2.5 as primary with kimi as fallback only. An operator reading MEMORY.md for dispatch instructions cannot determine which model to route Gold to.

SKILL.md L110, L460–478, and README.md L60 all consistently say mimo-v2.5 is primary, kimi is fallback. The consensus across 3 of 4 sources is mimo-primary, but MEMORY.md L23 is an active contradiction that must be resolved.

### C2 · Version Number Inconsistency (all four sources)
**Severity: MEDIUM**

| Source | Version stated |
|--------|---------------|
| SOUL.md L34 (four-repo section) | MAGI v1.2 |
| SOUL.md L120 (OCR strategy) | MAGI v2.0 |
| MEMORY.md L23 | MAGI v2.1 |
| SKILL.md header | version: "2.1" |
| SKILL.md L36 (architecture) | "v2.0" |
| README.md badge + diagram | Protocol v2.0 |

Four different version identifiers appear across sources: v1.2, v2.0, v2.1. SOUL.md alone contains both v1.2 and v2.0. An operator deploying "the current version" has no canonical reference.

### C3 · "Three Models" Count: 3 or 4?
**Severity: MEDIUM**

SKILL.md L115:
> `Three Gifts = three models: mimo-v2.5 + mimo-v2.5-pro (both Lite ¥39/月) + DS v4-pro (pay-per-use). kimi Andante ¥49/月 is surgical fallback only.`

MEMORY.md L27:
> `MAGI Gold 三模型全火力不降级: mimo-v2.5主力(Lite ¥39/月)+kimi(Andante ¥49/月,thinking=high)+DS v4-pro(max)`

SKILL.md enumerates 3 base models + kimi as a 4th (fallback). MEMORY.md counts kimi as one of the 3 "full firepower" models. The operator needs to know: is this a 3-model system with a 4th model as fallback, or a 3-model system where kimi is one of the 3? SKILL.md L115 explicitly says "Three Gifts = three models" — but the system actually uses 4 distinct models at runtime. This affects capacity planning and cost modeling.

### C4 · Text-Layer Path: DS-only vs DS+Fr+Myrrh
**Severity: MEDIUM**

SOUL.md L9 pipeline (condensed):
> `text-layer→zlib→DS / scanned→Tesseract→...→merge→Fr+Myrrh→QUINTE`

The "/" separates paths. The text-layer path terminates at "DS" without Fr+Myrrh. The scanned path includes Fr+Myrrh.

SKILL.md L41 pipeline diagram:
> `Document → Text layer? → YES → zlib extract → DS verify → Fr+Myrrh → QUINTE`

SKILL.md shows Fr+Myrrh on both paths. README.md L160 matches SKILL.md. SOUL.md omits Fr+Myrrh from the text-layer path. An operator building the pipeline from SOUL.md would skip semantic+adversarial review for text-layer documents — a significant quality regression.

### C5 · HIGHBALL Applicability to MAGI
**Severity: LOW (semantic tension)**

MEMORY.md L17:
> `MAGI=OCR校验预处理器(伯利恒,main,非QUINTE平级,不经过HIGHBALL)`

SKILL.md L493–497:
> `**HIGHBALL** — All 4 components apply to MAGI: KANSA (監査): Phase 3 dual-audit... KENGEN (権限): Phase 4 action items... BANNIN (番人): continuous monitoring... KOZO (小僧): Gift output format compliance check`

MEMORY.md says MAGI "does not pass through HIGHBALL." SKILL.md says all 4 HIGHBALL components apply. These positions are reconcilable (MEMORY.md may mean MAGI is subordinate, not governed by HIGHBALL gate logic), but the surface contradiction creates ambiguity for operators configuring the constraint layer.

---

## 2. GAPS

### G1 · `calibrated_threshold` — Undefined Critical Parameter [HIGH]
**Source**: SKILL.md L56, L58, L111, L475, L731

The entire Gold→kimi escalation path depends on `calibrated_threshold`. SKILL.md L731 explicitly states:
> `calibrated_threshold (TBD from benchmark, NOT 0.7)`

This value is undefined. Without it, kimi escalation is inoperable — the system cannot decide when to invoke the most expensive model. This is a deployment blocker.

### G2 · Pre-Deployment Calibration Not Executed [HIGH]
**Source**: SKILL.md Pitfall 0a-iii(1), L735

> `Calibrate mimo-v2.5 on 50-200 labeled shipping docs before deploy. Must achieve ≥95% precision at chosen threshold.`

This calibration is a QUINTE-mandated blocking condition (4/4 agents, 2026-06-18). It has not been performed. The pipeline cannot be deployed until calibration is complete and the ≥95% precision bar is met.

### G3 · Volume Gate Not Operationalized [MEDIUM]
**Source**: SKILL.md Pitfall 0a-iii(6), L735

> `Volume gate: <8 docs/week → all-kimi (¥39/mo not justified).`

The volume gate is specified as a QUINTE blocking condition but lacks:
- Measurement mechanism (how is doc count tracked?)
- Lookback window (trailing 7 days? calendar week?)
- Transition trigger (auto or manual switch?)
- Recovery condition (when to switch back to mimo-primary?)

### G4 · Circuit Breaker Implementation Missing [MEDIUM]
**Source**: MEMORY.md L27, SKILL.md Pitfall 0a-iii(3), README.md L181

> `Circuit breaker: mimo故障→all-kimi`

Mentioned in 3 sources but none specify:
- Failure detection criteria (HTTP 401 only? timeout? degraded accuracy? consecutive failures?)
- Detection mechanism (per-call check? health endpoint polling?)
- Auto-fallback vs alert-and-wait
- Recovery procedure (when/how to switch back)
- State persistence (survives restart?)

### G5 · Batch Kimi Escalation Format Unspecified [MEDIUM]
**Source**: SKILL.md L133–150

SKILL.md describes "batch composite kimi call with all cropped regions" but the operational details are missing:
- Region extraction and packaging format (base64 inline? file paths?)
- Prompt template (SKILL.md L137–139 shows a sketch, not a validated template)
- Output parsing schema (JSON structure? error handling?)
- Size limits (how many regions per batch? what if document has 50+ ambiguous fields?)

### G6 · No Monitoring or Telemetry [MEDIUM]
None of the four sources mention logging, metrics, alerting, or health checks. An operations-critical pipeline processing documents and routing between paid API services has zero observability design. Operators cannot:
- Track per-model cost accumulation
- Detect accuracy degradation
- Monitor convergence gate pass rates
- Alert on circuit breaker activation

### G7 · Output Path Violates MEMORY.md Prohibition [MEDIUM]
**Source**: SKILL.md L195 vs MEMORY.md L19

SKILL.md L195 specifies output to `/tmp/magi-audit/<topic-slug>/`. MEMORY.md L19 prohibits writing to `/tmp`:
> `NEVER write output files... to /tmp or /private/tmp. These are ephemeral on macOS (cleared on reboot/system cleanup).`

The SKILL.md output path contradicts a standing memory rule. Intermediate audit artifacts written to `/tmp` will be lost on reboot, breaking crash recovery and audit trails.

### G8 · mimo-v2.5 Confidence Score Semantics Undefined [MEDIUM]
The pipeline hinges on per-field confidence scores from mimo-v2.5 (SKILL.md L56, README.md L169). But:
- How does mimo-v2.5 emit confidence scores? (Not a native feature of the model)
- What is the score scale and meaning? (0-1 probability? ordinal?)
- How was the score calibrated against ground truth?
- What prompt engineering extracts structured confidence?

### G9 · Tesseract-v2 Cross-Check Parameters Undefined [LOW]
**Source**: SKILL.md L78

> `For every Gold correction, run Tesseract with alternative parameters.`

"Alternative parameters" are never specified. Without them, Tesseract-v2 is not reproducible and cannot be integrated into an automated pipeline.

### G10 · No Pre-Flight Dependency Check [LOW]
The pipeline depends on: qpdf, Tesseract 5.5.2, Python zlib, sips (macOS), mimo API, kimi CLI, DeepSeek API. No source defines a pre-flight health check to verify all dependencies are available before starting a MAGI run.

---

## 3. AMBIGUITY

### A1 · "mimo-v2.5" vs "mimo-v2.5-pro" Model Distinction
MEMORY.md L25 clarifies: `mimo-v2.5 is multimodal (can see images), mimo-v2.5-pro is text-only.` But README.md uses "mimo-v2.5-pro" in the architecture diagram without noting the text-only limitation. An implementor reading only the public README would not know that Frankincense's model cannot see images.

### A2 · kimi Model Identity
SOUL.md says "kimi(Andante ¥49/月)". MEMORY.md L25 says "kimi (K2.7 Code)". SKILL.md uses both "kimi" and "kimi Andante ¥49/月". README.md says only "kimi". Three different identifiers for the same model. Is the model "K2.7 Code" or "Andante"? Are these the same thing? Operators provisioning API access need a canonical identifier.

### A3 · Convergence Gate Composite Score
SKILL.md L188: `Composite per segment: visual(0.4) + semantic(0.3) + adversarial_risk(0.3). Overall ≥0.7, no CRITICAL → pass.`

How is per-segment composite aggregated to overall? Simple mean? Weighted by segment importance? Minimum? The computation is underspecified. Also: what distinguishes CRITICAL from non-CRITICAL? README.md defines CRITICAL as Myrrh's top severity, but the exact threshold is ambiguous.

### A4 · "Merge Consistency Gate" Never Defined
SKILL.md L64 pipeline diagram shows `→ merge consistency gate → Fr+Myrrh → QUINTE` after the batch kimi call. This gate appears nowhere else — not in the convergence gate section, not in the output structure, not in README.md. What does it check? What's the pass condition?

### A5 · Version Numbering (see C2)
The ambiguity itself is a contradiction — operators cannot identify the canonical version.

### A6 · "Three Gifts = three models" vs Actual Model Count (see C3)
SKILL.md asserts 3 base models + kimi fallback. MEMORY.md counts kimi as a core model. The operator doesn't know whether to provision 3 or 4 API endpoints.

### A7 · Text-Layer Detection Method
SOUL.md and SKILL.md pipelines branch on "Text layer?" but no source defines the detection method. Is it `qpdf --show-npages` with text extraction? `pdftotext` byte count threshold? Mixed documents (some pages text, some scanned) are not addressed.

### A8 · PDF-to-Image Pipeline for Tesseract
SKILL.md Pitfall 0c describes `qpdf --split-pages` + `sips` for kimi image conversion. But what renders PDF pages for the main Tesseract path? Tesseract needs image input. The pipeline says "Tesseract OCR" but doesn't specify the PDF→image conversion step (sips? ghostscript? poppler?).

---

## 4. DEPLOYABILITY

### D1 · BLOCKED: Pre-Deployment Calibration Not Complete [CRITICAL]
Per SKILL.md Pitfall 0a-iii (QUINTE 4/4 blocking condition): calibration on 50–200 labeled shipping docs must achieve ≥95% precision before deploy. This has not been done. **Deployment is blocked.**

### D2 · BLOCKED: `calibrated_threshold` Undefined [CRITICAL]
Without this value, the entire kimi escalation path is inoperable. The system cannot decide when to invoke the fallback model. **Deployment is blocked.**

### D3 · Gold Dispatch Conflict Blocks Operator Action [HIGH]
MEMORY.md L23 says route Gold to kimi. SKILL.md (and MEMORY.md L25–26) say route Gold to mimo-v2.5. An operator cannot execute the dispatch without resolving this contradiction. This is a direct operational blocker.

### D4 · Five External Service Dependencies [HIGH]
| Service | Failure impact | Recovery defined? |
|---------|---------------|-------------------|
| qpdf (local) | Cannot split/decrypt PDFs | No |
| Tesseract (local) | Cannot OCR | No |
| mimo API | Gold + Frankincense down | Circuit breaker → all-kimi (underspecified) |
| kimi CLI | Gold fallback unavailable | No |
| DeepSeek API | Myrrh + DS text tier down | No |

No service has a defined SLA, retry policy, timeout, or graceful degradation path (except the underspecified mimo→kimi circuit breaker).

### D5 · Three Separate Credential Systems [MEDIUM]
- mimo: `~/.local/share/mimocode/auth.json` (xiaomi key + base_url)
- kimi: `~/.kimi-code/bin/kimi` CLI with env vars (`KIMI_MODEL_THINKING_MODE`)
- DeepSeek: provider-configured in Hermes session

No unified credential management. Credential rotation requires touching three separate systems. No credential health check.

### D6 · No Dry-Run / Test Mode [MEDIUM]
No source describes a way to validate the pipeline without calling paid APIs. Operators cannot test routing logic, confidence thresholds, or circuit breaker behavior without incurring costs.

### D7 · Output Path Violation [MEDIUM]
SKILL.md writes to `/tmp` which MEMORY.md prohibits. Outputs are ephemeral and will be lost on reboot, breaking audit trails and crash recovery. The path must be relocated to a persistent directory.

### D8 · No Dependency Health Check [LOW]
Starting a MAGI run without verifying qpdf, Tesseract, zlib, and all three API endpoints are available will produce mid-pipeline failures with no recovery path.

### D9 · Volume Gate Requires Monitoring Infrastructure [LOW]
The <8 docs/week gate requires document counting infrastructure that doesn't exist. Without it, operators cannot determine when to switch to all-kimi mode.

---

## SUMMARY

| Category | Count | Critical | High | Medium | Low |
|----------|-------|----------|------|--------|-----|
| Contradictions | 5 | 0 | 2 (C1, C2) | 2 (C3, C4) | 1 (C5) |
| Gaps | 10 | 0 | 2 (G1, G2) | 5 (G3–G7) | 3 (G8–G10) |
| Ambiguity | 8 | 0 | 0 | 4 (A1–A4) | 4 (A5–A8) |
| Deployability | 9 | 2 (D1, D2) | 2 (D3, D4) | 3 (D5–D7) | 2 (D8, D9) |

**Deployment verdict**: NOT DEPLOYABLE. Two critical blocking conditions (D1: calibration not done, D2: threshold undefined) and two HIGH-severity operational blockers (D3: Gold dispatch contradiction, D4: unrecovered service dependencies) prevent production deployment.

**Top 5 actions before deploy**:
1. Complete mimo-v2.5 calibration on 50–200 labeled shipping docs, achieve ≥95% precision
2. Set and publish `calibrated_threshold` value from calibration results
3. Resolve MEMORY.md L23 Gold dispatch contradiction (align with SKILL.md mimo-primary consensus)
4. Define circuit breaker detection, trigger, and recovery procedures
5. Move output path from `/tmp` to persistent storage per MEMORY.md rules
