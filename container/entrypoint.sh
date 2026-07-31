#!/usr/bin/env bash
set -euo pipefail
umask 077

readonly ART=/artifacts
readonly INPUT=/input/original-brief.json
readonly EVIDENCE=/evidence
readonly EVIDENCE_MANIFEST=/evidence/evidence-manifest.json
readonly ASSIGNMENT_PLAN=/input/assignment-plan.json
readonly PROFILE_SOURCE=/profile-source
readonly SEAT_CONFIG=/config/seat.json
readonly POLICY=/config/policy.json
readonly HELPER=/usr/local/lib/magi/seat_artifacts.py
readonly PROFILE_ROOT=/runtime/hermes-home
readonly PROFILE_ID=magi-seat
readonly PROFILE_HOME="$PROFILE_ROOT/profiles/$PROFILE_ID"
readonly QUINTE_HOME=/runtime/quinte-home
readonly TMP_ROOT=/runtime/tmp
readonly MODE=${MAGI_SEAT_MODE:-build}
RUN_ID=

fail() { printf 'magi-seat: %s\n' "$*" >&2; exit 2; }
log() { printf '[%s] %s\n' "${SEAT_ID:-seat}" "$*" >&2; }
cancel_run() {
  [[ -n "$RUN_ID" ]] || return 0
  quinte --home "$QUINTE_HOME" cancel "$RUN_ID" --json >/dev/null 2>&1 || true
}
cancel_and_fail() {
  cancel_run
  fail "$*"
}
on_signal() {
  log "signal received; cancelling QUINTE run"
  cancel_run
  exit 130
}
trap on_signal HUP INT TERM

[[ -f "$SEAT_CONFIG" ]] || fail "seat config mount is incomplete"

# Final adjudication runs magi-agent (Codex) inside this isolated container.
# It never mounts original evidence and never reuses seat thesis/QUINTE mounts.
if [[ "$MODE" = final ]]; then
  [[ -f /final-input/packet.json ]] || fail "final adjudication packet mount is incomplete"
  [[ -f /opt/magi/bin/magi-agent && -d /opt/magi/lib/magi && -d /opt/magi/schemas ]] || fail "final adjudicator magi-agent mounts are incomplete"
  for mount in /config/seat.json /final-input/packet.json /opt/magi/bin/magi-agent /opt/magi/lib/magi /opt/magi/schemas; do
    mount_options=$(awk -v target="$mount" '$5 == target { print $6 }' /proc/self/mountinfo | tail -1)
    [[ ",$mount_options," == *,ro,* ]] || fail "required immutable input is not a read-only mount: $mount"
  done
  artifact_mount_options=$(awk -v target="/final-output" '$5 == target { print $6 }' /proc/self/mountinfo | tail -1)
  [[ -n "$artifact_mount_options" && ",$artifact_mount_options," != *,ro,* ]] || fail "final-output root must be a writable dedicated mount"
  KEY_ENV=$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["provider_key_env"])')
  BASE_ENV=$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["provider_base_url_env"])')
  BASE_URL=$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["provider_base_url"])')
  PROVIDER=$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["provider"])')
  TEXT_MODEL=$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["text_model"])')
  [[ "$KEY_ENV" = OPENAI_API_KEY && "$BASE_ENV" = OPENAI_BASE_URL ]] || fail "final adjudicator must use the scoped OpenAI binding"
  [[ -s /run/secrets/provider_api_key ]] || fail "provider_api_key secret is missing/empty"
  printf -v "$KEY_ENV" '%s' "$(cat /run/secrets/provider_api_key)"; export "$KEY_ENV"
  printf -v "$BASE_ENV" '%s' "$BASE_URL"; export "$BASE_ENV"
  export PYTHONPATH=/opt/magi/lib
  mkdir -p /final-output /runtime/tmp
  cat /final-input/packet.json | timeout "${HERMES_TIMEOUT_SECONDS:-3600}" python3 /opt/magi/bin/magi-agent \
    --backend codex --model "$TEXT_MODEL" --provider "$PROVIDER" \
    --base-url "$BASE_URL" --env-key "$KEY_ENV" \
    --schema-root /opt/magi/schemas --cwd /final-output \
    > /final-output/verdict.json
  [[ -s /final-output/verdict.json ]] || fail "final adjudicator produced no verdict"
  # Surface the closed verdict JSON on stdout for host harness capture when needed.
  cat /final-output/verdict.json
  exit 0
