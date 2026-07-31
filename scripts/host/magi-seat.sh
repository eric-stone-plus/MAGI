#!/usr/bin/env bash
set -euo pipefail
umask 077

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)
COMPOSE="$ROOT/container/compose.yml"

usage() {
  cat >&2 <<'EOF'
Usage:
  magi-seat.sh run --seat ID --trial DIR --brief FILE --evidence-manifest FILE --assignment-plan FILE --seat-config FILE --policy FILE --secret-file FILE [--profile-source DIR | --technical-base DIR --technical-agents FILE --technical-config FILE] [--json]
  magi-seat.sh agent
  magi-seat.sh reviewer-agent --seat ID
  magi-seat.sh final-agent

Secrets may be supplied by file. On macOS, --keychain-service NAME materializes
one temporary mode-0600 secret from Keychain and removes it on exit.
EOF
  exit 2
}

absolute() { python3 -c 'import os,sys; print(os.path.abspath(sys.argv[1]))' "$1"; }

profile_python() {
  if [[ -n "${MAGI_PROFILE_PYTHON:-}" ]]; then printf '%s\n' "$MAGI_PROFILE_PYTHON"; return; fi
  local candidate="$HOME/Private/agent-design/hermes/agent/.venv/bin/python"
  if [[ -x "$candidate" ]]; then printf '%s\n' "$candidate"; else printf '%s\n' python3; fi
}

default_technical_base() {
  local platform
  case "$(uname -s)" in Darwin) platform=mac;; Linux) platform=linux;; *) return 1;; esac
  printf '%s\n' "${MAGI_TECHNICAL_BASE:-$HOME/Private/agent-design/hermes/rules/$platform}"
}

default_technical_config() {
  if [[ -n "${MAGI_TECHNICAL_CONFIG:-}" ]]; then printf '%s\n' "$MAGI_TECHNICAL_CONFIG"; return; fi
  printf '%s\n' "${HERMES_HOME:-$HOME/.hermes/profiles/technical}/config.yaml"
}

compose_profile() {
  local seat=$1 trial=$2 base=$3 agents=$4 config=$5
  local overlay
  case "$seat" in
    seat-m) overlay=$ROOT/profiles/formalist;;
    seat-d) overlay=$ROOT/profiles/adversarial;;
    seat-g) overlay=$ROOT/profiles/empirical;;
  esac
  local root="$trial/trial-private/composed-profiles"
  local destination="$root/$seat"
  mkdir -p "$root"
  chmod 0700 "$trial/trial-private" "$root" 2>/dev/null || true
  "$(profile_python)" "$ROOT/scripts/host/lib/compose_profile.py" compose \
    --technical-base "$base" --technical-agents "$agents" --technical-config "$config" \
    --overlay "$overlay" --destination "$destination" --seat "$seat" >/dev/null
  printf '%s\n' "$destination"
}

sha256_file() {
  python3 - "$1" <<'PY'
import hashlib, sys
with open(sys.argv[1], "rb") as handle:
    print("sha256:" + hashlib.file_digest(handle, "sha256").hexdigest())
PY
}

secret_is_private() {
  local mode
  mode=$(stat -f '%Lp' "$1" 2>/dev/null || stat -c '%a' "$1" 2>/dev/null) || return 1
  [[ "$mode" = 600 || "$mode" = 400 ]]
}

