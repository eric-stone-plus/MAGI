# Containerized Independent Seats

This is MAGI's headless host/container contract for macOS, Linux, and Windows.
`container/source-lock.env` pins the reviewed QUINTE v2 source that provides
manifest 2.0, result 2.1, automatic Primary Arbiter execution, selected provider
credentials, and proxy propagation. Build and diagnostics reject any lock that
loses those capabilities.

## Fixed Seat Bindings

Every one of a seat's five parties and two arbiters stays on the seat family. The checked-in policy and seat files are closed production contracts, not templates:

| Seat | Profile lens | Family/provider | Model | Adapter | Endpoint |
| --- | --- | --- | --- | --- | --- |
| `seat-m` | specification review | MiMo/Xiaomi | `mimo-v2.5-pro` | `mimo` | `https://api.xiaomimimo.com/v1` |
| `seat-d` | failure analysis | DeepSeek | `deepseek-v4-pro` | `reasonix` | `https://api.deepseek.com/v1` |
| `seat-g` | evidence validation | OpenAI/APINebula | `gpt-5.6-sol` | `codex` | `https://apinebula.com/v1` |

`auto_primary_arbiter` is mandatory. The entrypoint starts QUINTE detached, polls every 30–60 seconds, accepts only `completed`, and rejects `waiting_primary_arbiter`, `degraded`, failed/cancelled, and unknown states. It never calls `quinte wait`, uses `--wait`, or creates a manual PA handoff.

## Private Hermes Profile Composition

The public `profiles/{formalist,adversarial,empirical}` directories retain
compatibility profile IDs, but contain only a seat review overlay (`SOUL.md`)
and closed metadata (`profile.json`). They are not runnable Hermes profiles and
contain no private rules.

At launch, the host composes a complete immutable profile under:

```text
<trial>/trial-private/composed-profiles/<seat>/
```

Inputs are:

- Platform rules base: `$HOME/Private/agent-design/hermes/rules/{mac,linux,win}` by default.
- Workspace `AGENTS.md`: explicit `--technical-agents` / `-TechnicalAgents`, or `MAGI_TECHNICAL_AGENTS`.
- Live technical config: `${HERMES_HOME:-$HOME/.hermes/profiles/technical}/config.yaml`, unless explicitly overridden.
- The checked-in seat overlay.

The composer preserves immutable base `SOUL.md`, safe `memories/{MEMORY,POSTMORTEM,USER}.md`, skills, hooks, and other rule assets. It appends the seat lens, adds independent-seat rules to the supplied `AGENTS.md`, disables every production toolset, leaves only the `no_mcp` sentinel, forces zero-write settings, clears both fallback-provider chains and secret-valued config leaves, rewrites private hook paths to `/runtime/hermes-home/profiles/magi-seat`, and prefixes bare Python hook paths with `python3` so read-only/noexec profiles remain runnable. Known runtime-only databases, caches, sessions, logs, and allowlist artifacts are excluded from the composed copy. Secret-bearing `.env`/auth files, symlinks in the otherwise eligible source tree, and unknown memory files are rejected instead of silently excluded.

`COMPOSITION.json` binds the base, overlay, seat, and composed-content digests. An unchanged destination is reusable on retry; tampered or source-divergent content fails closed. The container verifies the receipt from a read-only mount, copies it into ephemeral `/runtime`, and runs Hermes with that profile as both `HERMES_HOME` and cwd so its SOUL, AGENTS, memories, skills, hooks, and config resolve from one tree.

Private rules and composed profiles never enter the public repository or image.

## Isolation And Egress

The seat image runs as the invoking Unix UID/GID (Windows Docker Desktop defaults to Linux-container IDs `1000:1000`), on a read-only root filesystem with all capabilities dropped and `no-new-privileges`. `/runtime` and `/tmp` are private tmpfs mounts. The image contains only the pinned MiMo, Reasonix, and Codex CLIs; no host CLI profile or desktop session is mounted.

