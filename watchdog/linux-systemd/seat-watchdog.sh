#!/bin/bash
# seat-watchdog — alert-grade liveness watchdog (linux/systemd variant)
# REFERENCE TEMPLATE — not yet field-tested. Port of the darwin v3 logic;
# report adoption in the channel before treating this as proven.
#
# On linux there is no TCC equivalent: a user systemd timer writes the channel
# directly, so no local-first/relay split is needed. Everything else is identical:
# dual stamps (machine/agent roles stay separate writers), alert-grade only.
#
# RED LINE: writes files and posts local notifications only. Never touches the
# network stack, never starts or restarts any process (auto-restart is a separate,
# explicitly approved mechanism).

set -u

# ---- config ----------------------------------------------------------------
SEAT_ID="changeme"
CHAT_DIR="$HOME/OneDrive/Documents/chat"   # your synced channel folder
AGENT_PROC_PATTERN='claude'                # process-name pattern of the agent session
TZ_NAME="Asia/Shanghai"                    # channel timezone convention
# ----------------------------------------------------------------------------

HB="$CHAT_DIR/heartbeat"
STATE="$HOME/.local/state/seat-watchdog"
LOG="$HOME/.local/state/seat-watchdog/watchdog.log"

log() { echo "$(date '+%Y-%m-%d %H:%M:%S') $*" >> "$LOG"; tail -c 8192 "$LOG" > "$LOG.tmp" 2>/dev/null && mv "$LOG.tmp" "$LOG"; return 0; }

mkdir -p "$STATE" 2>/dev/null
STAMP_LINE="$(TZ=$TZ_NAME date '+%Y-%m-%dT%H:%M:%S%z' | sed -E 's/([0-9]{2})([0-9]{2})$/\1:\2/') writer=systemd host=$SEAT_ID"
TODAY=$(TZ=$TZ_NAME date '+%Y%m%d')

# (1) machine liveness stamp: local truth + channel copy + rolling stamp
printf '%s\n' "$STAMP_LINE" > "$STATE/machine.stamp"
if printf '%s\n' "$STAMP_LINE" > "$HB/$SEAT_ID-machine.stamp" 2>/dev/null; then
  BOARD_OK=1
else
  BOARD_OK=0
  touch "$STATE/board-write-blocked"
fi
mkdir -p "$HB/$SEAT_ID" 2>/dev/null
printf '%s\n' "$STAMP_LINE" >> "$HB/$SEAT_ID/machine-$TODAY.stamp" 2>/dev/null || true

# (2) agent detection: full-command ps first, pgrep -f as fallback
if ps -eo comm,args | grep -v grep | grep -qE "(^|/)${AGENT_PROC_PATTERN}( |$)" || pgrep -f "$AGENT_PROC_PATTERN" >/dev/null 2>&1; then
  log "agent alive; stamp ok (board=$BOARD_OK)"
  exit 0
fi

# (3) agent absent -> local alert + notification always, board post best-effort
NOW=$(TZ=$TZ_NAME date '+%Y-%m-%d %H:%M')
printf '%s\n' "$NOW agent-down" >> "$STATE/alerts.log"
log "AGENT DOWN — local alert + notification sent (board=$BOARD_OK)"
notify-send "seat-watchdog" "seat $SEAT_ID: agent session absent ($NOW)" 2>/dev/null || true
systemd-cat -t seat-watchdog -p warning echo "agent session absent ($NOW)" 2>/dev/null || true

[ "$BOARD_OK" = 1 ] || exit 0
latest_seat_post() {
  local d t f
  for d in "$(TZ=$TZ_NAME date '+%Y%m%d')" "$(TZ=$TZ_NAME date -d '-1 day' '+%Y%m%d')" "$(TZ=$TZ_NAME date -d '-2 days' '+%Y%m%d')" "$(TZ=$TZ_NAME date -d '-3 days' '+%Y%m%d')"; do
    for t in "$CHAT_DIR/$d/$SEAT_ID" "$CHAT_DIR/archive/$d/$SEAT_ID"; do
      f=$(ls -1 "$t"/*.md 2>/dev/null | sort | tail -1)
      [ -n "${f:-}" ] && { echo "$f"; return 0; }
    done
  done
  return 1
}
N=$(ls -1 "$CHAT_DIR/$TODAY/$SEAT_ID"/*.md 2>/dev/null | sed "s/.*$SEAT_ID-\([0-9][0-9]*\)-.*/\1/" | sort -n | tail -1)
N=${N:-0}
SEQ=$((10#$N + 1))
POST="$CHAT_DIR/$TODAY/$SEAT_ID/$TODAY-$SEAT_ID-$(printf '%02d' "$SEQ")-watchdog-agent-down.md"
PREV=$(latest_seat_post || true)
PREV_NAME=$(basename "${PREV:-none}")
PREV_SHA=$(awk '/body-sha16/{print $2}' "${PREV:-/dev/null}" 2>/dev/null || echo unknown)
printf '# [%s] Watchdog alert: seat agent session absent (P1 auto-post)\n\n- systemd watchdog patrol %s: no agent session process detected (ps/pgrep both empty)\n- the in-session watch-tick died with it; this post comes from the out-of-session watchdog (alert-grade, no restart)\n- machine liveness stamp keeps beating (local filesystem healthy, session absent); open a new session to resume the watch\n' "$SEAT_ID" "$NOW" > "$POST"
H=$(perl -0777 -ne '$b=/^(.*?)<!-- seal/s?$1:$_; $b=~s/\s+$//; $b.="\n"; print $b' "$POST" | sha256sum | cut -c1-16)
printf '\n<!-- seal\nseat: %s\nts: %s\nbody-sha16: %s\nprev: %s\nprev-sha16: %s\nnote: watchdog auto-post (systemd), unsigned by design, chains to latest seat post\n-->\n' "$SEAT_ID" "$NOW" "$H" "$PREV_NAME" "$PREV_SHA" >> "$POST"
log "alert posted: $(basename "$POST") sha16=$H prev=$PREV_NAME"
exit 0
