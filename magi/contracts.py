"""Closed production contracts for MAGI 0.2.0 artifacts."""

from __future__ import annotations

import re
from typing import Any

from .errors import ContractError
from .io import digest_value


DIGEST = re.compile(r"^sha256:[a-f0-9]{64}$")
SEVERITIES = {"LOW", "MEDIUM", "HIGH", "CRITICAL", "P0"}
HIGH_RISK = {"HIGH", "CRITICAL", "P0"}
DECISIONS = {"PASS", "BLOCK", "ESCALATE"}
HIGHBALL_TYPES = {
    "contradiction",
    "omission",
    "evidence_gap",
    "confidence_mismatch",
    "drift",
    "execution_mismatch",
    "silent_collapse",
}
DISPOSITIONS = {"verified", "falsified", "unresolved", "escalated", "discarded"}
CLOSURE_STATES = {"open", "closed", "blocked", "waived", "not_applicable"}
REQUIRED_CLOSURES = {"none", "edit", "test", "command", "block", "waiver", "human_review"}
ROUTE_PARTIES = (
    "Party A",
    "Party B",
    "Party C",
    "Party D",
    "Party E",
    "Counterpart Arbiter",
    "Primary Arbiter",
)

SEAT_BINDING_FIELDS = {
    "seat_id",
    "family",
    "provider",
    "text_model",
    "multimodal_model",
}
ROUTE_BINDING_FIELDS = {
    "party_id",
    "route_id",
    "adapter",
    "executable",
    "family",
    "provider",
    "text_model",
    "multimodal_model",
    "perspective",
}
DOSSIER_FIELDS = {
    "dossier_version",
    "seat_id",
    "profile_id",
    "profile_ref",
    "profile_sha256",
    "reviewer_profile_ref",
    "reviewer_profile_sha256",
    "thesis_ref",
    "thesis_sha256",
    "perspective_input_ref",
    "perspective_input_sha256",
    "original_brief_sha256",
    "derived_quinte_brief_sha256",
    "quinte_run_ref",
    "quinte_manifest_sha256",
    "quinte_result_sha256",
    # Evidence assignment / MAGI↔QUINTE mapping (nullable when no staged evidence plan).
    "assignment_plan_sha256",
    "assigned_evidence_refs",
    "evidence_mapping_ref",
    "evidence_mapping_sha256",
}
REVIEW_FINDING_FIELDS = {
    "id",
    "severity",
    "type",
    "finding",
    "evidence_refs",
    "disposition",
    "required_closure",
    "closure_state",
    "closure_evidence",
    "scope",
    "source_refs",
}
REVIEW_FIELDS = {
    "review_version",
    "reviewer_alias",
    "subject_alias",
    "reviewer_profile_binding",
    "methodology_trace",
    "summary",
    "findings",
    "dissent",
}
REVIEW_PROFILE_BINDING_FIELDS = {
    "profile_id",
    "profile_sha256",
    "profile_source_sha256",
    "thesis_sha256",
}
METHODOLOGY_TRACE_FIELDS = {"kind", "method", "application"}
FINAL_FIELDS = {
    "verdict_version",
    "decision",
    "summary",
    "recommendation",
    "findings",
    "dissent",
}
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
THESIS_CLAIM_FIELDS = {"id", "statement", "evidence_refs", "uncertainty", "boundary"}
PRODUCT_FIELDS = {
    "product_version",
    "product_sha256",
    "trial_id",
    "status",
    "runtime_sha256",
    "agent_config_sha256",
    "builder_config_sha256",
    "assignment_plan_ref",
    "assignment_plan_sha256",
    "evidence_manifest_ref",
    "evidence_manifest_sha256",
    "evidence_coverage_ref",
    "evidence_coverage_sha256",
    "original_brief_sha256",
    "action_binding_sha256",
    "question",
    "action_scope",
    "affected_paths",
    "final_decision",
    "final_dissent",
    "final_verdict_ref",
    "final_verdict_sha256",
    "residual_trace_ref",
    "residual_trace_sha256",
    "residual_reduction_ref",
    "residual_reduction_sha256",
    "seats",
    "cross_reviews",
    "final_adjudicator",
}
PRODUCT_SEAT_FIELDS = {
    "seat_id",
    "family",
    "provider",
    "text_model",
    "multimodal_model",
    "profile_sha256",
    "thesis_sha256",
    "dossier_ref",
    "dossier_sha256",
    "quinte_run_id",
    "quinte_manifest_sha256",
    "quinte_result_sha256",
    "assigned_evidence_refs",
    "evidence_mapping_ref",
    "evidence_mapping_sha256",
}
PRODUCT_REVIEW_FIELDS = {
    "artifact_ref",
    "sha256",
    "reviewer_seat_id",
    "reviewer_family",
    "reviewer_provider",
    "reviewer_text_model",
    "reviewer_multimodal_model",
    "reviewer_profile_id",
    "reviewer_profile_sha256",
    "reviewer_profile_source_sha256",
    "reviewer_agent_config_sha256",
    "methodology_trace_sha256",
    "reviewer_execution_receipt_ref",
    "reviewer_execution_receipt_sha256",
}
PRODUCT_FINAL_ADJUDICATOR_FIELDS = {
    "family",
    "provider",
    "text_model",
    "multimodal_model",
    "agent_config_sha256",
    "execution_mode",
    "execution_receipt_ref",
    "execution_receipt_sha256",
}