wait_for_proxy() {
  local service=$1 deadline=$(( $(date +%s) + 45 )) state
  while (( $(date +%s) <= deadline )); do
    state=$(docker compose -f "$COMPOSE" ps --format json "$service" 2>/dev/null | python3 -c '
import json, sys
raw=sys.stdin.read().strip()
if not raw: print(""); raise SystemExit
try:
    value=json.loads(raw)
except json.JSONDecodeError:
    value=json.loads(raw.splitlines()[-1])
if isinstance(value, list): value=value[0] if value else {}
print(value.get("Health", ""))
' 2>/dev/null || true)
    [[ "$state" = healthy ]] && return 0
    [[ "$state" = unhealthy ]] && break
    sleep 1
  done
  printf 'seat egress proxy did not become healthy: %s\n' "$service" >&2
  return 2
}

run_seat() {
  local seat= trial= brief= evidence_manifest= assignment_plan= profile= technical_base= technical_agents= technical_config=
  local seat_config= policy= secret= keychain= json=0
  while (($#)); do
    case "$1" in
      --seat) seat=$2; shift 2;; --trial) trial=$2; shift 2;; --brief) brief=$2; shift 2;;
      --evidence-manifest) evidence_manifest=$2; shift 2;; --assignment-plan) assignment_plan=$2; shift 2;;
      --profile-source) profile=$2; shift 2;; --technical-base) technical_base=$2; shift 2;;
      --technical-agents) technical_agents=$2; shift 2;; --technical-config) technical_config=$2; shift 2;;
      --policy) policy=$2; shift 2;;
      --seat-config) seat_config=$2; shift 2;;
      --secret-file) secret=$2; shift 2;; --keychain-service) keychain=$2; shift 2;;
      --json) json=1; shift;; *) usage;;
    esac
  done
  [[ "$seat" =~ ^seat-[mdg]$ && -n "$trial" && -n "$brief" && -n "$evidence_manifest" && -n "$assignment_plan" && -n "$seat_config" && -n "$policy" ]] || usage
  [[ -f "$brief" && -f "$evidence_manifest" && -f "$assignment_plan" && -f "$policy" && -f "$seat_config" ]] || { printf 'invalid brief, evidence manifest, assignment plan, seat config, or policy\n' >&2; exit 2; }
  python3 "$ROOT/scripts/host/lib/seat_artifacts.py" validate brief "$brief" >/dev/null || exit 2
  python3 "$ROOT/scripts/host/lib/seat_artifacts.py" validate seat "$seat_config" >/dev/null || exit 2
  python3 "$ROOT/scripts/host/lib/seat_artifacts.py" validate policy "$policy" --seat "$seat_config" >/dev/null || exit 2

  (
    local temp_secret=
    cleanup() { [[ -z "$temp_secret" ]] || rm -f -- "$temp_secret"; }
    trap cleanup EXIT HUP INT TERM
    if [[ -n "$keychain" ]]; then
      [[ "$(uname -s)" = Darwin ]] || { printf -- '--keychain-service is macOS-only\n' >&2; exit 2; }
      temp_secret=$(mktemp "${TMPDIR:-/tmp}/magi-provider-key.XXXXXX")
      chmod 0600 "$temp_secret"
      security find-generic-password -s "$keychain" -w > "$temp_secret"
      secret=$temp_secret
    fi
    [[ -n "$secret" && -f "$secret" && -s "$secret" ]] || { printf 'provider secret file is missing/empty\n' >&2; exit 2; }
    secret_is_private "$secret" || { printf 'provider secret file mode must be 0400 or 0600\n' >&2; exit 2; }

    trial=$(absolute "$trial"); brief=$(absolute "$brief")
    evidence_manifest=$(absolute "$evidence_manifest"); assignment_plan=$(absolute "$assignment_plan")
    MAGI_CONTAINER_UID=${MAGI_CONTAINER_UID:-$(id -u)}
    MAGI_CONTAINER_GID=${MAGI_CONTAINER_GID:-$(id -g)}
    export MAGI_CONTAINER_UID MAGI_CONTAINER_GID
    seat_config=$(absolute "$seat_config"); policy=$(absolute "$policy"); secret=$(absolute "$secret")
    [[ "$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))["seat_id"])' "$seat_config")" = "$seat" ]] || { printf 'seat config ID mismatch\n' >&2; exit 2; }
    if [[ -n "$profile" ]]; then
      [[ -z "$technical_base$technical_agents$technical_config" ]] || { printf 'choose --profile-source or technical composition, not both\n' >&2; exit 2; }
      profile=$(absolute "$profile")
      "$(profile_python)" "$ROOT/scripts/host/lib/compose_profile.py" validate "$profile" --seat "$seat" >/dev/null || exit 2
    else
      technical_base=${technical_base:-$(default_technical_base)}
      technical_agents=${technical_agents:-${MAGI_TECHNICAL_AGENTS:-}}
      technical_config=${technical_config:-$(default_technical_config)}
      [[ -n "$technical_agents" ]] || { printf 'set --technical-agents or MAGI_TECHNICAL_AGENTS\n' >&2; exit 2; }
      profile=$(compose_profile "$seat" "$trial" "$(absolute "$technical_base")" "$(absolute "$technical_agents")" "$(absolute "$technical_config")")
    fi
    [[ -f "$profile/config.yaml" && -f "$profile/profile.json" && -f "$profile/SOUL.md" && -f "$profile/AGENTS.md" ]] || { printf 'profile source is incomplete\n' >&2; exit 2; }
    python3 "$ROOT/scripts/host/lib/profile_digest.py" "$profile" >/dev/null || exit 2
    local artifact_root=${MAGI_SEAT_ARTIFACT_ROOT:-$trial/seat-work}
    artifact_root=$(absolute "$artifact_root")
    mkdir -p "$artifact_root/$seat"
    chmod 0700 "$trial" "$artifact_root" "$artifact_root/$seat" 2>/dev/null || true

    export MAGI_ARTIFACT_ROOT="$artifact_root" MAGI_ORIGINAL_BRIEF="$brief"
    export MAGI_EVIDENCE_ROOT="$(dirname "$evidence_manifest")" MAGI_ASSIGNMENT_PLAN="$assignment_plan"
    export MAGI_SEAT_M_PROFILE="$profile" MAGI_SEAT_D_PROFILE="$profile" MAGI_SEAT_G_PROFILE="$profile"
    export MAGI_SEAT_M_CONFIG="$seat_config" MAGI_SEAT_D_CONFIG="$seat_config" MAGI_SEAT_G_CONFIG="$seat_config"
    export MAGI_SEAT_M_POLICY="$policy" MAGI_SEAT_D_POLICY="$policy" MAGI_SEAT_G_POLICY="$policy"
    export MAGI_SEAT_M_SECRET_FILE="$secret" MAGI_SEAT_D_SECRET_FILE="$secret" MAGI_SEAT_G_SECRET_FILE="$secret"
    # Fail closed when a caller-supplied pin disagrees with the image about to run.
    # MAGI_REQUIRED_IMAGE_DIGEST is the assignment-plan / receipt pin (sha256:hex).
    if [[ -n "${MAGI_REQUIRED_IMAGE_DIGEST:-}" ]]; then
      python3 - "$ROOT" "${MAGI_SEAT_IMAGE:-magi-seat:local}" "$MAGI_REQUIRED_IMAGE_DIGEST" <<'PY' || exit 2
import sys
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root))
from magi.oci import inspect_image_digest, reconcile_declared_and_observed
observed = inspect_image_digest(sys.argv[2])
reconcile_declared_and_observed(declared_digest=sys.argv[3], observed_digest=observed)
print(observed)
PY
    fi
    docker compose -f "$COMPOSE" up -d "${seat}-egress"
    cleanup_proxy() { docker compose -f "$COMPOSE" rm -sf "${seat}-egress" >/dev/null 2>&1 || true; }
    trap 'cleanup_proxy; cleanup' EXIT HUP INT TERM
    wait_for_proxy "${seat}-egress"
    docker compose -f "$COMPOSE" run --rm "$seat"
    local done="$artifact_root/$seat/SEAT_DONE"
    [[ -f "$done" ]] || { printf 'seat did not produce SEAT_DONE\n' >&2; exit 1; }
    local dossier="$artifact_root/$seat/dossier.json"
    [[ -f "$dossier" ]] || { printf 'seat did not produce dossier.json\n' >&2; exit 1; }
    if ((json)); then
      python3 - "$seat" "$dossier" <<'PY'
