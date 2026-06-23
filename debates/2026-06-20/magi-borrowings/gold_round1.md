I'll map how QUINTE and the MAGI-style R1/R2/R3 flow are implemented in your codebase, then evaluate each borrowing against real dispatch and prompt constraints.
# QUINTE ← MAGI Ecosystem: Engineering Judgment

Grounded in your live stack: **Hermes SKILL.md orchestration** (markdown files, `terminal` CLI dispatch), **QUINTE v3.3 PROTOCOL** invariants, and the **quinte-engine** reference implementation in `Downloads/DEVELOPMENT/quinte-engine/`. Sources: jason-chao/MAGI (JSON, error tiers, pseudonyms) and fshiori/magi (ICE, mind-change tracking).

---

## Executive ranking (1 = do first)

| Rank | Item | Verdict | Priority |
|------|------|---------|----------|
| **1** | **D** Error classification | ✅ Viable | **P0** — extends existing retry/fallback; no invariant conflict |
| **2** | **A** Structured JSON | ✅ Viable (phased) | **P1** — unlocks automation for C/F/E; production is markdown-first today |
| **3** | **F** Mandatory file:line | ⚠️ Viable with guardrails | **P1** — upgrades Invariant #7 from downgrade → exclude; high false-negative risk |
| **4** | **C** Mind-change tracking | ✅ Viable | **P2** — pure additive to R2; no breaker if optional field |
| **5** | **B** R2 anonymous review | ⚠️ Marginal value | **P3** — fights QUINTE’s cross-model identity thesis |
| **6** | **E** Rapporteur confidence-weighting | ❌ Poor fit | **P4** — conflicts with KANSA dual-consul + MAGI no-weighted-vote |
| **7** | **G** Adaptive pre-check (≥80% → light R2) | ❌ Reject | **P5** — **direct Invariant #2 violation** |

---

## Per-item analysis

### A. Structured JSON `{verdict, confidence, reasoning_chain, evidence}`

**Viable?** Yes, phased. PROTOCOL already defines a loose R1 claims schema; quinte-engine has `ClaimsOutput.to_json()` and `prompt_templates.py` JSON hints. Production still archives markdown.

**Priority:** P1 — foundation for machine-readable diff, F enforcement, C deltas.

**What BREAKS:**
- **cc**: `--output-format stream-json` is explicitly banned (342KB unreadable event stream per `dispatch-constraints-20260619.md`).
- **grok (Gold)**: headless dispatch broken → JSON schema is moot until Gold works.
- **kimi (Fr)**: `always_thinking` → ~80% tokens before JSON body; fragile parse.
- **Auto-diff / claims pool**: today hm hand-summarizes; strict JSON without a parse layer → empty pools, false "all agents failed."

**Backward compatibility:** Keep markdown canonical; add optional `*_round1.json` sidecar. R2 continues embedding prose summaries until parse reliability ≥90%.

**Minimum viable path:**
1. Extend R1 prompt footer in `SKILL.md` + `prompt_templates.py`: "append fenced JSON block after prose."
2. Add `scripts/parse_agent_output.py` — extract JSON fence, validate against schema, fall back to markdown-only.
3. hm collection step: parse sidecar → populate claims for Phase 2 auto-diff.

**Files touched:**
| Layer | Files |
|-------|-------|
| Production | `.hermes/.../multi-agent-debate/SKILL.md`, `references/dispatch-improvements-20260620.md` |
| Spec | `Public/QUINTE/specs/PROTOCOL.md` §Phase 1 schema |
| Engine | `src/protocol/prompt_templates.py`, `src/validation/schema_validator.py`, new `src/validation/output_parser.py` |

**Production gotcha:** MiMo/cc will emit valid-looking JSON with hallucinated `file:line` in `evidence`. JSON compliance ≠ truth. You need schema validation **and** `EvidenceValidator` — not either/or.

---

### B. R2 anonymous review (pseudonyms)

**Viable?** Technically yes; **strategically weak** for QUINTE.

**Priority:** P3.

