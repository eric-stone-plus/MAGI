# Triadic Cross-Verification Runtime 0.2.0

MAGI is the cross-family decision layer. QUINTE remains the same-family
deliberation engine inside each seat.

## Decision pipeline

1. Three distinct, immutable technical review profiles form independent
   analyses from one original brief. No seat sees another thesis.
2. Each thesis is combined with the unchanged original question, action scope,
   affected paths, and action binding. A complete same-family QUINTE run tests
   that perspective. Its Primary and Counterpart arbiters belong to the same
   family as all five lanes.
3. Each completed product is frozen as a digest-bound seat dossier. MAGI
   requires QUINTE manifest `2.0` and result `2.1`; degraded, incomplete,
   reused, same-family, or mixed-route triads fail closed.
4. Dossiers are assigned random aliases. Every seat reviews both other
   anonymized dossiers through the same complete frozen Hermes profile that
   produced its thesis, yielding six directed cross-reviews. A native model
   wrapper without that profile is rejected.
5. An explicit final adjudicator emits `PASS`, `BLOCK`, or `ESCALATE` using a
   closed JSON contract. It synthesizes the profiled theses, full QUINTE
   dossiers, and six reviews; it is neither a vote tally nor residual merge.
6. A deterministic verifier rejects missing high-risk source findings,
   invented evidence, unsupported closure, hidden dissent, schema drift, or an
   unsafe `PASS`. It then emits a RASHOMON/HIGHBALL residual trace `1.1`.

The runtime proves provenance, process separation, and deterministic coverage.
It does not prove truth, statistical independence, model identity, or provider
availability. Container isolation reduces state leakage but does not remove
shared training, prompt, protocol, or final-adjudicator correlation.

## Contracts

- `schemas/profile.schema.json`: a non-secret independent review configuration.
- `schemas/thesis.schema.json`: the independent first-pass thesis.
- `schemas/dossier.schema.json`: frozen thesis/profile/perspective/QUINTE
  bindings, including the complete immutable reviewer profile tree.
- `schemas/cross-review.schema.json`: one directed anonymous cross-review,
  its reviewer-profile binding, and auditable methodology trace.
- `schemas/final-verdict.schema.json`: actionable final-adjudication result.
- `schemas/product-summary.schema.json`: closed, digest-bound verification
  receipt for HIGHBALL and other callers.

The Python runtime uses equivalent closed, stdlib-only validators at every
trust boundary. Files are written atomically and rechecked by digest on resume.

## Agent command boundary

`magi run` accepts a JSON configuration with one command per seat and one
final-adjudicator command:

```json
{
  "config_version": "1.0",
  "seat_agents": {
    "seat-m": {
      "argv": ["scripts/host/magi-seat.sh", "reviewer-agent", "--seat", "seat-m"],
      "timeout_seconds": 1800,
      "pass_env": ["MAGI_SEAT_M_PROFILE", "MAGI_SEAT_M_CONFIG", "MAGI_SEAT_M_SECRET_FILE"],
      "reviewer_profile_mode": "hermes_profile",
      "profile_source": "/absolute/trial/dossiers/seat-m/reviewer-profile",
      "execution": {
        "family": "mimo", "provider": "xiaomi", "text_model": "mimo-v2.5-pro",
        "multimodal_model": "mimo-v2.5", "mode": "container", "service": "seat-m",
        "image_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
      }
    },
    "seat-d": {
      "argv": ["scripts/host/magi-seat.sh", "reviewer-agent", "--seat", "seat-d"],
      "timeout_seconds": 1800,
      "pass_env": ["MAGI_SEAT_D_PROFILE", "MAGI_SEAT_D_CONFIG", "MAGI_SEAT_D_SECRET_FILE"],
      "reviewer_profile_mode": "hermes_profile",
      "profile_source": "/absolute/trial/dossiers/seat-d/reviewer-profile",
      "execution": {
        "family": "deepseek", "provider": "deepseek", "text_model": "deepseek-v4-pro",
        "multimodal_model": "deepseek-v4-pro", "mode": "container", "service": "seat-d",
        "image_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
      }
    },
    "seat-g": {
      "argv": ["scripts/host/magi-seat.sh", "reviewer-agent", "--seat", "seat-g"],
      "timeout_seconds": 1800,
      "pass_env": ["MAGI_SEAT_G_PROFILE", "MAGI_SEAT_G_CONFIG", "MAGI_SEAT_G_SECRET_FILE"],
      "reviewer_profile_mode": "hermes_profile",
      "profile_source": "/absolute/trial/dossiers/seat-g/reviewer-profile",
      "execution": {
        "family": "openai", "provider": "openai-api", "text_model": "gpt-5.6-sol",
        "multimodal_model": "gpt-5.6-sol", "mode": "container", "service": "seat-g",
        "image_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
      }
    }
  },
  "final_adjudicator": {
    "argv": ["scripts/host/magi-seat.sh", "final-agent"],
    "timeout_seconds": 1800,
    "pass_env": ["MAGI_FINAL_CONFIG", "MAGI_FINAL_SECRET_FILE"],
    "execution": {
      "family": "openai", "provider": "openai-api", "text_model": "gpt-5.6-sol",
      "multimodal_model": "gpt-5.6-sol", "mode": "container", "service": "final-adjudicator",
      "image_digest": "sha256:0000000000000000000000000000000000000000000000000000000000000000"
    }
  }
}
```

`execution` is required on every seat agent and the final adjudicator. Production
Finale launches Compose service `final-adjudicator` (`mode=container`) through
`scripts/host/magi-seat.sh final-agent`. Seat reviewers use their seat services.
When `MAGI_REQUIRED_IMAGE_DIGEST` is set, the launcher inspects
`MAGI_SEAT_IMAGE` and fails closed on pin mismatch before `docker compose run`.

Commands receive exactly one JSON object on stdin and must return exactly one
JSON object on stdout. The runtime never invokes a shell. It constructs a
minimal environment from basic host variables plus only the listed credential
variable names. Values are never stored in trial state. Once execution starts,
the config digest is frozen so resume cannot silently change a model command.
Every seat command must declare `reviewer_profile_mode=hermes_profile`, and its
absolute `profile_source` must resolve exactly to that seat's profile tree in
the frozen trial dossier. Cross Review `1.1` copies the assigned profile spec,
profile-tree, and thesis digests into the artifact and records at least one
declared method plus one declared failure check with their concrete
application. Resume and `verify-product` replay those checks.

## CLI and resume

```sh
bin/magi init ./trial \
  --trial-id trial-2026-001 \
  --brief ./brief.json \
  --seat seat-m --seat seat-d --seat seat-g \
  --action-boundary protected_write

# Freeze exactly one evidence boundary before dossier generation.
bin/magi stage-no-evidence ./trial --brief ./trial/input/original-brief.json

bin/magi register-dossier ./trial --seat seat-m --dossier ./seats/seat-m/dossier.json
bin/magi register-dossier ./trial --seat seat-d --dossier ./seats/seat-d/dossier.json
bin/magi register-dossier ./trial --seat seat-g --dossier ./seats/seat-g/dossier.json

bin/magi run ./trial --config ./agents.json
bin/magi status ./trial
bin/magi verify-product ./trial
```

The three dossier builders start concurrently; validated outputs are frozen in
deterministic seat-slot order. `run` resumes at the first missing directed review or final-adjudication output. Completed
reviews, the verdict, and the final trace are digest-bound in `trial.json`.
Changing any frozen artifact stops the run instead of recomputing over a mixed
history. Re-running a completed trial is idempotent.

