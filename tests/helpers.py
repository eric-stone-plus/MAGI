from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any

from magi.io import atomic_write_json, digest_bytes, digest_file, digest_tree, quinte_json_bytes
from magi.assignment import bind_assignment_plan


def digest_token(seed: str) -> str:
    return digest_bytes(seed.encode())


def original_brief() -> dict[str, Any]:
    return {
        "brief_version": "1.1",
        "question": "Should this design ship?",
        "context": "Original context",
        "evidence_roots": [],
        "snapshot_ignore": [],
        "attachments": [],
        "action_scope": "service release",
        "affected_paths": ["service/config.json"],
        "action_binding_sha256": digest_token("action"),
    }


def write_seat(base: Path, seat_id: str, family: str, severity: str = "HIGH") -> Path:
    root = base / seat_id
    run = root / "quinte-run"
    (run / "input").mkdir(parents=True)
    profile = {
        "profile_version": "1.0",
        "profile_id": {"seat-m": "formalist", "seat-d": "adversarial", "seat-g": "empirical"}[seat_id],
        "discipline": {
            "seat-m": "formal specification",
            "seat-d": "adversarial safety",
            "seat-g": "empirical measurement",
        }[seat_id],
        "epistemic_lens": "falsification",
        "methods": ["independent analysis"],
        "failure_checks": ["seek counterexample"],
        "instructions": "Do independent work.",
    }
    thesis = {
        "thesis_version": "1.0",
        "question": "Should this design ship?",
        "thesis": f"Thesis from {seat_id}",
        "claims": [
            {
                "id": f"claim-{seat_id}",
                "statement": "A material risk exists.",
                "evidence_refs": [],
                "uncertainty": "Runtime evidence is incomplete.",
                "boundary": "No production execution.",
            }
        ],
        "recommendation": "Do not ship yet.",
        "limitations": ["static review"],
    }
    atomic_write_json(root / "profile.json", profile)
    reviewer_profile = root / "reviewer-profile"
    reviewer_profile.mkdir()
    atomic_write_json(reviewer_profile / "profile.json", profile)
    (reviewer_profile / "SOUL.md").write_text(f"Profile methodology for {seat_id}\n")
    (reviewer_profile / "AGENTS.md").write_text("Immutable technical rules\n")
    (reviewer_profile / "config.yaml").write_text("memory:\n  memory_enabled: false\n")
    composed_content = _profile_content_digest(reviewer_profile)
    atomic_write_json(
        reviewer_profile / "COMPOSITION.json",
        {
            "base_sha256": digest_token(f"base-{seat_id}"),
            "composition_version": "1.0",
            "overlay_sha256": digest_token(f"overlay-{seat_id}"),
            "profile_id": profile["profile_id"],
            "seat_id": seat_id,
            "composed_content_sha256": composed_content,
        },
    )
    atomic_write_json(root / "thesis.json", thesis)
    original = original_brief()
    original_digest = digest_file(base / "original-brief.json")
    derived_context = (
        f"Triadic cross-verification expert seat {seat_id}\nProfile: {profile['profile_id']} "
        f"({digest_file(root / 'profile.json')})\nThesis: {digest_file(root / 'thesis.json')}\n\n"
        + json.dumps(thesis, ensure_ascii=False, sort_keys=True)
    )
    brief = {**original, "context": derived_context}
    atomic_write_json(run / "input" / "brief.json", brief)
    brief_digest = digest_bytes(
        quinte_json_bytes(
            {
                field: brief[field]
                for field in (
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
            }
        )
    )
    perspective = {
        "perspective_input_version": "1.0",
        "seat_id": seat_id,
        "original_brief_sha256": original_digest,
        "profile_id": profile["profile_id"],
        "profile_sha256": digest_file(root / "profile.json"),
        "thesis_sha256": digest_file(root / "thesis.json"),
        "original_question": original["question"],
        "action_scope": original["action_scope"],
        "affected_paths": original["affected_paths"],
        "action_binding_sha256": original["action_binding_sha256"],
        "derived_context": derived_context,
    }
    atomic_write_json(root / "perspective-input.json", perspective)
    snapshot = {
        "snapshot_version": "1.0",
        "created_at": "2026-07-31T00:00:00Z",
        "entries": [],
        "attachments": [],
        "total_bytes": 0,
    }
    atomic_write_json(run / "input" / "snapshot-manifest.json", snapshot)
    seat_binding = {
        "seat_id": seat_id,
        "family": family,
        "provider": f"provider-{family}",
        "text_model": f"model-{family}",
        "multimodal_model": f"model-{family}",
    }
    parties = [
        "Party A",
        "Party B",
        "Party C",
        "Party D",
        "Party E",
        "Counterpart Arbiter",
        "Primary Arbiter",
    ]
    routes = [
        {
            "party_id": party,
            "route_id": f"route-{index}",
            "adapter": f"adapter-{family}",
            "executable": f"agent-{family}",
            "perspective": "",
            **{key: seat_binding[key] for key in ("family", "provider", "text_model", "multimodal_model")},
        }
        for index, party in enumerate(parties)
    ]
    policy_routes = [{**route, "required": True} for route in routes]
    policy = {
        "policy_version": "2.0",
        "seat": seat_binding,
        "roster": policy_routes[:5],
        "counterpart_arbiter": policy_routes[5],
        "primary_arbiter": policy_routes[6],
        "auto_primary_arbiter": True,
        "text_model": seat_binding["text_model"],
        "multimodal_model": seat_binding["multimodal_model"],
        "max_parallel_r1": 5,
        "max_parallel_r2": 1,
        "r2_parallel": False,
        "max_attempts": 3,
        "timeout_seconds": 600,
        "retry_backoff_seconds": 15,
        "retry_backoff_max_seconds": 120,
        "r2_min_interval_seconds": 10,
        "max_output_bytes": 1048576,
        "max_snapshot_files": 2000,
        "max_snapshot_bytes": 20971520,
        "max_attachment_bytes": 10485760,
        "sandbox_mode": "strict",
    }
    atomic_write_json(run / "input" / "policy.json", policy)
    run_id = str(uuid.uuid5(uuid.NAMESPACE_DNS, seat_id))
    residual = {
        "id": f"risk-{seat_id}",
        "severity": severity,
        "residual_type": "engineering-defect",
        "source": "same-family QUINTE",
        "finding": f"Risk from {seat_id}",
        "evidence_refs": [],
        "disposition": "unresolved",
        "required_closure": "Fix and test the risk.",
        "closure_state": "open",
        "closure_evidence": [],
        "scope": "release gate",
    }
    result = {
        "result_version": "2.1",
        "run_id": run_id,
        "status": "completed",
        "brief_sha256": brief_digest,
        "question": original["question"],
        "action_scope": original["action_scope"],
        "affected_paths": original["affected_paths"],
        "action_binding_sha256": original["action_binding_sha256"],
        "summary": "Review complete.",
        "recommendation": "Block until fixed.",
        "dissent": [],
        "residuals": [residual],
        "trial_manifest": {
            "manifest_version": "1.0",
            "base_model_relation": "same_model",
            "perspective_count": 5,
            "perspectives": [
                {
                    "party_id": f"Party {letter}",
                    "route_id": f"route-{index}",
                    "r1_artifact": f"lanes/R1/{letter}.json",
                    "r2_artifact": f"lanes/R2/{letter}.json",
                    "independent_first_pass": True
                }
                for index, letter in enumerate("ABCDE")
            ],
            "perturbation_axes": ["role"],
            "independence_controls": ["isolated_context"],
            "contamination_risks": ["same_model_error_correlation"],
            "wall_time_seconds": 60,
        },
        "seat_binding": seat_binding,
        "route_bindings": routes,
    }
    atomic_write_json(run / "result.json", result)
    manifest = {
        "manifest_version": "2.0",
        "run_id": run_id,
        "created_at": "2026-07-31T00:00:00Z",
        "updated_at": "2026-07-31T00:10:00Z",
        "status": "completed",
        "brief_sha256": brief_digest,
        "policy_sha256": digest_bytes(
            quinte_json_bytes(json.loads((run / "input" / "policy.json").read_text()))
        ),
        "snapshot_sha256": digest_bytes(
            quinte_json_bytes(json.loads((run / "input" / "snapshot-manifest.json").read_text()))
        ),
        "runtime_sha256": digest_token(f"runtime-{seat_id}"),
        "protocol_version": "1.0",
        "effective_model": seat_binding["text_model"],
        "sandbox_mode": "strict",
        "current_phase": "R3",
        "error": None,
        "r3_input_receipt": {
            "artifact_ref": "r3/input-receipt.json",
            "sha256": digest_token(f"receipt-{seat_id}"),
        },
        "primary_arbiter_challenge": {"consumed": True},
        "primary_arbiter_submission": {
            "state": "accepted",
            "input_receipt_sha256": digest_token(f"receipt-{seat_id}"),
            "accepted_at": "2026-07-31T00:10:00Z",
        },
        "result_sha256": digest_file(run / "result.json"),
        "seat_binding": seat_binding,
        "route_bindings": routes,
    }
    atomic_write_json(run / "manifest.json", manifest)
    from magi.mapping import build_mapping_receipt

    # Fixtures bind an empty mapping receipt. The trial assignment plan digest is
    # attached later when generate/bind runs; leave dossier assignment hash null so
    # resume tests can freeze a real plan without rewriting every seat dossier.
    mapping = build_mapping_receipt(
        seat_id=seat_id,
        evidence_manifest={
            "evidence_manifest_version": "1.0",
            "source_files": [],
            "derived_frames": [],
        },
        evidence_manifest_sha256=digest_token(f"evidence-{seat_id}"),
        assignment_plan_sha256=digest_token(f"assignment-placeholder-{seat_id}"),
        assigned_evidence_refs=[],
        quinte_run_id=run_id,
        quinte_snapshot_manifest=snapshot,
        quinte_snapshot_manifest_ref="quinte-run/input/snapshot-manifest.json",
        quinte_snapshot_manifest_sha256=digest_file(run / "input" / "snapshot-manifest.json"),
    )
    atomic_write_json(root / "evidence-mapping-receipt.json", mapping)
    dossier = {
        "dossier_version": "1.0",
        "seat_id": seat_id,
        "profile_id": profile["profile_id"],
        "profile_ref": "profile.json",
        "profile_sha256": digest_file(root / "profile.json"),
        "reviewer_profile_ref": "reviewer-profile",
        "reviewer_profile_sha256": digest_tree(
            reviewer_profile,
            [
                path.relative_to(reviewer_profile)
                for path in reviewer_profile.rglob("*")
                if path.is_file()
            ],
        ),
        "thesis_ref": "thesis.json",
        "thesis_sha256": digest_file(root / "thesis.json"),
        "perspective_input_ref": "perspective-input.json",
        "perspective_input_sha256": digest_file(root / "perspective-input.json"),
        "original_brief_sha256": original_digest,
        "derived_quinte_brief_sha256": brief_digest,
        "quinte_run_ref": "quinte-run",
        "quinte_manifest_sha256": digest_file(run / "manifest.json"),
        "quinte_result_sha256": digest_file(run / "result.json"),
        "assignment_plan_sha256": None,
        "assigned_evidence_refs": [],
        "evidence_mapping_ref": "evidence-mapping-receipt.json",
        "evidence_mapping_sha256": digest_file(root / "evidence-mapping-receipt.json"),
    }
    atomic_write_json(root / "dossier.json", dossier)
    return root / "dossier.json"


def make_fixture(root: Path) -> list[Path]:
    atomic_write_json(root / "original-brief.json", original_brief())
    return [
        write_seat(root, "seat-m", "mimo"),
        write_seat(root, "seat-d", "deepseek"),
        write_seat(root, "seat-g", "openai"),
    ]


def assignment_plan(root: Path, *, trial_id: str) -> Path:
    checks = ["citation entailment", "contradiction scan", "high-risk closure"]
    seats = []
    dossier_paths = {path.parent.name: path for path in root.glob("seat-*/dossier.json")}
    for seat_id, family, focus in (
        ("seat-m", "mimo", "multimodal evidence reconstruction"),
        ("seat-d", "deepseek", "failure-chain challenge"),
        ("seat-g", "openai", "author-consistency and conclusion audit"),
    ):
        dossier = json.loads(dossier_paths[seat_id].read_text())
        result = json.loads(
            (dossier_paths[seat_id].parent / dossier["quinte_run_ref"] / "result.json").read_text()
        )
        binding = result["seat_binding"]
        seats.append(
            {
                "seat_id": seat_id,
                "family": binding["family"],
                "provider": binding["provider"],
                "text_model": binding["text_model"],
                "multimodal_model": binding["multimodal_model"],
                "profile_id": dossier["profile_id"],
                "profile_source_sha256": dossier["reviewer_profile_sha256"],
                "container_service": seat_id,
                "image_digest": "sha256:" + {"mimo": "4", "deepseek": "5", "openai": "6"}[family] * 64,
                "primary_focus": [focus],
                "mandatory_global_checks": list(checks),
                "evidence_refs": [],
                "carrier_capabilities": {
                    "carrier_id": family,
                    "snapshot_media_classes": ["document"],
                    "multimodal_media_types": [],
                    "allow_sampled_video": False,
                },
                "cost_rationale": "Use only where this family adds a distinct check.",
                "independence_class": "distinct_family_and_profile",
                "limitations": [],
            }
        )
    reviews = [
        {
            "reviewer_seat_id": reviewer,
            "subject_seat_id": subject,
            "review_kind": "artifact_review",
            "required_checks": ["challenge unsupported claims", "preserve material dissent"],
            "evidence_refs": [],
            "limitations": ["Original evidence is not exposed in artifact-review mode."],
        }
        for reviewer in ("seat-d", "seat-g", "seat-m")
        for subject in ("seat-d", "seat-g", "seat-m")
        if reviewer != subject
    ]
    value = bind_assignment_plan(
        {
            "assignment_plan_version": "1.0",
            "trial_id": trial_id,
            "objective": "Reduce decision-relevant residual uncertainty.",
            "global_checks": checks,
            "seats": seats,
            "cross_review_obligations": reviews,
            "finale_condition": {
                "allowed_outcomes": ["BLOCK", "ESCALATE", "PASS"],
                "material_residual_states": ["bounded_escalation", "closed", "falsified"],
                "required_receipts": ["evidence coverage", "residual reduction"],
                "stop_rule": "Stop when expected information gain is below the declared threshold.",
            },
            "limitations": ["One trial does not estimate a true error rate."],
        }
    )
    path = root / f"assignment-{trial_id}.json"
    atomic_write_json(path, value)
    return path


def finding(identifier: str, source_ref: str, severity: str = "HIGH") -> dict[str, Any]:
    return {
        "id": identifier,
        "severity": severity,
        "type": "evidence_gap",
        "finding": f"Finding {identifier}",
        "evidence_refs": [],
        "source_refs": [source_ref],
        "disposition": "unresolved",
        "required_closure": "human_review",
        "closure_state": "open",
        "closure_evidence": [],
        "scope": "release gate",
    }


def profiled_review_fields(payload: dict[str, Any]) -> dict[str, Any]:
    methodology = payload["reviewer_methodology"]
    return {
        "reviewer_profile_binding": payload["reviewer_profile_binding"],
        "methodology_trace": [
            {
                "kind": "method",
                "method": methodology["methods"][0],
                "application": "Applied this declared method to the anonymous dossier.",
            },
            {
                "kind": "failure_check",
                "method": methodology["failure_checks"][0],
                "application": "Applied this declared failure check to challenge the conclusion.",
            },
        ],
    }


def _profile_content_digest(root: Path) -> str:
    return digest_tree(
        root,
        [
            path.relative_to(root)
            for path in root.rglob("*")
            if path.is_file() and path.name != "COMPOSITION.json"
        ],
    )
