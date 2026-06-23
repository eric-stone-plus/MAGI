The comprehensive evaluation is written. Here's the executive summary:

---

## MAGI Borrowings → QUINTE Absorption: RANKED

### 1. F. Mandatory file:line citations — **P0 · SHIP NOW**
QUINTE already has: Invariant#7 evidence requirement, Kyōmon `file:line` discipline, schema with `evidence` field. Missing piece: hard gate — no citation = excluded from voting. **3 changes**: one ⛔ line in R1 prompt, one regex filter in Phase 2 auto-diff, schema tighten. Zero breakage.

### 2. D. Error classification — **P1 · START WITH 2-WAY**
Current uniform 180s kill→retry treats `rate_limit` and `timeout` identically. **MVI**: split `rate_limit` (exponential backoff) from `timeout` (shrink prompt). Requires error parsing in 6 dispatch wrappers (run_cc.py, codewhale, omp, grok, kimi, mimo) — each has different error formats. 90% of production value from the 2-way split.

### 3. C. Mind-change tracking — **P2 · ONE PROMPT LINE**
Add to R2 dispatch: *"If any R1 finding changed your mind, state what and why."* Zero infrastructure, zero breakage, nice audit trail. But QUINTE R2 agents don't have "initial positions" — they receive R1 outputs cold, so mind-change detection requires an extra reasoning step.

### 4. A. Structured JSON output — **P2 · MAGI TRIAL FIRST**
Schema already defined in PROTOCOL.md (loose mode). Risk: forcing cc/cw/omp into strict JSON may degrade quality. **MVI**: trial `--json` on MAGI doctors only (Gold/Fr/Myrrh produce shorter, more structured outputs). If quality holds across 5+ sessions, expand to core R1 agents. Parse logic bifurcates: JSON path vs markdown fallback.

### 5. B. Anonymous R2 review — **P3 · THEATER**
One `sed` in R2 prompt. But in QUINTE, agent identity IS model identity (cc=MiMo, cw=DeepSeek, etc.). Knowing "cc said X" carries model-provenance signal R2 cross-review uses. Also: R2 agents ARE the R1 agents — they recognize their own writing. True anonymity requires different reviewers, which violates Invariant#1.

### 6. E. Rapporteur confidence-weighting — **P3 · GOVERNANCE CONFLICT**
Self-reported confidence is unreliable. Giving "highest-confidence R1 agent" extra R3 weight undermines hm's constitutional *intercessio* (Tribune's veto) and the dual-consul model. MAGI is a collective — whose confidence? The most confident delegate?

