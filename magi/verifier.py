"""Deterministic final-verdict and HIGHBALL trace verification."""

from __future__ import annotations

from typing import Any

from .contracts import HIGH_RISK, validate_final, validate_residual_reduction_receipt
from .errors import ContractError
from .io import digest_value
from .seat import SeatProduct


SEVERITY_RANK = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3, "P0": 4}


def seat_source_ref(alias: str, residual_id: str) -> str:
    return f"seat:{alias}:residual:{residual_id}"


def review_source_ref(reviewer: str, subject: str, finding_id: str) -> str:
    return f"review:{reviewer}>{subject}:finding:{finding_id}"


def required_high_risk_refs(
    seats_by_alias: dict[str, SeatProduct], reviews: list[dict[str, Any]]
) -> set[str]:
    refs: set[str] = set()
    for alias, seat in seats_by_alias.items():
        for residual in seat.result["residuals"]:
            if residual["severity"] in HIGH_RISK:
                refs.add(seat_source_ref(alias, residual["id"]))
    for review in reviews:
        for finding in review["findings"]:
            if finding["severity"] in HIGH_RISK:
                refs.add(
                    review_source_ref(
                        review["reviewer_alias"], review["subject_alias"], finding["id"]
                    )
                )
    return refs


def all_source_refs(
    seats_by_alias: dict[str, SeatProduct], reviews: list[dict[str, Any]]
) -> set[str]:
    refs: set[str] = set()
    for alias, seat in seats_by_alias.items():
        refs.update(seat_source_ref(alias, residual["id"]) for residual in seat.result["residuals"])
    for review in reviews:
        refs.update(
            review_source_ref(review["reviewer_alias"], review["subject_alias"], finding["id"])
            for finding in review["findings"]
        )
    return refs


def verify_final(
    verdict: dict[str, Any],
    seats_by_alias: dict[str, SeatProduct],
    reviews: list[dict[str, Any]],
) -> dict[str, Any]:
    validate_final(verdict)
    valid_refs = all_source_refs(seats_by_alias, reviews)
    valid_evidence = all_evidence_refs(seats_by_alias)
    required_refs = required_high_risk_refs(seats_by_alias, reviews)
    source_severity = source_severities(seats_by_alias, reviews)
    evidence_by_source = source_evidence_refs(seats_by_alias, reviews)
    closure_evidence_by_source = source_closure_evidence_refs(seats_by_alias, reviews)
    closure_state_by_source = source_closure_states(seats_by_alias, reviews)
    represented: set[str] = set()
    for index, finding in enumerate(verdict["findings"]):
        source_refs = finding["source_refs"]
        invalid = sorted(set(source_refs) - valid_refs)
        if invalid:
            raise ContractError(
                f"final verdict finding {index} cites invalid source refs: {', '.join(invalid)}"
            )
        invalid_evidence = sorted(set(finding["evidence_refs"]) - valid_evidence)
        if invalid_evidence:
            raise ContractError(
                f"final verdict finding {index} cites invalid evidence refs: "
                + ", ".join(invalid_evidence)
            )
        supported_evidence = set().union(
            *(evidence_by_source[reference] for reference in source_refs)
        )
        unrelated_evidence = sorted(set(finding["evidence_refs"]) - supported_evidence)
        if unrelated_evidence:
            raise ContractError(
                f"final verdict finding {index} cites evidence unrelated to its sources: "
                + ", ".join(unrelated_evidence)
            )
        represented.update(source_refs)
        expected_severity = max(
            (source_severity[reference] for reference in source_refs),
            key=SEVERITY_RANK.__getitem__,
        )
        if finding["severity"] != expected_severity:
            raise ContractError(
                f"final verdict finding {index} must preserve the highest cited source severity"
            )
        supported_closure_evidence = set().union(
            *(closure_evidence_by_source[reference] for reference in source_refs)
        )
        invented_closure_evidence = sorted(
            set(finding["closure_evidence"]) - supported_closure_evidence
        )
        if invented_closure_evidence:
            raise ContractError(
                f"final verdict finding {index} invents closure evidence: "
                + ", ".join(invented_closure_evidence)
            )
        if any(closure_state_by_source[reference] == "blocked" for reference in source_refs):
            if finding["closure_state"] in {"closed", "waived", "not_applicable"}:
                raise ContractError(
                    f"final verdict finding {index} suppresses a blocked source state"
                )
        _verify_closure(finding, index)
    omitted = sorted(required_refs - represented)
    if omitted:
        raise ContractError(
            "final adjudicator omitted HIGH/CRITICAL/P0 findings: " + ", ".join(omitted)
        )
    required_dissent = sorted(source_dissent(seats_by_alias, reviews))
    if verdict["dissent"] != required_dissent:
        raise ContractError(
            "final adjudicator must preserve exactly the canonical seat and cross-review dissent"
        )

    blocking_high = [
        item
        for item in verdict["findings"]
        if item["severity"] in HIGH_RISK and item["closure_state"] in {"open", "blocked"}
    ]
    unresolved_high = [
        item
        for item in verdict["findings"]
        if item["severity"] in HIGH_RISK
        and item["disposition"] in {"unresolved", "escalated"}
    ]
    if verdict["decision"] == "PASS" and (blocking_high or unresolved_high):
        raise ContractError(
            "PASS conflicts with open, blocked, unresolved, or escalated high-risk findings"
        )
    if verdict["decision"] == "PASS" and verdict["dissent"]:
        raise ContractError("PASS cannot suppress material dissent")
    if verdict["decision"] == "BLOCK" and not blocking_high:
        raise ContractError("BLOCK requires at least one open or blocked high-risk finding")
    if verdict["decision"] == "ESCALATE" and not (unresolved_high or verdict["dissent"]):
        raise ContractError("ESCALATE requires unresolved high risk or material dissent")
    return verdict