import json, sys
print(json.dumps({"seat_id": sys.argv[1], "dossier_path": sys.argv[2]}, separators=(",", ":")))
PY
    else
      printf 'dossier: %s\n' "$dossier"
    fi
  )
}

agent_mode() {
  local payload seat trial brief output policy profile seat_config secret task assigned_digest
  local evidence_manifest assignment_plan assigned_evidence_digest assigned_plan_digest
  payload=$(cat)
  task=$(jq -er '.task' <<<"$payload")
  [[ "$task" = magi_build_seat ]] || { printf 'invalid builder task\n' >&2; exit 2; }
  seat=$(jq -er '.seat_id' <<<"$payload")
  trial=$(jq -er '.trial_dir' <<<"$payload")
  brief=$(jq -er '.original_brief_path' <<<"$payload")
  output=$(jq -er '.seat_output_dir' <<<"$payload")
  assigned_digest=$(jq -er '.original_brief_sha256' <<<"$payload")
  evidence_manifest=$(jq -er '.evidence_manifest_path' <<<"$payload")
  assignment_plan=$(jq -er '.assignment_plan_path' <<<"$payload")
  assigned_evidence_digest=$(jq -er '.evidence_manifest_sha256' <<<"$payload")
  assigned_plan_digest=$(jq -er '.assignment_plan_sha256' <<<"$payload")
  [[ "$seat" =~ ^seat-[mdg]$ ]] || { printf 'invalid seat assignment\n' >&2; exit 2; }
  case "$seat" in
    seat-m) profile=${MAGI_SEAT_M_PROFILE:-}; seat_config=${MAGI_SEAT_M_CONFIG:-$ROOT/container/seats/seat-m.json}; policy=${MAGI_SEAT_M_POLICY:-$ROOT/container/policies/seat-m.json}; secret=${MAGI_SEAT_M_SECRET_FILE:?};;
    seat-d) profile=${MAGI_SEAT_D_PROFILE:-}; seat_config=${MAGI_SEAT_D_CONFIG:-$ROOT/container/seats/seat-d.json}; policy=${MAGI_SEAT_D_POLICY:-$ROOT/container/policies/seat-d.json}; secret=${MAGI_SEAT_D_SECRET_FILE:?};;
    seat-g) profile=${MAGI_SEAT_G_PROFILE:-}; seat_config=${MAGI_SEAT_G_CONFIG:-$ROOT/container/seats/seat-g.json}; policy=${MAGI_SEAT_G_POLICY:-$ROOT/container/policies/seat-g.json}; secret=${MAGI_SEAT_G_SECRET_FILE:?};;
  esac
  [[ "$(absolute "$output")" = "$(absolute "$trial")/seat-work/$seat" ]] || { printf 'assigned output path mismatch\n' >&2; exit 2; }
  [[ "$(sha256_file "$brief")" = "$assigned_digest" ]] || { printf 'assigned original brief digest mismatch\n' >&2; exit 2; }
  [[ -f "$evidence_manifest" && "$(sha256_file "$evidence_manifest")" = "$assigned_evidence_digest" ]] || { printf 'assigned evidence manifest digest mismatch\n' >&2; exit 2; }
  [[ -f "$assignment_plan" && "$(sha256_file "$assignment_plan")" = "$assigned_plan_digest" ]] || { printf 'assigned assignment plan digest mismatch\n' >&2; exit 2; }
  mkdir -p "$(dirname "$output")"
  local profile_args=()
  if [[ -n "$profile" ]]; then profile_args=(--profile-source "$profile"); fi
  MAGI_SEAT_ARTIFACT_ROOT="$trial/seat-work" run_seat --seat "$seat" --trial "$trial" --brief "$brief" \
    --evidence-manifest "$evidence_manifest" --assignment-plan "$assignment_plan" "${profile_args[@]}" \
    --seat-config "$seat_config" --policy "$policy" --secret-file "$secret" --json
}