`verify-product` reloads every frozen dossier, all six reviews, the final
verdict, and the trace; revalidates all digests and contracts; reconstructs the
trace deterministically; checks the frozen runtime and configuration digests;
and emits a closed machine-readable product summary. Completed `run` and
`status` emit the same verified summary. The summary binds the
original brief and action, final decision, three family/profile/thesis/QUINTE
products, six cross-review digests, and exact final dissent. Its
`product_sha256` is the canonical
digest of every summary field except itself. `status` performs the same full
verification whenever the trial claims to be completed. HIGHBALL can consume
that summary as atomic execution evidence. MAGI never grants action
authorization.

The separate container layer produces thesis and QUINTE dossier artifacts on
macOS and Linux hosts. This runtime consumes the same Linux-container artifact
contract on either host; no host path or credential format enters the portable
trial contract. No display server, desktop session, or GUI is required.

## Verification

```sh
python3 -m unittest discover -v
python3 -m compileall -q magi tests
/Users/ericstone/Public/HIGHBALL/bin/validate-residual-trace.py \
  ./trial/final/residual-trace.json
```

The HIGHBALL validator uses exit `1` for a structurally valid trace that
intentionally blocks a strict action boundary because high-risk residuals are
open. Exit `2` indicates a malformed trace. MAGI's own `BLOCK` verdict is thus
expected to produce HIGHBALL exit `1`, not a false success exit `0`.

### Building dossiers

The host/container layer is exposed as a strict builder command instead of
being baked into the verifier:

```json
{
  "builder_version": "1.0",
  "seat_builders": {
    "seat-m": {"argv": ["scripts/host/magi-seat.sh", "agent"], "timeout_seconds": 7200, "pass_env": ["MAGI_SEAT_M_PROFILE", "MAGI_SEAT_M_SECRET_FILE"]},
    "seat-d": {"argv": ["scripts/host/magi-seat.sh", "agent"], "timeout_seconds": 7200, "pass_env": ["MAGI_SEAT_D_PROFILE", "MAGI_SEAT_D_SECRET_FILE"]},
    "seat-g": {"argv": ["scripts/host/magi-seat.sh", "agent"], "timeout_seconds": 7200, "pass_env": ["MAGI_SEAT_G_PROFILE", "MAGI_SEAT_G_SECRET_FILE"]}
  }
}
```

```sh
bin/magi build-dossiers ./trial --config ./builders.json --assignment-plan ./assignment-plan.json
```

Each builder receives a `magi_build_seat` JSON object on stdin and returns
exactly `{"seat_id":"...","dossier_path":"..."}`. The dossier must stay
under its assigned `<trial>/seat-work/<seat-id>` directory. MAGI validates it,
copies the complete product under `<trial>/dossiers/<seat-id>`, verifies the
copy, and removes write bits. Source symlinks are rejected; the copy is
validated in a temporary sibling directory before an atomic rename. Resume
adopts a valid renamed copy if interruption happened immediately before state
persistence, skips already-frozen seats, and rejects a changed builder config
digest.

`bin/magi-agent` supplies strict native adapters for model-only helpers and the
final-adjudication boundary. Production cross-review uses
`magi-seat.sh reviewer-agent` so the reviewer is the same complete frozen
Hermes profile, not a bare provider wrapper:

- `--backend mimo --model mimo-v2.5-pro --provider xiaomi --base-url URL
  --env-key XIAOMI_API_KEY`: native `mimo run --pure --format json`, with an
  ephemeral `MIMOCODE_HOME` and immutable `magi` agent denying tools and
  external actions.
- `--backend reasonix --model deepseek-v4-pro`: maximum reasoning with no
  allowed tools and `dontAsk` permission mode.
- `--backend codex --model gpt-5.6-sol --provider NAME --base-url URL
  --env-key NAME`: ephemeral/read-only `codex exec`, ignored user config and
  rules, Responses API, closed `--output-schema`, and a scoped credential env
  name. The key value never enters argv, prompt, output, or state.

OMP, CodeWhale, OpenCode, Kilo, and Claude are deliberately outside the
production seat-carrier allowlist; there is no fallback to them.

All native adapters parse exactly one JSON object and revalidate the closed
task contract after model output. Their commands are intentionally explicit;
production configuration must pin the model and provider identity.
