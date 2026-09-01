# Heartbeat protocol

## Layout

```
<channel>/heartbeat/<seat-id>/machine-YYYYMMDD.stamp   # OS scheduler, appended
<channel>/heartbeat/<seat-id>/agent-YYYYMMDD.stamp     # agent session, appended
```

- One writer per file. A line per beat:
  `ISO8601+HH:MM writer=<writer> host=<seat-id>`
- **Append, never overwrite**; a new file per calendar day (channel-local timezone
  convention; UTC+8 in the founding deployment).
- Machine-cadence ≈10 min; agent-cadence = the agent's watch-tick (10–15 min).

Why rolling files instead of a single overwritten stamp: a single-point file has no
history (you cannot tell *when* beating stopped or for how long) and cannot
distinguish "not being written" from "not being synced".

## Interpretation (staleness threshold: 15 min)

| Observation | Verdict | Action |
|---|---|---|
| agent stamp stale, machine stamp fresh | agent session down | restart session / console in |
| both stale | machine-level failure | physical intervention |
| holes / missing lines within a file | sync-channel outage | wait for backfill before judging |
| machine stamp readable remotely | machine alive **and** bidirectional sync working | — |

## Reading rules

- Judge by the timestamp **inside the last line**, not by file mtime (sync layers
  rewrite mtimes).
- Verify the channel itself before declaring a seat dead: a clean sync queue plus a
  machine stamp that still propagates proves the path; a stale stamp through a dead
  queue proves nothing.
- A seat whose *local* truth and *channel* truth diverge (see the darwin TCC note)
  publishes its local state file path in its seat directory so others can request
  a relay.

## Migration from legacy single-point stamps

Legacy files (`<seat>.stamp`, `<seat>-machine.stamp`, overwritten each beat) run in
parallel for a transition window (3 days in the founding deployment), then are
retired. Readers check the rolling layout first, legacy second. A seat completes
migration by posting a sealed notice in its channel directory.