reviewer_agent_mode() {
  local payload task profile seat_config secret packet_dir output_dir reviewer_seat=
  [[ ${1:-} = --seat && -n ${2:-} && $# -eq 2 ]] || usage
  reviewer_seat=$2
  payload=$(cat)
  task=$(jq -er '.task' <<<"$payload")
  [[ "$task" = magi_cross_review ]] || { printf 'invalid reviewer task\n' >&2; exit 2; }
  case "$reviewer_seat" in
    seat-m) profile=${MAGI_SEAT_M_PROFILE:?}; seat_config=${MAGI_SEAT_M_CONFIG:-$ROOT/container/seats/seat-m.json}; secret=${MAGI_SEAT_M_SECRET_FILE:?};;
    seat-d) profile=${MAGI_SEAT_D_PROFILE:?}; seat_config=${MAGI_SEAT_D_CONFIG:-$ROOT/container/seats/seat-d.json}; secret=${MAGI_SEAT_D_SECRET_FILE:?};;
    seat-g) profile=${MAGI_SEAT_G_PROFILE:?}; seat_config=${MAGI_SEAT_G_CONFIG:-$ROOT/container/seats/seat-g.json}; secret=${MAGI_SEAT_G_SECRET_FILE:?};;
    *) printf 'invalid reviewer seat assignment\n' >&2; exit 2;;
  esac
  profile=$(absolute "$profile")
  seat_config=$(absolute "$seat_config"); secret=$(absolute "$secret")
  "$(profile_python)" "$ROOT/scripts/host/lib/compose_profile.py" validate "$profile" \
    --seat "$reviewer_seat" >/dev/null || exit 2
  [[ -f "$seat_config" && -f "$secret" ]] || { printf 'reviewer seat config/secret missing\n' >&2; exit 2; }
  secret_is_private "$secret" || { printf 'reviewer secret file mode must be 0400 or 0600\n' >&2; exit 2; }
  packet_dir=$(mktemp -d "${TMPDIR:-/tmp}/magi-review-packet.XXXXXX")
  output_dir=$(mktemp -d "${TMPDIR:-/tmp}/magi-review-output.XXXXXX")
  cleanup_review() { rm -rf -- "$packet_dir" "$output_dir"; docker compose -f "$COMPOSE" rm -sf "$reviewer_seat-egress" >/dev/null 2>&1 || true; }
  trap cleanup_review EXIT HUP INT TERM
  printf '%s\n' "$payload" > "$packet_dir/packet.json"; chmod 0400 "$packet_dir/packet.json"; chmod 0700 "$output_dir"
  export MAGI_CONTAINER_UID=${MAGI_CONTAINER_UID:-$(id -u)} MAGI_CONTAINER_GID=${MAGI_CONTAINER_GID:-$(id -g)}
  export MAGI_SEAT_MODE=review MAGI_ORIGINAL_BRIEF="$packet_dir/packet.json" MAGI_ARTIFACT_ROOT="$output_dir"
  export MAGI_SEAT_M_PROFILE="$profile" MAGI_SEAT_D_PROFILE="$profile" MAGI_SEAT_G_PROFILE="$profile"
  export MAGI_SEAT_M_CONFIG="$seat_config" MAGI_SEAT_D_CONFIG="$seat_config" MAGI_SEAT_G_CONFIG="$seat_config"
  export MAGI_SEAT_M_POLICY="$ROOT/container/policies/seat-m.json" MAGI_SEAT_D_POLICY="$ROOT/container/policies/seat-d.json" MAGI_SEAT_G_POLICY="$ROOT/container/policies/seat-g.json"
  export MAGI_SEAT_M_SECRET_FILE="$secret" MAGI_SEAT_D_SECRET_FILE="$secret" MAGI_SEAT_G_SECRET_FILE="$secret"
  export MAGI_REVIEW_PACKET_M="$packet_dir/packet.json" MAGI_REVIEW_PACKET_D="$packet_dir/packet.json" MAGI_REVIEW_PACKET_G="$packet_dir/packet.json"
  export MAGI_REVIEW_OUTPUT_M="$output_dir" MAGI_REVIEW_OUTPUT_D="$output_dir" MAGI_REVIEW_OUTPUT_G="$output_dir"
  docker compose -f "$COMPOSE" up -d "$reviewer_seat-egress"
  wait_for_proxy "$reviewer_seat-egress"
  docker compose -f "$COMPOSE" run --rm "$reviewer_seat"
  [[ -f "$output_dir/review.json" ]] || { printf 'profiled reviewer produced no result\n' >&2; exit 1; }
  cat "$output_dir/review.json"
}

