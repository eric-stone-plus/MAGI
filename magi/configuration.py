"""Deterministic production configuration and assignment-plan generation."""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

from .assignment import bind_assignment_plan
from .errors import ContractError
from .evidence import MULTIMODAL_IMAGE_TYPES, check_carrier_capabilities
from .io import atomic_write_json, read_json


SEATS = ("seat-m", "seat-d", "seat-g")
FOCUS = {
    "seat-m": ["formal invariants and multimodal evidence reconstruction"],
    "seat-d": ["failure-chain challenge and counterexample search"],
    "seat-g": ["provenance, arithmetic, and conclusion consistency audit"],
}
GLOBAL_CHECKS = [
    "citation entailment",
    "contradiction scan",
    "high-risk closure",
    "original-question and action-boundary preservation",
]
# Production evidence policy: identity is frozen by seat; exposure is capability-aware.
# OpenAI/Codex is cost-controlled and does not receive original media in assignment.
SEAT_EVIDENCE_POLICY = {
    "seat-m": "multimodal_primary",
    "seat-d": "text_document_only",
    "seat-g": "artifact_provenance_only",
}


def require_finale_container_execution(execution: dict[str, Any]) -> dict[str, Any]:
    """Production Finale must declare the isolated Compose final-adjudicator path."""

    if not isinstance(execution, dict):
        raise ContractError("final adjudicator execution must be an object")
    if execution.get("mode") != "container":
        raise ContractError("final adjudicator execution.mode must be container")
    if execution.get("service") != "final-adjudicator":
        raise ContractError(
            "final adjudicator execution.service must be final-adjudicator"
        )
    digest = execution.get("image_digest")
    if not isinstance(digest, str) or not _digest(digest):
        raise ContractError("final adjudicator execution.image_digest must be a sha256 digest")
    return execution


