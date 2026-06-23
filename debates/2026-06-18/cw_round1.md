TASK: Kimi efficiency

---

## RANKED SAVINGS STRATEGIES

### Tier 1 — Immediate (High Impact, Low Risk)
1. **Disable thinking/reasoning output for non-diagnostic calls**
   - Kimi defaults to outputting ~80% thinking tokens. Set `thinking_enabled=false` on all MAGI Gold dispatch calls except when reasoning trace is explicitly needed for audit/debug.
   - Estimated savings: 60–70% of per-call token burn.

2. **Truncate thinking max_tokens ceiling**
   - Where thinking output is required, cap `thinking_max_tokens` at 800 (down from default ~4096). A diagnostic trace rarely benefits from more than a few hundred tokens of reasoning.
   - Estimated savings: 30–40% reduction on thinking-enabled calls.

3. **Strip thinking from response before downstream processing**
   - On calls where thinking is returned, discard the `reasoning_content` field in the MAGI Gold handler. Pass only `content` to the next stage of the pipeline.
   - Savings: eliminates double-counting of thinking tokens in accumulated context windows.

### Tier 2 — Near-Term (Medium Impact, Some Coordination)
4. **Consolidate multi-call patterns into single prompts**
   - The SOF test triggered 2 calls. Audit all MAGI Gold dispatch paths for unnecessary serialization. Where two calls are semantically sequential (e.g., classify → generate), combine into a single structured prompt with delimited output sections.
   - Estimated savings: 40–50% round-trip overhead (system prompt duplication, token padding).

5. **Cache system prompt as prefix**
   - Kimi supports `prefix_cache`. Pre-store the MAGI Gold system prompt to avoid re-billing on every call. Only effective when prompt structure is stable.
   - Savings: system prompt tokens (~500–2000) per call after cache warm.

6. **Temperature and sampling optimization**
   - Remove explicit `temperature` and `top_p` params to let provider defaults handle it. Some providers bill extra tokens for explicit sampling overrides.
   - Minimal savings but zero risk.

### Tier 3 — Strategic (Long-Term, Requires Architecture)
7. **Rate-limit budget-aware dispatch**
   - Implement per-session/per-hour token budgets. If near quota, downgrade non-critical calls to cheaper models or shorter prompts.
   - Prevents quota exhaustion but requires dispatch middleware.

8. **Response compression pipeline**
   - Post-process Kimi responses to compress verbose output (deduplicate, summarize redundancies) before they enter the agent's context window cascade.
   - Savings compound across conversation turns.

---

## RISKS

| Risk | Severity | Mitigation |
|------|----------|------------|
| Disabling thinking on complex reasoning tasks degrades answer quality | HIGH | Whitelist thinking for `magi:diagnose`, `magi:audit`, and `magi:complex_plan` dispatch tags. Disable for all others. |
| Capped thinking truncates critical reasoning mid-chain | MEDIUM | Monitor truncation rate. If >5% of thinking-enabled calls hit the cap, raise ceiling incrementally. |
| Combined prompts increase per-call latency | MEDIUM | Only combine when total combined token count stays under 8K input. Split if exceeding. |
| Prefix cache invalidation on prompt churn | LOW | Hash the system prompt; only enable cache when hash is stable for ≥10 calls. |
| Stripping thinking loses audit trail | LOW | Archive reasoning traces to cold storage (logs/S3) rather than keeping them in-context. |

---

## DISPATCH TEMPLATE

```json
{
  "dispatch": {
    "model": "kimi",
    "params": {
      "temperature": null,
      "top_p": null,
      "thinking_enabled": false,
      "prefix_cache": true
    },
    "overrides": {
      "magi:diagnose": {
        "thinking_enabled": true,
        "thinking_max_tokens": 800
      },
      "magi:audit": {
        "thinking_enabled": true,
        "thinking_max_tokens": 800
      },
      "magi:complex_plan": {
        "thinking_enabled": true,
        "thinking_max_tokens": 1200
      },
      "magi:generate": {
        "thinking_enabled": false,
        "max_tokens": 4096
      },
      "magi:classify": {
        "thinking_enabled": false,
        "max_tokens": 256
      },
      "magi:summarize": {
        "thinking_enabled": false,
        "max_tokens": 2048
      }
    },
    "post_process": {
      "strip_thinking": true,
      "archive_thinking": "cold_storage",
      "compress_output": false
    },
    "budget": {
      "session_cap_tokens": 100000,
      "hourly_cap_tokens": 80000,
      "downgrade_on_warning": "deepseek-v3"
    }
  }
}
```

**Usage notes:**
- Default: thinking OFF, prefix cache ON, no explicit temp/top_p.
- Three whitelisted tags get thinking ON with tight caps.
- Classify/summarize/generate tags get thinking OFF and appropriate output limits.
- Post-processing strips thinking from pipeline context; archives to cold storage for audit.
- Budget guardrails prevent a repeat of the 13%-quota-in-2-calls scenario.