fi

[[ -f "$PROFILE_SOURCE/profile.json" && -f "$PROFILE_SOURCE/SOUL.md" && -f "$PROFILE_SOURCE/config.yaml" ]] || fail "invalid independent review profile mount"
[[ -f "$PROFILE_SOURCE/AGENTS.md" ]] || fail "independent review profile is missing shared rules"
[[ -f "$PROFILE_SOURCE/COMPOSITION.json" ]] || fail "production profile is not host-composed from private technical rules"
if [[ "$MODE" = build ]]; then
  [[ -f "$INPUT" && -f "$POLICY" && -f "$EVIDENCE_MANIFEST" && -f "$ASSIGNMENT_PLAN" ]] || fail "build input/policy/evidence/assignment mount is incomplete"
elif [[ "$MODE" = review ]]; then
  [[ -f /review-input/packet.json ]] || fail "review packet mount is incomplete"
else
  fail "unknown seat execution mode: $MODE"
fi

required_mounts=("$PROFILE_SOURCE" "$SEAT_CONFIG")
if [[ "$MODE" = build ]]; then required_mounts+=("$INPUT" "$POLICY" "$EVIDENCE" "$ASSIGNMENT_PLAN"); else required_mounts+=(/review-input/packet.json); fi
for mount in "${required_mounts[@]}"; do
mount_options=$(awk -v target="$mount" '$5 == target { print $6 }' /proc/self/mountinfo | tail -1)
  [[ ",$mount_options," == *,ro,* ]] || fail "required immutable input is not a read-only mount: $mount"
done
output_mount=/artifacts
[[ "$MODE" = review ]] && output_mount=/review-output
artifact_mount_options=$(awk -v target="$output_mount" '$5 == target { print $6 }' /proc/self/mountinfo | tail -1)
[[ -n "$artifact_mount_options" && ",$artifact_mount_options," != *,ro,* ]] || fail "output root must be a writable dedicated mount"

python3 - "$PROFILE_SOURCE" <<'PY' || fail "unsafe independent review profile tree"
import hashlib, json, os, pathlib, sys

root = pathlib.Path(sys.argv[1])
for path in root.rglob("*"):
    relative = path.relative_to(root)
    if path.is_symlink():
        raise SystemExit(f"profile symlink is forbidden: {relative}")
    if path.is_file() and (path.name == ".env" or path.name.endswith(".env")):
        raise SystemExit(f"secret-bearing profile file is forbidden: {relative}")
receipt=json.load(open(root / "COMPOSITION.json"))
required={"base_sha256","composition_version","overlay_sha256","profile_id","seat_id","composed_content_sha256"}
if set(receipt) != required or receipt["composition_version"] != "1.0":
    raise SystemExit("profile composition receipt is malformed")
h=hashlib.sha256()
for path in sorted(p for p in root.rglob("*") if p.is_file() and p.name != "COMPOSITION.json"):
    rel=path.relative_to(root).as_posix().encode(); data=path.read_bytes()
    h.update(len(rel).to_bytes(8,"big")); h.update(rel)
    h.update(len(data).to_bytes(8,"big")); h.update(data)
if receipt["composed_content_sha256"] != "sha256:" + h.hexdigest():
    raise SystemExit("profile composition content digest mismatch")
PY

