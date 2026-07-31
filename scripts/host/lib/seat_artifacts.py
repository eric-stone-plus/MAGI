#!/usr/bin/env python3
"""Closed MAGI seat artifacts and canonical JSON helpers."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any


PROFILE_FIELDS = {
    "profile_version",
    "profile_id",
    "discipline",
    "epistemic_lens",
    "methods",
    "failure_checks",
    "instructions",
}
THESIS_FIELDS = {
    "thesis_version",
    "question",
    "thesis",
    "claims",
    "recommendation",
    "limitations",
}
CLAIM_FIELDS = {"id", "statement", "evidence_refs", "uncertainty", "boundary"}
PERSPECTIVE_FIELDS = {
    "perspective_input_version",
    "seat_id",
    "original_brief_sha256",
    "profile_id",
    "profile_sha256",
    "thesis_sha256",
    "original_question",
    "action_scope",
    "affected_paths",
    "action_binding_sha256",
    "derived_context",
}
SEAT_FIELDS = {
    "seat_config_version",
    "seat_id",
    "profile_id",
    "model_family",
    "provider",
    "text_model",
    "multimodal_model",
    "provider_key_env",
    "provider_base_url_env",
    "provider_base_url",
}
ASSIGNMENT_PLAN_FIELDS = {
    "assignment_plan_version", "trial_id", "objective", "global_checks", "seats",
    "cross_review_obligations", "finale_condition", "limitations", "plan_binding_sha256",
}
EVIDENCE_MANIFEST_FIELDS = {
    "evidence_manifest_version", "original_brief_ref", "original_brief_sha256",
    "source_root", "staged_root_ref", "source_files", "derived_frames",
    "evidence_set_sha256", "limitations",
}
KEY_ENVS = {"XIAOMI_API_KEY", "DEEPSEEK_API_KEY", "OPENAI_API_KEY"}
BASE_URL_ENVS = {"XIAOMI_BASE_URL", "DEEPSEEK_BASE_URL", "OPENAI_BASE_URL"}
DIGEST_PREFIX = "sha256:"
BRIEF_FIELDS = {
    "brief_version",
    "question",
    "context",
    "evidence_roots",
    "snapshot_ignore",
    "attachments",
    "action_scope",
    "affected_paths",
    "action_binding_sha256",
}
ROUTE_PARTIES = (
    "Party A",
    "Party B",
    "Party C",
    "Party D",
    "Party E",
    "Counterpart Arbiter",
    "Primary Arbiter",
)
POLICY_FIELDS = {
    "policy_version",
    "seat",
    "roster",
    "counterpart_arbiter",
    "primary_arbiter",
    "auto_primary_arbiter",
    "text_model",
    "multimodal_model",
    "max_parallel_r1",
    "max_parallel_r2",
    "r2_parallel",
    "max_attempts",
    "timeout_seconds",
    "retry_backoff_seconds",
    "retry_backoff_max_seconds",
    "r2_min_interval_seconds",
    "max_output_bytes",
    "max_snapshot_files",
    "max_snapshot_bytes",
    "max_attachment_bytes",
    "sandbox_mode",
}
ROUTE_POLICY_FIELDS = {
    "party_id",
    "route_id",
    "adapter",
    "executable",
    "required",
    "family",
    "provider",
    "text_model",
    "multimodal_model",
    "perspective",
}
ROUTE_BINDING_FIELDS = ROUTE_POLICY_FIELDS - {"required"}
PRODUCTION_SEATS = {
    "seat-m": {
        "profile_id": "formalist",
        "model_family": "mimo",
        "provider": "xiaomi",
        "text_model": "mimo-v2.5-pro",
        "multimodal_model": "mimo-v2.5",
        "provider_key_env": "XIAOMI_API_KEY",
        "provider_base_url_env": "XIAOMI_BASE_URL",
        "provider_base_url": "https://api.xiaomimimo.com/v1",
        "adapter": "mimo",
        "executable": "mimo",
    },
    "seat-d": {
        "profile_id": "adversarial",
        "model_family": "deepseek",
        "provider": "deepseek",
        "text_model": "deepseek-v4-pro",
        "multimodal_model": "deepseek-v4-pro",
        "provider_key_env": "DEEPSEEK_API_KEY",
        "provider_base_url_env": "DEEPSEEK_BASE_URL",
        "provider_base_url": "https://api.deepseek.com/v1",
        "adapter": "reasonix",
        "executable": "reasonix",
    },
    "seat-g": {
        "profile_id": "empirical",
        "model_family": "openai",
        "provider": "openai-api",
        "text_model": "gpt-5.6-sol",
        "multimodal_model": "gpt-5.6-sol",
        "provider_key_env": "OPENAI_API_KEY",
        "provider_base_url_env": "OPENAI_BASE_URL",
        "provider_base_url": "https://apinebula.com/v1",
        "adapter": "codex",
        "executable": "codex",
    },
}


class ContractError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode()


def digest_bytes(value: bytes) -> str:
    return "sha256:" + hashlib.sha256(value).hexdigest()


def digest_file(path: Path) -> str:
    return digest_bytes(path.read_bytes())


def digest_tree(root: Path) -> str:
    hasher = hashlib.sha256()
    for path in sorted(path for path in root.rglob("*") if path.is_file()):
        relative = path.relative_to(root).as_posix().encode()
        data = path.read_bytes()
        hasher.update(len(relative).to_bytes(8, "big"))
        hasher.update(relative)
        hasher.update(len(data).to_bytes(8, "big"))
        hasher.update(data)
    return "sha256:" + hasher.hexdigest()


def digest(value: Any, label: str) -> str:
    candidate = text(value, label)
    if len(candidate) != len(DIGEST_PREFIX) + 64 or not candidate.startswith(DIGEST_PREFIX):
        raise ContractError(f"{label} must be a sha256 digest")
    try:
        int(candidate[len(DIGEST_PREFIX) :], 16)
    except ValueError as exc:
        raise ContractError(f"{label} must be a sha256 digest") from exc
    return candidate


def read_object(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON object {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"{path} must contain a JSON object")
    return value


def closed(value: dict[str, Any], fields: set[str], label: str) -> None:
    if set(value) != fields:
        unknown = sorted(set(value) - fields)
        missing = sorted(fields - set(value))
        raise ContractError(f"{label} closed-field mismatch; unknown={unknown}, missing={missing}")


def text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty string")
    return value


def string_list(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value) or not all(isinstance(x, str) for x in value):
        raise ContractError(f"{label} must be a{' non-empty' if nonempty else ''} string array")
    return value


def validate_profile(value: dict[str, Any], expected_id: str | None = None) -> dict[str, Any]:
    closed(value, PROFILE_FIELDS, "profile")
    if value.get("profile_version") != "1.0":
        raise ContractError("profile_version must be 1.0")
    for field in ("profile_id", "discipline", "epistemic_lens", "instructions"):
        text(value.get(field), f"profile.{field}")
    string_list(value.get("methods"), "profile.methods", nonempty=True)
    string_list(value.get("failure_checks"), "profile.failure_checks", nonempty=True)
    if expected_id is not None and value["profile_id"] != expected_id:
        raise ContractError("profile_id does not match seat configuration")
    return value


def validate_thesis(value: dict[str, Any], question: str) -> dict[str, Any]:
    closed(value, THESIS_FIELDS, "thesis")
    if value.get("thesis_version") != "1.0" or value.get("question") != question:
        raise ContractError("thesis version/question does not match the original brief")
    for field in ("question", "thesis", "recommendation"):
        text(value.get(field), f"thesis.{field}")
    string_list(value.get("limitations"), "thesis.limitations")
    claims = value.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ContractError("thesis.claims must be a non-empty array")
    seen: set[str] = set()
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            raise ContractError(f"thesis.claims[{index}] must be an object")
        closed(claim, CLAIM_FIELDS, f"thesis.claims[{index}]")
        claim_id = text(claim.get("id"), f"thesis.claims[{index}].id")
        if claim_id in seen:
            raise ContractError(f"duplicate thesis claim id {claim_id}")
        seen.add(claim_id)
        for field in ("statement", "uncertainty", "boundary"):
            text(claim.get(field), f"thesis.claims[{index}].{field}")
        string_list(claim.get("evidence_refs"), f"thesis.claims[{index}].evidence_refs")
    return value


def validate_original_brief(value: dict[str, Any]) -> dict[str, Any]:
    closed(value, BRIEF_FIELDS, "original brief")
    if value.get("brief_version") != "1.1":
        raise ContractError("original brief_version must be 1.1")
    text(value.get("question"), "brief.question")
    context = value.get("context")
    if context is not None and not isinstance(context, str):
        raise ContractError("brief.context must be a string or null")
    string_list(value.get("evidence_roots"), "brief.evidence_roots")
    string_list(value.get("snapshot_ignore"), "brief.snapshot_ignore")
    string_list(value.get("attachments"), "brief.attachments")
    action_scope = value.get("action_scope")
    if action_scope is not None and not isinstance(action_scope, str):
        raise ContractError("brief.action_scope must be a string or null")
    string_list(value.get("affected_paths"), "brief.affected_paths")
    action_binding = value.get("action_binding_sha256")
    if action_binding is not None:
        digest(action_binding, "brief.action_binding_sha256")
    return value


def validate_seat(value: dict[str, Any]) -> dict[str, Any]:
    closed(value, SEAT_FIELDS, "seat config")
    if value.get("seat_config_version") != "1.0":
        raise ContractError("seat_config_version must be 1.0")
    for field in SEAT_FIELDS - {"seat_config_version"}:
        text(value.get(field), f"seat.{field}")
    if value["provider_key_env"] not in KEY_ENVS:
        raise ContractError("provider_key_env is outside the allowlist")
    if value["provider_base_url_env"] not in BASE_URL_ENVS:
        raise ContractError("provider_base_url_env is outside the allowlist")
    if value["seat_id"] not in PRODUCTION_SEATS:
        raise ContractError("seat_id is outside the production seat allowlist")
    expected = PRODUCTION_SEATS[value["seat_id"]]
    for field in SEAT_FIELDS - {"seat_config_version", "seat_id"}:
        if value[field] != expected[field]:
            raise ContractError(f"seat.{field} does not match the production seat binding")
    if not value["provider_base_url"].startswith("https://"):
        raise ContractError("provider_base_url must use https")
    if ".invalid" in value["provider_base_url"]:
        raise ContractError("provider_base_url is a placeholder")
    return value


def seat_binding(seat: dict[str, Any]) -> dict[str, str]:
    return {
        "seat_id": seat["seat_id"],
        "family": seat["model_family"],
        "provider": seat["provider"],
        "text_model": seat["text_model"],
        "multimodal_model": seat["multimodal_model"],
    }


def validate_policy(value: dict[str, Any], seat: dict[str, Any]) -> list[dict[str, Any]]:
    closed(value, POLICY_FIELDS, "policy")
    if value.get("policy_version") != "2.0":
        raise ContractError("policy_version must be 2.0")
    expected_binding = seat_binding(seat)
    if value.get("seat") != expected_binding:
        raise ContractError("policy.seat does not match the immutable seat config")
    if value.get("auto_primary_arbiter") is not True:
        raise ContractError("policy.auto_primary_arbiter must be true")
    if value.get("text_model") != seat["text_model"] or value.get(
        "multimodal_model"
    ) != seat["multimodal_model"]:
        raise ContractError("policy model aliases do not match the immutable seat config")
    roster = value.get("roster")
    if not isinstance(roster, list) or len(roster) != 5:
        raise ContractError("policy.roster must contain exactly five parties")
    routes = [*roster, value.get("counterpart_arbiter"), value.get("primary_arbiter")]
    expected_adapter = PRODUCTION_SEATS[seat["seat_id"]]["adapter"]
    expected_executable = PRODUCTION_SEATS[seat["seat_id"]]["executable"]
    route_ids: set[str] = set()
    perspectives: set[str] = set()
    bindings: list[dict[str, Any]] = []
    for index, raw in enumerate(routes):
        if not isinstance(raw, dict):
            raise ContractError(f"policy route {index} must be an object")
        closed(raw, ROUTE_POLICY_FIELDS, f"policy route {index}")
        if raw.get("party_id") != ROUTE_PARTIES[index]:
            raise ContractError("policy routes must cover the fixed seven-role order")
        route_id = text(raw.get("route_id"), f"policy route {index}.route_id")
        if route_id in route_ids:
            raise ContractError("policy route_id values must be globally unique")
        route_ids.add(route_id)
        perspective = text(raw.get("perspective"), f"policy route {index}.perspective")
        if perspective in perspectives:
            raise ContractError("policy perspectives must be distinct")
        perspectives.add(perspective)
        if raw.get("required") is not True:
            raise ContractError(f"policy route {index} must be required")
        if raw.get("adapter") != expected_adapter or raw.get("executable") != expected_executable:
            raise ContractError(
                f"policy route {index} must use the production {expected_adapter} adapter"
            )
        for route_field, seat_field in (
            ("family", "model_family"),
            ("provider", "provider"),
            ("text_model", "text_model"),
            ("multimodal_model", "multimodal_model"),
        ):
            if raw.get(route_field) != seat[seat_field]:
                raise ContractError(
                    f"policy route {index}.{route_field} does not match the immutable seat config"
                )
        bindings.append({field: raw[field] for field in ROUTE_BINDING_FIELDS})
    return bindings


def atomic_json(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = canonical_bytes(value)
    fd, tmp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(tmp_name, 0o600)
        os.replace(tmp_name, path)
    finally:
        if os.path.exists(tmp_name):
            os.unlink(tmp_name)


def command_validate(args: argparse.Namespace) -> None:
    value = read_object(Path(args.path))
    if args.kind == "profile":
        validate_profile(value, args.expected_id)
    elif args.kind == "thesis":
        validate_thesis(value, args.question)
    elif args.kind == "seat":
        validate_seat(value)
    elif args.kind == "policy":
        if not args.seat:
            raise ContractError("policy validation requires --seat")
        seat = validate_seat(read_object(Path(args.seat)))
        validate_policy(value, seat)
    elif args.kind == "brief":
        validate_original_brief(value)
    print(digest_bytes(canonical_bytes(value)))


def command_canonicalize(args: argparse.Namespace) -> None:
    source = Path(args.source)
    destination = Path(args.destination)
    value = read_object(source)
    if args.kind == "profile":
        validate_profile(value, args.expected_id)
    elif args.kind == "thesis":
        validate_thesis(value, args.question)
    atomic_json(destination, value)
    print(digest_file(destination))


def command_derive(args: argparse.Namespace) -> None:
    seat = validate_seat(read_object(Path(args.seat)))
    profile_path = Path(args.profile)
    thesis_path = Path(args.thesis)
    original_path = Path(args.original_brief)
    profile = validate_profile(read_object(profile_path), seat["profile_id"])
    original = validate_original_brief(read_object(original_path))
    manifest = read_object(Path(args.evidence_manifest))
    closed(manifest, EVIDENCE_MANIFEST_FIELDS, "evidence manifest")
    if manifest.get("evidence_manifest_version") != "1.0" or manifest.get("staged_root_ref") != "trial-private/evidence":
        raise ContractError("evidence manifest version/root is invalid")
    if digest(manifest.get("original_brief_sha256"), "evidence manifest.original_brief_sha256") != digest_file(original_path):
        raise ContractError("evidence manifest does not bind the original brief")
    assignment = read_object(Path(args.assignment_plan))
    closed(assignment, ASSIGNMENT_PLAN_FIELDS, "assignment plan")
    if assignment.get("assignment_plan_version") != "1.0":
        raise ContractError("assignment plan version is invalid")
    selected = [item for item in assignment.get("seats", []) if isinstance(item, dict) and item.get("seat_id") == seat["seat_id"]]
    if len(selected) != 1:
        raise ContractError("assignment plan does not bind exactly one matching seat")
    assignment_seat = selected[0]
    for assignment_field, seat_field in (
        ("family", "model_family"), ("provider", "provider"),
        ("text_model", "text_model"), ("multimodal_model", "multimodal_model"),
        ("profile_id", "profile_id"),
    ):
        if assignment_seat.get(assignment_field) != seat[seat_field]:
            raise ContractError(f"assignment plan {assignment_field} does not match seat config")
    question = text(original.get("question"), "brief.question")
    thesis = validate_thesis(read_object(thesis_path), question)
    profile_sha = digest_file(profile_path)
    thesis_sha = digest_file(thesis_path)
    original_sha = digest_file(original_path)
    derived_context = (
        f"MAGI independent review seat {seat['seat_id']}\n"
        f"Profile: {profile['profile_id']} ({profile_sha})\n"
        f"Thesis: {thesis_sha}\n\n"
        + canonical_bytes(thesis).decode()
    )
    perspective = {
        "perspective_input_version": "1.0",
        "seat_id": seat["seat_id"],
        "original_brief_sha256": original_sha,
        "profile_id": profile["profile_id"],
        "profile_sha256": profile_sha,
        "thesis_sha256": thesis_sha,
        "original_question": question,
        "action_scope": original.get("action_scope"),
        "affected_paths": original.get("affected_paths", []),
        "action_binding_sha256": original.get("action_binding_sha256"),
        "derived_context": derived_context,
    }
    closed(perspective, PERSPECTIVE_FIELDS, "perspective input")
    brief = dict(original)
    focus = string_list(assignment_seat.get("primary_focus"), "assignment seat.primary_focus", nonempty=True)
    global_checks = string_list(assignment_seat.get("mandatory_global_checks"), "assignment seat.mandatory_global_checks", nonempty=True)
    brief["context"] = (
        derived_context
        + "\nFrozen primary focus: " + json.dumps(focus, ensure_ascii=False)
        + "\nMandatory complete checks: " + json.dumps(global_checks, ensure_ascii=False)
    )
    exposure_refs = set(
        string_list(assignment_seat.get("evidence_refs"), "assignment seat.evidence_refs")
    )
    manifest_items = [*manifest.get("source_files", []), *manifest.get("derived_frames", [])]
    by_ref = {
        item.get("evidence_ref"): item for item in manifest_items if isinstance(item, dict)
    }
    if not exposure_refs.issubset(by_ref):
        raise ContractError("assignment plan exposes evidence outside the manifest")
    # Only open the snapshot tree when this seat was assigned at least one snapshot exposure.
    snapshot_assigned = any(
        "snapshot" in set(by_ref[reference].get("exposure_modes") or [])
        for reference in exposure_refs
    )
    brief["evidence_roots"] = ["/evidence/snapshot"] if snapshot_assigned else []
    brief["attachments"] = sorted(
        "/evidence/" + by_ref[reference]["staged_ref"]
        for reference in exposure_refs
        if "multimodal_attachment" in set(by_ref[reference].get("exposure_modes") or [])
    )
    # Hide every staged snapshot path that was not assigned to this seat so QUINTE
    # cannot re-snapshot unassigned multimodal or sibling-seat media from the shared mount.
    ignore: list[str] = []
    for reference, item in by_ref.items():
        if reference in exposure_refs:
            continue
        staged = item.get("staged_ref")
        if not isinstance(staged, str) or not staged.startswith("snapshot/"):
            continue
        relative = staged[len("snapshot/") :]
        if relative:
            ignore.append(relative)
    brief["snapshot_ignore"] = sorted(set(ignore))
    atomic_json(Path(args.perspective_output), perspective)
    atomic_json(Path(args.brief_output), brief)


def build_seat_mapping_receipt(
    *,
    seat_id: str,
    evidence_manifest: dict[str, Any],
    evidence_manifest_sha256: str,
    assignment_plan_sha256: str,
    assigned_evidence_refs: list[str],
    quinte_run_id: str,
    quinte_snapshot_manifest: dict[str, Any],
    quinte_snapshot_manifest_ref: str,
    quinte_snapshot_manifest_sha256: str,
) -> dict[str, Any]:
    """Join MAGI staged digests to QUINTE snapshot/attachment entries (container helper)."""

    assigned = string_list(assigned_evidence_refs, "assigned_evidence_refs")
    items = {
        item["evidence_ref"]: item
        for item in [
            *evidence_manifest.get("source_files", []),
            *evidence_manifest.get("derived_frames", []),
        ]
        if isinstance(item, dict) and isinstance(item.get("evidence_ref"), str)
    }
    missing = sorted(set(assigned) - set(items))
    if missing:
        raise ContractError("assigned evidence missing from MAGI manifest: " + ", ".join(missing))
    by_digest: dict[str, list[dict[str, Any]]] = {}
    seen_local: set[str] = set()
    for raw in quinte_snapshot_manifest.get("entries") or []:
        if not isinstance(raw, dict):
            raise ContractError("QUINTE snapshot entry must be an object")
        local_ref = text(raw.get("snapshot_ref"), "snapshot_ref")
        if local_ref in seen_local:
            raise ContractError(f"duplicate QUINTE-local ref: {local_ref}")
        seen_local.add(local_ref)
        digest_value = digest(raw.get("sha256"), "snapshot.sha256")
        by_digest.setdefault(digest_value, []).append(
            {
                "local_ref": local_ref,
                "kind": "snapshot",
                "source_name": text(raw.get("source_name"), "source_name"),
                "sha256": digest_value,
                "bytes": raw.get("bytes"),
                "media_type": text(raw.get("media_type"), "media_type"),
            }
        )
    for raw in quinte_snapshot_manifest.get("attachments") or []:
        if not isinstance(raw, dict):
            raise ContractError("QUINTE attachment entry must be an object")
        local_ref = text(raw.get("attachment_ref"), "attachment_ref")
        if local_ref in seen_local:
            raise ContractError(f"duplicate QUINTE-local ref: {local_ref}")
        seen_local.add(local_ref)
        digest_value = digest(raw.get("sha256"), "attachment.sha256")
        by_digest.setdefault(digest_value, []).append(
            {
                "local_ref": local_ref,
                "kind": "attachment",
                "source_name": text(raw.get("source_name"), "source_name"),
                "sha256": digest_value,
                "bytes": raw.get("bytes"),
                "media_type": text(raw.get("media_type"), "media_type"),
            }
        )
    mappings: list[dict[str, Any]] = []
    used_local: set[str] = set()
    for reference in assigned:
        item = items[reference]
        staged_digest = digest(item.get("sha256"), f"{reference}.sha256")
        candidates = list(by_digest.get(staged_digest, []))
        if not candidates:
            raise ContractError(
                f"no QUINTE-local entry matches staged digest for {reference}"
            )
        local_refs = sorted({entry["local_ref"] for entry in candidates})
        if used_local & set(local_refs):
            raise ContractError(
                "QUINTE-local ref already mapped to another canonical item"
            )
        used_local.update(local_refs)
        mappings.append(
            {
                "canonical_ref": reference,
                "staged_ref": item["staged_ref"],
                "staged_sha256": staged_digest,
                "size_bytes": item["size_bytes"],
                "media_type": item["media_type"],
                "media_class": item["media_class"],
                "exposure_modes": list(item["exposure_modes"]),
                "quinte_local_refs": local_refs,
                "quinte_entries": sorted(candidates, key=lambda value: value["local_ref"]),
            }
        )
    all_local = {
        entry["local_ref"] for entries in by_digest.values() for entry in entries
    }
    receipt: dict[str, Any] = {
        "mapping_receipt_version": "1.0",
        "seat_id": seat_id,
        "evidence_manifest_sha256": evidence_manifest_sha256,
        "assignment_plan_sha256": assignment_plan_sha256,
        "assigned_evidence_refs": assigned,
        "quinte_run_id": quinte_run_id,
        "quinte_snapshot_manifest_ref": quinte_snapshot_manifest_ref,
        "quinte_snapshot_manifest_sha256": quinte_snapshot_manifest_sha256,
        "mappings": mappings,
        "unmapped_canonical_refs": [],
        "unmapped_quinte_local_refs": sorted(all_local - used_local),
        "limitations": sorted(
            {
                "Mapping joins staged digests to QUINTE snapshot/attachment entries; it does not prove model perception.",
                "Unmapped QUINTE-local refs are reported when the snapshot tree contains extra files.",
            }
        ),
        "receipt_binding_sha256": "",
    }
    receipt["receipt_binding_sha256"] = digest_bytes(
        canonical_bytes(
            {key: value for key, value in receipt.items() if key != "receipt_binding_sha256"}
        )
    )
    return receipt


def command_dossier(args: argparse.Namespace) -> None:
    seat = validate_seat(read_object(Path(args.seat)))
    root = Path(args.output).resolve().parent
    paths = {
        "profile_ref": Path(args.profile).resolve(),
        "reviewer_profile_ref": Path(args.reviewer_profile).resolve(),
        "thesis_ref": Path(args.thesis).resolve(),
        "perspective_input_ref": Path(args.perspective).resolve(),
        "quinte_run_ref": Path(args.run_dir).resolve(),
    }
    for label, path in paths.items():
        if root not in path.parents:
            raise ContractError(f"{label} must resolve below the dossier directory")
    reviewer_profile = paths["reviewer_profile_ref"]
    if not reviewer_profile.is_dir():
        raise ContractError("reviewer_profile_ref must be a directory")
    if any(path.is_symlink() for path in reviewer_profile.rglob("*")):
        raise ContractError("reviewer profile must not contain symlinks")
    receipt = read_object(reviewer_profile / "COMPOSITION.json")
    if (
        receipt.get("composition_version") != "1.0"
        or receipt.get("seat_id") != seat["seat_id"]
        or receipt.get("profile_id") != seat["profile_id"]
    ):
        raise ContractError("reviewer profile composition does not match immutable seat config")
    if validate_profile(read_object(reviewer_profile / "profile.json"), seat["profile_id"]) != validate_profile(
        read_object(paths["profile_ref"]), seat["profile_id"]
    ):
        raise ContractError("reviewer profile metadata differs from profile artifact")
    manifest = paths["quinte_run_ref"] / "manifest.json"
    result = paths["quinte_run_ref"] / "result.json"
    manifest_value = read_object(manifest)
    result_value = read_object(result)
    if manifest_value.get("status") != "completed" or result_value.get("status") != "completed":
        raise ContractError("QUINTE result status must be completed")
    if manifest_value.get("manifest_version") != "2.0":
        raise ContractError("QUINTE manifest_version must be 2.0")
    if result_value.get("result_version") != "2.1":
        raise ContractError("QUINTE result_version must be 2.1")
    manifest_brief_digest = digest(manifest_value.get("brief_sha256"), "manifest.brief_sha256")
    if manifest_brief_digest != result_value.get("brief_sha256"):
        raise ContractError("QUINTE manifest/result brief digests differ")
    manifest_seat_binding = manifest_value.get("seat_binding")
    result_binding = result_value.get("seat_binding")
    if not isinstance(manifest_seat_binding, dict) or manifest_seat_binding != result_binding:
        raise ContractError("QUINTE manifest/result seat bindings differ")
    expected_binding = seat_binding(seat)
    if manifest_seat_binding != expected_binding:
        raise ContractError("QUINTE seat binding does not match immutable seat config")
    if manifest_value.get("route_bindings") != result_value.get("route_bindings"):
        raise ContractError("QUINTE manifest/result route bindings differ")
    policy = read_object(paths["quinte_run_ref"] / "input" / "policy.json")
    policy_bindings = validate_policy(policy, seat)
    if policy_bindings != manifest_value.get("route_bindings"):
        raise ContractError("QUINTE input policy route bindings do not match manifest/result")
    perspective = read_object(paths["perspective_input_ref"])
    if perspective.get("seat_id") != seat["seat_id"] or perspective.get("profile_id") != seat["profile_id"]:
        raise ContractError("perspective input does not match immutable seat config")
    assignment_plan_sha256 = None
    assigned_refs: list[str] = []
    mapping_ref = None
    mapping_sha = None
    if args.evidence_manifest and args.assignment_plan:
        evidence_path = Path(args.evidence_manifest).resolve()
        assignment_path = Path(args.assignment_plan).resolve()
        evidence_manifest = read_object(evidence_path)
        closed(evidence_manifest, EVIDENCE_MANIFEST_FIELDS, "evidence manifest")
        assignment = read_object(assignment_path)
        closed(assignment, ASSIGNMENT_PLAN_FIELDS, "assignment plan")
        selected = [
            item
            for item in assignment.get("seats", [])
            if isinstance(item, dict) and item.get("seat_id") == seat["seat_id"]
        ]
        if len(selected) != 1:
            raise ContractError("assignment plan does not bind exactly one matching seat")
        assigned_refs = string_list(selected[0].get("evidence_refs"), "assignment seat.evidence_refs")
        snapshot_path = paths["quinte_run_ref"] / "input" / "snapshot-manifest.json"
        if not snapshot_path.is_file():
            raise ContractError("QUINTE snapshot-manifest.json is required for mapping receipt")
        quinte_snapshot = read_object(snapshot_path)
        run_id = text(manifest_value.get("run_id"), "QUINTE manifest.run_id")
        assignment_plan_sha256 = digest_file(assignment_path)
        mapping_receipt = build_seat_mapping_receipt(
            seat_id=seat["seat_id"],
            evidence_manifest=evidence_manifest,
            evidence_manifest_sha256=digest_file(evidence_path),
            assignment_plan_sha256=assignment_plan_sha256,
            assigned_evidence_refs=assigned_refs,
            quinte_run_id=run_id,
            quinte_snapshot_manifest=quinte_snapshot,
            quinte_snapshot_manifest_ref=str(snapshot_path.relative_to(root)),
            quinte_snapshot_manifest_sha256=digest_file(snapshot_path),
        )
        mapping_path = Path(args.output).resolve().parent / "evidence-mapping-receipt.json"
        atomic_json(mapping_path, mapping_receipt)
        mapping_ref = "evidence-mapping-receipt.json"
        mapping_sha = digest_file(mapping_path)
    elif assigned_refs:
        raise ContractError("assigned evidence requires evidence-manifest and assignment-plan inputs")
    dossier = {
        "dossier_version": "1.0",
        "seat_id": seat["seat_id"],
        "profile_id": seat["profile_id"],
        "profile_ref": str(paths["profile_ref"].relative_to(root)),
        "profile_sha256": digest_file(paths["profile_ref"]),
        "reviewer_profile_ref": str(paths["reviewer_profile_ref"].relative_to(root)),
        "reviewer_profile_sha256": digest_tree(paths["reviewer_profile_ref"]),
        "thesis_ref": str(paths["thesis_ref"].relative_to(root)),
        "thesis_sha256": digest_file(paths["thesis_ref"]),
        "perspective_input_ref": str(paths["perspective_input_ref"].relative_to(root)),
        "perspective_input_sha256": digest_file(paths["perspective_input_ref"]),
        "original_brief_sha256": digest(perspective.get("original_brief_sha256"), "perspective.original_brief_sha256"),
        # QUINTE hashes the compact serde Brief, not the pretty persisted file.
        "derived_quinte_brief_sha256": manifest_brief_digest,
        "quinte_run_ref": str(paths["quinte_run_ref"].relative_to(root)),
        "quinte_manifest_sha256": digest_file(manifest),
        "quinte_result_sha256": digest_file(result),
        "assignment_plan_sha256": assignment_plan_sha256,
        "assigned_evidence_refs": assigned_refs,
        "evidence_mapping_ref": mapping_ref,
        "evidence_mapping_sha256": mapping_sha,
    }
    atomic_json(Path(args.output), dossier)


def parser() -> argparse.ArgumentParser:
    top = argparse.ArgumentParser()
    subs = top.add_subparsers(dest="command", required=True)
    validate = subs.add_parser("validate")
    validate.add_argument("kind", choices=("profile", "thesis", "seat", "policy", "brief"))
    validate.add_argument("path")
    validate.add_argument("--seat")
    validate.add_argument("--expected-id")
    validate.add_argument("--question", default="")
    validate.set_defaults(function=command_validate)
    canonical = subs.add_parser("canonicalize")
    canonical.add_argument("kind", choices=("profile", "thesis"))
    canonical.add_argument("source")
    canonical.add_argument("destination")
    canonical.add_argument("--expected-id")
    canonical.add_argument("--question", default="")
    canonical.set_defaults(function=command_canonicalize)
    derive = subs.add_parser("derive")
    derive.add_argument("--seat", required=True)
    derive.add_argument("--profile", required=True)
    derive.add_argument("--thesis", required=True)
    derive.add_argument("--original-brief", required=True)
    derive.add_argument("--evidence-manifest", required=True)
    derive.add_argument("--assignment-plan", required=True)
    derive.add_argument("--perspective-output", required=True)
    derive.add_argument("--brief-output", required=True)
    derive.set_defaults(function=command_derive)
    dossier = subs.add_parser("dossier")
    dossier.add_argument("--seat", required=True)
    dossier.add_argument("--profile", required=True)
    dossier.add_argument("--reviewer-profile", required=True)
    dossier.add_argument("--thesis", required=True)
    dossier.add_argument("--perspective", required=True)
    dossier.add_argument("--run-dir", required=True)
    dossier.add_argument("--output", required=True)
    dossier.add_argument("--evidence-manifest", default="")
    dossier.add_argument("--assignment-plan", default="")
    dossier.set_defaults(function=command_dossier)
    return top


def main() -> int:
    try:
        args = parser().parse_args()
        args.function(args)
        return 0
    except ContractError as exc:
        print(f"seat artifact contract error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