### 7. G. Adaptive pre-check — **⛔ BLOCKED**
Violates Invariant#2 (*Never skip R2 — unanimous R1 can be shared blind spot*), SOUL.md ⛔ *"不自判简化"*, ⛔ *"含 QUINTE 即全量"*, and the Clinical Mixed-Vendor 2026 theoretical anchor. Cannot implement without rewriting core invariants.
ity: cc=MiMo, cw/omp/rx=DeepSeek, MAGI delegates=grok/kimi/mimo. Knowing "cc said X" carries signal about model provenance. Stripping names strips that signal. R2 cross-review benefits from knowing source bias (e.g., rx's factual claims weight 0.5×).

**Protocol conflict**: None. Pure prompt change. But conflicts with *operational intuition* — R2's value is cross-model blind-spot detection, which requires knowing which model said what.

**Code impact**:
- **Prompt template**: R2 prompt changes `cc_round1.md` → `Agent_A_round1.md`, etc. One string-replace in the R2 context assembly.

- **No parse logic changes**. R2 outputs just reference different identifiers.

- **MAGI output tagging**: Currently `[MAGI 2/3]` or `[MAGI 3/3]` annotations reveal that this is MAGI collective output — would need stripping too.

**MVI**: Literally one `sed` in the R2 prompt assembly. 5 seconds of work.

**Hidden complexity**: Outputs self-identify. cc's verbose style, cw's implementation-heavy analysis, omp's speed-focused brevity — experienced reviewers identify the source from content alone. Pseudonyms are theater unless content is also homogenized (which destroys value). Also, current R2 agents are the SAME agents as R1 (cc/cw/omp/hm review each other) — they will recognize their own writing. True anonymity requires different reviewers, which violates Invariant#1 (participant count/structure).

---

## C. Mind-Change Tracking

**Viability**: HIGH. Pure prompt addition. No structural changes.

**Protocol conflict**: None. Complements existing R2 cross-review. QUINTE R2 already surfaces disagreements; mind-change tracking just makes the persuasion dynamic explicit.

**Code impact**:
- **Prompt template**: Add one line to R2 dispatch prompt: `For each R1 finding you disagree with, state: (a) your initial position before reading R1 outputs, (b) whether any R1 argument changed your mind, (c) what specifically changed it.`
- **No parse logic changes**. Mind-change annotations are human-readable output fed to R3.

**MVI**: One line in R2 prompt template in SKILL.md. Zero dispatch code changes.

**Hidden complexity**: R2 agents in QUINTE don't have "initial positions" — they receive R1 outputs cold. They'd need to form an initial position first, then compare. This doubles R2 thinking time. Also, mind-change tracking makes more sense for MAGI's internal convergence (3 delegates change minds during consensus) than for QUINTE R2 cross-review.

---

## D. Error Classification

**Viability**: HIGH. Directly addresses production reliability.

**Protocol conflict**: None. Enhances existing timeout/retry protocol without changing governance.

**Current state**: QUINTE has uniform 180s timeout → kill → shrink prompt → retry. 3 consecutive failures → escalate. Special cases exist ad-hoc:
- cc on MiMo: "zero timeout" (known platform property)
- MAGI delegates: per-delegate retry (max 3), degrade to `[MAGI hm-solo]`
- rx: output quality gate (detect empty/tool_call-only output → MAGI fallback)

**Code impact**:
- **Dispatch wrappers** need error-type parsing from stdout/stderr:
  - `run_cc.py`: parse claude exit code + stderr for `rate_limit`, `auth_error`, `timeout`
  - `codewhale exec`: parse exit codes (cw has structured exits)
  - `omp -p`: parse stderr for API error codes
  - MAGI delegates: grok/kimi/mimo CLI each have different error formats
- **SKILL.md retry protocol**: Replace uniform 180s kill→retry with classification table:
  ```
  rate_limit → exponential backoff (1s, 2s, 4s, 8s), max 3 retries → escalate
  timeout → shrink prompt 50%, retry once → escalate
  auth_error → immediate escalate (don't retry — won't fix)
  deprecated_model → switch to fallback model from profile config
  unknown → existing 180s kill→retry→escalate
  ```
- **Hermes oversight**: hm must recognize error types in agent output and apply correct recovery. Currently hm just sees "agent failed / timed out." Error classification requires structured error reporting from dispatch wrappers.
- **Backward compatibility**: All existing retry logic stays as fallback for `unknown` category.

**MVI**: Start with 2-way split: `rate_limit` vs `timeout`. These cover 90% of failures. Add exponential backoff to dispatch wrappers (Python time.sleep for cc, shell sleep for others). Expand to 5-way later.

**Hidden complexity**: Each agent's dispatch CLI has different error formats:
- cc (Claude Code via MiMo API): Anthropic-style error JSON in stderr
- cw (codewhale): custom exit codes + stderr
- omp: OpenAI-style error codes from proxy
- MAGI grok: xAI error format
- MAGI kimi: Moonshot error format
- MAGI mimo: Xiaomi error format

Error parsing is the long pole — 6 different error format parsers needed. A wrong parse means `rate_limit` misclassified as `unknown` → wrong recovery → wasted retries.

---

## E. Rapporteur Confidence-Weighting

**Viability**: LOW. Protocol conflict with R3 governance model.

**Protocol conflict**: R3 is designed as **dual-consul verdict** (hm Consul A + KANSA B), not a weighted average of R1 agents. hm holds final arbiter authority (*intercessio* — Tribune's veto). Giving extra R3 weight to "highest-confidence R1 agent" undermines hm's constitutional role. Also, self-reported confidence is unreliable — the most confident agent may be the most overconfident.

**Code impact**:
- **R3 verdict rules** in PROTOCOL.md §6 would need rewriting:
  - Current: hm + KANSA B independently draft verdicts → merge (consensus adopted, dissent annotated)
  - Proposed: hm + KANSA B + extra weight for highest-confidence R1 agent on per-claim basis
- This changes the governance model from "separation of powers" to "confidence-weighted council" — fundamentally different architecture.

**MVI**: Not viable without governance redesign. If pursued, start with non-binding "advisory weight" — R3 arbiters SEE the high-confidence agent's view flagged but aren't bound by it.

**Hidden complexity**: Confidence scores are per-claim in the existing schema (`claims[].confidence`), not per-agent. To weight an agent, you need per-agent aggregate confidence, which doesn't exist. Also, MAGI is a collective element — whose confidence do you use? The most confident delegate? The average? The converged output's internal confidence ratio?

---

## F. Mandatory file:line Citations

**Viability**: HIGH. QUINTE already has 80% of the infrastructure.

**Protocol conflict**: None. Hardens existing Invariant#7 (evidence requirement) and Kyōmon (鏡門) file:line discipline.

**Current state**:
- Invariant#7: "Claims without evidence → downgraded weight in verdict"
- Schema: `"evidence": "string (file:line or command output)"`
- Kyōmon: hm's own comparative claims must have `[鏡門 ✓]` with file:line
- R1 agents currently cite evidence inconsistently — some claims have grep output, others are bare assertions

**Code impact**:
- **R1 prompt template**: Add to dispatch prompt:
  ```
  ⛔ Each claim MUST include a verifiable citation: file:line, grep output, command result, or runtime output.
  Claims without citations are EXCLUDED from voting — they will not enter the consensus or dispute pools.
  ```
- **Phase 2 auto-diff**: Add citation-check filter. Before hashing claims for consensus/dispute pools, scan each claim for evidence pattern (`file:line` regex, `grep` output block, backtick-delimited command output). Claims with no match → dropped with annotation `[NO-CITATION]`.
- **Schema update**: Change `"evidence"` from `"string"` to required (non-empty, non-placeholder).
- **R2 prompts**: No change needed — R2 only sees claims that survived the citation filter.

**MVI**: Add one ⛔ line to R1 prompt template. Add one regex check in Phase 2 (hm's auto-diff logic). Schema already has the field.

**Hidden complexity**: Not all valid evidence fits `file:line`. Runtime behavior observations, web search results, LSP hover output, DAP variable inspection — these are valid evidence types without file:line format. The citation regex needs to be permissive enough: `file:line` OR `grep <pattern>` output OR backtick-delimited command output OR `> tool_output`. Also, MAGI delegates (Gold/Fr/Myrrh) may not have filesystem access — their evidence is reasoning chains, not file:line. Need MAGI-specific exemption.

---

## G. Adaptive Pre-Check

**Viability**: ⛔ BLOCKED. Directly violates multiple ⛔ iron laws.

**Protocol conflict**:
- Invariant#2: "Never skip R2. Unanimous R1 can be shared blind spot."
- SOUL.md ⛔: "不自判简化" (don't self-judge simplification)
- SOUL.md ⛔: "含 QUINTE 即全量" (QUINTE = full R1+R2+R3)
- SOUL.md ⛔: "R2 永不跳过"
- Theoretical anchor: Clinical Mixed-Vendor 2026 — homogeneous teams produce correlated failure modes. R1 unanimity is precisely the condition where R2 is MOST needed (to catch shared blind spots).

**Code impact**: None — cannot be implemented without rewriting core invariants.

**MVI**: N/A.

**Hidden complexity**: Even if the iron laws were revised, "80% consensus" is a brittle threshold. QUINTE claims are heterogeneous — 5 agents might agree on 80% of claims while disagreeing on the 20% that are load-bearing. Consensus percentage doesn't capture claim criticality.

---

## Ranked Implementation Order

| Rank | Candidate | Priority | Cost | Breakage Risk | Rationale |
|------|-----------|----------|------|---------------|-----------|
| **1** | **F. Mandatory file:line** | P0 | 2 lines + 1 regex | Zero | Hardens existing Invariant#7. Already 80% built. |
| **2** | **D. Error classification** | P1 | 6 error parsers + retry table | Medium | Highest production reliability gain. Start with rate_limit vs timeout split. |
| **3** | **C. Mind-change tracking** | P2 | 1 prompt line | Zero | Free audit trail improvement. Zero infra change. |
| **4** | **A. Structured JSON** | P2 | Parse logic rewrite + 5 prompt templates | Medium-High | Trial on MAGI doctors first. Risk of quality degradation on cc/cw/omp. |
| **5** | **B. Anonymous review** | P3 | 1 sed | Zero | Questionable value — model identity IS agent identity in QUINTE. |
| **6** | **E. Rapporteur weighting** | P3 | R3 governance rewrite | High | Conflicts with dual-consul model. Self-reported confidence unreliable. |
| **⛔** | **G. Adaptive pre-check** | BLOCKED | N/A | N/A | Violates Invariant#2 + 3 ⛔ iron laws. Cannot implement. |

---

## Code Constraints Summary (for kimi/grok focus)

### Dispatch Code Changes Required

| Candidate | run_cc.py | codewhale exec | omp -p | reasonix run | MAGI delegates | Phase 2 auto-diff |
|-----------|-----------|----------------|--------|-------------|----------------|-------------------|
| A. JSON | Add `--json` schema to prompt | Same | Same | N/A (R2 only) | Same (already structured) | Replace regex parse with json.loads |
| B. Anon | None | None | None | None | Strip [MAGI] tags | Filter agent-name references |
| C. Mind-change | None | None | None | None | None | None |
| D. Errors | Parse stderr for error codes | Parse exit codes | Parse stderr | Parse stderr | Parse 3 different error formats | None |
| E. Weight | None | None | None | None | None | Compute per-agent confidence aggregate |
| F. Citations | Add ⛔ citation requirement to prompt | Same | Same | N/A | Add MAGI exemption | Add citation regex filter pre-hash |
| G. Adaptive | BLOCKED | BLOCKED | BLOCKED | BLOCKED | BLOCKED | BLOCKED |

### Prompt Template Changes

| Candidate | R1 dispatch | R2 dispatch | R3 verdict |
|-----------|-------------|-------------|------------|
| A. JSON | + schema + "respond in JSON" | + "claims are JSON objects" | + parse JSON claims |
| B. Anon | None | s/agent_name/Agent_X/g | None |
| C. Mind-change | None | + "state if R1 changed your mind" | None |
| D. Errors | None | None | None (dispatch wrappers change) |
| E. Weight | None | None | + "weight R1 high-confidence agent" |
| F. Citations | + ⛔ "no citation = excluded" | None | + citation gate check |
| G. Adaptive | BLOCKED | BLOCKED | BLOCKED |

### Minimum Viable Implementation Per Candidate

**F (Citation Gate)**: 3 changes:
1. `SKILL.md` R1 dispatch prompt: add `⛔ Each claim MUST include file:line or command output. No citation → excluded from voting.`
2. Phase 2 auto-diff (hm's logic): before hashing, regex-scan claims for `\b\S+:\d+\b` or backtick-delimited command blocks. No match → drop with `[NO-CITATION]`.
3. Schema update: `"evidence"` → `"required"` in Phase 1 schema block.

**D (Error Classification)**: Start with rate_limit/timeout split only:
1. Each dispatch wrapper: after subprocess completion, check exit code + stderr for `rate_limit` / `429` vs `timeout` / `timed out`.
2. `SKILL.md` retry protocol: `rate_limit` → backoff (1s/2s/4s/8s), `timeout` → shrink prompt 50% + retry once, `other` → existing 180s kill→retry→escalate.
3. hm oversight: receive `{agent, error_class, action}` instead of `{agent, failed}`.

**C (Mind-Change)**: One line in SKILL.md R2 prompt section.

**A (JSON)**: Trial on MAGI doctors only first:
1. Add `--json-schema` to MAGI dispatch: `grok -p --json '{"verdict":..., "confidence":..., "reasoning":..., "evidence":...}' "question"`
2. Phase 2: if MAGI output is valid JSON, parse directly; else fallback to markdown parse.
3. Wait 5+ sessions to measure quality impact before expanding to cc/cw/omp.

---

## Verdict

QUINTE should absorb **F, D, C** in that order. **A** needs MAGI-only trial first. **B** and **E** are low-priority / design-conflicted. **G** is blocked by iron law.

Total implementation cost for F+D+C: ~3 prompt lines, 2 dispatch wrapper changes (error parsing in run_cc.py + codewhale), 1 Phase 2 logic change (citation filter). Ship in one session.