SERVICE_SEAT_ID=${SEAT_ID:?SEAT_ID environment is required}
SEAT_ID=$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["seat_id"])')
[[ "$SEAT_ID" = "$SERVICE_SEAT_ID" ]] || fail "seat config does not match service assignment"
[[ "$SEAT_ID" = "$(python3 -c 'import json;print(json.load(open("/profile-source/COMPOSITION.json"))["seat_id"])')" ]] || fail "profile composition receipt does not match service assignment"
python3 "$HELPER" validate seat "$SEAT_CONFIG" >/dev/null || fail "seat configuration validation failed"
if [[ "$MODE" = build ]]; then
  python3 "$HELPER" validate policy "$POLICY" --seat "$SEAT_CONFIG" >/dev/null || fail "seat policy validation failed"
  python3 "$HELPER" validate brief "$INPUT" >/dev/null || fail "original brief validation failed"
  python3 - "$ASSIGNMENT_PLAN" "$SEAT_CONFIG" <<'PY' || fail "assignment plan does not bind the mounted seat"
import json, sys

plan = json.load(open(sys.argv[1]))
seat = json.load(open(sys.argv[2]))
matches = [item for item in plan.get("seats", []) if item.get("seat_id") == seat.get("seat_id")]
if len(matches) != 1:
    raise SystemExit("assignment plan must bind the service seat exactly once")
assigned = matches[0]
mapping = {
    "family": "model_family",
    "provider": "provider",
    "text_model": "text_model",
    "multimodal_model": "multimodal_model",
    "profile_id": "profile_id",
}
for plan_key, seat_key in mapping.items():
    if assigned.get(plan_key) != seat.get(seat_key):
        raise SystemExit(f"assignment {plan_key} does not match seat config")
PY
fi
PROFILE_SPEC_SHA256=$(python3 "$HELPER" validate profile "$PROFILE_SOURCE/profile.json" --expected-id "$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["profile_id"])')")

# Every invocation starts from immutable sources. Never reuse a stale policy, marker, or profile tree.
rm -rf "$PROFILE_ROOT" "$QUINTE_HOME" "$TMP_ROOT"
mkdir -p "$PROFILE_HOME" "$QUINTE_HOME/runs" "$TMP_ROOT"
cp -a "$PROFILE_SOURCE/." "$PROFILE_HOME/"
if [[ "$MODE" = review ]]; then
  packet_binding=$(python3 -c 'import json; print(json.dumps(json.load(open("/review-input/packet.json"))["reviewer_profile_binding"],sort_keys=True,separators=(",",":")))')
  actual_binding=$(python3 - "$PROFILE_SOURCE" <<'PY'
import hashlib,json,pathlib,sys
root=pathlib.Path(sys.argv[1]); profile=json.load(open(root/"profile.json")); receipt=json.load(open(root/"COMPOSITION.json"))
h=hashlib.sha256()
for path in sorted(p for p in root.rglob("*") if p.is_file()):
 rel=path.relative_to(root).as_posix().encode(); data=path.read_bytes()
 h.update(len(rel).to_bytes(8,"big")); h.update(rel); h.update(len(data).to_bytes(8,"big")); h.update(data)
packet=json.load(open("/review-input/packet.json"))
print(json.dumps({"profile_id":profile["profile_id"],"profile_sha256":packet["reviewer_profile_binding"]["profile_sha256"],"profile_source_sha256":"sha256:"+h.hexdigest(),"thesis_sha256":packet["reviewer_profile_binding"]["thesis_sha256"]},sort_keys=True,separators=(",",":")))
PY
  )
  [[ "$packet_binding" = "$actual_binding" ]] || fail "review packet is not bound to mounted frozen profile"
  PROMPT=$(python3 - <<'PY'
import json
packet=json.load(open('/review-input/packet.json'))
print("Continue in the same independent review seat whose complete immutable Hermes profile is active. "
      "Review only the anonymous subject dossier. Apply the declared methodology and explain its concrete use in methodology_trace. "
      "Copy reviewer_profile_binding exactly. Return exactly one Cross Review 1.1 JSON object, no markdown.\n\n"+
      json.dumps(packet,ensure_ascii=False,sort_keys=True))
PY
  )
  cd "$PROFILE_HOME"
  timeout "${HERMES_TIMEOUT_SECONDS:-3600}" hermes --profile "$PROFILE_ID" \
    --provider "$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["provider"])')" \
    --model "$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["text_model"])')" \
    -z "$PROMPT" > /review-output/review.json
  exit 0
