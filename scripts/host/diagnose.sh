#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)
errors=0
check() { if "$@" >/dev/null 2>&1; then printf 'PASS %s\n' "$*"; else printf 'FAIL %s\n' "$*"; errors=$((errors+1)); fi; }

check command -v docker
check docker compose version
check command -v git
check command -v python3
check command -v uv
PROFILE_PYTHON=${MAGI_PROFILE_PYTHON:-$HOME/Private/agent-design/hermes/agent/.venv/bin/python}
check "$PROFILE_PYTHON" -c 'import yaml'

LOCK="$ROOT/container/source-lock.env"
# shellcheck disable=SC1090
source "$LOCK"
QUINTE_REPO=${QUINTE_REPO:-$HOME/Public/QUINTE}
check git -C "$QUINTE_REPO" cat-file -e "$QUINTE_COMMIT^{commit}"
if git -C "$QUINTE_REPO" show "$QUINTE_COMMIT:schemas/run-manifest.schema.json" 2>/dev/null | grep -q '"const": "2.0"' \
  && git -C "$QUINTE_REPO" show "$QUINTE_COMMIT:schemas/result.schema.json" 2>/dev/null | grep -q '"const": "2.1"'; then
  printf 'PASS locked QUINTE exposes manifest 2.0/result 2.1\n'
else
  printf 'FAIL locked QUINTE lacks reviewed seat contracts (manifest 2.0/result 2.1)\n'
  errors=$((errors+1))
fi

if git -C "$QUINTE_REPO" show "$QUINTE_COMMIT:src/adapters.rs" 2>/dev/null | grep -q '"HTTP_PROXY"'; then
  printf 'PASS locked QUINTE propagates the mandatory seat proxy\n'
else
  printf 'FAIL locked QUINTE strips the mandatory seat proxy\n'
  errors=$((errors+1))
fi
if git -C "$QUINTE_REPO" show "$QUINTE_COMMIT:src/adapters.rs" 2>/dev/null | grep -q 'QUINTE_PROVIDER_KEY_ENV'; then
  printf 'PASS locked QUINTE uses the single seat credential selector\n'
else
  printf 'FAIL locked QUINTE still depends on per-harness host credential state\n'
  errors=$((errors+1))
fi

for profile in formalist adversarial empirical; do
  check python3 "$ROOT/scripts/host/lib/seat_artifacts.py" validate profile "$ROOT/profiles/$profile/profile.json" --expected-id "$profile"
  if find "$ROOT/profiles/$profile" -mindepth 1 -maxdepth 1 -type f ! -name SOUL.md ! -name profile.json | grep -q .; then
    printf 'FAIL %s contains private-profile stand-ins instead of overlay-only files\n' "$profile"
    errors=$((errors+1))
  else
    printf 'PASS %s is an overlay-only public profile\n' "$profile"
  fi
done
for seat in seat-m seat-d seat-g; do
  check python3 "$ROOT/scripts/host/lib/seat_artifacts.py" validate seat "$ROOT/container/seats/$seat.json"
  check python3 "$ROOT/scripts/host/lib/seat_artifacts.py" validate policy "$ROOT/container/policies/$seat.json" --seat "$ROOT/container/seats/$seat.json"
done

exit "$errors"
