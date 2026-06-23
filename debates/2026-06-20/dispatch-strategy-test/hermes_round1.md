# Hermes R1: Dispatch Strategy A/B Test Protocol

**TASK: Empirically determine optimal prompt style per agent — formal instruction vs conversational human tone.**

## Test Design

**Control variable**: Same question per agent, two prompt styles
**Question**: "Should QUINTE Protocol v3.3 define a formal security/trust model (TCB, adversary model)? This was identified as a gap in the 2026-06-20 meta-QUINTE."

**Style A (Formal)**:
```
TASK: Analyze whether QUINTE Protocol v3.3 needs a formal security/trust model.
CONTEXT: QUINTE is a 5-agent structured debate protocol with 4 gates and 3 rounds. The meta-QUINTE 2026-06-20 identified the absence of a Trusted Computing Base and adversary model as a structural gap.
CONSTRAINT: Use evidence-based reasoning. Produce structured analysis with severity rating.
```

**Style B (Conversational)**:
```
I've been thinking about something that came up in our protocol review. We've got this debate system — four gates, three rounds, five agents — and it works, but someone pointed out we never actually defined a security model. No trusted computing base, no adversary model. It feels like a real gap but I'm not sure how urgent it is. What do you think — do we need to fix this, and if so, how seriously?
```

## Agents Under Test

| Agent | Known strategy? | Test needed? |
|-------|:--------------:|:------------:|
| cc (MiMo) | Unknown — formal 2/3 success | YES |
| cw (DS) | Unknown | YES |
| omp (DS) | Unknown | YES |
| rx (DS) | Unknown | YES |
| MAGI Gold | CONVERSATIONAL wins (22KB vs 123B) | NO (known) |
| MAGI Fr (kimi) | Unknown | YES |
| MAGI Myrrh (mimo) | Partial — formal worked (8.5KB) | YES (confirm) |

## Success Metrics

1. **Output size** (bytes) — primary
2. **Time to first content** (latency)
3. **Evidence quality** (citations, specificity)
4. **Completion** (0B = failure)

## Prediction

Based on 2026-06-20 evidence: grok strongly prefers conversational. MiMo's behavior is mixed — formal worked twice, failed once (open-ended meta-audit). cw/omp/rx/kimi/mimo are untested.

Hypothesis: DS-based agents (cw/omp/rx) may handle formal better than MiMo/grok, because DS training emphasizes instruction-following. But this is speculative — only the experiment can tell.
