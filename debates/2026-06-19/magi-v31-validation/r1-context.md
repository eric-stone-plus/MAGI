# R1 Context — MAGI v3.1 Validation

## Current config
MAGI = grok/kimi/mimo:
- Gold → grok-build --effort max --reasoning-effort xhigh
- Frankincense → kimi K2.7 (always_thinking)
- Myrrh → mimo-v2.5-pro

## Change from v3.0
- Old: DS/mimo/kimi (Myrrh = hm's same model → fake heterogeneity)
- New: grok/kimi/mimo (true three-architecture heterogeneity)
- Myrrh was hm direct (DS v4-pro) → now independent mimo CLI

## Questions for R1
1. Is grok/kimi/mimo the optimal three-model set? Compare vs alternatives (DS/grok/kimi, DS/mimo/grok, etc.)
2. Fixed role mapping (Gold=grok, Fr=kimi, Myrrh=mimo) vs dynamic routing by task type?
3. CLI flags optimal? Gold: max+xhigh. Fr: default. Myrrh: default.
4. Blind spots: task types where all three share correlated failures?
5. Convergence gate ≥2/3 still correct for this model set?

## Context
- Model heterogeneity is the critical factor (Zhang 2025)
- Mixed-vendor avoids correlated blind spots (Clinical EACL 2026)
- Fr's always_thinking is unbillable overhead — use for contextual reasoning only
- Gold's --effort max --reasoning-effort xhigh is user-mandated (override benchmark)
