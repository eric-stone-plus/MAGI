#!/usr/bin/env bash
set -euo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd -P)
COMPOSE="$ROOT/container/compose.yml"
ENV_FILE="$ROOT/container/compose.static.env"
PROJECT="magi-proxy-test-$$"
PROXY_IMAGE=ghcr.io/tarampampam/3proxy@sha256:39e8f1e745290e9afccb0bee39058d4908e5781da4d4d11b48848b39080bf24c

cleanup() {
  docker compose -p "$PROJECT" --env-file "$ENV_FILE" -f "$COMPOSE" down --remove-orphans >/dev/null 2>&1 || true
}
trap cleanup EXIT HUP INT TERM

docker compose -p "$PROJECT" --env-file "$ENV_FILE" -f "$COMPOSE" up -d \
  seat-m-egress seat-d-egress seat-g-egress >/dev/null

for seat in m d g; do
  service="seat-$seat-egress"
  deadline=$(( $(date +%s) + 45 ))
  while :; do
    health=$(docker compose -p "$PROJECT" --env-file "$ENV_FILE" -f "$COMPOSE" \
      ps --format json "$service" | python3 -c '
import json, sys
value=json.load(sys.stdin)
if isinstance(value, list): value=value[0] if value else {}
print(value.get("Health", ""))
')
    [[ "$health" = healthy ]] && break
    [[ "$health" != unhealthy && $(date +%s) -le $deadline ]] || {
      printf 'proxy topology test: %s did not become healthy\n' "$service" >&2
      exit 1
    }
    sleep 1
  done
done

for seat in m d g; do
  case "$seat" in m) other=d;; d) other=g;; g) other=m;; esac
  network="${PROJECT}_seat-${seat}-private"
  docker run --rm --network "$network" --entrypoint /bin/sh "$PROXY_IMAGE" -c \
    "nc -z seat-${seat}-egress 3128"
  if docker run --rm --network "$network" --entrypoint /bin/sh "$PROXY_IMAGE" -c \
    "nslookup seat-${other}-egress >/dev/null 2>&1"; then
    printf 'proxy topology test: cross-seat DNS leaked from seat-%s to seat-%s\n' "$seat" "$other" >&2
    exit 1
  fi
  status=$(docker run --rm --network "$network" --entrypoint /bin/sh "$PROXY_IMAGE" -c \
    "printf 'CONNECT example.com:443 HTTP/1.1\r\nHost: example.com:443\r\n\r\n' | nc seat-${seat}-egress 3128 | head -1")
  case "$status" in *" 403 "*) ;; *)
    printf 'proxy topology test: forbidden CONNECT was not rejected for seat-%s: %s\n' "$seat" "$status" >&2
    exit 1;;
  esac
done

printf 'PASS proxy topology: same-seat reachable, cross-seat hidden, forbidden CONNECT rejected\n'