fi

mkdir -p "$ART"
cp "$POLICY" "$QUINTE_HOME/policy.json"
rm -f "$ART/SEAT_DONE" "$ART/dossier.json" "$ART/thesis.raw"

quinte --home "$QUINTE_HOME" policy validate --json >/dev/null || fail "QUINTE rejected the immutable seat policy"

PROFILE_SOURCE_SHA256=$(python3 - "$PROFILE_HOME" <<'PY'
import hashlib, pathlib, sys
root = pathlib.Path(sys.argv[1])
h = hashlib.sha256()
for path in sorted(p for p in root.rglob("*") if p.is_file()):
    rel = path.relative_to(root).as_posix().encode()
    h.update(len(rel).to_bytes(8, "big")); h.update(rel)
    data = path.read_bytes(); h.update(len(data).to_bytes(8, "big")); h.update(data)
print("sha256:" + h.hexdigest())
PY
)

# Docker secrets never become container-level environment metadata.
KEY_ENV=$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["provider_key_env"])')
BASE_ENV=$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["provider_base_url_env"])')
BASE_URL=$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["provider_base_url"])')
PROVIDER=$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["provider"])')
TEXT_MODEL=$(python3 -c 'import json;print(json.load(open("/config/seat.json"))["text_model"])')
case "$KEY_ENV" in XIAOMI_API_KEY|DEEPSEEK_API_KEY|OPENAI_API_KEY) ;; *) fail "provider key env is not allowed";; esac
case "$BASE_ENV" in XIAOMI_BASE_URL|DEEPSEEK_BASE_URL|OPENAI_BASE_URL) ;; *) fail "provider base URL env is not allowed";; esac
[[ -s /run/secrets/provider_api_key ]] || fail "provider_api_key secret is missing/empty"
printf -v "$KEY_ENV" '%s' "$(cat /run/secrets/provider_api_key)"; export "$KEY_ENV"
printf -v "$BASE_ENV" '%s' "$BASE_URL"; export "$BASE_ENV"
case "$SEAT_ID" in
  seat-d) QUINTE_PROVIDER_KEY_ENV=DEEPSEEK_API_KEY ;;
  seat-g) QUINTE_PROVIDER_KEY_ENV=OPENAI_API_KEY ;;
  seat-m) QUINTE_PROVIDER_KEY_ENV=XIAOMI_API_KEY ;;
esac
QUINTE_PROVIDER_BASE_URL_ENV=$BASE_ENV
export QUINTE_PROVIDER_KEY_ENV QUINTE_PROVIDER_BASE_URL_ENV

cp "$PROFILE_SOURCE/profile.json" "$ART/profile.json"
chmod 0600 "$ART/profile.json"
rm -rf "$ART/reviewer-profile"
cp -a "$PROFILE_SOURCE" "$ART/reviewer-profile"
chmod -R a-w "$ART/reviewer-profile"