# Compose still interpolates every service when loading the project file.
# Final-only launches must still satisfy sibling seat variable requirements.
export_finale_compose_placeholders() {
  local config=$1 secret=$2 packet=$3 output=$4
  export MAGI_CONTAINER_UID=${MAGI_CONTAINER_UID:-$(id -u)}
  export MAGI_CONTAINER_GID=${MAGI_CONTAINER_GID:-$(id -g)}
  export MAGI_CODE_ROOT="$ROOT"
  export MAGI_FINAL_CONFIG="$config"
  export MAGI_FINAL_SECRET_FILE="$secret"
  export MAGI_FINAL_PACKET="$packet"
  export MAGI_FINAL_OUTPUT="$output"
  # Sibling seat services are not started, but their ${VAR:?} expansions still run.
  export MAGI_ORIGINAL_BRIEF="$packet"
  export MAGI_EVIDENCE_ROOT="$output"
  export MAGI_ASSIGNMENT_PLAN="$packet"
  export MAGI_ARTIFACT_ROOT="$output"
  export MAGI_SEAT_M_PROFILE="$output"
  export MAGI_SEAT_D_PROFILE="$output"
  export MAGI_SEAT_G_PROFILE="$output"
  export MAGI_SEAT_M_CONFIG="$config"
  export MAGI_SEAT_D_CONFIG="$config"
  export MAGI_SEAT_G_CONFIG="$config"
  export MAGI_SEAT_M_POLICY="${MAGI_SEAT_M_POLICY:-$ROOT/container/policies/seat-m.json}"
  export MAGI_SEAT_D_POLICY="${MAGI_SEAT_D_POLICY:-$ROOT/container/policies/seat-d.json}"
  export MAGI_SEAT_G_POLICY="${MAGI_SEAT_G_POLICY:-$ROOT/container/policies/seat-g.json}"
  export MAGI_SEAT_M_SECRET_FILE="${MAGI_SEAT_M_SECRET_FILE:-$secret}"
  export MAGI_SEAT_D_SECRET_FILE="${MAGI_SEAT_D_SECRET_FILE:-$secret}"
  export MAGI_SEAT_G_SECRET_FILE="${MAGI_SEAT_G_SECRET_FILE:-$secret}"
  export MAGI_REVIEW_PACKET_M="$packet"
  export MAGI_REVIEW_PACKET_D="$packet"
  export MAGI_REVIEW_PACKET_G="$packet"
  export MAGI_REVIEW_OUTPUT_M="$output"
  export MAGI_REVIEW_OUTPUT_D="$output"
  export MAGI_REVIEW_OUTPUT_G="$output"
}

