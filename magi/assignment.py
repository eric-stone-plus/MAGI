"""Frozen task-focus and evidence-exposure plans for three immutable seats."""

from __future__ import annotations

from typing import Any

from .errors import ContractError
from .io import digest_value


PLAN_FIELDS = {
    "assignment_plan_version",
    "trial_id",
    "objective",
    "global_checks",
    "seats",
    "cross_review_obligations",
    "finale_condition",
    "limitations",
    "plan_binding_sha256",
}
SEAT_FIELDS = {
    "seat_id",
    "family",
    "provider",
    "text_model",
    "multimodal_model",
    "profile_id",
    "profile_source_sha256",
    "container_service",
    "image_digest",
    "primary_focus",
    "mandatory_global_checks",
    "evidence_refs",
    "carrier_capabilities",
    "cost_rationale",
    "independence_class",
    "limitations",
}
CARRIER_FIELDS = {
    "carrier_id",
    "snapshot_media_classes",
    "multimodal_media_types",
    "allow_sampled_video",
}
REVIEW_FIELDS = {
    "reviewer_seat_id",
    "subject_seat_id",
    "review_kind",
    "required_checks",
    "evidence_refs",
    "limitations",
}
FINALE_FIELDS = {
    "allowed_outcomes",
    "material_residual_states",
    "required_receipts",
    "stop_rule",
}