QUESTION=$(python3 -c 'import json;print(json.load(open("/input/original-brief.json"))["question"])')
PROMPT=$(python3 - "$PROFILE_SOURCE/profile.json" "$INPUT" "$ASSIGNMENT_PLAN" "$SEAT_CONFIG" <<'PY'
import json, sys
profile=json.load(open(sys.argv[1])); brief=json.load(open(sys.argv[2]))
assignment=json.load(open(sys.argv[3])); seat=json.load(open(sys.argv[4]))
matches=[item for item in assignment.get("seats", []) if item.get("seat_id")==seat.get("seat_id")]
if len(matches)!=1:
    raise SystemExit("assignment plan must bind this seat exactly once for thesis focus")
assigned=matches[0]
focus=assigned.get("primary_focus") or []
evidence_refs=assigned.get("evidence_refs") or []
limitations=assigned.get("limitations") or []
family=assigned.get("family") or seat.get("model_family")
# Honest multimodal boundary: only MiMo may claim original media inspection in thesis.
# Other families treat thesis as pre-evidence hypothesis over focus + frozen brief text.
if family == "mimo" and evidence_refs:
    evidence_clause=(
        "Assigned original evidence catalogue (canonical MAGI refs): "
        + json.dumps(evidence_refs, ensure_ascii=False)
        + ". Prefer native multimodal inspection of mounted assigned images when present; "
        "do not invent inspection of unassigned paths."
    )
else:
    evidence_clause=(
        "This seat's thesis phase is a pre-evidence / artifact-focus hypothesis: "
        "original media is not assigned for native inspection in this phase "
        f"(assigned_evidence_refs={json.dumps(evidence_refs, ensure_ascii=False)}). "
        "Do not claim image or frame inspection from paths in prose."
    )
contract={
 "thesis_version":"1.0", "question":brief["question"], "thesis":"non-empty string",
 "claims":[{"id":"C1","statement":"non-empty string","evidence_refs":[],"uncertainty":"non-empty string","boundary":"non-empty string"}],
 "recommendation":"non-empty string", "limitations":[]}
print(
 "You are the independent review seat described by this closed technical profile:\n"
 + json.dumps(profile,ensure_ascii=False,sort_keys=True)
 + "\n\nFrozen primary focus for this seat (do not drop these emphases):\n"
 + json.dumps(focus, ensure_ascii=False)
 + "\n\nEvidence boundary:\n" + evidence_clause
 + "\n\nSeat limitations:\n" + json.dumps(limitations, ensure_ascii=False)
 + "\n\nAnalyze this original brief without consulting another seat:\n"
 + json.dumps(brief,ensure_ascii=False,sort_keys=True)
 + "\n\nReturn exactly one JSON object, no markdown, matching this shape and no extra fields:\n"
 + json.dumps(contract,ensure_ascii=False,sort_keys=True)
)
PY
)

python3 - "$SEAT_CONFIG" "$ART/seat-manifest.json" "$PROFILE_SOURCE_SHA256" "$PROFILE_SPEC_SHA256" <<'PY'
import json, os, sys, tempfile
seat=json.load(open(sys.argv[1])); destination=sys.argv[2]
value={
 "seat_manifest_version":"1.0", "seat_id":seat["seat_id"],
 "profile_diversity":{"profile_id":seat["profile_id"],"profile_source_sha256":sys.argv[3],"profile_spec_sha256":sys.argv[4]},
 "model_family":{"family":seat["model_family"],"provider":seat["provider"],"text_model":seat["text_model"],"multimodal_model":seat["multimodal_model"]}}
data=(json.dumps(value,ensure_ascii=False,indent=2,sort_keys=True)+"\n").encode()
fd,tmp=tempfile.mkstemp(prefix=".seat-manifest.",dir=os.path.dirname(destination))
with os.fdopen(fd,"wb") as out: out.write(data); out.flush(); os.fsync(out.fileno())
os.chmod(tmp,0o600); os.replace(tmp,destination)
PY
log "phase 0: independent seat thesis (profile_source=$PROFILE_SOURCE_SHA256 profile_spec=$PROFILE_SPEC_SHA256)"
# Hermes discovers AGENTS.md from cwd, while SOUL/skills/memories/config are
# profile-root scoped. Running inside the composed profile activates both.
cd "$PROFILE_HOME"
timeout "${HERMES_TIMEOUT_SECONDS:-3600}" hermes --profile "$PROFILE_ID" \
  --provider "$PROVIDER" \
  --model "$TEXT_MODEL" \
  -z "$PROMPT" > "$ART/thesis.raw"

