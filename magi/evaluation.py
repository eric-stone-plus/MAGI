"""Deterministic residual stress and ablation scoring.

This module consumes pre-recorded JSON artifacts.  It performs no model calls,
semantic inference, file discovery, or mutation of source evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .errors import ContractError


FIXTURE_FIELDS = {
    "fixture_version",
    "case_id",
    "evidence_catalog",
    "oracle_claims",
    "arms",
    "experiment_order",
    "stop_policy",
}
EVIDENCE_FIELDS = {"evidence_ref", "supports_claim_ids"}
CLAIM_FIELDS = {
    "claim_id",
    "equivalence_key",
    "statement",
    "severity",
    "material",
    "required",
    "acceptable_evidence_refs",
}
ARM_FIELDS = {
    "arm_id",
    "arm_type",
    "nominal_model_calls",
    "outputs",
    "reported_differences",
}
OUTPUT_FIELDS = {"artifact_id", "stage", "family", "review_mode", "findings"}
FINDING_FIELDS = {
    "finding_id",
    "claim_id",
    "severity",
    "relation",
    "target_ref",
    "evidence_refs",
    "text",
}
DIFFERENCE_FIELDS = {"left_ref", "right_ref"}
STOP_FIELDS = {
    "baseline_min_material_recall",
    "baseline_min_high_risk_recall",
    "baseline_min_precision",
    "max_unsupported_findings",
    "max_severity_drifts",
    "profile_max_false_difference_ratio",
    "stop_profiles_without_material_novelty",
    "stop_cross_review_without_material_novelty",
    "stop_when_all_required_claims_supported",
}

SEVERITY_ORDER = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3, "P0": 4}
HIGH_RISK = {"HIGH", "CRITICAL", "P0"}
ARM_TYPES = {"baseline", "profiles", "cross_review", "author_consistency", "stress"}
REVIEW_MODES = {"independent", "author_consistency"}
RELATIONS = {"assertion", "challenge"}


def load_fixture(path: Path) -> dict[str, Any]:
    """Read and validate a closed residual-stress fixture."""

    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read evaluation fixture {path}: {exc}") from exc
    return validate_fixture(value)


def validate_fixture(value: Any) -> dict[str, Any]:
    fixture = _object(value, "evaluation fixture")
    _closed(fixture, FIXTURE_FIELDS, "evaluation fixture")
    if fixture.get("fixture_version") != "1.0":
        raise ContractError("evaluation fixture_version must be 1.0")
    _text(fixture.get("case_id"), "evaluation fixture case_id")

    evidence = _object_array(fixture.get("evidence_catalog"), "evidence_catalog", nonempty=True)
    evidence_refs: set[str] = set()
    for index, item in enumerate(evidence):
        label = f"evidence_catalog[{index}]"
        _closed(item, EVIDENCE_FIELDS, label)
        reference = _text(item.get("evidence_ref"), f"{label}.evidence_ref")
        if not reference.startswith("snapshot://") or reference in evidence_refs:
            raise ContractError(f"{label}.evidence_ref must be a unique snapshot reference")
        evidence_refs.add(reference)
        _string_array(item.get("supports_claim_ids"), f"{label}.supports_claim_ids", nonempty=True)

    claims = _object_array(fixture.get("oracle_claims"), "oracle_claims", nonempty=True)
    claim_ids: set[str] = set()
    equivalence_keys: set[str] = set()
    for index, claim in enumerate(claims):
        label = f"oracle_claims[{index}]"
        _closed(claim, CLAIM_FIELDS, label)
        claim_id = _text(claim.get("claim_id"), f"{label}.claim_id")
        equivalence = _text(claim.get("equivalence_key"), f"{label}.equivalence_key")
        if claim_id in claim_ids:
            raise ContractError(f"duplicate oracle claim_id: {claim_id}")
        if equivalence in equivalence_keys:
            raise ContractError(f"duplicate oracle equivalence_key: {equivalence}")
        claim_ids.add(claim_id)
        equivalence_keys.add(equivalence)
        _text(claim.get("statement"), f"{label}.statement")
        _severity(claim.get("severity"), f"{label}.severity")
        for field in ("material", "required"):
            if not isinstance(claim.get(field), bool):
                raise ContractError(f"{label}.{field} must be boolean")
        acceptable = set(
            _string_array(
                claim.get("acceptable_evidence_refs"),
                f"{label}.acceptable_evidence_refs",
                nonempty=True,
            )
        )
        if not acceptable <= evidence_refs:
            raise ContractError(f"{label} names evidence outside evidence_catalog")

    for index, item in enumerate(evidence):
        unknown = sorted(set(item["supports_claim_ids"]) - claim_ids)
        if unknown:
            raise ContractError(f"evidence_catalog[{index}] supports unknown claims: {unknown}")

    arms = _object_array(fixture.get("arms"), "arms", nonempty=True)
    arm_ids: set[str] = set()
    artifact_ids: set[str] = set()
    finding_by_ref: dict[str, dict[str, Any]] = {}
    finding_arm_index: dict[str, int] = {}
    for arm_index, arm in enumerate(arms):
        label = f"arms[{arm_index}]"
        _closed(arm, ARM_FIELDS, label)
        arm_id = _text(arm.get("arm_id"), f"{label}.arm_id")
        if arm_id in arm_ids:
            raise ContractError(f"duplicate arm_id: {arm_id}")
        arm_ids.add(arm_id)
        if arm.get("arm_type") not in ARM_TYPES:
            raise ContractError(f"{label}.arm_type is invalid")
        calls = arm.get("nominal_model_calls")
        if not isinstance(calls, int) or isinstance(calls, bool) or calls < 0:
            raise ContractError(f"{label}.nominal_model_calls must be a non-negative integer")
        outputs = _object_array(arm.get("outputs"), f"{label}.outputs", nonempty=True)
        for output_index, output in enumerate(outputs):
            output_label = f"{label}.outputs[{output_index}]"
            _closed(output, OUTPUT_FIELDS, output_label)
            artifact_id = _text(output.get("artifact_id"), f"{output_label}.artifact_id")
            if artifact_id in artifact_ids:
                raise ContractError(f"duplicate evaluation artifact_id: {artifact_id}")
            artifact_ids.add(artifact_id)
            _text(output.get("stage"), f"{output_label}.stage")
            _text(output.get("family"), f"{output_label}.family")
            if output.get("review_mode") not in REVIEW_MODES:
                raise ContractError(f"{output_label}.review_mode is invalid")
            findings = _object_array(
                output.get("findings"), f"{output_label}.findings", nonempty=True
            )
            finding_ids: set[str] = set()
            for finding_index, finding in enumerate(findings):
                finding_label = f"{output_label}.findings[{finding_index}]"
                _closed(finding, FINDING_FIELDS, finding_label)
                finding_id = _text(finding.get("finding_id"), f"{finding_label}.finding_id")
                if finding_id in finding_ids:
                    raise ContractError(f"duplicate finding_id in {artifact_id}: {finding_id}")
                finding_ids.add(finding_id)
                _text(finding.get("claim_id"), f"{finding_label}.claim_id")
                _severity(finding.get("severity"), f"{finding_label}.severity")
                if finding.get("relation") not in RELATIONS:
                    raise ContractError(f"{finding_label}.relation is invalid")
                if finding["relation"] == "assertion" and finding.get("target_ref") is not None:
                    raise ContractError(f"{finding_label}.assertion must not have target_ref")
                if finding["relation"] == "challenge":
                    _text(finding.get("target_ref"), f"{finding_label}.target_ref")
                _string_array(
                    finding.get("evidence_refs"), f"{finding_label}.evidence_refs", nonempty=True
                )
                _text(finding.get("text"), f"{finding_label}.text")
                finding_ref = _finding_ref(artifact_id, finding_id)
                finding_by_ref[finding_ref] = finding
                finding_arm_index[finding_ref] = arm_index

    for arm_index, arm in enumerate(arms):
        for output_index, output in enumerate(arm["outputs"]):
            for finding_index, finding in enumerate(output["findings"]):
                if finding["relation"] == "challenge":
                    target_ref = finding["target_ref"]
                    label = f"arms[{arm_index}].outputs[{output_index}].findings[{finding_index}]"
                    if target_ref not in finding_by_ref:
                        raise ContractError(f"{label} targets an unknown finding")
                    if finding_arm_index[target_ref] >= arm_index:
                        raise ContractError(f"{label} must target a finding from an earlier arm")
                    if finding_by_ref[target_ref]["relation"] != "assertion":
                        raise ContractError(f"{label} must target an assertion")
        differences = _object_array(
            arm.get("reported_differences"), f"arms[{arm_index}].reported_differences"
        )
        for difference_index, difference in enumerate(differences):
            label = f"arms[{arm_index}].reported_differences[{difference_index}]"
            _closed(difference, DIFFERENCE_FIELDS, label)
            for field in DIFFERENCE_FIELDS:
                reference = _text(difference.get(field), f"{label}.{field}")
                if reference not in finding_by_ref:
                    raise ContractError(f"{label}.{field} names an unknown finding")
            if difference["left_ref"] == difference["right_ref"]:
                raise ContractError(f"{label} must compare two different findings")

    order = _string_array(fixture.get("experiment_order"), "experiment_order", nonempty=True)
    if len(order) != len(set(order)) or not set(order) <= arm_ids:
        raise ContractError("experiment_order must name distinct declared arms")
    arms_by_id = {arm["arm_id"]: arm for arm in arms}
    if any(arms_by_id[arm_id]["arm_type"] == "stress" for arm_id in order):
        raise ContractError("stress arms must not appear in experiment_order")

    stop = _object(fixture.get("stop_policy"), "stop_policy")
    _closed(stop, STOP_FIELDS, "stop_policy")
    for field in (
        "baseline_min_material_recall",
        "baseline_min_high_risk_recall",
        "baseline_min_precision",
        "profile_max_false_difference_ratio",
    ):
        value = stop.get(field)
        if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 1:
            raise ContractError(f"stop_policy.{field} must be a number from 0 to 1")
    for field in ("max_unsupported_findings", "max_severity_drifts"):
        value = stop.get(field)
        if not isinstance(value, int) or isinstance(value, bool) or value < 0:
            raise ContractError(f"stop_policy.{field} must be a non-negative integer")
    for field in (
        "stop_profiles_without_material_novelty",
        "stop_cross_review_without_material_novelty",
        "stop_when_all_required_claims_supported",
    ):
        if not isinstance(stop.get(field), bool):
            raise ContractError(f"stop_policy.{field} must be boolean")
    return fixture


def evaluate_arm(fixture: dict[str, Any], arm_id: str) -> dict[str, Any]:
    """Score one arm against atomic claims and digest-bound evidence labels."""

    validate_fixture(fixture)
    arms = {arm["arm_id"]: arm for arm in fixture["arms"]}
    if arm_id not in arms:
        raise ContractError(f"unknown evaluation arm: {arm_id}")
    arm = arms[arm_id]
    claims = {claim["claim_id"]: claim for claim in fixture["oracle_claims"]}
    evidence = {
        item["evidence_ref"]: set(item["supports_claim_ids"])
        for item in fixture["evidence_catalog"]
    }
    findings_by_ref = _all_findings(fixture)

    supported_by_claim: dict[str, list[dict[str, Any]]] = {}
    unsupported: list[dict[str, Any]] = []
    linked_challenges: list[str] = []
    severity_drifts: list[dict[str, str]] = []
    author_consistency_count = 0
    total_findings = 0
    for output in arm["outputs"]:
        if output["review_mode"] == "author_consistency":
            author_consistency_count += len(output["findings"])
        for finding in output["findings"]:
            total_findings += 1
            finding_ref = _finding_ref(output["artifact_id"], finding["finding_id"])
            claim = claims.get(finding["claim_id"])
            unknown_refs = sorted(set(finding["evidence_refs"]) - set(evidence))
            non_entailing = sorted(
                reference
                for reference in finding["evidence_refs"]
                if reference in evidence and finding["claim_id"] not in evidence[reference]
            )
            unacceptable = (
                sorted(set(finding["evidence_refs"]) - set(claim["acceptable_evidence_refs"]))
                if claim is not None
                else []
            )
            target_valid = (
                finding["relation"] != "challenge"
                or finding["target_ref"] in findings_by_ref
            )
            if claim is None or unknown_refs or non_entailing or unacceptable or not target_valid:
                unsupported.append(
                    {
                        "finding_ref": finding_ref,
                        "claim_id": finding["claim_id"],
                        "unknown_evidence_refs": unknown_refs,
                        "non_entailing_evidence_refs": non_entailing,
                        "unacceptable_evidence_refs": unacceptable,
                        "reason": "unknown_claim" if claim is None else "citation_or_target_invalid",
                    }
                )
                continue
            record = {"finding": finding, "output": output, "finding_ref": finding_ref}
            supported_by_claim.setdefault(finding["claim_id"], []).append(record)
            if finding["relation"] == "challenge":
                linked_challenges.append(finding_ref)
            if SEVERITY_ORDER[finding["severity"]] < SEVERITY_ORDER[claim["severity"]]:
                severity_drifts.append(
                    {
                        "finding_ref": finding_ref,
                        "claim_id": finding["claim_id"],
                        "expected": claim["severity"],
                        "observed": finding["severity"],
                    }
                )

    supported_claims = set(supported_by_claim)
    independent_claims = {
        claim_id
        for claim_id, records in supported_by_claim.items()
        if any(record["output"]["review_mode"] == "independent" for record in records)
    }
    author_claims = {
        claim_id
        for claim_id, records in supported_by_claim.items()
        if any(record["output"]["review_mode"] == "author_consistency" for record in records)
    }
    material = {claim_id for claim_id, claim in claims.items() if claim["material"]}
    required = {claim_id for claim_id, claim in claims.items() if claim["required"]}
    high_risk = {
        claim_id
        for claim_id, claim in claims.items()
        if claim["required"] and claim["severity"] in HIGH_RISK
    }
    same_family_echoes: list[dict[str, Any]] = []
    for claim_id, records in sorted(supported_by_claim.items()):
        independent = [
            record for record in records if record["output"]["review_mode"] == "independent"
        ]
        families = sorted({record["output"]["family"] for record in independent})
        if len(independent) > 1 and len(families) == 1:
            same_family_echoes.append(
                {
                    "claim_id": claim_id,
                    "observation_count": len(independent),
                    "independent_family_count": 1,
                    "family": families[0],
                }
            )

    false_differences: list[dict[str, str]] = []
    substantive_differences: list[dict[str, str]] = []
    for difference in arm["reported_differences"]:
        left = findings_by_ref[difference["left_ref"]]
        right = findings_by_ref[difference["right_ref"]]
        left_claim = claims.get(left["claim_id"])
        right_claim = claims.get(right["claim_id"])
        same = (
            left_claim is not None
            and right_claim is not None
            and left_claim["equivalence_key"] == right_claim["equivalence_key"]
        )
        (false_differences if same else substantive_differences).append(difference)
    difference_count = len(false_differences) + len(substantive_differences)
    supported_findings = sum(len(records) for records in supported_by_claim.values())
    return {
        "arm_id": arm_id,
        "arm_type": arm["arm_type"],
        "nominal_model_calls": arm["nominal_model_calls"],
        "total_findings": total_findings,
        "supported_findings": supported_findings,
        "supported_claim_ids": sorted(supported_claims),
        "independent_supported_claim_ids": sorted(independent_claims),
        "author_consistency_claim_ids": sorted(author_claims),
        "author_consistency_observation_count": author_consistency_count,
        "precision": _ratio(supported_findings, total_findings),
        "material_recall": _ratio(len(supported_claims & material), len(material)),
        "high_risk_recall": _ratio(len(supported_claims & high_risk), len(high_risk)),
        "omitted_required_claim_ids": sorted(required - supported_claims),
        "omitted_high_risk_claim_ids": sorted(high_risk - supported_claims),
        "unsupported_findings": unsupported,
        "severity_drifts": severity_drifts,
        "same_family_echoes": same_family_echoes,
        "linked_challenge_refs": sorted(linked_challenges),
        "false_differences": false_differences,
        "substantive_differences": substantive_differences,
        "false_difference_ratio": _ratio(len(false_differences), difference_count),
        "fail_closed": bool(unsupported),
    }


def evaluate_experiment(fixture: dict[str, Any]) -> dict[str, Any]:
    """Evaluate ordered ablations and apply pre-registered stopping rules."""

    validate_fixture(fixture)
    claims = {claim["claim_id"]: claim for claim in fixture["oracle_claims"]}
    required = {claim_id for claim_id, claim in claims.items() if claim["required"]}
    material = {claim_id for claim_id, claim in claims.items() if claim["material"]}
    policy = fixture["stop_policy"]
    independent_cumulative: set[str] = set()
    calls = 0
    steps: list[dict[str, Any]] = []
    stopped = False
    for arm_id in fixture["experiment_order"]:
        metrics = evaluate_arm(fixture, arm_id)
        calls += metrics["nominal_model_calls"]
        current = set(metrics["independent_supported_claim_ids"])
        novel = current - independent_cumulative
        novel_material = novel & material
        independent_cumulative.update(current)
        decision, reasons = _stop_decision(
            metrics,
            policy,
            novel_material=novel_material,
            cumulative=independent_cumulative,
            required=required,
        )
        step = {
            "arm_id": arm_id,
            "arm_type": metrics["arm_type"],
            "nominal_model_calls": metrics["nominal_model_calls"],
            "cumulative_nominal_model_calls": calls,
            "novel_independent_claim_ids": sorted(novel),
            "novel_material_independent_claim_ids": sorted(novel_material),
            "cumulative_independent_claim_ids": sorted(independent_cumulative),
            "decision": decision,
            "reasons": reasons,
        }
        steps.append(step)
        if decision.startswith("STOP") or decision == "FAIL_CLOSED":
            stopped = True
            break
    return {
        "case_id": fixture["case_id"],
        "steps": steps,
        "stopped": stopped,
        "final_decision": steps[-1]["decision"],
        "nominal_model_calls_before_stop": calls,
        "independent_supported_claim_ids": sorted(independent_cumulative),
        "author_consistency_is_independent": False,
    }


def _stop_decision(
    metrics: dict[str, Any],
    policy: dict[str, Any],
    *,
    novel_material: set[str],
    cumulative: set[str],
    required: set[str],
) -> tuple[str, list[str]]:
    if metrics["fail_closed"] or len(metrics["unsupported_findings"]) > policy["max_unsupported_findings"]:
        return "FAIL_CLOSED", ["unsupported claim or citation"]
    arm_type = metrics["arm_type"]
    if arm_type == "baseline":
        failures: list[str] = []
        if metrics["material_recall"] < policy["baseline_min_material_recall"]:
            failures.append("material recall below threshold")
        if metrics["high_risk_recall"] < policy["baseline_min_high_risk_recall"]:
            failures.append("high-risk recall below threshold")
        if metrics["precision"] < policy["baseline_min_precision"]:
            failures.append("precision below threshold")
        if len(metrics["severity_drifts"]) > policy["max_severity_drifts"]:
            failures.append("severity drift exceeds threshold")
        return ("CONTINUE", failures) if failures else ("STOP_BASELINE_SUFFICIENT", ["baseline met all gates"])
    if arm_type == "profiles":
        if (
            policy["stop_profiles_without_material_novelty"]
            and not novel_material
        ):
            return "STOP_NO_PROFILE_INCREMENT", ["profiles added no supported material claim"]
        if metrics["false_difference_ratio"] > policy["profile_max_false_difference_ratio"]:
            return "STOP_FALSE_DIFFERENCE_DOMINANT", ["false differences exceed threshold"]
    if arm_type == "cross_review" and policy["stop_cross_review_without_material_novelty"] and not novel_material:
        return "STOP_NO_CROSS_REVIEW_INCREMENT", ["cross-review added no supported material claim"]
    if arm_type == "author_consistency":
        return "STOP_AUTHOR_CONSISTENCY_ONLY", ["author-consistency output is excluded from independent support"]
    if policy["stop_when_all_required_claims_supported"] and required <= cumulative:
        return "STOP_ACCEPTANCE_MET", ["all required claims have independent support"]
    return "CONTINUE", ["a pre-registered gate remains open"]


def _all_findings(fixture: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        _finding_ref(output["artifact_id"], finding["finding_id"]): finding
        for arm in fixture["arms"]
        for output in arm["outputs"]
        for finding in output["findings"]
    }


def _finding_ref(artifact_id: str, finding_id: str) -> str:
    return f"finding://{artifact_id}/{finding_id}"


def _ratio(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 6) if denominator else 1.0


def _object(value: Any, label: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    return value


def _object_array(value: Any, label: str, *, nonempty: bool = False) -> list[dict[str, Any]]:
    if (
        not isinstance(value, list)
        or (nonempty and not value)
        or not all(isinstance(item, dict) for item in value)
    ):
        raise ContractError(f"{label} must be a{' non-empty' if nonempty else ''} object array")
    return value


def _string_array(value: Any, label: str, *, nonempty: bool = False) -> list[str]:
    if (
        not isinstance(value, list)
        or (nonempty and not value)
        or not all(isinstance(item, str) and item.strip() for item in value)
        or len(value) != len(set(value))
    ):
        raise ContractError(f"{label} must be a unique{' non-empty' if nonempty else ''} string array")
    return value


def _closed(value: dict[str, Any], fields: set[str], label: str) -> None:
    unknown = sorted(set(value) - fields)
    missing = sorted(fields - set(value))
    if unknown or missing:
        raise ContractError(f"{label} closed-field mismatch; unknown={unknown}, missing={missing}")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty string")
    return value


def _severity(value: Any, label: str) -> str:
    if value not in SEVERITY_ORDER:
        raise ContractError(f"{label} is invalid")
    return value
