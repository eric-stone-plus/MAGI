#!/usr/bin/env bash
# MAGI 席位容器入口:seed 凭证与 QUINTE_HOME → 跑一次完整 QUINTE →
# PA handoff 时等宿主桥接 → 把结果摘要落到 /artifacts。
# 注意:`quinte run` 到达 waiting_primary_arbiter 时以 **exit 0** 返回
# (CLI.md exit-code 表),状态必须从 stdout 的 JSON envelope 解析,不能看 rc。
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
  return 0
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
  return 0
}

copy_dir  /cred/omp-agent            "$HOME/.omp/agent"
copy_file /cred/codewhale-config.toml "$HOME/.codewhale/config.toml"
copy_file /cred/opencode-auth.json    "$HOME/.local/share/opencode/auth.json"
copy_file /cred/kilo-auth.json        "$HOME/.local/share/kilo/auth.json"
# mimo 凭证三候选(adapters.rs 顺序:share/mimo → share/mimocode → config/mimo)
copy_file /cred/mimocode/auth.json    "$HOME/.local/share/mimocode/auth.json"
copy_file /cred/mimo-share/auth.json  "$HOME/.local/share/mimo/auth.json"
copy_file /cred/mimo-config/auth.json "$HOME/.config/mimo/auth.json"
copy_dir  /cred/claude               "$HOME/.claude"

# --- 2) state seed ---
mkdir -p "$STATE/runs"
if [ ! -f "$STATE/policy.json" ]; then
  cp "$POLICY_SRC" "$STATE/policy.json"
  log "policy seeded from $POLICY_SRC"
fi

[ -f "$BRIEF" ] || { log "FATAL: $BRIEF not found"; exit 64; }

# --- 3) 跑 run(--wait 在专用容器内是正确形态;会话侧禁令不适用于此)---
LOG="$ART/run-$(date +%Y%m%dT%H%M%S)"
log "run start"
set +e
timeout 7200 quinte run --home "$STATE" --brief "$BRIEF" --wait --json >"$LOG.json" 2>"$LOG.err"
rc=$?
set -e

parse_env() { # key — 从 stdout envelope 取 data.<key>
  python3 - "$1" "$LOG.json" <<'PY' 2>/dev/null
import json, sys
key, path = sys.argv[1], sys.argv[2]
for line in reversed(open(path).read().splitlines()):
    line = line.strip()
    if line.startswith("{"):
        try:
            print(json.loads(line).get("data", {}).get(key, ""))
            break
        except Exception:
            continue
PY
}

RUN_ID=$(parse_env run_id)
STATUS=$(parse_env status)
if [ -z "$RUN_ID" ]; then
  RUN_ID=$(basename "$(ls -1dt "$STATE"/runs/*/ 2>/dev/null | head -1 || echo unknown)")
fi
log "run exited rc=$rc run_id=$RUN_ID status=$STATUS"

finish() { # rc status
  printf 'seat=%s run_id=%s rc=%s status=%s\n' "$SEAT_ID" "$RUN_ID" "$1" "$2" > "$ART/SEAT_DONE"
  log "done rc=$1 status=$2"
  exit "$1"
}

# --- 4) PA handoff:写标记,等宿主 PA 桥(submit 即触发 deterministic merge)---
if [ "$STATUS" = "waiting_primary_arbiter" ]; then
  echo "$RUN_ID" > "$ART/PA_HANDOFF"
  log "PA handoff:宿主在席容器内 exec primary-arbiter request/submit(见 README)"
  deadline=$(( $(date +%s) + 5400 ))
  while [ ! -f "$STATE/runs/$RUN_ID/result.json" ]; do
    if [ "$(date +%s)" -gt "$deadline" ]; then
      log "FATAL: PA 桥超时(90min)"
      finish 10 "pa_bridge_timeout"
    fi
    sleep 30
  done
  STATUS=$(python3 -c "import json;print(json.load(open('$STATE/runs/$RUN_ID/result.json')).get('status','unknown'))" 2>/dev/null || echo unknown)
  [ "$STATUS" = "completed" ] || [ "$STATUS" = "degraded" ] && finish 0 "$STATUS"
  finish 1 "$STATUS"
fi

# --- 5) 直接终态 ---
if [ "$rc" -eq 0 ] && { [ "$STATUS" = "completed" ] || [ "$STATUS" = "degraded" ]; }; then
  finish 0 "$STATUS"
fi
finish "${rc:-1}" "${STATUS:-unknown}"