def generate_production_config(
    *,
    repo_root: Path,
    trial_dir: Path,
    trial_id: str,
    evidence_manifest: Path,
    profile_sources: dict[str, Path],
    image_digest: str,
    output_dir: Path,
) -> dict[str, Path]:
    """Write builders, agents, and the frozen three-seat assignment plan."""

    root = repo_root.resolve()
    trial = trial_dir.resolve()
    output = output_dir.resolve()
    if not trial_id.strip():
        raise ContractError("trial_id must be non-empty")
    if not _digest(image_digest):
        raise ContractError("image_digest must be a sha256 digest")
    manifest = read_json(evidence_manifest.resolve())
    evidence_items = _evidence_items(manifest)
    seats: list[dict[str, Any]] = []
    builders: dict[str, Any] = {}
    agents: dict[str, Any] = {}
    for seat_id in SEATS:
        seat_config = read_json(root / "container" / "seats" / f"{seat_id}.json")
        if seat_config.get("seat_id") != seat_id:
            raise ContractError(f"seat config id mismatch for {seat_id}")
        profile = profile_sources[seat_id].resolve()
        profile_digest = _profile_tree_digest(profile)
        assigned_items = assign_evidence_for_seat(seat_id, seat_config, evidence_items)
        assigned_refs = sorted(item["evidence_ref"] for item in assigned_items)
        carrier = carrier_capabilities_for_seat(seat_config, assigned_items)
        # Always validate the assigned subset (empty means no original media).
        # Never pass None here — that would check the whole manifest and break DeepSeek/Codex.
        check_carrier_capabilities(manifest, carrier, evidence_refs=assigned_refs)
        seats.append(
            {
                "seat_id": seat_id,
                "family": seat_config["model_family"],
                "provider": seat_config["provider"],
                "text_model": seat_config["text_model"],
                "multimodal_model": seat_config["multimodal_model"],
                "profile_id": seat_config["profile_id"],
                "profile_source_sha256": profile_digest,
                "container_service": seat_id,
                "image_digest": image_digest,
                "primary_focus": FOCUS[seat_id],
                "mandatory_global_checks": list(GLOBAL_CHECKS),
                "evidence_refs": assigned_refs,
                "carrier_capabilities": carrier,
                "cost_rationale": _cost_rationale(seat_id),
                "independence_class": "distinct_family_profile_and_container",
                "limitations": sorted(
                    set(_seat_limitations(seat_id, assigned_refs, evidence_items))
                ),
            }
        )
        builders[seat_id] = {
            "argv": [str(root / "scripts" / "host" / "magi-seat.sh"), "agent"],
            "timeout_seconds": 7200,
            "pass_env": [
                f"MAGI_SEAT_{seat_id[-1].upper()}_PROFILE",
                f"MAGI_SEAT_{seat_id[-1].upper()}_SECRET_FILE",
            ],
        }
        frozen_profile = trial / "dossiers" / seat_id / "reviewer-profile"
        agents[seat_id] = {
            "argv": [
                str(root / "scripts" / "host" / "magi-seat.sh"),
                "reviewer-agent",
                "--seat",
                seat_id,
            ],
            "timeout_seconds": 3600,
            "pass_env": [
                f"MAGI_SEAT_{seat_id[-1].upper()}_PROFILE",
                f"MAGI_SEAT_{seat_id[-1].upper()}_CONFIG",
                f"MAGI_SEAT_{seat_id[-1].upper()}_SECRET_FILE",
            ],
            "reviewer_profile_mode": "hermes_profile",
            "profile_source": str(frozen_profile),
            "execution": _execution(seat_config, seat_id, image_digest),
        }
    # Review containers do not mount original evidence yet — claim only artifact review.
    reviews = [
        {
            "reviewer_seat_id": reviewer,
            "subject_seat_id": subject,
            "review_kind": "artifact_review",
            "required_checks": [
                "challenge unsupported claims",
                "preserve material dissent",
                "trace every material challenge to a subject source",
            ],
            "evidence_refs": [],
            "limitations": sorted(
                {
                    "Review is limited to frozen artifacts; original evidence is not mounted in review containers."
                }
            ),
        }
        for reviewer in SEATS
        for subject in SEATS
        if reviewer != subject
    ]
    assignment = bind_assignment_plan(
        {
            "assignment_plan_version": "1.0",
            "trial_id": trial_id,
            "objective": (
                "Reduce decision-relevant residual uncertainty through three independent "
                "profiles, complete single-family QUINTE runs, six directed reviews, and Finale."
            ),
            "global_checks": list(GLOBAL_CHECKS),
            "seats": seats,
            "cross_review_obligations": reviews,
            "finale_condition": {
                "allowed_outcomes": ["BLOCK", "ESCALATE", "PASS"],
                "material_residual_states": ["bounded_escalation", "closed", "falsified"],
                "required_receipts": ["evidence coverage", "residual reduction"],
                "stop_rule": (
                    "Stop after Finale when all material residuals are closed, falsified, or "
                    "bounded for explicit escalation; stop an optional repeated arm when it "
                    "adds no material novel finding."
                ),
            },
            "limitations": sorted(
                {
                    "Dynamic evidence assignment changes focus and exposure only; frozen family/profile/container identity never swaps mid-trial.",
                    "One trial does not estimate a universal confidence percentage or true error rate.",
                }
            ),
        }
    )
    final_config = read_json(root / "container" / "seats" / "seat-g.json")
    agent_config = {
        "config_version": "1.0",
        "seat_agents": agents,
        "final_adjudicator": {
            "argv": [str(root / "scripts" / "host" / "magi-seat.sh"), "final-agent"],
            "timeout_seconds": 3600,
            "pass_env": [
                "MAGI_FINAL_CONFIG",
                "MAGI_FINAL_SECRET_FILE",
                "MAGI_REQUIRED_IMAGE_DIGEST",
                "MAGI_SEAT_IMAGE",
            ],
            # Production Finale launches Compose service final-adjudicator.
            "execution": _execution(
                final_config,
                "final-adjudicator",
                image_digest,
                mode="container",
            ),
        },
    }
    paths = {
        "assignment_plan": output / "assignment-plan.json",
        "builders": output / "builders.json",
        "agents": output / "agents.json",
    }
    output.mkdir(parents=True, exist_ok=True)
    atomic_write_json(paths["assignment_plan"], assignment)
    atomic_write_json(paths["builders"], {"builder_version": "1.0", "seat_builders": builders})
    atomic_write_json(paths["agents"], agent_config)
    return paths


def assign_evidence_for_seat(
    seat_id: str, seat_config: dict[str, Any], evidence_items: list[dict[str, Any]]
) -> list[dict[str, Any]]:
    """Return the carrier-readable, policy-allowed subset for one frozen seat."""

    family = seat_config.get("model_family")
    if not isinstance(family, str) or not family.strip():
        raise ContractError(f"seat {seat_id} model_family is required")
    policy = SEAT_EVIDENCE_POLICY.get(seat_id)
    if policy is None:
        raise ContractError(f"unknown seat id for evidence policy: {seat_id}")
    if policy == "artifact_provenance_only":
        return []
    if policy == "text_document_only":
        if family != "deepseek":
            raise ContractError(
                f"seat {seat_id} text_document_only policy requires deepseek family"
            )
        return [
            item
            for item in evidence_items
            if item.get("media_class") == "document"
            and "snapshot" in set(item.get("exposure_modes") or [])
            and not _is_derived_frame(item)
        ]
    if policy == "multimodal_primary":
        if family != "mimo":
            raise ContractError(
                f"seat {seat_id} multimodal_primary policy requires mimo family"
            )
        selected: list[dict[str, Any]] = []
        for item in evidence_items:
            if _is_derived_frame(item):
                if item.get("media_type") in MULTIMODAL_IMAGE_TYPES:
                    selected.append(item)
                continue
            modes = set(item.get("exposure_modes") or [])
            media_class = item.get("media_class")
            media_type = item.get("media_type")
            if media_class == "video":
                # Raw video is not a native carrier; derived frames are assigned separately.
                continue
            if "snapshot" in modes and media_class in {"document", "image"}:
                selected.append(item)
                continue
            if (
                "multimodal_attachment" in modes
                and media_type in MULTIMODAL_IMAGE_TYPES
            ):
                selected.append(item)
        return selected
    raise ContractError(f"unsupported evidence policy for {seat_id}: {policy}")


