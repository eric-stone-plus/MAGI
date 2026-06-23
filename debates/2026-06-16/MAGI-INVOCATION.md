# MAGI — Invocation & Mechanism

> 2026-06-14 · How to actually run MAGI

## Trigger

User says "magi [topic]" → load `magi` skill → execute full protocol.

No LITE mode. No FLASH mode. Full protocol or nothing.

## Execution Flow

### Phase 0 — The Star (星)

hm performs:
1. Decompose the question into testable sub-claims
2. Gather evidence (files, documents, code, data)
3. Assign Gifts (who gets Gold, Frankincense, Myrrh)
4. Clarify with user if ambiguous (Star gate — the only interactive phase)

**Gift assignment default**: hm = Myrrh (domain knowledge → best at risk).
Delegates get Gold and Frankincense.

### Phase 1 — The Offering (獻禮)

Parallel dispatch via `delegate_task`:

```python
delegate_task(tasks=[
    {
        "goal": "You are GOLD (金)... [Gift prompt + evidence]",
        "toolsets": ["terminal", "file"]
    },
    {
        "goal": "You are FRANKINCENSE (乳香)... [Gift prompt + evidence]",
        "toolsets": ["terminal", "file"]
    }
])
```

hm simultaneously produces Myrrh analysis (not delegated — hm holds Myrrh).

All three outputs written to `/tmp/magi-audit/<topic-slug>/phase1_*.md`.

### Phase 2 — The Journey (旅路)

Dialectical spiral. Each Gift reviews the PREVIOUS Gift's output:

```
Gold reviews Myrrh's Phase 1
Frankincense reviews Gold's Phase 1
Myrrh reviews Frankincense's Phase 1
```

Each review is dispatched via `delegate_task` (or hm does Myrrh's review directly).
Reviews written to `/tmp/magi-audit/<topic-slug>/phase2_cycle1_*.md`.

Default: 1 cycle (3 reviews). Can extend to 2-3 cycles if Phase 3 fails.

### Phase 3 — The Manger (馬槽)

hm evaluates convergence:

| Dimension | Weight | Score Range |
|-----------|--------|-------------|
| Factual | 0.4 | 0.0-1.0 |
| Interpretive | 0.3 | 0.0-1.0 |
| Risk | 0.3 | 0.0-1.0 |

Weighted sum ≥0.7 → converged.
Weighted sum <0.7 → identify weakest dimension → restart Phase 2 focused on that.
Max 2 restarts.

### Phase 4 — The Revelation (啟示)

hm synthesizes final output:
- 判定 (Verdict) — clear, actionable conclusion
- 確信トポロジー (Confidence Topology) — every claim rated
- 既知の未知 (Known Unknowns) — explicit gaps
- 行動項目 (Action Items) — next steps
- 異議記録 (Dissent Record) — unresolved disagreements

## Delegate Dispatch Details

### delegate_task 401 Fallback

When mimo API key is invalid, `delegate_task` returns 401.
Fallback: `claude -p --model mimo-v2.5-pro --effort max` via terminal background.

```python
# Primary: delegate_task (inherits mimo)
delegate_task(tasks=[...])

# Fallback: claude -p (delegate_task 401)
terminal(background=True, notify_on_complete=True, timeout=300,
  command='HOME=/Users/ericstone claude -p --model mimo-v2.5-pro --effort max "prompt" > /tmp/output.txt 2>&1')
```

### 429 Rate Limit

mimo free tier has concurrent limits. Max 2 parallel delegates.
Serial start with ≥10s gap if needed.
Never fallback to DeepSeek — user's cost, mimo is free.

### cc Effort Levels

`claude --effort` valid values: low/medium/high/xhigh/max.
MAGI requires `max`. Default `xhigh` is not enough.

## Prompt Templates

Each Gift has a prompt template in `prompts/{gold,frankincense,myrrh}.md`.
Templates define:
- The Gift's epistemological stance
- Output format (unique per Gift — structural anti-drift)
- Behavioral rules
- Anti-drift checks ("If you find yourself doing X, STOP")

## Output Structure

```
/tmp/magi-audit/<topic-slug>/
├── phase0_star.md
├── phase1_gold.md
├── phase1_frankincense.md
├── phase1_myrrh.md
├── phase2_cycle1_gold.md
├── phase2_cycle1_frankincense.md
├── phase2_cycle1_myrrh.md
├── phase3_manger.md
├── phase4_revelation.md
└── manifest.json
```

## Integration with QUINTE

MAGI's Revelation can feed into QUINTE as evidence:

```
MAGI Revelation → QUINTE R1 evidence package → QUINTE R2 cross-review → QUINTE R3 verdict
```

This is the "MAGI investigates, QUINTE authorizes" pipeline.
MAGI does the heavy lifting (investigation, analysis, confidence mapping).
QUINTE does the final authorization (push, deploy, commit).