python3 "$HELPER" canonicalize thesis "$ART/thesis.raw" "$ART/thesis.json" --question "$QUESTION" >/dev/null
rm -f "$ART/thesis.raw"
python3 "$HELPER" derive --seat "$SEAT_CONFIG" --profile "$ART/profile.json" --thesis "$ART/thesis.json" \
  --original-brief "$INPUT" --evidence-manifest "$EVIDENCE_MANIFEST" \
  --assignment-plan "$ASSIGNMENT_PLAN" \
  --perspective-output "$ART/perspective-input.json" --brief-output "$ART/quinte-brief.json"

log "phase 1: same-family QUINTE (detached worker + automatic Primary Arbiter)"
quinte --home "$QUINTE_HOME" run --brief "$ART/quinte-brief.json" --json \
  > "$ART/quinte-run.json" 2> "$ART/quinte-run.err" || fail "QUINTE could not start"

RUN_ID=$(python3 - "$ART/quinte-run.json" <<'PY'
import json, sys
for line in reversed(open(sys.argv[1]).read().splitlines()):
    try:
        value=json.loads(line)
        while isinstance(value, dict) and isinstance(value.get("data"), dict):
            value=value["data"]
        if isinstance(value, dict) and value.get("run_id"):
            print(value["run_id"]); break
    except json.JSONDecodeError: pass
PY
)
[[ -n "$RUN_ID" ]] || fail "QUINTE did not report a run_id"
RUN_DIR="$QUINTE_HOME/runs/$RUN_ID"

deadline=$(( $(date +%s) + ${QUINTE_TIMEOUT_SECONDS:-7200} ))
poll_seconds=${QUINTE_POLL_SECONDS:-30}
[[ "$poll_seconds" =~ ^[0-9]+$ && "$poll_seconds" -ge 30 && "$poll_seconds" -le 60 ]] || fail "QUINTE_POLL_SECONDS must be 30..60"
while :; do
  (( $(date +%s) <= deadline )) || cancel_and_fail "QUINTE run timed out and was cancelled: $RUN_ID"
  if ! quinte --home "$QUINTE_HOME" status "$RUN_ID" --json > "$ART/quinte-status.json"; then
    cancel_run
    fail "QUINTE status polling failed: $RUN_ID"
  fi
status=$(python3 - "$ART/quinte-status.json" <<'PY'
import json, sys
value=json.load(open(sys.argv[1]))
while isinstance(value, dict) and isinstance(value.get("data"), dict):
    value=value["data"]
print(value.get("status", "") if isinstance(value, dict) else "")
PY
)
  case "$status" in
    completed) break ;;
    queued|preflight|r1_running|r1_gate|r2_packet|r2_running|r2_gate|r3_cc|merging|cancelling) sleep "$poll_seconds" ;;
    waiting_primary_arbiter) cancel_and_fail "automatic Primary Arbiter invariant failed: $RUN_ID" ;;
    degraded|failed|failed_policy|cancelled) fail "QUINTE ended in rejected state '$status': $RUN_ID" ;;
    *) cancel_and_fail "QUINTE returned unknown state '$status': $RUN_ID" ;;
  esac
done

[[ -f "$RUN_DIR/manifest.json" && -f "$RUN_DIR/result.json" ]] || fail "QUINTE did not complete"
rm -rf "$ART/quinte-run"
cp -a "$RUN_DIR" "$ART/quinte-run"
python3 "$HELPER" dossier --seat "$SEAT_CONFIG" --profile "$ART/profile.json" \
  --reviewer-profile "$ART/reviewer-profile" \
  --thesis "$ART/thesis.json" --perspective "$ART/perspective-input.json" \
  --run-dir "$ART/quinte-run" --output "$ART/dossier.json" \
  --evidence-manifest "$EVIDENCE_MANIFEST" --assignment-plan "$ASSIGNMENT_PLAN"
printf '{"dossier_path":"%s","seat_id":"%s"}\n' "$ART/dossier.json" "$SEAT_ID" > "$ART/SEAT_DONE"
log "dossier frozen"
