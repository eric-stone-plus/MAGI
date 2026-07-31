"""Observed OCI / image provenance helpers.

Production container launches must not silently accept a different image than
the digest frozen into the assignment plan and execution receipts.
"""

from __future__ import annotations

import json
import subprocess
from typing import Any

from .errors import ContractError


def normalize_image_digest(value: str) -> str:
    """Accept sha256:<hex>, sha256://<hex>, or bare 64-hex; return sha256:<hex>."""

    if not isinstance(value, str) or not value.strip():
        raise ContractError("image digest must be a non-empty string")
    raw = value.strip()
    if raw.startswith("sha256://"):
        raw = "sha256:" + raw[len("sha256://") :]
    if raw.startswith("sha256:"):
        hexpart = raw[7:]
    else:
        hexpart = raw
    if len(hexpart) != 64:
        raise ContractError("image digest must be a 64-hex sha256 digest")
    try:
        int(hexpart, 16)
    except ValueError as exc:
        raise ContractError("image digest must be a 64-hex sha256 digest") from exc
    return "sha256:" + hexpart.lower()


def extract_digest_from_repo_digest(repo_digest: str) -> str | None:
    """Parse registry/name@sha256:hex into sha256:hex."""

    if not isinstance(repo_digest, str) or "@sha256:" not in repo_digest:
        return None
    _, digest = repo_digest.rsplit("@", 1)
    try:
        return normalize_image_digest(digest)
    except ContractError:
        return None


def extract_digest_from_image_id(image_id: str) -> str | None:
    """Parse docker image Id (sha256:hex) into sha256:hex."""

    if not isinstance(image_id, str):
        return None
    try:
        return normalize_image_digest(image_id)
    except ContractError:
        return None


def reconcile_declared_and_observed(
    *,
    declared_digest: str,
    observed_digest: str | None,
    allow_missing_observation: bool = False,
) -> str:
    """Fail closed when an observed digest disagrees with the declared pin."""

    declared = normalize_image_digest(declared_digest)
    if observed_digest is None:
        if allow_missing_observation:
            return declared
        raise ContractError("container image observation is required for provenance")
    observed = normalize_image_digest(observed_digest)
    if observed != declared:
        raise ContractError(
            f"observed image digest {observed} does not match declared pin {declared}"
        )
    return observed


def inspect_image_digest(image_ref: str) -> str:
    """Return the best available RepoDigest/Id digest for a local docker image."""

    if not isinstance(image_ref, str) or not image_ref.strip():
        raise ContractError("image reference must be a non-empty string")
    try:
        completed = subprocess.run(
            ["docker", "image", "inspect", image_ref, "--format", "{{json .}}"],
            check=False,
            capture_output=True,
            text=True,
            timeout=30,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ContractError(f"docker image inspect failed to start: {exc}") from exc
    if completed.returncode != 0:
        detail = (completed.stderr or completed.stdout or "").strip()[-500:]
        raise ContractError(f"docker image inspect failed for {image_ref}: {detail}")
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise ContractError("docker image inspect returned non-JSON") from exc
    return digest_from_inspect_payload(payload)


def digest_from_inspect_payload(payload: dict[str, Any]) -> str:
    """Extract a stable digest from a docker image inspect object."""

    if not isinstance(payload, dict):
        raise ContractError("docker inspect payload must be an object")
    repo_digests = payload.get("RepoDigests") or []
    if isinstance(repo_digests, list):
        for item in repo_digests:
            candidate = extract_digest_from_repo_digest(item) if isinstance(item, str) else None
            if candidate is not None:
                return candidate
    image_id = payload.get("Id")
    candidate = extract_digest_from_image_id(image_id) if isinstance(image_id, str) else None
    if candidate is None:
        raise ContractError("docker inspect payload has no usable image digest")
    return candidate


def read_source_lock(path: str | bytes) -> dict[str, str]:
    """Parse container/source-lock.env KEY=VALUE lines into a dict."""

    from pathlib import Path

    lock_path = Path(path)
    if not lock_path.is_file():
        raise ContractError(f"source-lock.env missing: {lock_path}")
    values: dict[str, str] = {}
    for line in lock_path.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        values[key.strip()] = value.strip().strip("\"'")
    for required in ("HERMES_COMMIT", "QUINTE_COMMIT"):
        if required not in values or not values[required]:
            raise ContractError(f"source-lock.env missing {required}")
        if len(values[required]) < 7:
            raise ContractError(f"source-lock.env {required} is not a full commit id")
    return values