def validate_assignment_plan(value: Any) -> dict[str, Any]:
    plan = _object(value, "assignment plan")
    _closed(plan, PLAN_FIELDS, "assignment plan")
    if plan.get("assignment_plan_version") != "1.0":
        raise ContractError("assignment plan version must be 1.0")
    for field in ("trial_id", "objective"):
        _text(plan.get(field), f"assignment plan.{field}")
    global_checks = _strings(plan.get("global_checks"), "assignment plan.global_checks", True)
    seats = plan.get("seats")
    if not isinstance(seats, list) or len(seats) != 3:
        raise ContractError("assignment plan must contain exactly three seats")
    seat_ids: set[str] = set()
    families: set[str] = set()
    profiles: set[str] = set()
    services: set[str] = set()
    for index, raw in enumerate(seats):
        label = f"assignment plan.seats[{index}]"
        seat = _object(raw, label)
        _closed(seat, SEAT_FIELDS, label)
        for field in (
            "seat_id", "family", "provider", "text_model", "multimodal_model",
            "profile_id", "container_service", "cost_rationale", "independence_class",
        ):
            _text(seat.get(field), f"{label}.{field}")
        _digest(seat.get("profile_source_sha256"), f"{label}.profile_source_sha256")
        _digest(seat.get("image_digest"), f"{label}.image_digest")
        focus = _strings(seat.get("primary_focus"), f"{label}.primary_focus", True)
        checks = _strings(
            seat.get("mandatory_global_checks"),
            f"{label}.mandatory_global_checks",
            True,
        )
        if checks != global_checks:
            raise ContractError(
                f"{label}.mandatory_global_checks must copy the complete global check set"
            )
        if set(focus) & set(checks):
            raise ContractError(f"{label}.primary_focus must add emphasis, not duplicate checks")
        _strings(seat.get("evidence_refs"), f"{label}.evidence_refs")
        _strings(seat.get("limitations"), f"{label}.limitations")
        carrier = _object(seat.get("carrier_capabilities"), f"{label}.carrier_capabilities")
        _closed(carrier, CARRIER_FIELDS, f"{label}.carrier_capabilities")
        _text(carrier.get("carrier_id"), f"{label}.carrier_capabilities.carrier_id")
        _strings(
            carrier.get("snapshot_media_classes"),
            f"{label}.carrier_capabilities.snapshot_media_classes",
        )
        _strings(
            carrier.get("multimodal_media_types"),
            f"{label}.carrier_capabilities.multimodal_media_types",
        )
        if not isinstance(carrier.get("allow_sampled_video"), bool):
            raise ContractError(f"{label}.carrier_capabilities.allow_sampled_video must be boolean")
        seat_ids.add(seat["seat_id"])
        families.add(seat["family"])
        profiles.add(seat["profile_source_sha256"])
        services.add(seat["container_service"])
    if any(len(values) != 3 for values in (seat_ids, families, profiles, services)):
        raise ContractError(
            "assignment plan must bind three distinct seats, families, profiles, and containers"
        )
    reviews = plan.get("cross_review_obligations")
    if not isinstance(reviews, list) or len(reviews) != 6:
        raise ContractError("assignment plan must contain six directed cross-review obligations")
    pairs: set[tuple[str, str]] = set()
    for index, raw in enumerate(reviews):
        label = f"assignment plan.cross_review_obligations[{index}]"
        review = _object(raw, label)
        _closed(review, REVIEW_FIELDS, label)
        reviewer = _text(review.get("reviewer_seat_id"), f"{label}.reviewer_seat_id")
        subject = _text(review.get("subject_seat_id"), f"{label}.subject_seat_id")
        if reviewer not in seat_ids or subject not in seat_ids or reviewer == subject:
            raise ContractError(f"{label} has an invalid directed seat pair")
        pairs.add((reviewer, subject))
        kind = _text(review.get("review_kind"), f"{label}.review_kind")
        if kind not in {"artifact_review", "evidence_review", "author_consistency_review"}:
            raise ContractError(f"{label}.review_kind is invalid")
        _strings(review.get("required_checks"), f"{label}.required_checks", True)
        evidence_refs = _strings(review.get("evidence_refs"), f"{label}.evidence_refs")
        _strings(review.get("limitations"), f"{label}.limitations")
        if kind == "artifact_review" and evidence_refs:
            raise ContractError(f"{label} artifact review must not claim original-evidence exposure")
    expected_pairs = {(left, right) for left in seat_ids for right in seat_ids if left != right}
    if pairs != expected_pairs:
        raise ContractError("assignment plan must cover every directed cross-review pair exactly once")
    finale = _object(plan.get("finale_condition"), "assignment plan.finale_condition")
    _closed(finale, FINALE_FIELDS, "assignment plan.finale_condition")
    if _strings(finale.get("allowed_outcomes"), "finale.allowed_outcomes", True) != [
        "BLOCK", "ESCALATE", "PASS"
    ]:
        raise ContractError("Finale allowed outcomes must be the sorted closed decision set")
    if _strings(
        finale.get("material_residual_states"), "finale.material_residual_states", True
    ) != ["bounded_escalation", "closed", "falsified"]:
        raise ContractError("Finale material residual states are invalid")
    _strings(finale.get("required_receipts"), "finale.required_receipts", True)
    _text(finale.get("stop_rule"), "finale.stop_rule")
    _strings(plan.get("limitations"), "assignment plan.limitations", True)
    _digest(plan.get("plan_binding_sha256"), "assignment plan.plan_binding_sha256")
    expected = digest_value(
        {key: item for key, item in plan.items() if key != "plan_binding_sha256"}
    )
    if plan["plan_binding_sha256"] != expected:
        raise ContractError("assignment plan binding digest does not match")
    return plan


def bind_assignment_plan(value: dict[str, Any]) -> dict[str, Any]:
    plan = dict(value)
    plan["plan_binding_sha256"] = ""
    plan["plan_binding_sha256"] = digest_value(
        {key: item for key, item in plan.items() if key != "plan_binding_sha256"}
    )
    return validate_assignment_plan(plan)


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    return value


def _closed(value: dict[str, Any], fields: set[str], label: str) -> None:
    if set(value) != fields:
        raise ContractError(f"{label} has a closed-field mismatch")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty string")
    return value


def _strings(value: Any, label: str, nonempty: bool = False) -> list[str]:
    if (
        not isinstance(value, list)
        or (nonempty and not value)
        or not all(isinstance(item, str) and item.strip() for item in value)
        or value != sorted(set(value))
    ):
        raise ContractError(f"{label} must be a sorted unique string array")
    return value


def _digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 71 or not value.startswith("sha256:"):
        raise ContractError(f"{label} must be a sha256 digest")
    try:
        int(value[7:], 16)
    except ValueError as exc:
        raise ContractError(f"{label} must be a sha256 digest") from exc
    return value
