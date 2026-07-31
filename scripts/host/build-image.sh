#!/usr/bin/env bash
set -euo pipefail
umask 077

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)
LOCK="$ROOT/container/source-lock.env"
IMAGE=${MAGI_SEAT_IMAGE:-magi-seat:local}
HERMES_REPO=${HERMES_REPO:-${MAGI_HERMES_REPO:-$HOME/Private/agent-design/hermes/agent}}
QUINTE_REPO=${QUINTE_REPO:-/Users/ericstone/Public/QUINTE}

[[ -f "$LOCK" ]] || { printf 'missing %s\n' "$LOCK" >&2; exit 2; }
# shellcheck disable=SC1090
source "$LOCK"
[[ "$HERMES_COMMIT" =~ ^[0-9a-f]{40}$ && "$QUINTE_COMMIT" =~ ^[0-9a-f]{40}$ ]] || {
  printf 'source-lock.env must contain full commit IDs\n' >&2; exit 2;
}

for repo in "$HERMES_REPO" "$QUINTE_REPO"; do
  git -C "$repo" rev-parse --is-inside-work-tree >/dev/null
done
git -C "$HERMES_REPO" cat-file -e "$HERMES_COMMIT^{commit}"
git -C "$QUINTE_REPO" cat-file -e "$QUINTE_COMMIT^{commit}"
git -C "$QUINTE_REPO" show "$QUINTE_COMMIT:schemas/run-manifest.schema.json" | grep -q '"const": "2.0"' || {
  printf 'locked QUINTE commit lacks run manifest 2.0; update only after reviewed v2 is committed\n' >&2
  exit 2
}
git -C "$QUINTE_REPO" show "$QUINTE_COMMIT:schemas/result.schema.json" | grep -q '"const": "2.1"' || {
  printf 'locked QUINTE commit lacks result 2.1; update only after reviewed v2 is committed\n' >&2
  exit 2
}
git -C "$QUINTE_REPO" show "$QUINTE_COMMIT:src/adapters.rs" | grep -q '"HTTP_PROXY"' || {
  printf 'locked QUINTE commit does not propagate the mandatory egress proxy to lanes\n' >&2
  exit 2
}
git -C "$QUINTE_REPO" show "$QUINTE_COMMIT:src/adapters.rs" | grep -q 'QUINTE_PROVIDER_KEY_ENV' || {
  printf 'locked QUINTE commit does not bind lanes to the single seat credential selector\n' >&2
  exit 2
}
git -C "$QUINTE_REPO" show "$QUINTE_COMMIT:src/policy.rs" | grep -q 'auto_primary_arbiter' || {
  printf 'locked QUINTE commit lacks automatic Primary Arbiter policy support\n' >&2
  exit 2
}
require_adapter_branch() {
  local adapter=$1
  git -C "$QUINTE_REPO" grep -q -E \
    "^[[:space:]]*\"${adapter}\"[[:space:]]*=>[[:space:]]*\\{" \
    "$QUINTE_COMMIT" -- src/adapters.rs || {
      printf 'locked QUINTE commit lacks the production %s adapter branch\n' "$adapter" >&2
      exit 2
    }
}
require_adapter_branch mimo
require_adapter_branch reasonix
require_adapter_branch codex

BUILD_ROOT=$(mktemp -d "${TMPDIR:-/tmp}/magi-seat-build.XXXXXX")
cleanup() { rm -rf "$BUILD_ROOT"; }
trap cleanup EXIT
mkdir -p "$BUILD_ROOT/sources/hermes" "$BUILD_ROOT/sources/quinte" "$BUILD_ROOT/container" "$BUILD_ROOT/scripts/host/lib"

git -C "$HERMES_REPO" archive "$HERMES_COMMIT" | tar -x -C "$BUILD_ROOT/sources/hermes"
git -C "$QUINTE_REPO" archive "$QUINTE_COMMIT" | tar -x -C "$BUILD_ROOT/sources/quinte"
printf '%s\n' "$HERMES_COMMIT" > "$BUILD_ROOT/sources/hermes/.source-commit"
printf '%s\n' "$QUINTE_COMMIT" > "$BUILD_ROOT/sources/quinte/.source-commit"

# Export the exact locked Hermes dependency set with hashes; install the local wheel separately.
uv export --project "$BUILD_ROOT/sources/hermes" --frozen --no-dev --no-emit-project \
  --format requirements.txt --output-file "$BUILD_ROOT/sources/hermes/container-requirements.txt"
cp "$ROOT/container/Dockerfile" "$ROOT/container/entrypoint.sh" "$BUILD_ROOT/container/"
cp "$ROOT/scripts/host/lib/seat_artifacts.py" "$BUILD_ROOT/scripts/host/lib/"

DOCKER_BUILDKIT=1 docker build --pull \
  --build-arg "HERMES_COMMIT=$HERMES_COMMIT" \
  --build-arg "QUINTE_COMMIT=$QUINTE_COMMIT" \
  --label "org.opencontainers.image.hermes.revision=$HERMES_COMMIT" \
  --label "org.opencontainers.image.quinte.revision=$QUINTE_COMMIT" \
  --tag "$IMAGE" "$BUILD_ROOT"

printf '{"hermes_commit":"%s","image":"%s","quinte_commit":"%s"}\n' \
  "$HERMES_COMMIT" "$IMAGE" "$QUINTE_COMMIT"
