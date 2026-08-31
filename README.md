# MAGI

A three-seat decision organ: three physically isolated seats (`arch`, `mac`, `fedora`)
deliberate over a file-based coordination channel, and a human arbiter (eric) issues
final rulings. The name is just a name.

MAGI is a governance protocol, not a product. It exists to make multi-agent
deliberation auditable: sealed message chains, Ed25519 signatures, machine-sourced
numbers only, pre-registered gates, and explicit quorum/degradation rules.

- **[CHARTER.md](CHARTER.md)** — the operating charter (v0.1), the single source of
  truth for how the organ works.

## Layout

| Path | Content |
|---|---|
| `CHARTER.md` | The charter: scope, seat domains, communication integrity, decision cycle, deterministic gates, quorum, two-speed modes, authorization boundary, amendment procedure |
| `AGENTS.md` | Contribution rules for agent sessions working in this repo |

## Non-goals

MAGI produces **recommendations only** (rulings + confidence + counterfactuals).
Execution authority lives elsewhere (downstream executor systems and the human
arbiter). The organ never executes.
