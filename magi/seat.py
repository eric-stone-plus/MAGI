"""Fail-closed loader for a frozen independent-review seat dossier."""

from __future__ import annotations

import re
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .contracts import (
    CLOSURE_STATES,
    DISPOSITIONS,
    ROUTE_BINDING_FIELDS,
    ROUTE_PARTIES,
    closed,
    digest,
    string_list,
    text,
    validate_dossier,
    validate_profile,
    validate_route_bindings,
    validate_seat_binding,
    validate_thesis,
)
from .errors import ContractError
from .io import digest_bytes, digest_file, digest_tree, quinte_json_bytes, read_json
from .mapping import validate_mapping_receipt


MANIFEST_2_FIELDS = {
    "manifest_version",
    "run_id",
    "created_at",
    "updated_at",
    "status",
    "brief_sha256",
    "policy_sha256",
    "snapshot_sha256",
    "runtime_sha256",
    "protocol_version",
    "effective_model",
    "sandbox_mode",
    "current_phase",
    "error",
    "r3_input_receipt",
    "primary_arbiter_challenge",
    "primary_arbiter_submission",
    "result_sha256",
    "seat_binding",
    "route_bindings",
}
RESULT_21_FIELDS = {
    "result_version",
    "run_id",
    "status",
    "brief_sha256",
    "question",
    "action_scope",
    "affected_paths",
    "action_binding_sha256",
    "summary",
    "recommendation",
    "dissent",
    "residuals",
    "trial_manifest",
    "seat_binding",
    "route_bindings",
}
BRIEF_11_FIELDS = {
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
QUINTE_RESIDUAL_FIELDS = {
    "id",
    "severity",
    "residual_type",
    "source",
    "finding",
    "evidence_refs",
    "disposition",
    "required_closure",
    "closure_state",
    "closure_evidence",
    "scope",
}
TRIAL_PERSPECTIVE_FIELDS = {
    "party_id",
    "route_id",
    "r1_artifact",
    "r2_artifact",
    "independent_first_pass",
}


@dataclass(frozen=True)
class SeatProduct:
    dossier_path: Path
    dossier: dict[str, Any]
    run_dir: Path
    brief: dict[str, Any]
    manifest: dict[str, Any]
    result: dict[str, Any]

    @property
    def seat_id(self) -> str:
        return self.dossier["seat_id"]

    @property
    def family(self) -> str:
        return self.result["seat_binding"]["family"]

    @property
    def run_id(self) -> str:
        return self.result["run_id"]

    @property
    def result_sha256(self) -> str:
        return self.dossier["quinte_result_sha256"]

    @property
    def reviewer_profile_path(self) -> Path:
        return _resolve_under(
            self.dossier_path.parent,
            self.dossier["reviewer_profile_ref"],
            "reviewer_profile_ref",
        )

    def reviewer_profile(self) -> dict[str, Any]:
        return validate_profile(
            read_json(self.reviewer_profile_path / "profile.json"),
            self.dossier["profile_id"],
        )

    def reviewer_profile_binding(self) -> dict[str, str]:
        return {
            "profile_id": self.dossier["profile_id"],
            "profile_sha256": self.dossier["profile_sha256"],
            "profile_source_sha256": self.dossier["reviewer_profile_sha256"],
            "thesis_sha256": self.dossier["thesis_sha256"],
        }

    def anonymous_view(self, alias: str) -> dict[str, Any]:
        raw_thesis = read_json(
            _resolve_under(self.dossier_path.parent, self.dossier["thesis_ref"], "thesis_ref")
        )
        secrets = _identity_tokens(self)
        thesis = _redact(raw_thesis, secrets, alias)
        result = _redact({
            "status": self.result["status"],
            "question": self.result["question"],
            "action_scope": self.result["action_scope"],
            "affected_paths": self.result["affected_paths"],
            "summary": self.result["summary"],
            "recommendation": self.result["recommendation"],
            "dissent": self.result["dissent"],
            "residuals": [_anonymous_residual(item, alias, secrets) for item in self.result["residuals"]],
        }, secrets, alias)
        return {
            "alias": alias,
            "thesis": thesis,
            "quinte_result": result,
        }

    def adjudicator_view(self, alias: str) -> dict[str, Any]:
        view = self.anonymous_view(alias)
        return {
            **view,
            "integrity": {
                "profile_sha256": self.dossier["profile_sha256"],
                "thesis_sha256": self.dossier["thesis_sha256"],
                "quinte_result_sha256": self.result_sha256,
            },
        }


def load_seat_dossier(path: Path) -> SeatProduct:
    dossier_path = path.resolve()
    dossier = validate_dossier(read_json(dossier_path))
    root = dossier_path.parent
    profile_path = _resolve_under(root, dossier["profile_ref"], "profile_ref")
    reviewer_profile_path = _resolve_under(
        root, dossier["reviewer_profile_ref"], "reviewer_profile_ref"
    )
    thesis_path = _resolve_under(root, dossier["thesis_ref"], "thesis_ref")
    perspective_input_path = _resolve_under(
        root, dossier["perspective_input_ref"], "perspective_input_ref"
    )
    run_dir = _resolve_under(root, dossier["quinte_run_ref"], "quinte_run_ref")
    if not run_dir.is_dir():
        raise ContractError(f"dossier quinte_run_ref is not a directory: {run_dir}")
    if digest_file(profile_path) != dossier["profile_sha256"]:
        raise ContractError("dossier profile digest does not match profile artifact")
    if not reviewer_profile_path.is_dir():
        raise ContractError("dossier reviewer_profile_ref is not a directory")
    reviewer_files = [
        path.relative_to(reviewer_profile_path)
        for path in reviewer_profile_path.rglob("*")
        if path.is_file()
    ]
    if digest_tree(reviewer_profile_path, reviewer_files) != dossier["reviewer_profile_sha256"]:
        raise ContractError("dossier reviewer profile tree digest does not match artifact")
    for path in reviewer_profile_path.rglob("*"):
        if path.is_symlink():
            raise ContractError("dossier reviewer profile contains a symlink")
    composition = read_json(reviewer_profile_path / "COMPOSITION.json")
    required_composition = {
        "base_sha256",
        "composition_version",
        "overlay_sha256",
        "profile_id",
        "seat_id",
        "composed_content_sha256",
    }
    if (
        set(composition) != required_composition
        or composition.get("composition_version") != "1.0"
        or composition.get("seat_id") != dossier["seat_id"]
        or composition.get("profile_id") != dossier["profile_id"]
    ):
        raise ContractError("dossier reviewer profile composition receipt is invalid")
    composed_paths = [
        path.relative_to(reviewer_profile_path)
        for path in reviewer_profile_path.rglob("*")
        if path.is_file() and path.name != "COMPOSITION.json"
    ]
    if digest_tree(reviewer_profile_path, composed_paths) != composition.get(
        "composed_content_sha256"
    ):
        raise ContractError("dossier reviewer profile composed-content digest is invalid")
    reviewer_profile = validate_profile(
        read_json(reviewer_profile_path / "profile.json"), dossier["profile_id"]
    )
    if reviewer_profile != validate_profile(read_json(profile_path), dossier["profile_id"]):
        raise ContractError("dossier reviewer profile metadata differs from profile artifact")
    if digest_file(thesis_path) != dossier["thesis_sha256"]:
        raise ContractError("dossier thesis digest does not match thesis artifact")
    if digest_file(perspective_input_path) != dossier["perspective_input_sha256"]:
        raise ContractError("dossier perspective input digest does not match artifact")
    validate_profile(read_json(profile_path), dossier["profile_id"])
    thesis = read_json(thesis_path)
    perspective_input = read_json(perspective_input_path)
    if perspective_input.get("original_brief_sha256") != dossier["original_brief_sha256"]:
        raise ContractError("perspective input original brief digest does not match dossier")
    if perspective_input.get("profile_sha256") != dossier["profile_sha256"]:
        raise ContractError("perspective input profile digest does not match dossier")
    if perspective_input.get("thesis_sha256") != dossier["thesis_sha256"]:
        raise ContractError("perspective input thesis digest does not match dossier")
    if not isinstance(perspective_input.get("derived_context"), str) or not perspective_input[
        "derived_context"
    ].strip():
        raise ContractError("perspective input derived_context must be a non-empty string")
    validate_thesis(thesis, perspective_input.get("original_question"))

    manifest_path = run_dir / "manifest.json"
    result_path = run_dir / "result.json"
    brief_path = run_dir / "input" / "brief.json"
    if digest_file(manifest_path) != dossier["quinte_manifest_sha256"]:
        raise ContractError("dossier manifest digest does not match QUINTE manifest")
    if digest_file(result_path) != dossier["quinte_result_sha256"]:
        raise ContractError("dossier result digest does not match QUINTE result")

    manifest = read_json(manifest_path)
    result = read_json(result_path)
    brief = read_json(brief_path)
    _validate_manifest(manifest, result_path)
    _validate_result(result)
    _validate_brief(brief)
    _validate_result_evidence(result, run_dir)
    if dossier["derived_quinte_brief_sha256"] != manifest["brief_sha256"]:
        raise ContractError("dossier derived QUINTE brief digest does not match manifest")
    _validate_derived_brief(brief, perspective_input, dossier)
    _validate_dossier_mapping(dossier, root, run_dir, manifest)

    if manifest["run_id"] != result["run_id"]:
        raise ContractError("QUINTE manifest and result run_id differ")
    if manifest["brief_sha256"] != result["brief_sha256"]:
        raise ContractError("QUINTE manifest and result brief digest differ")
    if digest_bytes(_quinte_brief_bytes(brief)) != manifest["brief_sha256"]:
        raise ContractError("QUINTE brief bytes do not match manifest brief digest")
    if digest_file(result_path) != manifest["result_sha256"]:
        raise ContractError("QUINTE result does not match manifest result digest")
    policy = read_json(run_dir / "input" / "policy.json")
    snapshot = read_json(run_dir / "input" / "snapshot-manifest.json")
    if digest_bytes(quinte_json_bytes(policy)) != manifest["policy_sha256"]:
        raise ContractError("QUINTE policy does not match manifest policy digest")
    if digest_bytes(quinte_json_bytes(snapshot)) != manifest["snapshot_sha256"]:
        raise ContractError("QUINTE snapshot manifest does not match its digest binding")
    if result["question"] != brief["question"]:
        raise ContractError("QUINTE result question does not match brief")
    if result["action_scope"] != brief.get("action_scope"):
        raise ContractError("QUINTE result action_scope does not match brief")
    if result["affected_paths"] != brief.get("affected_paths", []):
        raise ContractError("QUINTE result affected_paths do not match brief")
    if result["action_binding_sha256"] != brief.get("action_binding_sha256"):
        raise ContractError("QUINTE result action binding does not match brief")
    _validate_policy(policy, manifest)
    if manifest["seat_binding"] != result["seat_binding"]:
        raise ContractError("QUINTE manifest and result seat bindings differ")
    if manifest["route_bindings"] != result["route_bindings"]:
        raise ContractError("QUINTE manifest and result route bindings differ")
    if dossier["seat_id"] != result["seat_binding"]["seat_id"]:
        raise ContractError("dossier seat_id does not match QUINTE seat binding")
    return SeatProduct(dossier_path, dossier, run_dir, brief, manifest, result)


def _validate_dossier_mapping(
    dossier: dict[str, Any], root: Path, run_dir: Path, manifest: dict[str, Any]
) -> None:
    assigned = dossier.get("assigned_evidence_refs") or []
    mapping_ref = dossier.get("evidence_mapping_ref")
    mapping_sha = dossier.get("evidence_mapping_sha256")
    if mapping_ref is None and mapping_sha is None:
        if assigned:
            raise ContractError("dossier assigned evidence lacks a mapping receipt")
        return
    mapping_path = _resolve_under(root, mapping_ref, "evidence_mapping_ref")
    if digest_file(mapping_path) != mapping_sha:
        raise ContractError("dossier evidence mapping digest does not match artifact")
    receipt = validate_mapping_receipt(read_json(mapping_path))
    if receipt["seat_id"] != dossier["seat_id"]:
        raise ContractError("evidence mapping seat_id does not match dossier")
    if receipt["assigned_evidence_refs"] != list(assigned):
        raise ContractError("evidence mapping assigned refs do not match dossier")
    if dossier.get("assignment_plan_sha256") is not None:
        if receipt["assignment_plan_sha256"] != dossier["assignment_plan_sha256"]:
            raise ContractError("evidence mapping assignment plan digest does not match dossier")
    if receipt["quinte_run_id"] != manifest["run_id"]:
        raise ContractError("evidence mapping quinte_run_id does not match QUINTE manifest")
    snapshot_path = run_dir / "input" / "snapshot-manifest.json"
    if digest_file(snapshot_path) != receipt["quinte_snapshot_manifest_sha256"]:
        raise ContractError("evidence mapping snapshot-manifest digest does not match run files")
    # Local ref must resolve under the seat dossier root when relative.
    snapshot_ref = receipt["quinte_snapshot_manifest_ref"]
    if not Path(snapshot_ref).is_absolute():
        bound = _resolve_under(root, snapshot_ref, "mapping.quinte_snapshot_manifest_ref")
        if bound.resolve() != snapshot_path.resolve():
            raise ContractError("evidence mapping snapshot-manifest ref does not resolve to run input")


def validate_trial_seats(seats: list[SeatProduct]) -> None:
    if len(seats) != 3:
        raise ContractError("MAGI requires exactly three seat dossiers")
    checks = {
        "seat IDs": [seat.seat_id for seat in seats],
        "run IDs": [seat.run_id for seat in seats],
        "families": [seat.family for seat in seats],
        "profiles": [seat.dossier["profile_sha256"] for seat in seats],
        "theses": [seat.dossier["thesis_sha256"] for seat in seats],
        "QUINTE results": [seat.result_sha256 for seat in seats],
    }
    for label, values in checks.items():
        if len(set(values)) != 3:
            raise ContractError(f"three seats must have distinct {label}")
    original_brief_digests = {seat.dossier["original_brief_sha256"] for seat in seats}
    questions = {seat.result["question"] for seat in seats}
    actions = {seat.result["action_binding_sha256"] for seat in seats}
    scopes = {seat.result["action_scope"] for seat in seats}
    affected_paths = {tuple(seat.result["affected_paths"]) for seat in seats}
    if (
        len(original_brief_digests) != 1
        or len(questions) != 1
        or len(actions) != 1
        or len(scopes) != 1
        or len(affected_paths) != 1
    ):
        raise ContractError("three seats must share one original brief, question, and action binding")


def _validate_manifest(value: dict[str, Any], result_path: Path) -> None:
    closed(value, MANIFEST_2_FIELDS, "QUINTE manifest")
    if value.get("manifest_version") != "2.0":
        raise ContractError("QUINTE manifest_version must be 2.0")
    if value.get("status") != "completed":
        raise ContractError("QUINTE manifest must be completed")
    try:
        uuid.UUID(str(value.get("run_id")))
    except ValueError as exc:
        raise ContractError("QUINTE manifest run_id must be a UUID") from exc
    for field in ("brief_sha256", "policy_sha256", "snapshot_sha256", "runtime_sha256", "result_sha256"):
        digest(value.get(field), f"QUINTE manifest.{field}")
    if value.get("error") is not None:
        raise ContractError("completed QUINTE manifest must not carry an error")
    submission = value.get("primary_arbiter_submission")
    if not isinstance(submission, dict) or submission.get("state") != "accepted":
        raise ContractError("QUINTE Primary Arbiter submission must be accepted")
    if submission.get("accepted_at") is None:
        raise ContractError("QUINTE Primary Arbiter acceptance timestamp is missing")
    challenge = value.get("primary_arbiter_challenge")
    if not isinstance(challenge, dict) or challenge.get("consumed") is not True:
        raise ContractError("QUINTE Primary Arbiter challenge must be consumed")
    input_receipt = value.get("r3_input_receipt")
    if not isinstance(input_receipt, dict):
        raise ContractError("QUINTE R3 input receipt binding is missing")
    digest(input_receipt.get("sha256"), "QUINTE manifest.r3_input_receipt.sha256")
    if input_receipt.get("artifact_ref") != "r3/input-receipt.json":
        raise ContractError("QUINTE R3 input receipt reference is invalid")
    if submission.get("input_receipt_sha256") != input_receipt["sha256"]:
        raise ContractError("QUINTE Primary Arbiter submission does not bind R3 inputs")
    seat = validate_seat_binding(value.get("seat_binding"), "QUINTE manifest.seat_binding")
    validate_route_bindings(value.get("route_bindings"), seat, "QUINTE manifest.route_bindings")


def _validate_result(value: dict[str, Any]) -> None:
    closed(value, RESULT_21_FIELDS, "QUINTE result")
    if value.get("result_version") != "2.1":
        raise ContractError("QUINTE result_version must be 2.1")
    if value.get("status") != "completed":
        raise ContractError("QUINTE result must be completed, not degraded")
    for field in ("run_id", "question", "summary", "recommendation"):
        text(value.get(field), f"QUINTE result.{field}")
    digest(value.get("brief_sha256"), "QUINTE result.brief_sha256")
    digest(value.get("action_binding_sha256"), "QUINTE result.action_binding_sha256")
    string_list(value.get("affected_paths"), "QUINTE result.affected_paths")
    string_list(value.get("dissent"), "QUINTE result.dissent")
    residuals = value.get("residuals")
    if not isinstance(residuals, list):
        raise ContractError("QUINTE result.residuals must be an array")
    seen: set[str] = set()
    for index, raw in enumerate(residuals):
        if not isinstance(raw, dict):
            raise ContractError(f"QUINTE result.residuals[{index}] must be an object")
        closed(raw, QUINTE_RESIDUAL_FIELDS, f"QUINTE result.residuals[{index}]")
        residual_id = text(raw.get("id"), f"QUINTE result.residuals[{index}].id")
        if residual_id in seen:
            raise ContractError(f"QUINTE result has duplicate residual id {residual_id}")
        seen.add(residual_id)
        if raw.get("severity") not in {"LOW", "MEDIUM", "HIGH", "CRITICAL", "P0"}:
            raise ContractError(f"QUINTE result.residuals[{index}].severity is invalid")
        if raw.get("disposition") not in DISPOSITIONS:
            raise ContractError(f"QUINTE result.residuals[{index}].disposition is invalid")
        if raw.get("closure_state") not in CLOSURE_STATES:
            raise ContractError(f"QUINTE result.residuals[{index}].closure_state is invalid")
        for field in ("residual_type", "source", "finding", "required_closure", "scope"):
            text(raw.get(field), f"QUINTE result.residuals[{index}].{field}")
        string_list(raw.get("evidence_refs"), f"QUINTE result.residuals[{index}].evidence_refs")
        string_list(raw.get("closure_evidence"), f"QUINTE result.residuals[{index}].closure_evidence")
    seat = validate_seat_binding(value.get("seat_binding"), "QUINTE result.seat_binding")
    validate_route_bindings(value.get("route_bindings"), seat, "QUINTE result.route_bindings")
    _validate_quinte_trial_manifest(value.get("trial_manifest"), value["route_bindings"])


def _validate_brief(value: dict[str, Any]) -> None:
    unknown = sorted(set(value) - BRIEF_11_FIELDS)
    if unknown:
        raise ContractError(f"QUINTE brief has unknown fields: {', '.join(unknown)}")
    if value.get("brief_version") != "1.1":
        raise ContractError("QUINTE brief_version must be 1.1")
    text(value.get("question"), "QUINTE brief.question")
    digest(value.get("action_binding_sha256"), "QUINTE brief.action_binding_sha256")


def _validate_quinte_trial_manifest(
    value: Any, route_bindings: list[dict[str, Any]]
) -> None:
    if not isinstance(value, dict):
        raise ContractError("QUINTE result.trial_manifest must be an object")
    fields = {
        "manifest_version",
        "base_model_relation",
        "perspective_count",
        "perspectives",
        "perturbation_axes",
        "independence_controls",
        "contamination_risks",
        "wall_time_seconds",
    }
    closed(value, fields, "QUINTE result.trial_manifest")
    if value.get("manifest_version") != "1.0":
        raise ContractError("QUINTE trial manifest version must be 1.0")
    if value.get("base_model_relation") != "same_model":
        raise ContractError("QUINTE inner trial manifest must disclose same_model relation")
    if value.get("perspective_count") != 5:
        raise ContractError("QUINTE trial manifest must disclose five perspectives")
    perspectives = value.get("perspectives")
    if not isinstance(perspectives, list) or len(perspectives) != 5:
        raise ContractError("QUINTE trial manifest must contain five perspectives")
    for index, item in enumerate(perspectives):
        if not isinstance(item, dict):
            raise ContractError(f"QUINTE trial manifest perspective {index} must be an object")
        closed(item, TRIAL_PERSPECTIVE_FIELDS, f"QUINTE trial manifest perspective {index}")
        if item.get("party_id") != ROUTE_PARTIES[index]:
            raise ContractError("QUINTE trial manifest must use fixed Party A-E order")
        if item.get("route_id") != route_bindings[index]["route_id"]:
            raise ContractError("QUINTE trial manifest perspective route does not match route bindings")
        for field in ("r1_artifact", "r2_artifact"):
            text(item.get(field), f"QUINTE trial manifest perspective {index}.{field}")
        if item.get("independent_first_pass") is not True:
            raise ContractError("every QUINTE perspective must disclose independent_first_pass=true")
    for field in ("perturbation_axes", "independence_controls", "contamination_risks"):
        string_list(value.get(field), f"QUINTE result.trial_manifest.{field}")
    wall_time = value.get("wall_time_seconds")
    if wall_time is not None and (not isinstance(wall_time, int) or isinstance(wall_time, bool) or wall_time < 0):
        raise ContractError("QUINTE trial manifest wall_time_seconds is invalid")


def _validate_policy(policy: dict[str, Any], manifest: dict[str, Any]) -> None:
    fields = {
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
    closed(policy, fields, "QUINTE policy")
    if policy.get("policy_version") != "2.0":
        raise ContractError("QUINTE policy_version must be 2.0")
    if policy.get("auto_primary_arbiter") is not True:
        raise ContractError("MAGI requires QUINTE auto_primary_arbiter=true for headless execution")
    seat = validate_seat_binding(policy.get("seat"), "QUINTE policy.seat")
    if seat != manifest["seat_binding"]:
        raise ContractError("QUINTE policy seat binding does not match manifest")
    if policy.get("text_model") != seat["text_model"] or policy.get(
        "multimodal_model"
    ) != seat["multimodal_model"]:
        raise ContractError("QUINTE policy model aliases do not match seat binding")
    roster = policy.get("roster")
    if not isinstance(roster, list) or len(roster) != 5:
        raise ContractError("QUINTE policy must contain exactly five roster routes")
    routes = [*roster, policy.get("counterpart_arbiter"), policy.get("primary_arbiter")]
    normalized: list[dict[str, Any]] = []
    route_fields = ROUTE_BINDING_FIELDS | {"required"}
    for index, raw in enumerate(routes):
        if not isinstance(raw, dict):
            raise ContractError(f"QUINTE policy route {index} must be an object")
        closed(raw, route_fields, f"QUINTE policy route {index}")
        if raw.get("required") is not True:
            raise ContractError(f"QUINTE policy route {index} must be required")
        normalized.append({key: raw[key] for key in ROUTE_BINDING_FIELDS})
    validate_route_bindings(normalized, seat, "QUINTE policy route bindings")
    if normalized != manifest["route_bindings"]:
        raise ContractError("QUINTE policy route bindings do not match manifest")


def _validate_result_evidence(result: dict[str, Any], run_dir: Path) -> None:
    snapshot = read_json(run_dir / "input" / "snapshot-manifest.json")
    entries = snapshot.get("entries")
    if not isinstance(entries, list):
        raise ContractError("QUINTE snapshot manifest entries must be an array")
    valid_refs: set[str] = set()
    for index, entry in enumerate(entries):
        if not isinstance(entry, dict):
            raise ContractError(f"QUINTE snapshot entry {index} must be an object")
        reference = entry.get("snapshot_ref")
        expected = entry.get("sha256")
        if not isinstance(reference, str) or not reference.startswith("snapshot://"):
            raise ContractError(f"QUINTE snapshot entry {index} has invalid reference")
        digest(expected, f"QUINTE snapshot entry {index}.sha256")
        relative = reference.removeprefix("snapshot://")
        target = (run_dir / "input" / "snapshot" / relative).resolve()
        snapshot_root = (run_dir / "input" / "snapshot").resolve()
        if target != snapshot_root and snapshot_root not in target.parents:
            raise ContractError(f"QUINTE snapshot entry {index} escapes snapshot root")
        if digest_file(target) != expected:
            raise ContractError(f"QUINTE snapshot artifact digest mismatch: {reference}")
        valid_refs.add(reference)
    for index, residual in enumerate(result["residuals"]):
        for reference in residual["evidence_refs"] + residual["closure_evidence"]:
            if reference and reference not in valid_refs:
                raise ContractError(
                    f"QUINTE result residual {index} has invalid evidence ref {reference}"
                )


def _validate_derived_brief(
    brief: dict[str, Any], perspective_input: dict[str, Any], dossier: dict[str, Any]
) -> None:
    fields = {
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
    closed(perspective_input, fields, "perspective input")
    if perspective_input.get("perspective_input_version") != "1.0":
        raise ContractError("perspective input version must be 1.0")
    expected = {
        "seat_id": dossier["seat_id"],
        "original_brief_sha256": dossier["original_brief_sha256"],
        "profile_id": dossier["profile_id"],
        "profile_sha256": dossier["profile_sha256"],
        "thesis_sha256": dossier["thesis_sha256"],
        "original_question": brief["question"],
        "action_scope": brief.get("action_scope"),
        "affected_paths": brief.get("affected_paths", []),
        "action_binding_sha256": brief.get("action_binding_sha256"),
        "derived_context": brief.get("context"),
    }
    for field, expected_value in expected.items():
        if perspective_input.get(field) != expected_value:
            raise ContractError(f"derived QUINTE brief does not match perspective input field {field}")


def _resolve_under(root: Path, reference: str, label: str) -> Path:
    ref = Path(reference)
    candidate = (root / ref).resolve() if not ref.is_absolute() else ref.resolve()
    if candidate != root and root not in candidate.parents:
        raise ContractError(f"{label} escapes the dossier directory")
    return candidate


def _quinte_brief_bytes(brief: dict[str, Any]) -> bytes:
    field_order = (
        "brief_version",
        "question",
        "context",
        "evidence_roots",
        "snapshot_ignore",
        "attachments",
        "action_scope",
        "affected_paths",
        "action_binding_sha256",
    )
    ordered = {field: brief[field] for field in field_order if field in brief}
    return quinte_json_bytes(ordered)


def _identity_tokens(seat: SeatProduct) -> set[str]:
    binding = seat.result["seat_binding"]
    tokens = {
        seat.seat_id,
        seat.dossier["profile_id"],
        binding["family"],
        binding["provider"],
        binding["text_model"],
        binding["multimodal_model"],
    }
    for route in seat.result["route_bindings"]:
        tokens.update((route["route_id"], route["adapter"], route["executable"]))
    return {token for token in tokens if token}


def _redact(value: Any, secrets: set[str], alias: str) -> Any:
    if isinstance(value, dict):
        return {key: _redact(item, secrets, alias) for key, item in value.items()}
    if isinstance(value, list):
        return [_redact(item, secrets, alias) for item in value]
    if isinstance(value, str):
        redacted = value
        for secret in sorted(secrets, key=len, reverse=True):
            # Treat identifiers as whole tokens so a short model name cannot
            # corrupt unrelated prose while still redacting case variants.
            pattern = rf"(?<![\w]){re.escape(secret)}(?![\w])"
            redacted = re.sub(pattern, alias, redacted, flags=re.IGNORECASE)
        return redacted
    return value


def _anonymous_residual(
    residual: dict[str, Any], alias: str, secrets: set[str]
) -> dict[str, Any]:
    redacted = _redact(residual, secrets, alias)
    redacted["source"] = alias
    redacted["evidence_refs"] = [
        f"seat:{alias}:evidence:{reference}" for reference in residual["evidence_refs"]
    ]
    redacted["closure_evidence"] = [
        f"seat:{alias}:evidence:{reference}" for reference in residual["closure_evidence"]
    ]
    return redacted