def all_evidence_refs(seats_by_alias: dict[str, SeatProduct]) -> set[str]:
    refs: set[str] = set()
    for alias, seat in seats_by_alias.items():
        for residual in seat.result["residuals"]:
            for reference in residual["evidence_refs"] + residual["closure_evidence"]:
                if reference:
                    refs.add(f"seat:{alias}:evidence:{reference}")
    return refs


def source_evidence_refs(
    seats_by_alias: dict[str, SeatProduct], reviews: list[dict[str, Any]]
) -> dict[str, set[str]]:
    values: dict[str, set[str]] = {}
    for alias, seat in seats_by_alias.items():
        for residual in seat.result["residuals"]:
            values[seat_source_ref(alias, residual["id"])] = {
                f"seat:{alias}:evidence:{reference}"
                for reference in residual["evidence_refs"] + residual["closure_evidence"]
                if reference
            }
    for review in reviews:
        for finding in review["findings"]:
            reference = review_source_ref(
                review["reviewer_alias"], review["subject_alias"], finding["id"]
            )
            values[reference] = set(finding["evidence_refs"])
            for source_ref in finding["source_refs"]:
                if source_ref != reference and source_ref in values:
                    values[reference].update(values[source_ref])
    return values


def source_closure_evidence_refs(
    seats_by_alias: dict[str, SeatProduct], reviews: list[dict[str, Any]]
) -> dict[str, set[str]]:
    values: dict[str, set[str]] = {}
    for alias, seat in seats_by_alias.items():
        for residual in seat.result["residuals"]:
            values[seat_source_ref(alias, residual["id"])] = {
                f"seat:{alias}:evidence:{reference}"
                for reference in residual["closure_evidence"]
                if reference
            }
    for review in reviews:
        for finding in review["findings"]:
            evidence = {item for item in finding["closure_evidence"] if item}
            reference = review_source_ref(
                review["reviewer_alias"], review["subject_alias"], finding["id"]
            )
            values[reference] = evidence
    return values


def source_closure_states(
    seats_by_alias: dict[str, SeatProduct], reviews: list[dict[str, Any]]
) -> dict[str, str]:
    values: dict[str, str] = {}
    for alias, seat in seats_by_alias.items():
        for residual in seat.result["residuals"]:
            values[seat_source_ref(alias, residual["id"])] = residual["closure_state"]
    for review in reviews:
        for finding in review["findings"]:
            reference = review_source_ref(
                review["reviewer_alias"], review["subject_alias"], finding["id"]
            )
            values[reference] = finding["closure_state"]
    return values


