#!/usr/bin/env bash
# MAGI 席位容器入口:seed 凭证与 QUINTE_HOME → 跑一次完整 QUINTE →
# PA handoff 时等宿主桥接 → 把结果摘要落到 /artifacts。
set -euo pipefail

: "${SEAT_ID:?SEAT_ID required}"
POLICY_SRC=/config/policy.json
STATE=/state
ART=/artifacts
BRIEF=/input/brief.json

log() { printf '[%s] %s\n' "$SEAT_ID" "$*"; }

# --- 1) 凭证注入:只读挂载 → $HOME(挂载源缺失或为目录则跳过并告警)---
copy_file() { # src dst
  if [ -f "$1" ]; then
    mkdir -p "$(dirname "$2")"
    cp -f "$1" "$2" && chmod 600 "$2"
    log "cred: $2"
  else
    log "WARN cred missing: $1"
  fi
}
copy_dir() { # src dst
  if [ -d "$1" ] && [ -n "$(ls -A "$1" 2>/dev/null)" ]; then
    mkdir -p "$2"
    cp -a "$1/." "$2/"
    chmod -R go-rwx "$2"
    log "cred: $2"
  else
    log "WARN cred dir missing/empty: $1"
  fi
}

copy_dir  /cred/omp-agent            "$HOME/.omp/agent"
copy_file /cred/codewhale-config.toml "$HOME/.codewhale/config.toml"
copy_file /cred/opencode-auth.json    "$HOME/.local/share/opencode/auth.json"
copy_file /cred/kilo-auth.json        "$HOME/.local/share/kilo/auth.json"
# mimo 凭证三候选(adapters.rs 顺序:share/mimo → share/mimocode → config/mimo)
if ! copy_file /cred/mimocode/auth.json "$HOME/.local/share/mimocode/auth.json"; then :; fi
copy_file /cred/mimo-share/auth.json  "$HOME/.local/share/mimo/auth.json" || true
copy_file /cred/mimo-config/auth.json "$HOME/.config/mimo/auth.json" || true
copy_dir  /cred/claude               "$HOME/.claude"

# --- 2) state seed ---
mkdir -p "$STATE/runs"
if [ ! -f "$STATE/policy.json" ]; then
  cp "$POLICY_SRC" "$STATE/policy.json"
  log "policy seeded from $POLICY_SRC"
fi

[ -f "$BRIEF" ] || { log "FATAL: $BRIEF not found"; exit 64; }

# --- 3) 跑 run(--wait 在专用容器内是正确形态;会话侧禁令不适用于此)---
log "run start"
set +e
timeout 7200 quinte run --home "$STATE" --brief "$BRIEF" --wait --json | tee "$ART/run-$(date +%Y%m%dT%H%M%S).log"
rc=${PIPESTATUS[0]}
set -e

RUN_DIR=$(ls -1dt "$STATE"/runs/*/ 2>/dev/null | head -1 || true)
RUN_ID=$(basename "${RUN_DIR:-unknown}")
log "run exited rc=$rc run_id=$RUN_ID"

# --- 4) PA handoff(rc=10):写标记,等宿主 PA 桥把 run 推完 ---
if [ "$rc" -eq 10 ]; then
  echo "$RUN_ID" > "$ART/PA_HANDOFF"
  log "PA handoff: host 执行 quinte primary-arbiter request/submit --home <此 state 卷>"
  deadline=$(( $(date +%s) + 5400 ))
  while [ ! -f "$STATE/runs/$RUN_ID/result.json" ]; do
    if [ "$(date +%s)" -gt "$deadline" ]; then
      log "FATAL: PA 桥超时(90min)"
      exit 10
    fi
    sleep 30
  done
  rc=0
fi

# --- 5) 结果摘要 ---
STATUS="unknown"
if [ -f "$STATE/runs/$RUN_ID/result.json" ]; then
  STATUS=$(python3 -c "import json;print(json.load(open('$STATE/runs/$RUN_ID/result.json')).get('status','unknown'))" 2>/dev/null || echo unknown)
fi
printf 'seat=%s run_id=%s rc=%s status=%s\n' "$SEAT_ID" "$RUN_ID" "$rc" "$STATUS" > "$ART/SEAT_DONE"
log "done status=$STATUS"
[ "$rc" -eq 0 ] && [ "$STATUS" = "completed" ]
