# MAGI

A multi-seat decision organ: two or more physically isolated seats deliberate over a
file-based coordination channel, and a human arbiter issues final rulings. The name
is just a name. The protocol is seat-count agnostic — nothing in it assumes a
particular roster of machines.

MAGI is a governance protocol, not a product. It exists to make multi-agent
deliberation auditable: sealed message chains, Ed25519 signatures, machine-sourced
numbers only, pre-registered gates, and explicit quorum/degradation rules.

- **[CHARTER.md](CHARTER.md)** — the operating charter (v0.2), the single source of
  truth for how the organ works.
- **[watchdog/](watchdog/)** — the reference seat-liveness watchdog and heartbeat
  protocol (POSIX shell; launchd and systemd variants).

## Layout

| Path | Content |
|---|---|
| `CHARTER.md` | The charter: scope, seat mandates, communication integrity, decision cycle, deterministic gates, quorum, two-speed modes, authorization boundary, amendment procedure |
| `AGENTS.md` | Contribution rules for agent sessions working in this repo |
| `watchdog/` | Seat-liveness watchdog: heartbeat protocol doc + darwin (launchd) and linux (systemd) reference implementations |

## Non-goals

MAGI produces **recommendations only** (rulings + confidence + counterfactuals).
Execution authority lives elsewhere (downstream executor systems and the human
arbiter). The organ never executes. The watchdog is liveness **observability only**:
it alerts, it never restarts anything.

## License

GPL-3.0-or-later. This program is free software: you may redistribute and/or modify it under the terms of the GNU General Public License v3 (see `LICENSE`).