def source_dissent(
    seats_by_alias: dict[str, SeatProduct], reviews: list[dict[str, Any]]
) -> set[str]:
    seat_dissent = {
        dissent.strip()
        for alias, seat in seats_by_alias.items()
        for dissent in seat.anonymous_view(alias)["quinte_result"]["dissent"]
        if dissent.strip()
    }
    review_dissent = {
        dissent.strip()
        for review in reviews
        for dissent in review["dissent"]
        if dissent.strip()
    }
    return seat_dissent | review_dissent


def source_severities(
    seats_by_alias: dict[str, SeatProduct], reviews: list[dict[str, Any]]
) -> dict[str, str]:
    values: dict[str, str] = {}
    for alias, seat in seats_by_alias.items():
        for residual in seat.result["residuals"]:
            values[seat_source_ref(alias, residual["id"])] = residual["severity"]
    for review in reviews:
        for finding in review["findings"]:
            values[
                review_source_ref(
                    review["reviewer_alias"], review["subject_alias"], finding["id"]
                )
            ] = finding["severity"]
    return values


def build_highball_trace(
    verdict: dict[str, Any],
    seats_by_alias: dict[str, SeatProduct],
    reviews: list[dict[str, Any]],
    *,
    action_boundary: str,
) -> dict[str, Any]:
    first = next(iter(seats_by_alias.values()))
    decision = {"PASS": "pass", "BLOCK": "block", "ESCALATE": "escalate"}[verdict["decision"]]
    perspectives = []
    for alias, seat in sorted(seats_by_alias.items()):
        binding = seat.result["seat_binding"]
        perspectives.append(
            {
                "id": alias,
                "role": "independent seat analysis plus same-family QUINTE dossier",
                "route": f"{binding['family']}/{binding['text_model']}",
                "artifact": str(seat.dossier_path),
                "prompt_hash": seat.dossier["thesis_sha256"],
                "independent_first_pass": True,
            }
        )
    residuals = []
    for item in verdict["findings"]:
        evidence = "; ".join(item["source_refs"] + item["evidence_refs"]) or None
        residuals.append(
            {
                "id": item["id"],
                "severity": item["severity"],
                "type": item["type"],
                "source": "; ".join(item["source_refs"]),
                "finding": item["finding"],
                "affected_paths": first.result["affected_paths"],
                "error_signature": None,
                "evidence": evidence,
                "disposition": item["disposition"],
                "required_closure": item["required_closure"],
                "closure_state": item["closure_state"],
                "closure_evidence": item["closure_evidence"],
                "scope": item["scope"],
            }
        )
    return {
        "trace_version": "1.1",
        "question": first.result["question"],
        "instrument": "MAGI",
        "residuals": residuals,
        "trial_manifest": {
            "manifest_version": "1.0",
            "base_model_relation": "heterogeneous_models",
            "perspective_count": 3,
            "perspectives": perspectives,
            "perturbation_axes": [
                "foundation_model_family",
                "independent_expert_profile",
                "same_family_quinte_deliberation",
                "anonymous_full_cross_review",
            ],
            "independence_controls": [
                "independent_thesis_before_exchange",
                "distinct_profile_digest",
                "distinct_quinte_run",
                "distinct_result_digest",
                "freeze_before_anonymous_exchange",
            ],
            "contamination_risks": [
                "shared_original_brief",
                "shared_protocol_structure",
                "final_adjudicator_model_correlation",
            ],
            "cost": {
                "total_tokens": None,
                "wall_time_seconds": None,
                "tool_calls": None,
                "human_minutes": None,
            },
        },
        "action_boundary": action_boundary,
        "highball_decision": decision,
        "action_binding_sha256": first.result["action_binding_sha256"],
    }


