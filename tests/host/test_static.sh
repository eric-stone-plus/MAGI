#!/usr/bin/env bash
set -euo pipefail
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)
PROFILE_PYTHON=${MAGI_PROFILE_PYTHON:-$HOME/Private/agent-design/hermes/agent/.venv/bin/python}
if [[ ! -x "$PROFILE_PYTHON" ]] || ! "$PROFILE_PYTHON" -c 'import yaml' >/dev/null 2>&1; then
  printf 'MAGI_PROFILE_PYTHON must name a Python with PyYAML: %s\n' "$PROFILE_PYTHON" >&2
  exit 2
fi

bash -n "$ROOT/container/entrypoint.sh" "$ROOT/scripts/host/build-image.sh" \
  "$ROOT/scripts/host/diagnose.sh" "$ROOT/scripts/host/magi-seat.sh"
PYTHONDONTWRITEBYTECODE=1 "$PROFILE_PYTHON" -m unittest discover -s "$ROOT/tests/host" -p 'test_*.py'
if command -v pwsh >/dev/null 2>&1; then
  pwsh -NoLogo -NoProfile -Command "[void][ScriptBlock]::Create([IO.File]::ReadAllText('$ROOT/scripts/host/magi-seat.ps1'))"
else
  printf 'SKIP PowerShell parser check (pwsh unavailable)\n'
fi
docker compose --env-file "$ROOT/container/compose.static.env" -f "$ROOT/container/compose.yml" config --quiet
if docker info >/dev/null 2>&1; then
  "$ROOT/tests/host/test_proxy_topology.sh"
else
  printf 'SKIP proxy topology integration (Docker daemon unavailable)\n'
fi
