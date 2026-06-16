# Gift Assignment Guide (贈り物割り当てガイド)

## Principle

Each MAGI execution assigns three Gifts to three agents: **hm + 2 delegates**.
hm always holds one Gift. The assignment depends on the problem type and
the strengths of each delegate.

## Assignment Matrix

### hm's Default Gift

hm should hold the Gift that benefits most from **domain knowledge and
session context**:

| Problem domain | hm holds | Why |
|---------------|----------|-----|
| Business (finance, contracts, demurrage) | Myrrh (risk) | hm knows the business context best; can spot domain-specific risks |
| Code (review, architecture, debugging) | Myrrh (risk) | hm knows the codebase and deployment constraints |
| Data (validation, analysis, modeling) | Gold (verification) | hm can cross-check against raw data in session |
| Legal (clauses, compliance, disputes) | Myrrh (risk) | hm has contract knowledge and precedent memory |

**Default**: hm holds Myrrh. The adversarial role benefits most from
domain expertise — knowing where things typically break requires experience.

### Delegate Assignment

| Delegate | Best at | Assign Gold when... | Assign Frankincense when... |
|----------|---------|-------------------|-----------------------------|
| delegate A | Detail work | Problem needs precise verification | Problem needs pattern recognition |
| delegate B | Big-picture | Problem is data-heavy | Problem is cross-domain |

### Concrete Examples

**Code review**:
- Gold → delegate A (line-by-line verification)
- Frankincense → delegate B (architectural synthesis)
- Myrrh → hm (knows deployment risks, edge cases)

**Financial analysis**:
- Gold → delegate A (numerical verification)
- Frankincense → delegate B (trend synthesis)
- Myrrh → hm (knows business context, can spot anomalies)

**Contract review**:
- Gold → delegate A (clause-by-clause verification)
- Frankincense → delegate B (portfolio-level patterns)
- Myrrh → hm (knows precedent, dispute history)

**Architecture decision**:
- Gold → hm (can verify against existing codebase)
- Frankincense → delegate A (synthesizes options)
- Myrrh → delegate B (adversarial stress test)

## Dynamic Reassignment

In Phase 2 (spiral), the Gift assignments stay the same — each Gift
reviews the previous Gift's output through their fixed lens. Reassignment
only happens between full MAGI runs.

## MAGI-LITE Assignment

In LITE mode (Phase 1 + Phase 4 only), the same assignment rules apply.
The difference is no spiral — each Gift produces one analysis, hm synthesizes.

## MAGI-FLASH Assignment

In FLASH mode, only Gold exists. hm runs Gold directly — no delegates.
This is pure verification with Gold's epistemological discipline.