def build_residual_reduction_receipt(
    verdict: dict[str, Any],
    seats_by_alias: dict[str, SeatProduct],
    reviews: list[dict[str, Any]],
) -> dict[str, Any]:
    """Measure observable cross-review contribution without claiming true error probability."""
    seat_refs = sorted(
        seat_source_ref(alias, residual["id"])
        for alias, seat in seats_by_alias.items()
        for residual in seat.result["residuals"]
    )
    review_refs = sorted(
        review_source_ref(review["reviewer_alias"], review["subject_alias"], finding["id"])
        for review in reviews
        for finding in review["findings"]
    )
    review_novel: list[str] = []
    review_linked: list[str] = []
    challenged_seat_refs: set[str] = set()
    for review in reviews:
        for finding in review["findings"]:
            reference = review_source_ref(
                review["reviewer_alias"], review["subject_alias"], finding["id"]
            )
            linked_seat_refs = {
                item for item in finding["source_refs"] if item.startswith("seat:")
            }
            (review_linked if linked_seat_refs else review_novel).append(reference)
            if finding["disposition"] in {"falsified", "discarded"}:
                challenged_seat_refs.update(linked_seat_refs)
    represented = sorted(
        {
            reference
            for finding in verdict["findings"]
            for reference in finding["source_refs"]
        }
    )
    unresolved = sorted(
        finding["id"]
        for finding in verdict["findings"]
        if finding["closure_state"] in {"open", "blocked"}
        or finding["disposition"] in {"unresolved", "escalated"}
    )
    final_finding_ids = sorted(finding["id"] for finding in verdict["findings"])
    final_falsified_or_discarded = sorted(
        {
            reference
            for finding in verdict["findings"]
            if finding["disposition"] in {"falsified", "discarded"}
            for reference in finding["source_refs"]
        }
    )
    receipt: dict[str, Any] = {
        "receipt_version": "1.0",
        "metric_scope": (
            "observable contribution of six directed cross-reviews and final adjudication"
        ),
        "baseline_scope": (
            "three independent single-family QUINTE seat products before cross-review"
        ),
        "seat_residual_source_refs": seat_refs,
        "cross_review_source_refs": review_refs,
        "cross_review_novel_source_refs": sorted(review_novel),
        "cross_review_linked_source_refs": sorted(review_linked),
        "challenged_seat_source_refs": sorted(challenged_seat_refs),
        "final_represented_source_refs": represented,
        "final_falsified_or_discarded_source_refs": final_falsified_or_discarded,
        "final_finding_ids": final_finding_ids,
        "final_unresolved_finding_ids": unresolved,
        "counts": {
            "seat_residuals": len(seat_refs),
            "cross_review_findings": len(review_refs),
            "cross_review_novel_findings": len(review_novel),
            "cross_review_linked_findings": len(review_linked),
            "challenged_seat_residuals": len(challenged_seat_refs),
            "final_represented_sources": len(represented),
            "final_falsified_or_discarded_sources": len(final_falsified_or_discarded),
            "final_findings": len(verdict["findings"]),
            "final_unresolved_findings": len(unresolved),
        },
        "limitations": [
            "Novel means no cited seat residual; it is not proof that the finding is true.",
            "Falsified or discarded is an adjudication disposition, not measured error correction.",
            "This receipt does not estimate a true error rate, confidence level, or remaining 5 percent.",
            "Residual reduction requires repeated labeled calibration and an explicit single-QUINTE ablation.",
        ],
        "binding_sha256": "",
    }
    receipt["binding_sha256"] = digest_value(
        {key: value for key, value in receipt.items() if key != "binding_sha256"}
    )
    return validate_residual_reduction_receipt(receipt)


def _verify_closure(finding: dict[str, Any], index: int) -> None:
    state = finding["closure_state"]
    evidence = [item for item in finding["closure_evidence"] if item.strip()]
    if evidence:
        allowed_prefixes = (
            "block:",
            "file:",
            "command:",
            "runtime:",
            "source:",
            "waiver:",
            "seat:",
        )
        invalid = [item for item in evidence if not item.startswith(allowed_prefixes)]
        if invalid:
            raise ContractError(
                f"final verdict finding {index} has untyped closure evidence"
            )
    if state in {"closed", "blocked", "waived", "not_applicable"}:
        if not evidence:
            raise ContractError(
                f"final verdict finding {index} claims {state} without closure evidence"
            )
        if not finding["scope"].strip():
            raise ContractError(f"final verdict finding {index} closure has no scope")
    if state == "blocked" and not any(
        item.startswith(("block:", "command:", "runtime:", "source:", "seat:"))
        for item in evidence
    ):
        raise ContractError(
            f"final verdict finding {index} blocked state lacks a typed block record"
        )
    if state == "closed" and finding["disposition"] in {"unresolved", "escalated"}:
        raise ContractError(
            f"final verdict finding {index} has unsupported closed/unresolved combination"
        )