**What BREAKS:**
- **Cross-model diversity audit** (Invariant #4): you need to know *who* used *which* provider. Pseudonyms hide the exact signal QUINTE optimizes for.
- **镜門 Kyōmon**: comparative claims require agent-attributed evidence chains.
- **MAGI model-name-leak-scan**: post-hoc deanonymization is trivial (writing style, citation patterns, grok vs kimi latency).
- **R2 embedding**: cw/omp/kimi get `≤500 char` R1 summaries — pseudonym mapping must live in hm’s head or a lookup table hm maintains manually.

**Minimum viable path:**
1. hm builds `pseudonym_map.json` before R2 dispatch.
2. R2 prompts say "Review Participant X7K2's claims" — never cc/cw/omp.
3. R2 outputs use pseudonyms; hm re-maps before R3 KANSA.

**Files touched:** `SKILL.md` R2 template, new `references/r2-anonymization.md`, engine `build_r2_prompt()` + mapping helper.

**Production gotcha (kimi & grok):** Fr (kimi) produces long filesystem-heavy R1; Myrrh (mimo) is terse. Pseudonyms don’t hide epistemic fingerprints — R2 “blindness” is cosmetic. MAGI internal convergence already gives you one anonymous collective vote in R1; doubling anonymity in R2 buys little.

---

### C. Mind-change tracking (`changed from X to Y because Z`)

**Viable?** Yes — fshiori ICE pattern; fits R2’s adversarial purpose.

**Priority:** P2.

**What BREAKS:** Nothing structural if optional. Conflicts only with agents that never read R1 (rx gets embedded summary — no prior position to change from).

**Minimum viable path:**
1. Add to R2 prompt template:
   ```json
   "position_delta": {"prior": "...", "current": "...", "because": "..."}
   ```
2. hm archives `*_round2_deltas.json` alongside `*_round2.md`.
3. R3 KANSA prompt: "weight mind-changes with cited counter-evidence higher than reaffirmations."

**Files touched:** `SKILL.md` R2 section, `prompt_templates.py` `build_r2_prompt()`, `orchestrator.py` `execute_r2()`, spec `extensions.md`.

**Production gotcha:** Models **fabricate** mind-changes ("I previously believed X") when they never stated X in R1. Require `prior` to match a hash of an actual R1 claim (from A’s structured JSON) or mark `[UNVERIFIED_DELTA]`.

---

### D. Error classification → differentiated recovery

**Viable?** **Highest ROI.** Partially exists: per-delegate retry (max 3), `rx_output_degraded()`, 180s deadline, MAGI hm-solo fallback, grok 400/auth failures documented in SKILL.

**Priority:** P0.

**What BREAKS:** Nothing if you wrap existing retry logic — you’re formalizing what hm already does ad hoc.

**Gap vs jason-chao:** Today everything is `retry + shrink prompt`. No `deprecated` → skip agent, `rate_limit` → backoff queue, `auth` → key rotation path.

**Minimum viable path:**
```python
# classify_dispatch_failure(stderr, exit_code, output_bytes) → enum
# RecoveryPolicy: RETRY_SHRINK | RETRY_BACKOFF | SKIP_AGENT | ROTATE_KEY | MAGI_FALLBACK
```

| Class | Signal | Recovery | Agent notes |
|-------|--------|----------|-------------|
| `deprecated` | grok 400 Bad Request, invalid flag | Skip + `[AGENT: deprecated]` | Gold currently here |
| `auth` | 401, exit 127, empty auth.json | Rotate key / smoke test | cc MiMo nested key gotcha |
| `rate_limit` | 429, quota messages | 10–15s gap, max 2 parallel | mimo, kimi weekly quota |
| `timeout` | 0B at 60s, 180s deadline | Shrink ≤400 chars, retry | kimi thinking tax |
| `unknown` | everything else | existing 3× retry | — |

**Files touched:**
| Layer | Files |
|-------|-------|
| Production | `SKILL.md` §MAGI dispatch, `references/dispatch-failure-postmortem-20260619.md`, `references/dispatch-improvements-20260620.md` |
| Engine | `src/exceptions.py`, new `src/protocol/error_classifier.py`, `orchestrator.py` `_run_agent_r1()` |
| MAGI | `Public/MAGI/lib/magi.py` delegate timeout handling |

**Production gotcha (kimi & grok):** **grok failures look like timeouts** (0B, SIGTERM at 300s) not `deprecated`. Misclassification → 3 useless retries burning 9+ minutes. **kimi failures look like slow success** (file grows after 120s of thinking) — `timeout` classifier must use the 60s midpoint check from dispatch-improvements, not wall-clock alone.

---

### E. Rapporteur confidence-weighting (highest-confidence R1 → extra R3 weight)

**Viable?** Poor fit for QUINTE governance.

**Priority:** P4 — defer or reject.

**What BREAKS:**
- **KANSA dual-consul** (hm + Auditor B parallel, dissent preserved) — weighting one R1 voice collapses two-consul design.
- **MAGI PROTOCOL**: "No weighted voting. No confidence score. Binary gate."
- **Polybian framing**: checks-and-balances, not meritocracy of confidence.
- **rx 0.5x factual weight** already in `R3_AUDITOR_CONSTRAINT` — adding R1 rapporteur weight stacks opaque multipliers.

**Minimum viable (if forced):** Soft annotation only — `[RAPPORTEUR: cc, confidence=0.92]` in R3 prompt, no numeric weight in verdict math. Consul A may mention it; Auditor B must not be bound by it.

**Files touched:** `prompt_templates.py` `R3_*_CONSTRAINT`, `orchestrator.py` `_compute_consensus()`, PROTOCOL §Phase 6.

**Production gotcha:** **Confidence is uncalibrated.** cc MiMo reports 0.95 on wrong answers routinely. Weighting by self-reported confidence amplifies the loudest hallucinator, not the best researcher. kimi’s high-confidence file:line citations are strong; grok’s are unavailable — weighting favors Fr, breaks MAGI collective design.

---

### F. Mandatory file:line in R1 (no citation = vote excluded)

**Viable?** Yes, but **strict exclusion is a breaking upgrade** over current Invariant #7 ("downgraded weight").

**Priority:** P1 — high value for code audits; dangerous for exploratory/non-repo questions.

**What BREAKS:**
- **Invariant #7 semantics** — exclusion vs downgrade.
- **Auto-diff quorum**: R1 has 5 elements; excluding 2–3 agents → consensus pool never reaches 3/5 thresholds in engine `execute_auto_diff()`.
- **Non-code questions** (strategy, economics): legitimate R1 with grep/runtime evidence but no `file:line` → entire agent silenced.
- **MAGI collective**: internal convergence produces one vote; if Gold/Fr/Myrrh mix cited and uncited claims, exclusion logic for the collective is undefined.
- **Evidence_validator** already accepts `grep`, `$ cmd`, test results at weight 0.8–0.9 — strict `file:line`-only rule contradicts the validator.

**Minimum viable path:**
1. **Tiered gate** (borrow jason-chao’s dual-layer idea from your Greek-Rome R4 verdict):
   - **Hard exclude**: code/audit topics — claims without `file:line` or command output excluded from vote.
   - **Soft downgrade**: other topics — keep Invariant #7.
2. Reuse `evidence_validator.py` `FILE_LINE` regex; extend for `path:line-line` ranges.
3. R1→R2 gate (already planned in dispatch-improvements) + per-claim filter.

**Files touched:** `evidence_validator.py`, `claims_validator.py`, `SKILL.md` Pre-R1 + collection, PROTOCOL §5 Invariant #7, `references/omp-source-audit-capability.md` (omp already does this well).

**Production gotcha (kimi & grok):**
- **kimi (Fr)**: best file:line agent when given paths — **best ROI for F**.
- **grok (Gold)**: unusable → MAGI collective may ship with only Fr+Myrrh citations → `[MAGI 2/3]` with 1/3 of epistemic coverage excluded.
- **False negatives**: `src/foo.py` (no line), `README.md` (no line), multi-line ranges — regex too strict → mass exclusion → R2 operates on 1 agent → false confidence.

---

### G. Adaptive pre-check (R1 ≥80% consensus → lighter R2)

**Viable?** **Reject** as specified.

**Priority:** P5 — do not implement.

**What BREAKS:**
- **Invariant #2**: "Never skip R2. Unanimous R1 can be shared blind spot."
- **Recursive QUINTE §Phase 7**: "No shortcuts — a nested debate is a debate."
- **SKILL.md**: "R2 始终执行——确认性审计或争议标注"
- **extensions.md**: "R2 never skipped"
- **Semantic PBFT**: R2 is the refutation layer; skipping it removes Byzantine detection.

**Historical note:** `worked-example-event-pipeline.md` (2026-05) says "Two-party consensus → skip Round 2" — that predates v3.3 and is **superseded**.

**If you want cost savings:** Run **full R2 rx-only** (1 agent, embedded summaries) as "light R2" — still satisfies Invariant #2’s confirmatory audit without skipping. That is not what G describes.

**Minimum viable alternative:** R1 Rashomon ratio annotation → if `|consensus|/|union| ≥ 0.8`, flag `[HIGH_CONSENSUS]` in R3 but **still run 5-agent R2**.

**Production gotcha:** 80% agreement on a **shared wrong answer** is exactly what QUINTE was built to catch (cc 71% timeout lesson, cross-model MiMo-only blind-spot discovery 2026-06-20). G optimizes for cost at the expense of the core value proposition.

---

## Kimi & Grok: cross-cutting dispatch constraints

These affect **every** borrowing:

| Constraint | Impact on borrowings |
|------------|---------------------|
| **grok headless broken** | A/B/E/G involving Gold are blocked until grok CLI fixed; D must classify as `deprecated` not `timeout` |
| **kimi `-p` only, no `-y`** | Dispatch template changes are breaker-sensitive; combine flags → instant fail |
| **kimi 80% thinking tax** | A/C/F JSON at end of output — parser must scan tail, not `head -1` |
| **kimi = filesystem explorer** | F favors Fr; must give file paths in prompt, not "answer without tools" |
| **R2 sandbox blindness** | cw/omp/kimi cannot read `/tmp/` — B/C/F require embedded summaries ≤500 chars |
| **MAGI = collective R1 vote** | Per-delegate JSON (A/C/F) needs delegate-level files before convergence merge |
| **delegate_task forbidden** | All automation must use `terminal` CLI — shapes D’s recovery (can't route through parent) |

---

## Recommended absorption sequence

```
Phase 0 (now):     D — error classifier + recovery policies
Phase 1 (2–3d):    A — JSON sidecar parser (markdown remains canonical)
Phase 1b (parallel): F — tiered evidence gate on code topics only
Phase 2 (1wk):     C — mind-change deltas (requires A’s claim hashes)
Phase 3 (defer):   B, E — only if automation pain justifies complexity
Never:           G — amend Invariant #2 first if you really want this
```

**Smallest shippable bundle:** **D + A + F(tiered)** gives you machine-readable outputs, differentiated recovery for kimi/grok/mimo failure modes, and citation discipline without gutting R2 or KANSA.

If you want, I can draft the `error_classifier.py` + `parse_agent_output.py` MVP against `quinte-engine` and the matching SKILL.md diff for production dispatch.