Each seat attaches only to its own `internal: true` network. Its dedicated 3proxy sidecar bridges that network to a separate outbound network and permits CONNECT only to the assigned provider host on port 443. Seat services have no direct outbound route, cannot resolve another seat's proxy, and wait for their proxy health check before starting. There is no `host.docker.internal` or caller-supplied generic proxy.

The provider key enters as one Docker secret file. The entrypoint sets one family-specific key/base-URL pair plus the selector variables `QUINTE_PROVIDER_KEY_ENV` and `QUINTE_PROVIDER_BASE_URL_ENV`. Reviewed QUINTE v2 must copy only that selected pair and the mandatory proxy variables into each lane's otherwise minimal environment.

The proxy constrains destination host/port, not HTTP path or request content. DNS and TLS remain provider-side; this is an egress gate, not traffic inspection.

## Build And Diagnose

Hermes source is read only from the private agent-design checkout; MAGI and QUINTE source remain authoritative under `Public`:

```sh
MAGI_PROFILE_PYTHON="$HOME/Private/agent-design/hermes/agent/.venv/bin/python" \
  scripts/host/diagnose.sh
scripts/host/build-image.sh
```

`build-image.sh` exports exact committed trees via `git archive`; it never builds
a dirty worktree. `container/source-lock.env` contains full commit IDs, and both
commands fail closed if either commit or any required production capability
drifts.

## Direct Runs

macOS/Linux, composing from private rules:

```sh
MAGI_TECHNICAL_AGENTS=/absolute/workspace/AGENTS.md \
scripts/host/magi-seat.sh run \
  --seat seat-m \
  --trial /absolute/trial \
  --brief /absolute/trial/input/original-brief.json \
  --seat-config container/seats/seat-m.json \
  --policy container/policies/seat-m.json \
  --secret-file /absolute/private/seat-m.key \
  --json
```

`--keychain-service` can materialize a macOS Keychain secret into a temporary mode-0600 file. An already composed profile can be supplied with `--profile-source`; it still must pass receipt/digest validation.

PowerShell exposes the equivalent `-Seat`, `-Trial`, `-Brief`, `-TechnicalAgents`, `-SeatConfig`, `-Policy`, and `-SecretFile` parameters. `-CredentialTarget` uses Windows Credential Manager. Windows is statically maintained in CI; a real Credential Manager plus Docker Desktop E2E is not claimed until run on a Windows host.

Both launchers write only to `<trial>/seat-work/<seat>` and return `{"seat_id":"...","dossier_path":"..."}` in JSON mode. Secrets must be private files (POSIX `0400`/`0600`) or platform credential-store materializations. Never put them in `.env`, Compose overrides, JSON, profiles, or image layers.

## Artifacts

The dossier builder requires:

- completed QUINTE manifest 2.0 and result 2.1;
- matching semantic brief digests;
- identical manifest/result seat and route bindings;
- bindings equal to the immutable seat configuration and input policy;
- profile, thesis, and perspective files below the seat artifact root.

`derived_quinte_brief_sha256` is copied from QUINTE's semantic `manifest.brief_sha256`; it is not the raw hash of pretty-printed `input/brief.json`.

## Verification

```sh
MAGI_PROFILE_PYTHON="$HOME/Private/agent-design/hermes/agent/.venv/bin/python" \
  tests/host/test_static.sh
git diff --check
scripts/host/diagnose.sh
```

The static suite covers closed seat/policy/profile contracts, profile composition and tamper/retry behavior, dossier binding, shell syntax, PowerShell parsing when available, and Compose rendering. With a local Docker daemon it also starts the three proxy sidecars and verifies same-seat reachability, cross-seat DNS isolation, and a 403 for non-allowlisted CONNECT, without contacting a provider.

CI installs pinned `PyYAML==6.0.3`; runs Python contracts on Ubuntu, macOS, and Windows; parses both launcher families; renders Compose on Unix; and executes proxy topology integration on Linux. macOS host contracts and Docker proxy topology are locally verified. Windows remains static/CI-only. No credentialed provider or model inference E2E is part of these tests.
