# Example: Full MAGI on Code Review

## Scenario

Review a new pricing calculation module for a fuel trading platform.
The module calculates demurrage charges based on vessel laytime data.

---

## Phase 0 — The Star (hm)

**Problem decomposition**:
1. Is the laytime calculation formula correct? (verifiable)
2. Does the module handle edge cases? (testable)
3. Is the architecture sound for future extension? (evaluable)

**Evidence**:
- `src/pricing/demurrage.py` — main module
- `tests/test_demurrage.py` — test suite
- `spec/laytime-formula.md` — business specification

**Gift assignment**:
- Gold → delegate A (detail-oriented, good at formula verification)
- Frankincense → delegate B (architectural thinking)
- Myrrh → hm (knows the business domain, can spot edge cases)

---

## Phase 1 — 三博士獻礼 (parallel)

### Gold's output (excerpt):
```
Verified Facts:
1. Formula at line 42: rate * days * (1 - discount) — matches spec §3.2 ✅
2. Half-rate at line 67: triggers when demurrage > 3 days — spec says > 2 days ❌
3. Weather deduction at line 89: only applies to FM exceptions — matches spec §4.1 ✅

Key Claims:
| Claim | Evidence | Verdict |
|-------|----------|---------|
| Half-rate threshold | line 67 vs spec §3.4 | ❌ Refuted (off by 1 day) |

What I Cannot Determine:
- Whether the spec itself is correct (only verifying code-to-spec, not spec-to-contract)
```

### Frankincense's output (excerpt):
```
Contextual Synthesis:
The module follows a standard laytime calculation pattern but introduces
a custom half-rate mechanism that isn't industry-standard. This creates
a "domain drift" risk — future developers may not understand why this
module differs from textbook laytime calculations.

Pattern: The module has 3 pricing paths (normal, half-rate, emergency)
but only 2 are tested. The emergency path (line 112) has zero test
coverage — a "dark path" pattern.

What I Cannot Connect:
- How this module interacts with the COA (Contract of Affreightment) system
```

### Myrrh's output (excerpt):
```
Risk Map:
| Risk | Severity | Likelihood | Category |
|------|----------|-----------|----------|
| Half-rate off by 1 day | HIGH | CERTAIN | factual |
| Emergency path untested | HIGH | POSSIBLE | structural |
| Timezone handling (line 95) | MEDIUM | LIKELY | contextual |

Failure Conditions:
- IF vessel arrives at 23:59 UTC and system uses local time, THEN
  laytime starts on wrong day → demurrage off by 1 day's rate
- IF emergency pricing path is triggered, THEN no test validates
  the output → silent incorrect charges possible

What I Cannot Break:
- The core formula (rate * days * discount) — verified against spec,
  simple enough to be obviously correct
```

---

## Phase 2 — The Journey (cycle 1)

### Gold reviews Myrrh (excerpt):
```
Myrrh claims timezone handling at line 95 is a risk.
Verification: line 95 uses datetime.utcnow() — correct for UTC.
BUT: line 98 converts to local time using pytz.timezone("Asia/Shanghai").
This is hardcoded — if the vessel operates in a different timezone,
the conversion is wrong. Myrrh's risk is VERIFIED.

Updated: Myrrh's timezone risk → HIGH confidence.
```

### Frankincense reviews Gold (excerpt):
```
Gold verified 3 facts and refuted 1. Pattern: the one refuted fact
(half-rate threshold) is in a function that was added in the last commit
by a developer who didn't write the spec. This suggests a "knowledge
transfer gap" — the implementation diverged from the spec because
the implementer didn't have full context.

This connects to a broader pattern: the module has 3 authors and
no shared documentation of the pricing logic.
```

### Myrrh reviews Frankincense (excerpt):
```
Frankincense identifies a "knowledge transfer gap" — plausible but
unfalsifiable from code alone. Need git blame + developer interview
to confirm. Risk: this narrative could be used to excuse the bug
rather than fix it.

Frankincense's "dark path" observation for the emergency pricing
is STRONG — I tried to construct a test case and the path requires
a specific combination of vessel type + port congestion that I
cannot generate from the available test data. This is a genuine
blind spot.
```

---

## Phase 3 — The Manger (hm)

```
FACTUAL: 0.9 — All Gifts now agree on the half-rate bug and timezone risk.
Minor disagreement on whether the spec itself is correct (Gold says outside scope,
Myrrh says it should be checked).

INTERPRETIVE: 0.8 — Frankincense's "knowledge transfer gap" narrative is accepted
by Gold but questioned by Myrrh (plausible but unfalsifiable).

RISK: 0.7 — All major risks identified. Emergency path risk still unquantified
(no test data available). Myrrh accepts this as "known unknown."

OVERALL: 0.9*0.4 + 0.8*0.3 + 0.7*0.3 = 0.36 + 0.24 + 0.21 = 0.81
CONVERGED: YES (≥0.7)
```

---

## Phase 4 — Gift

```markdown
# Gift — Demurrage Module Code Review

## 判定 (Verdict)
The module has 2 confirmed bugs (half-rate threshold, timezone hardcoding)
and 1 structural risk (untested emergency path). DO NOT deploy until
these are fixed. The core formula is correct.

## 確信トポロジー (Confidence Topology)
| Claim | Confidence | Evidence | Dissent |
|-------|-----------|----------|---------|
| Half-rate threshold wrong | High | Gold: line 67 vs spec §3.4 | None |
| Timezone hardcoded | High | Gold: line 98 pytz hardcode | None |
| Emergency path untested | High | Myrrh: zero coverage | None |
| Knowledge transfer gap | Medium | Frankincense: 3 authors, no docs | Myrrh: unfalsifiable |

## 既知の未知 (Known Unknowns)
- Whether the spec itself matches the contract (need contract review)
- Emergency path behavior under real conditions (need integration test)

## 行動項目 (Action Items)
1. Fix half-rate threshold: change `> 3` to `> 2` at line 67
2. Make timezone configurable: replace hardcoded "Asia/Shanghai"
3. Add integration test for emergency pricing path
4. Document pricing logic for future developers

## 異議記録 (Dissent Record)
Myrrh questioned whether the spec should be verified against the contract
(Gold and Frankincense considered this out of scope). Recommend separate
contract review as follow-up.
```
