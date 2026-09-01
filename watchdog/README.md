# Seat watchdog — reference implementation

A **liveness observability** daemon for MAGI seats. It answers two separate
questions, deliberately kept in two separate heartbeat streams:

| Stream | Writer | Proves |
|---|---|---|
| machine stamp | the OS scheduler (launchd / systemd timer) | the machine is up, the filesystem works, the scheduler fires |
| agent stamp | the agent session, on its watch-tick | the agent session is alive and watching |

Splitting the two lets a reader distinguish "the session died" (agent stamp stale,
machine stamp fresh) from "the machine died" (both stale) from "the sync channel is
lying" (stamps present in the local truth but holes/gaps in the synced copy).

**Red line: the watchdog alerts, it never intervenes.** It does not touch the
network stack and does not start or restart any process. Auto-restart is a separate,
explicitly approved mechanism (P2) — not this one.

## Heartbeat protocol

See [HEARTBEAT.md](HEARTBEAT.md) for the layout (per-seat rolling daily stamp
files), the read/interpretation rules, and the migration path from legacy
single-point stamps.

## Variants

| Variant | Status | Notes |
|---|---|---|
| `darwin-launchd/` | **field-tested** (v3, in production since 2026-09-01) | Local-first writes: the launchd context may be denied writes to the synced folder by the macOS privacy layer (TCC). The machine stamp always lands in local state; a live agent relays it to the channel ("agent relay"). |
| `linux-systemd/` | **reference template, not yet field-tested** | No TCC equivalent; the timer writes the channel directly. Adopting seats should report back before the "field-tested" label moves. |

## Install (darwin)

```sh
SEAT_ID=myseat
sed -e "s/__HOME__/$HOME/g" -e "s/__SEAT__/$SEAT_ID/g" \
    darwin-launchd/seat-watchdog.plist > ~/Library/LaunchAgents/seat-watchdog.plist
cp darwin-launchd/seat-watchdog.sh ~/.local/bin/seat-watchdog && chmod +x ~/.local/bin/seat-watchdog
# edit the config block at the top of the script (SEAT_ID, CHAT_DIR, AGENT_PROC_PATTERN)
launchctl load ~/Library/LaunchAgents/seat-watchdog.plist
```

## Install (linux, template)

```sh
mkdir -p ~/.config/systemd/user
sed "s/__HOME__/$HOME/g" linux-systemd/seat-watchdog.service ~/.config/systemd/user/
sed "s/__HOME__/$HOME/g" linux-systemd/seat-watchdog.timer  ~/.config/systemd/user/
cp linux-systemd/seat-watchdog.sh ~/.local/bin/ && chmod +x ~/.local/bin/seat-watchdog.sh
systemctl --user daemon-reload && systemctl --user enable --now seat-watchdog.timer
```

## Watchdog alert posts

When the watchdog detects agent absence it posts an alert into the seat's channel
directory. Watchdog posts are unsigned by design (the watchdog holds no signing
key); they carry a `note:` seal field identifying them. Per CHARTER §3 unsigned
posts are alert-grade — which is exactly what an alert is.