RESIDUAL_REDUCTION_FIELDS = {
    "receipt_version",
    "metric_scope",
    "baseline_scope",
    "seat_residual_source_refs",
    "cross_review_source_refs",
    "cross_review_novel_source_refs",
    "cross_review_linked_source_refs",
    "challenged_seat_source_refs",
    "final_represented_source_refs",
    "final_falsified_or_discarded_source_refs",
    "final_finding_ids",
    "final_unresolved_finding_ids",
    "counts",
    "limitations",
    "binding_sha256",
}
RESIDUAL_REDUCTION_COUNT_FIELDS = {
    "seat_residuals",
    "cross_review_findings",
    "cross_review_novel_findings",
    "cross_review_linked_findings",
    "challenged_seat_residuals",
    "final_represented_sources",
    "final_falsified_or_discarded_sources",
    "final_findings",
    "final_unresolved_findings",
}


def require_object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    return value


def closed(value: dict[str, Any], fields: set[str], label: str) -> None:
    unknown = sorted(set(value) - fields)
    missing = sorted(fields - set(value))
    if unknown:
        raise ContractError(f"{label} has unknown fields: {', '.join(unknown)}")
    if missing:
        raise ContractError(f"{label} is missing fields: {', '.join(missing)}")


def text(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty string")
    return value


def digest(value: Any, label: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or DIGEST.fullmatch(value) is None:
        raise ContractError(f"{label} must be a sha256 digest")
    return value


def string_list(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if not isinstance(value, list) or (nonempty and not value) or not all(isinstance(x, str) for x in value):
        requirement = "non-empty " if nonempty else ""
        raise ContractError(f"{label} must be a {requirement}string array")
    return value


def validate_seat_binding(value: Any, label: str) -> dict[str, Any]:
    binding = require_object(value, label)
    closed(binding, SEAT_BINDING_FIELDS, label)
    for field in SEAT_BINDING_FIELDS:
        text(binding.get(field), f"{label}.{field}")
    return binding


def validate_route_bindings(value: Any, seat: dict[str, Any], label: str) -> list[dict[str, Any]]:
    if not isinstance(value, list) or len(value) != 7:
        raise ContractError(f"{label} must contain exactly seven route bindings")
    route_ids: set[str] = set()
    for index, raw in enumerate(value):
        route = require_object(raw, f"{label}[{index}]")
        closed(route, ROUTE_BINDING_FIELDS, f"{label}[{index}]")
        party = text(route.get("party_id"), f"{label}[{index}].party_id")
        if party != ROUTE_PARTIES[index]:
            raise ContractError(f"{label} must use the fixed seven-route order")
        for field in ("route_id", "adapter", "executable"):
            text(route.get(field), f"{label}[{index}].{field}")
        if route["route_id"] in route_ids:
            raise ContractError(f"{label} must use seven distinct route IDs")
        route_ids.add(route["route_id"])
        if not isinstance(route.get("perspective"), str):
            raise ContractError(f"{label}[{index}].perspective must be a string")
        for field in ("family", "provider", "text_model", "multimodal_model"):
            text(route.get(field), f"{label}[{index}].{field}")
            if route[field] != seat[field]:
                raise ContractError(f"{label}[{index}].{field} does not match seat binding")
    return value


def validate_dossier(value: Any) -> dict[str, Any]:
    dossier = require_object(value, "dossier")
    closed(dossier, DOSSIER_FIELDS, "dossier")
    if dossier.get("dossier_version") != "1.0":
        raise ContractError("dossier.dossier_version must be 1.0")
    for field in (
        "seat_id",
        "profile_id",
        "profile_ref",
        "reviewer_profile_ref",
        "thesis_ref",
        "perspective_input_ref",
        "quinte_run_ref",
    ):
        text(dossier.get(field), f"dossier.{field}")
    for field in (
        "profile_sha256",
        "reviewer_profile_sha256",
        "thesis_sha256",
        "perspective_input_sha256",
        "original_brief_sha256",
        "derived_quinte_brief_sha256",
        "quinte_manifest_sha256",
        "quinte_result_sha256",
    ):
        digest(dossier.get(field), f"dossier.{field}")
    digest(dossier.get("assignment_plan_sha256"), "dossier.assignment_plan_sha256", nullable=True)
    assigned = string_list(
        dossier.get("assigned_evidence_refs"), "dossier.assigned_evidence_refs"
    )
    mapping_ref = dossier.get("evidence_mapping_ref")
    mapping_sha = dossier.get("evidence_mapping_sha256")
    if mapping_ref is None and mapping_sha is None:
        # No mapping artifact is allowed only when no original evidence was assigned.
        if assigned:
            raise ContractError(
                "dossier with assigned evidence must bind an evidence mapping receipt"
            )
    else:
        text(mapping_ref, "dossier.evidence_mapping_ref")
        digest(mapping_sha, "dossier.evidence_mapping_sha256")
    return dossier


def validate_profile(value: Any, expected_id: str | None = None) -> dict[str, Any]:
    profile = require_object(value, "profile")
    closed(profile, PROFILE_FIELDS, "profile")
    if profile.get("profile_version") != "1.0":
        raise ContractError("profile.profile_version must be 1.0")
    for field in ("profile_id", "discipline", "epistemic_lens", "instructions"):
        text(profile.get(field), f"profile.{field}")
    string_list(profile.get("methods"), "profile.methods", nonempty=True)
    string_list(profile.get("failure_checks"), "profile.failure_checks", nonempty=True)
    if expected_id is not None and profile["profile_id"] != expected_id:
        raise ContractError("profile.profile_id does not match dossier")
    return profile


def validate_thesis(value: Any, question: str | None = None) -> dict[str, Any]:
    thesis = require_object(value, "thesis")
    closed(thesis, THESIS_FIELDS, "thesis")
    if thesis.get("thesis_version") != "1.0":
        raise ContractError("thesis.thesis_version must be 1.0")
    for field in ("question", "thesis", "recommendation"):
        text(thesis.get(field), f"thesis.{field}")
    if question is not None and thesis["question"] != question:
        raise ContractError("thesis question does not match original question")
    string_list(thesis.get("limitations"), "thesis.limitations")
    claims = thesis.get("claims")
    if not isinstance(claims, list) or not claims:
        raise ContractError("thesis.claims must be a non-empty array")
    seen: set[str] = set()
    for index, raw in enumerate(claims):
        claim = require_object(raw, f"thesis.claims[{index}]")
        closed(claim, THESIS_CLAIM_FIELDS, f"thesis.claims[{index}]")
        claim_id = text(claim.get("id"), f"thesis.claims[{index}].id")
        if claim_id in seen:
            raise ContractError(f"thesis has duplicate claim id {claim_id}")
        seen.add(claim_id)
        for field in ("statement", "uncertainty", "boundary"):
            text(claim.get(field), f"thesis.claims[{index}].{field}")
        string_list(claim.get("evidence_refs"), f"thesis.claims[{index}].evidence_refs")
    return thesis


def validate_finding(value: Any, label: str) -> dict[str, Any]:
    finding = require_object(value, label)
    closed(finding, REVIEW_FINDING_FIELDS, label)
    text(finding.get("id"), f"{label}.id")
    if finding.get("severity") not in SEVERITIES:
        raise ContractError(f"{label}.severity is invalid")
    if finding.get("type") not in HIGHBALL_TYPES:
        raise ContractError(f"{label}.type is invalid")
    text(finding.get("finding"), f"{label}.finding")
    string_list(finding.get("evidence_refs"), f"{label}.evidence_refs")
    string_list(finding.get("source_refs"), f"{label}.source_refs", nonempty=True)
    if finding.get("disposition") not in DISPOSITIONS:
        raise ContractError(f"{label}.disposition is invalid")
    if finding.get("required_closure") not in REQUIRED_CLOSURES:
        raise ContractError(f"{label}.required_closure is invalid")
    if finding.get("closure_state") not in CLOSURE_STATES:
        raise ContractError(f"{label}.closure_state is invalid")
    string_list(finding.get("closure_evidence"), f"{label}.closure_evidence")
    if not isinstance(finding.get("scope"), str):
        raise ContractError(f"{label}.scope must be a string")
    return finding


def validate_review(
    value: Any,
    reviewer: str,
    subject: str,
    *,
    expected_profile_binding: dict[str, str] | None = None,
    profile: dict[str, Any] | None = None,
) -> dict[str, Any]:
    review = require_object(value, "cross-review")
    closed(review, REVIEW_FIELDS, "cross-review")
    if review.get("review_version") != "1.1":
        raise ContractError("cross-review.review_version must be 1.1")
    if review.get("reviewer_alias") != reviewer or review.get("subject_alias") != subject:
        raise ContractError("cross-review aliases do not match the assigned anonymous packet")
    binding = require_object(
        review.get("reviewer_profile_binding"), "cross-review.reviewer_profile_binding"
    )
    closed(
        binding,
        REVIEW_PROFILE_BINDING_FIELDS,
        "cross-review.reviewer_profile_binding",
    )
    text(binding.get("profile_id"), "cross-review.reviewer_profile_binding.profile_id")
    for field in ("profile_sha256", "profile_source_sha256", "thesis_sha256"):
        digest(binding.get(field), f"cross-review.reviewer_profile_binding.{field}")
    if expected_profile_binding is not None and binding != expected_profile_binding:
        raise ContractError("cross-review reviewer profile binding does not match assigned seat")

    methodology = review.get("methodology_trace")
    if not isinstance(methodology, list) or not methodology:
        raise ContractError("cross-review.methodology_trace must be a non-empty array")
    seen_methodology: set[tuple[str, str]] = set()
    kinds: set[str] = set()
    allowed: dict[str, set[str]] | None = None
    if profile is not None:
        allowed = {
            "method": set(string_list(profile.get("methods"), "profile.methods", nonempty=True)),
            "failure_check": set(
                string_list(profile.get("failure_checks"), "profile.failure_checks", nonempty=True)
            ),
        }
    for index, raw in enumerate(methodology):
        item = require_object(raw, f"cross-review.methodology_trace[{index}]")
        closed(item, METHODOLOGY_TRACE_FIELDS, f"cross-review.methodology_trace[{index}]")
        kind = item.get("kind")
        if kind not in {"method", "failure_check"}:
            raise ContractError(
                f"cross-review.methodology_trace[{index}].kind is invalid"
            )
        method = text(item.get("method"), f"cross-review.methodology_trace[{index}].method")
        text(item.get("application"), f"cross-review.methodology_trace[{index}].application")
        identity = (kind, method)
        if identity in seen_methodology:
            raise ContractError("cross-review.methodology_trace contains duplicates")
        seen_methodology.add(identity)
        kinds.add(kind)
        if allowed is not None and method not in allowed[kind]:
            raise ContractError(
                "cross-review methodology is not declared by the assigned reviewer profile"
            )
    if kinds != {"method", "failure_check"}:
        raise ContractError(
            "cross-review.methodology_trace must apply a method and a failure check"
        )

    text(review.get("summary"), "cross-review.summary")
    findings = review.get("findings")
    if not isinstance(findings, list):
        raise ContractError("cross-review.findings must be an array")
    seen: set[str] = set()
    for index, finding in enumerate(findings):
        validate_finding(finding, f"cross-review.findings[{index}]")
        if finding["id"] in seen:
            raise ContractError(f"cross-review contains duplicate finding id {finding['id']}")
        seen.add(finding["id"])
    string_list(review.get("dissent"), "cross-review.dissent")
    return review


def validate_final(value: Any) -> dict[str, Any]:
    verdict = require_object(value, "final verdict")
    closed(verdict, FINAL_FIELDS, "final verdict")
    if verdict.get("verdict_version") != "1.0":
        raise ContractError("final verdict.verdict_version must be 1.0")
    if verdict.get("decision") not in DECISIONS:
        raise ContractError("final verdict.decision is invalid")
    for field in ("summary", "recommendation"):
        text(verdict.get(field), f"final verdict.{field}")
    findings = verdict.get("findings")
    if not isinstance(findings, list):
        raise ContractError("final verdict.findings must be an array")
    seen: set[str] = set()
    for index, finding in enumerate(findings):
        validate_finding(finding, f"final verdict.findings[{index}]")
        if finding["id"] in seen:
            raise ContractError(f"final verdict contains duplicate finding id {finding['id']}")
        seen.add(finding["id"])
    string_list(verdict.get("dissent"), "final verdict.dissent")
    return verdict


def validate_residual_reduction_receipt(value: Any) -> dict[str, Any]:
    receipt = require_object(value, "residual-reduction receipt")
    closed(receipt, RESIDUAL_REDUCTION_FIELDS, "residual-reduction receipt")
    if receipt.get("receipt_version") != "1.0":
        raise ContractError("residual-reduction receipt version must be 1.0")
    for field in ("metric_scope", "baseline_scope"):
        text(receipt.get(field), f"residual-reduction receipt.{field}")
    reference_fields = (
        "seat_residual_source_refs",
        "cross_review_source_refs",
        "cross_review_novel_source_refs",
        "cross_review_linked_source_refs",
        "challenged_seat_source_refs",
        "final_represented_source_refs",
        "final_falsified_or_discarded_source_refs",
        "final_finding_ids",
        "final_unresolved_finding_ids",
    )
    for field in reference_fields:
        values = string_list(receipt.get(field), f"residual-reduction receipt.{field}")
        if values != sorted(set(values)):
            raise ContractError(
                f"residual-reduction receipt.{field} must be sorted and unique"
            )
    limitations = string_list(
        receipt.get("limitations"),
        "residual-reduction receipt.limitations",
        nonempty=True,
    )
    if not any("error rate" in item.lower() for item in limitations):
        raise ContractError(
            "residual-reduction receipt must state that it does not measure true error rate"
        )
    counts = require_object(receipt.get("counts"), "residual-reduction receipt.counts")
    closed(counts, RESIDUAL_REDUCTION_COUNT_FIELDS, "residual-reduction receipt.counts")
    if any(
        not isinstance(value, int) or isinstance(value, bool) or value < 0
        for value in counts.values()
    ):
        raise ContractError(
            "residual-reduction receipt counts must be non-negative integers"
        )
    expected_counts = {
        "seat_residuals": len(receipt["seat_residual_source_refs"]),
        "cross_review_findings": len(receipt["cross_review_source_refs"]),
        "cross_review_novel_findings": len(receipt["cross_review_novel_source_refs"]),
        "cross_review_linked_findings": len(receipt["cross_review_linked_source_refs"]),
        "challenged_seat_residuals": len(receipt["challenged_seat_source_refs"]),
        "final_represented_sources": len(receipt["final_represented_source_refs"]),
        "final_falsified_or_discarded_sources": len(
            receipt["final_falsified_or_discarded_source_refs"]
        ),
        "final_findings": len(receipt["final_finding_ids"]),
        "final_unresolved_findings": len(receipt["final_unresolved_finding_ids"]),
    }
    if counts != expected_counts:
        raise ContractError("residual-reduction receipt counts do not match its source lists")
    seat_refs = set(receipt["seat_residual_source_refs"])
    review_refs = set(receipt["cross_review_source_refs"])
    novel_refs = set(receipt["cross_review_novel_source_refs"])
    linked_refs = set(receipt["cross_review_linked_source_refs"])
    if novel_refs | linked_refs != review_refs or novel_refs & linked_refs:
        raise ContractError(
            "residual-reduction receipt novel/linked reviews must partition all cross-reviews"
        )
    if not set(receipt["challenged_seat_source_refs"]).issubset(seat_refs):
        raise ContractError("residual-reduction receipt challenges cite unknown seat residuals")
    if not set(receipt["final_represented_source_refs"]).issubset(seat_refs | review_refs):
        raise ContractError(
            "residual-reduction receipt final representation cites unknown sources"
        )
    if not set(receipt["final_falsified_or_discarded_source_refs"]).issubset(
        set(receipt["final_represented_source_refs"])
    ):
        raise ContractError(
            "residual-reduction receipt discarded sources must be represented in the final verdict"
        )
    digest(receipt.get("binding_sha256"), "residual-reduction receipt.binding_sha256")
    expected = digest_value(
        {key: item for key, item in receipt.items() if key != "binding_sha256"}
    )
    if receipt["binding_sha256"] != expected:
        raise ContractError("residual-reduction receipt binding digest does not match")
    return receipt


def validate_product_summary(value: Any) -> dict[str, Any]:
    product = require_object(value, "product summary")
    closed(product, PRODUCT_FIELDS, "product summary")
    if product.get("product_version") != "1.0" or product.get("status") != "completed":
        raise ContractError("product summary must be a completed version 1.0 product")
    for field in (
        "product_sha256",
        "runtime_sha256",
        "agent_config_sha256",
        "assignment_plan_sha256",
        "evidence_manifest_sha256",
        "evidence_coverage_sha256",
        "original_brief_sha256",
        "action_binding_sha256",
        "final_verdict_sha256",
        "residual_trace_sha256",
        "residual_reduction_sha256",
    ):
        digest(product.get(field), f"product summary.{field}")
    digest(product.get("builder_config_sha256"), "product summary.builder_config_sha256", nullable=True)
    for field in (
        "trial_id",
        "question",
        "assignment_plan_ref",
        "evidence_manifest_ref",
        "evidence_coverage_ref",
        "final_verdict_ref",
        "residual_trace_ref",
        "residual_reduction_ref",
    ):
        text(product.get(field), f"product summary.{field}")
    if product.get("action_scope") is not None and not isinstance(product["action_scope"], str):
        raise ContractError("product summary.action_scope must be a string or null")
    string_list(product.get("affected_paths"), "product summary.affected_paths")
    if product.get("final_decision") not in DECISIONS:
        raise ContractError("product summary.final_decision is invalid")
    string_list(product.get("final_dissent"), "product summary.final_dissent")
    seats = product.get("seats")
    if not isinstance(seats, list) or len(seats) != 3:
        raise ContractError("product summary.seats must contain exactly three seats")
    seat_ids: set[str] = set()
    families: set[str] = set()
    run_ids: set[str] = set()
    for index, raw in enumerate(seats):
        seat = require_object(raw, f"product summary.seats[{index}]")
        closed(seat, PRODUCT_SEAT_FIELDS, f"product summary.seats[{index}]")
        for field in (
            "seat_id",
            "family",
            "provider",
            "text_model",
            "multimodal_model",
            "dossier_ref",
            "quinte_run_id",
        ):
            text(seat.get(field), f"product summary.seats[{index}].{field}")
        for field in (
            "profile_sha256",
            "thesis_sha256",
            "dossier_sha256",
            "quinte_manifest_sha256",
            "quinte_result_sha256",
        ):
            digest(seat.get(field), f"product summary.seats[{index}].{field}")
        string_list(
            seat.get("assigned_evidence_refs"),
            f"product summary.seats[{index}].assigned_evidence_refs",
        )
        mapping_ref = seat.get("evidence_mapping_ref")
        mapping_sha = seat.get("evidence_mapping_sha256")
        if mapping_ref is None and mapping_sha is None:
            if seat.get("assigned_evidence_refs"):
                raise ContractError(
                    f"product summary.seats[{index}] assigned evidence requires a mapping receipt"
                )
        else:
            text(mapping_ref, f"product summary.seats[{index}].evidence_mapping_ref")
            digest(mapping_sha, f"product summary.seats[{index}].evidence_mapping_sha256")
        seat_ids.add(seat["seat_id"])
        families.add(seat["family"])
        run_ids.add(seat["quinte_run_id"])
    if len(seat_ids) != 3 or len(families) != 3 or len(run_ids) != 3:
        raise ContractError("product summary seats must bind three distinct IDs, families, and runs")
    seats_by_id = {seat["seat_id"]: seat for seat in seats}
    reviews = product.get("cross_reviews")
    if not isinstance(reviews, list) or len(reviews) != 6:
        raise ContractError("product summary.cross_reviews must contain exactly six reviews")
    refs: set[str] = set()
    execution_refs: set[str] = set()
    reviewer_counts: dict[str, int] = {}
    reviewer_bindings: dict[str, tuple[Any, ...]] = {}
    for index, raw in enumerate(reviews):
        review = require_object(raw, f"product summary.cross_reviews[{index}]")
        closed(review, PRODUCT_REVIEW_FIELDS, f"product summary.cross_reviews[{index}]")
        ref = text(review.get("artifact_ref"), f"product summary.cross_reviews[{index}].artifact_ref")
        for field in (
            "reviewer_seat_id",
            "reviewer_family",
            "reviewer_provider",
            "reviewer_text_model",
            "reviewer_multimodal_model",
            "reviewer_profile_id",
            "reviewer_execution_receipt_ref",
        ):
            text(review.get(field), f"product summary.cross_reviews[{index}].{field}")
        for field in (
            "sha256",
            "reviewer_profile_sha256",
            "reviewer_profile_source_sha256",
            "reviewer_agent_config_sha256",
            "methodology_trace_sha256",
            "reviewer_execution_receipt_sha256",
        ):
            digest(review.get(field), f"product summary.cross_reviews[{index}].{field}")
        refs.add(ref)
        execution_refs.add(review["reviewer_execution_receipt_ref"])
        reviewer_id = review["reviewer_seat_id"]
        reviewer_counts[reviewer_id] = reviewer_counts.get(reviewer_id, 0) + 1
        seat = seats_by_id.get(reviewer_id)
        if seat is None:
            raise ContractError("product summary review does not identify a product seat")
        for review_field, seat_field in (
            ("reviewer_family", "family"),
            ("reviewer_provider", "provider"),
            ("reviewer_text_model", "text_model"),
            ("reviewer_multimodal_model", "multimodal_model"),
            ("reviewer_profile_sha256", "profile_sha256"),
        ):
            if review[review_field] != seat[seat_field]:
                raise ContractError(
                    f"product summary review {review_field} does not match its product seat"
                )
        binding = tuple(review[field] for field in (
            "reviewer_family", "reviewer_provider", "reviewer_text_model",
            "reviewer_multimodal_model", "reviewer_profile_id",
            "reviewer_profile_sha256", "reviewer_profile_source_sha256",
            "reviewer_agent_config_sha256",
        ))
        if reviewer_id in reviewer_bindings and reviewer_bindings[reviewer_id] != binding:
            raise ContractError("product summary changes a frozen reviewer binding")
        reviewer_bindings[reviewer_id] = binding
    if len(refs) != 6:
        raise ContractError("product summary cross-review refs must be distinct")
    if len(execution_refs) != 6:
        raise ContractError("product summary reviewer execution receipt refs must be distinct")
    if set(reviewer_counts) != seat_ids or any(count != 2 for count in reviewer_counts.values()):
        raise ContractError("product summary must contain exactly two reviews from each seat")
    final_adjudicator = require_object(
        product.get("final_adjudicator"), "product summary.final_adjudicator"
    )
    closed(
        final_adjudicator,
        PRODUCT_FINAL_ADJUDICATOR_FIELDS,
        "product summary.final_adjudicator",
    )
    for field in (
        "family", "provider", "text_model", "multimodal_model",
        "execution_mode", "execution_receipt_ref",
    ):
        text(final_adjudicator.get(field), f"product summary.final_adjudicator.{field}")
    for field in ("agent_config_sha256", "execution_receipt_sha256"):
        digest(final_adjudicator.get(field), f"product summary.final_adjudicator.{field}")
    expected_product_digest = digest_value(
        {key: item for key, item in product.items() if key != "product_sha256"}
    )
    if product["product_sha256"] != expected_product_digest:
        raise ContractError("product summary.product_sha256 does not match its identity fields")
    return product