final_agent_mode() {
  local payload task output config secret packet_dir observed
  payload=$(cat)
  task=$(jq -er '.task' <<<"$payload")
  [[ "$task" = magi_final_adjudication ]] || { printf 'invalid final adjudicator task\n' >&2; exit 2; }
  config=$(absolute "${MAGI_FINAL_CONFIG:-$ROOT/container/seats/seat-g.json}")
  secret=$(absolute "${MAGI_FINAL_SECRET_FILE:?set MAGI_FINAL_SECRET_FILE}")
  [[ -f "$config" && -f "$secret" ]] || { printf 'final adjudicator config/secret missing\n' >&2; exit 2; }
  secret_is_private "$secret" || { printf 'final adjudicator secret file mode must be 0400 or 0600\n' >&2; exit 2; }
  local key_env base_env
  key_env=$(jq -er '.provider_key_env' "$config")
  base_env=$(jq -er '.provider_base_url_env' "$config")
  [[ "$key_env" = OPENAI_API_KEY && "$base_env" = OPENAI_BASE_URL ]] || {
    printf 'final adjudicator must use the scoped OpenAI binding\n' >&2; exit 2;
  }
  # Production Finale always reconciles the frozen image pin before compose run.
  [[ -n "${MAGI_REQUIRED_IMAGE_DIGEST:-}" ]] || {
    printf 'MAGI_REQUIRED_IMAGE_DIGEST must be set to the frozen execution.image_digest pin\n' >&2
    exit 2
  }
  observed=$(python3 - "$ROOT" "${MAGI_SEAT_IMAGE:-magi-seat:local}" "$MAGI_REQUIRED_IMAGE_DIGEST" <<'PY' || exit 2
import sys
from pathlib import Path
root = Path(sys.argv[1])
sys.path.insert(0, str(root))
from magi.oci import inspect_image_digest, reconcile_declared_and_observed
observed = inspect_image_digest(sys.argv[2])
reconcile_declared_and_observed(declared_digest=sys.argv[3], observed_digest=observed)
print(observed)
PY
)
  packet_dir=$(mktemp -d "${TMPDIR:-/tmp}/magi-final-packet.XXXXXX")
  output=$(mktemp -d "${TMPDIR:-/tmp}/magi-final-output.XXXXXX")
  cleanup_final() {
    rm -rf -- "$packet_dir" "$output"
    docker compose -f "$COMPOSE" rm -sf final-adjudicator-egress >/dev/null 2>&1 || true
  }
  trap cleanup_final EXIT HUP INT TERM
  printf '%s\n' "$payload" > "$packet_dir/packet.json"
  chmod 0400 "$packet_dir/packet.json"
  chmod 0700 "$output"
  export_finale_compose_placeholders "$config" "$secret" "$packet_dir/packet.json" "$output"
  # Fail closed if compose cannot interpolate the final-only launch environment.
  docker compose -f "$COMPOSE" config --quiet >/dev/null
  docker compose -f "$COMPOSE" up -d final-adjudicator-egress
  wait_for_proxy final-adjudicator-egress
  docker compose -f "$COMPOSE" run --rm final-adjudicator
  [[ -f "$output/verdict.json" ]] || { printf 'final adjudicator produced no verdict\n' >&2; exit 1; }
  printf '%s\n' "$observed" > "$output/observed-image-digest.txt"
  cat "$output/verdict.json"
}

case "${1:-}" in
  run) shift; run_seat "$@";;
  agent) shift; (($#==0)) || usage; agent_mode;;
  reviewer-agent) shift; reviewer_agent_mode "$@";;
  final-agent) shift; (($#==0)) || usage; final_agent_mode;;
  *) usage;;
esac
