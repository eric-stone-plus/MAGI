[0m
> build · mimo-v2.5-pro
[0m
[0m⚙ [0mmemory Memory search: 10 results
[0m⚙ [0mmemory Memory search: 8 results
Let me first understand QUINTE's current architecture and MAGI context before analyzing each borrowing.
[0m⚙ [0mmemory Memory search: 10 results
Now let me read the actual SKILL.md files to understand current implementation specifics.
[0m⚙ [0mmemory Memory search: 10 results
[0m
[0m$ [0mls ~/.hermes/profiles/technical/skills/multi-agent-debate/ 2>/dev/null || echo "NOT FOUND"
kansa-audit
references
scripts
SKILL.md
[0m
Let me read the actual SKILL.md to understand current dispatch, output format, and protocol specifics.
[0m$ [0mls ~/.hermes/profiles/technical/skills/multi-agent-debate/magi/ 2>/dev/null || echo "NOT FOUND"
NOT FOUND
[0m
[0m$ [0mwc -l ~/.hermes/profiles/technical/skills/multi-agent-debate/SKILL.md
746 /Users/ericstone/.hermes/profiles/technical/skills/multi-agent-debate/SKILL.md
[0m
[0m$ [0mls ~/.hermes/profiles/technical/skills/multi-agent-debate/scripts/
cc_dispatch.py
dispatch_cc.py
omp_run.py
run_cc.py
[0m
[0m→ [0mRead .hermes/profiles/technical/skills/multi-agent-debate/SKILL.md[90m [limit=150][0m
[0m→ [0mRead .hermes/profiles/technical/skills/multi-agent-debate/SKILL.md[90m [offset=150, limit=200][0m
[0m→ [0mRead .hermes/profiles/technical/skills/multi-agent-debate/scripts/cc_dispatch.py
[0m→ [0mRead .hermes/profiles/technical/skills/multi-agent-debate/SKILL.md[90m [limit=200, offset=350][0m
[0m→ [0mRead .hermes/profiles/technical/skills/multi-agent-debate/SKILL.md[90m [limit=200, offset=550][0m
Now I have full context. Let me rank by implementation cost and deliver the analysis.

---

## QUINTE × MAGI: 7 Borrowings Analysis

**Ranked by implementation cost ascending** (cheapest first)

---

### 1. D — Error Classification (deprecated/auth/rate_limit/timeout/unknown → different recovery)

**What breaks**: Nothing structurally. SKILL.md L246-252 already has a flat timeout protocol (180s → kill → retry). L368 has per-model failure recovery but it's ad-hoc prose, not a typed taxonomy. The dispatch scripts (`cc_dispatch.py`, `omp_run.py`) have zero error handling — `subprocess.run` returns exit code, that's it.

**Minimum viable implementation**:
- `cc_dispatch.py` L12-29: Add stderr capture + pattern match on exit code + stderr content. Return a dict `{"status": "timeout|auth|rate_limit|unknown", "stderr": ..., "exit_code": ...}` instead of bare `int`.
- `omp_run.py`: Same treatment.
- SKILL.md L246-252: Replace flat "180s → kill → retry" with a 4-branch recovery table:
  ```
  auth (401/403) → check key freshness → retry once
  rate_limit (429) → backoff 30s → retry
  timeout (180s zero-output) → shrink prompt → retry
  unknown → log + MAGI fallback
  ```
- ~30 lines of Python per dispatch script, ~15 lines of SKILL.md prose.

**Hidden gotcha**: `cw` uses `exec --auto` which swallows errors into stdout. stderr pattern matching won't work for cw — you'd need to parse stdout for error signatures too. cw's binary is closed-source; error format could change silently.

---

### 2. F — Mandatory file:line Citations (no citation = vote excluded)

**What breaks**: R1 agents currently produce freeform markdown. L564 requires "evidence" from hm but cc/cw/omp have no such constraint. L497 Gate 0 checks agent *presence*, not output *quality*. R2 agents reviewing R1 output have no mechanical way to verify "this claim has a source."

**Minimum viable implementation**:
- SKILL.md L234-244 (R1 结果强制要求): Add to each R1 prompt template:
  ```
  Every factual claim MUST cite file:line or search command + result.
  Format: `[source: path/to/file:L42]` or `[search: grep -rn "pattern" → found at L42]`.
  Claims without citations are HYPOTHESES and must be tagged [HYPOTHESIS: uncited].
  ```
- R2 prompt template (L254-261): Add validation step — "Before evaluating any R1 claim, verify its citation exists and is accurate. Flag phantom citations."
- R3 merge logic (L284-309): "Votes from agents whose R1 output has >50% uncited claims get weight 0.5×."
- ~20 lines of prompt additions across 3 templates. Zero code changes.

**Hidden gotcha**: rx (R2) is pure-reasoning, no tools — it *cannot* verify citations exist. This rule would structurally disadvantage rx in R2, conflicting with L307 where rx already has 0.5× weight on factual disputes. You'd need to exempt rx from citation verification (rx flags "uncited" based on pattern, not file access) or accept that rx's verification is shallow.

---

### 3. B — R2 Anonymous Review Pseudonyms

**What breaks**: R2 currently identifies reviewers by agent name (L254-261: "审别人不审自己"). R3 merge (L284-309) uses agent identity for tie-breaking and weight. L307: "rx 在事实争议中权重 0.5×" — this *requires* knowing who said what.

**Minimum viable implementation**:
- SKILL.md R2 section: Add a shuffle step after R2 collection — hm assigns pseudonyms (Reviewer A/B/C/D/E) to R2 outputs before R3 sees them. R3 prompt sees only pseudonyms.
- R3 merge: Identity-based rules (rx 0.5×, hm defer) get replaced by a "reasoning quality" heuristic evaluated blind. After R3 draft, hm reveals mapping and re-applies identity rules only for tie-breaking.
- ~25 lines of SKILL.md, ~10 lines of prompt template. One extra hm step (assign pseudonyms + shuffle).

**Hidden gotcha**: R3's "hm 自身 R1 发现被 R2 争议时须 defer" (L308) is identity-dependent. If hm doesn't know which R2 review challenges its R1, it can't defer. You'd need a two-phase R3: blind evaluation → reveal → identity-based override. Adds latency and complexity. Also: 5 agents with very different output styles (cw's verbose exploration vs omp's terse analysis) make true anonymization nearly impossible — hm will recognize authorship by style.

---

### 4. C — Mind-Change Tracking (R2 records 'changed from X to Y because Z')

**What breaks**: R2 currently outputs "一致/分歧/各执一词" categories (L257-259). There's no mechanism for an agent to say "In R1 I thought X, now I think Y because agent Z showed me evidence E." R2 is framed as cross-review of *others*, not self-revision.

**Minimum viable implementation**:
- R2 prompt template: Add a `## Mind Changes` section requirement:
  ```
  If reviewing others' R1 changed your position on any point, record:
  ### Mind Change #N
  - **Was**: [your R1 position]
  - **Now**: [revised position]  
  - **Because**: [specific evidence from which agent's R1, with file:line]
  - **Confidence**: [high/medium/low]
  ```
- R3 merge (L284-309): Mind changes with "high" confidence from ≥2 agents on the same point → elevated to "convergent revision" status, weighted above simple majority votes.
- ~20 lines prompt addition. No code changes.

**Hidden gotcha**: Agents don't have persistent memory between R1 and R2 — R2 gets R1 outputs embedded in prompt. An agent can't truly "change its mind" because it's a fresh invocation. It can only say "given what I now see from others, I'd revise." This is weaker than genuine mind-change tracking (which implies introspection over a trajectory). Also: L261 says "R2 的价值不在投票取多数，在交叉检测的不对称性" — mind-change tracking shifts R2 toward convergence, which could undermine the adversarial value.

---

### 5. A — Structured JSON {verdict, confidence, reasoning_chain, evidence} per Agent Output

**What breaks**: All agent outputs are freeform markdown files (`hermes_round1.md`, `claude_round1.md`, etc.). R3 merge (L284-309) does prose-level comparison. There's no machine-parseable structure — hm reads files manually. L497 Gate 0 checks agent *presence* (file exists + >500 bytes), not output *structure*.

**Minimum viable implementation**:
- SKILL.md: Add to every R1/R2 prompt template:
  ```
  End your output with a structured block:
  ```json
  {"verdict": "PASS|FAIL|CONDITIONAL|BLOCKED",
   "confidence": 0.0-1.0,
   "reasoning_chain": ["step1", "step2", ...],
   "evidence": [{"claim": "...", "source": "file:L42", "type": "primary|inferred"}]}
  ```
- R3 merge: hm extracts JSON blocks from all R1/R2 outputs programmatically. Disagreements auto-detected by verdict field mismatch. Confidence field enables weighting.
- Gate 0 validation (L497): Add JSON parse check — "file exists + >500 bytes + valid JSON block at end."
- ~30 lines prompt additions. ~15 lines validation logic (could be a bash `jq` one-liner in the checklist).

**Hidden gotcha**: LLMs are unreliable at self-assessed confidence. A 0.9 confidence from cc MiMo and 0.9 from omp DS are not comparable — different models have different calibration curves. The `confidence` field will be noisy unless you calibrate per-model (which requires historical data). Also: forcing JSON at the end of a markdown output means agents might produce truncated JSON if they hit token limits — the structured block gets cut. Need a "JSON-first" output mode or a two-pass approach (analysis → structured extraction).

---

### 6. E — Rapporteur Confidence-Weighting (highest-confidence R1 agent gets extra R3 weight)

**What breaks**: R3 voting is currently 1-agent-1-vote with identity-based exceptions (rx 0.5× on facts, hm defer on self). L305-309. No mechanism to weight by "how confident was this agent in R1."

**Minimum viable implementation**:
- **Depends on A** (structured JSON with confidence field). Without A, there's no confidence signal to weight by.
- SKILL.md R3 section: Replace flat voting with:
  ```
  R3 weight = base_weight × (1 + normalized_confidence)
  where base_weight: hm=1.0, cc=1.0, cw=1.0, omp=1.0, rx=0.5 (facts) or 1.0 (logic)
  normalized_confidence = (agent_confidence - mean_all_confidences) / std_all_confidences
  ```
- ~15 lines SKILL.md. ~10 lines if you want a bash calculator script.

**Hidden gotcha**: This creates a perverse incentive — agents that express higher confidence get more weight, regardless of accuracy. LLMs are known to be poorly calibrated (overconfident on wrong answers, underconfident on right ones). Without a historical accuracy tracker per-agent-per-domain, this is adding noise dressed as signal. Also: MAGI's internal ≥2/3 convergence gate (L369) already produces a confidence signal (2/3 vs 3/3), but it's not exposed to R3. You'd need to plumb MAGI's internal vote split into the structured output.

---

### 7. G — Adaptive Pre-check (R1 ≥80% consensus → lighter R2)

**What breaks**: L317: "R2 不因 R1 一致而跳过——同模型一致可能只是共享盲区." This is a *hard invariant* — the entire R2-mandatory philosophy (L261, backed by POSTMORTEM #19/#21) is built on the premise that consensus is not safety. L248-250: "五方缺一不可."

**Minimum viable implementation**:
- SKILL.md: Add a conditional R2 mode after R1 collection:
  ```
  IF R1 verdict agreement ≥ 4/5 AND max(confidence) - min(confidence) < 0.2:
    → R2-LIGHT: each agent reviews only the dissenting minority (if any)
    → Skip full cross-review, do targeted verification of dissent
  ELSE:
    → R2-FULL: standard cross-review (current protocol)
  ```
- R2-light prompt: "Agent X dissented on point Y. Verify their evidence. If valid, escalate. If invalid, explain why."
- ~20 lines SKILL.md. No code.

**Hidden gotcha**: This directly contradicts L317's hard invariant and POSTMORTEM #21's lesson ("R2 的价值不在投票取多数，在交叉检测的不对称性"). The "shared blind spot" problem (POSTMORTEM #19, L261) means 80% consensus could be *exactly* when R2 is most valuable — all agents miss the same thing. You'd need a safety valve: "R2-light *never* applies to domains where historical postmortems exist" or "R2-light triggers a mandatory MAGI external audit as compensation." This is the most architecturally risky borrowing — it trades protocol rigor for speed, and QUINTE's entire value proposition is rigor.

---

### Summary Table

| Rank | Borrowing | Lines Changed | Code? | Risk | Depends On |
|------|-----------|--------------|-------|------|------------|
| 1 | D. Error classification | ~45 | Yes (Python) | Low | — |
| 2 | F. Mandatory citations | ~20 | No (prompt) | Low | — |
| 3 | B. Anonymous pseudonyms | ~35 | No (prompt+process) | Medium | — |
| 4 | C. Mind-change tracking | ~20 | No (prompt) | Medium | — |
| 5 | A. Structured JSON | ~45 | Minimal (jq) | Medium | — |
| 6 | E. Confidence-weighting | ~25 | No (prompt) | High | A |
| 7 | G. Adaptive pre-check | ~20 | No (prompt) | **Critical** | A |

**Recommendation**: Start with D + F (lowest cost, lowest risk, no dependencies). A is the foundation for E and G but carries LLM-calibration risk. G should be last and treated as experimental — it directly attacks QUINTE's core invariant.