def carrier_capabilities_for_seat(
    seat_config: dict[str, Any], assigned_items: list[dict[str, Any]]
) -> dict[str, Any]:
    """Declare carrier capability matching family policy and the assigned subset."""

    family = seat_config["model_family"]
    seat_id = seat_config["seat_id"]
    policy = SEAT_EVIDENCE_POLICY[seat_id]
    if policy == "artifact_provenance_only" or family == "openai":
        return {
            "carrier_id": family,
            "snapshot_media_classes": ["document"],
            "multimodal_media_types": [],
            "allow_sampled_video": False,
        }
    if policy == "text_document_only" or family == "deepseek":
        return {
            "carrier_id": family,
            "snapshot_media_classes": ["document"],
            "multimodal_media_types": [],
            "allow_sampled_video": False,
        }
    # MiMo multimodal primary
    multimodal_types = sorted(
        {
            item["media_type"]
            for item in assigned_items
            if item.get("media_type") in MULTIMODAL_IMAGE_TYPES
            and (
                "multimodal_attachment" in set(item.get("exposure_modes") or [])
                or _is_derived_frame(item)
            )
        }
    )
    snapshot_classes = sorted(
        {
            item["media_class"]
            for item in assigned_items
            if "snapshot" in set(item.get("exposure_modes") or [])
            and item.get("media_class") in {"document", "image"}
        }
        or {"document", "image"}
    )
    has_frames = any(_is_derived_frame(item) for item in assigned_items)
    return {
        "carrier_id": family,
        "snapshot_media_classes": snapshot_classes,
        "multimodal_media_types": multimodal_types,
        "allow_sampled_video": has_frames,
    }


def _evidence_items(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [*manifest.get("source_files", []), *manifest.get("derived_frames", [])]


def _is_derived_frame(item: dict[str, Any]) -> bool:
    if "source_id" in item:
        return True
    reference = item.get("evidence_ref")
    return isinstance(reference, str) and reference.startswith("snapshot://derived/")


def _cost_rationale(seat_id: str) -> str:
    return {
        "seat-m": "MiMo owns original multimodal evidence once per phase; stop when declared information-gain is met.",
        "seat-d": "DeepSeek runs text/document counterexample search once; never burn images on a text-only carrier.",
        "seat-g": "Codex audits frozen artifacts, arithmetic, citations, and provenance; original media is not re-exposed.",
    }[seat_id]


def _seat_limitations(
    seat_id: str, assigned_refs: list[str], all_items: list[dict[str, Any]]
) -> list[str]:
    total = len(all_items)
    assigned = len(assigned_refs)
    boundary = {
        "seat-m": (
            f"Evidence boundary: multimodal primary inspects {assigned} of {total} staged "
            "items (documents, images, and derived frames when present)."
        ),
        "seat-d": (
            f"Evidence boundary: text/document carrier receives {assigned} of {total} staged "
            "items; image, video, audio, binary, and derived frames are excluded."
        ),
        "seat-g": (
            f"Evidence boundary: original media is not exposed ({assigned} of {total} staged "
            "items assigned); this seat verifies frozen dossiers, arithmetic, citations, and provenance."
        ),
    }[seat_id]
    return [
        "Distinct providers and containers reduce, but do not prove absence of correlated error.",
        boundary,
    ]


def _profile_tree_digest(profile: Path) -> str:
    receipt = read_json(profile / "COMPOSITION.json")
    digest = receipt.get("composed_content_sha256")
    if not _digest(digest):
        raise ContractError(f"profile composition receipt is invalid: {profile}")
    hasher = hashlib.sha256()
    for path in sorted(item for item in profile.rglob("*") if item.is_file()):
        relative = path.relative_to(profile).as_posix().encode()
        raw = path.read_bytes()
        hasher.update(len(relative).to_bytes(8, "big"))
        hasher.update(relative)
        hasher.update(len(raw).to_bytes(8, "big"))
        hasher.update(raw)
    return "sha256:" + hasher.hexdigest()


def _execution(
    seat: dict[str, Any],
    service: str,
    image_digest: str,
    *,
    mode: str = "container",
) -> dict[str, str]:
    if mode not in {"container", "host"}:
        raise ContractError("execution mode must be container or host")
    return {
        "family": seat["model_family"],
        "provider": seat["provider"],
        "text_model": seat["text_model"],
        "multimodal_model": seat["multimodal_model"],
        "mode": mode,
        "service": service,
        "image_digest": image_digest,
    }


def _digest(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 71 and value.startswith("sha256:")
