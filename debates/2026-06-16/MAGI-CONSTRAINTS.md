# MAGI — Constraints & Failure Modes

> 2026-06-14 · Hard constraints, known pitfalls, anti-patterns

## Hard Constraints

| Constraint | Value | Rationale |
|-----------|-------|-----------|
| Agents | 3 (hm + 2 delegates) | Three Gifts, three epistemological stances |
| Model | mimo-v2.5-pro only | Free tier, token-rich, no DeepSeek dependency |
| Max spiral cycles | 3 (9 total reviews) | Diminishing returns after 3 cycles |
| Max convergence restarts | 2 | If still divergent after 3 attempts, output with divergence |
| Delegate timeout | 300s per phase | mimo free tier has latency variability |
| Total protocol timeout | 1800s (30 min) | Hard cap for full MAGI |
| Convergence threshold | ≥0.7 | Below = insufficient alignment |
| Convergence weights | 0.4/0.3/0.3 | Factual > Interpretive = Risk |

## Known Pitfalls

### 1. Gift Confusion (贈り物混乱)

**Symptom**: A delegate outputs in the wrong Gift's format.
Gold produces a risk map instead of verification tables.
Frankincense produces a verification checklist instead of narrative.

**Detection**: Structural mismatch — each Gift has a unique output format.
If Gold's output doesn't contain "## Verified Facts" and "## Confidence Level",
it's Gift confusion.

**Recovery**: Flag as drift, kill delegate, retry with reinforced prompt.

### 2. hm Self-Exemption (hm 自己免除)

**Symptom**: hm holds Myrrh but skips the adversarial analysis,
jumping straight to synthesis/verdict. hm treats itself as
orchestrator-only, not as a Gift carrier.

**Detection**: Check if hm's Phase 1 output contains "## Risk Map"
and "## Fragility Points". If missing, hm self-exempted.

**Prevention**: "hm MUST produce a Gift output like any apostle.
hm cannot skip Myrrh and just synthesize."

### 3. Convergence Cheating (収束不正)

**Symptom**: hm evaluates convergence as ≥0.7 when the Gifts
clearly disagree. hm forces convergence to avoid another spiral cycle.

**Detection**: Compare hm's convergence score with the actual
alignment in the Gift outputs. If Gold says "fact X is true" and
Myrrh says "fact X is unverified", factual score should be <0.5.

**Prevention**: KANSA (監査) — a second arbiter independently
evaluates convergence. If KANSA's score diverges from hm's by >0.2,
flag for review.

### 4. Same-Model Blind Spot (同模型盲点)

**Symptom**: All three Gifts share the same training data and
knowledge cutoff. They may converge on a shared error.

**Detection**: This is inherent to MAGI's design (same model).
Unlike QUINTE (cross-model with DeepSeek), MAGI trades model
diversity for speed and cost.

**Mitigation**: For high-stakes questions, feed MAGI's output
into QUINTE for cross-model verification. MAGI investigates,
QUINTE authorizes.

### 5. Delegate Timeout (使徒超時)

**Symptom**: A delegate hangs for 300s+ without output.

**Recovery**: Kill → reduce evidence package size → retry.
If 3 retries fail, proceed with 2 Gifts (note in Revelation).

### 6. Spiral Oscillation (螺旋振動)

**Symptom**: Phase 2 keeps producing the same disagreements.
Convergence score oscillates around 0.6 without improving.

**Detection**: If convergence score changes by <0.05 between
cycles, the spiral has plateaued.

**Recovery**: Stop after 2 cycles, output with explicit
divergence notes in the Revelation.

## Anti-Patterns

### DON'T use MAGI for push authorization

MAGI produces investigation results, not authorization decisions.
Push authorization belongs to QUINTE (with HIGHBALL KENGEN gate).

### DON'T skip Phase 2 (The Journey)

Even if Phase 1 shows apparent consensus, run at least 1 spiral cycle.
"Apparent consensus" from parallel analysis may be shared blind spot.
The spiral's value is in cross-perspectival stress-testing.

### DON'T let hm hold Gold or Frankincense

Default assignment: hm = Myrrh. This is because hm has domain knowledge
(session context, memory, user history) which is most valuable for
adversarial analysis. Gold and Frankincense are better suited to delegates
who bring fresh, unbiased perspective.

Exception: Architecture decisions where hm needs to verify against the
existing codebase → hm = Gold, delegates = Frankincense + Myrrh.

### DON'T use delegate_task for MAGI-LITE

There is no MAGI-LITE. Full protocol or nothing. If you want a quick
check, just do it manually — MAGI is for when you need the full
dialectical spiral.

## Relationship to QUINTE Pitfalls

Many of QUINTE's hard-won pitfalls apply to MAGI:

| QUINTE Pitfall | Applies to MAGI? | Adaptation |
|---------------|-----------------|------------|
| cc 71% timeout | YES (delegates use same dispatch) | Same mitigation: ≤400 chars prompt |
| cw auto-execution | YES | Same: "Do NOT execute any shell commands" |
| hm R1 coverage inflation | YES | Phase 0 must enumerate all evidence |
| hm direction errors | YES | Gold's verification catches these |
| write_file corruption | YES | Use `patch` not `write_file` for edits |
| /tmp contamination | YES | Topic-specific subdirectories |
| 429 rate limit | YES | Max 2 parallel delegates |
