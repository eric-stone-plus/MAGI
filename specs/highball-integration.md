# HIGHBALL Integration — Rubicon Moment Interface

## Source
QUINTE R10 debate synthesis. MAGI operates in epistemic domain; HIGHBALL governs operational domain.

## Principle
MAGI thinks freely. HIGHBALL reviews executable actions.
MAGI output crosses into operational domain at the Rubicon Moment.

## Interface Specification

```
MAGI Output → HIGHBALL Classifier
  │
  ├─ Safe (low risk, high reversibility, low urgency)
  │   → Direct execution, no KANSA review
  │
  ├─ Uncertain (medium risk profile)
  │   → KANSA review: reversibility, resource cost, opportunity cost
  │   → KANSA does NOT review philosophical correctness or truth claims
  │   → Outcome: execute | veto
  │
  └─ Dangerous (high risk, low reversibility)
      → Automatic veto + Deadlock Record
```

## MAGI Output Schema for Rubicon Moment

```
{
  synthesis: {
    conclusion: str,
    commitments: {preserved: [], negated: [], emergent: [], suspended: []},
    triz_route: "time"|"space"|"state",
    new_variable_count: int
  },
  risk_self_assessment: {
    reversibility: 0-1,
    urgency: 0-1,
    downstream_type: "human"|"m2m"
  }
}
```

## KANSA Review Scope
KANSA reviews operational criteria only:
- Reversibility of proposed action
- Current resource/time constraints
- Opportunity cost of not acting
- M2M downstream → Mode B always (forced resolution)

KANSA does NOT review:
- Philosophical correctness
- Reasoning quality
- Truth claims of the synthesis

## Power Isolation
- MAGI can conclude ANYTHING in logical space
- HIGHBALL cannot interfere with MAGI's thinking
- MAGI's conclusion can be locked in sandbox (vetoed) but cannot be censored

## Related
- aufhebung-formal.md — Synthesis protocol
- ../../HIGHBALL/specs/kansa-two-domain.md — Domain separation
- ../../HIGHBALL/specs/rubicon-aps.md — APS decision after Rubicon Moment
