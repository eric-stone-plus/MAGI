"""Resumable triadic exchange and final adjudication runtime."""

from __future__ import annotations

import itertools
import os
import re
import secrets
import shutil
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .contracts import (
    validate_final,
    validate_product_summary,
    validate_residual_reduction_receipt,
    validate_review,
)
from .errors import ContractError, StateError
from .io import atomic_write_json, digest_file, digest_value, read_json, runtime_digest
from .runner import CommandRunner, CommandSpec
from .seat import SeatProduct, load_seat_dossier, validate_trial_seats
from .verifier import build_highball_trace, build_residual_reduction_receipt, verify_final
from .verifier import all_evidence_refs
from .assignment import validate_assignment_plan
from .evidence import check_carrier_capabilities


TRIAL_FIELDS = {
    "trial_version",
    "trial_id",
    "created_at",
    "updated_at",
    "status",
    "action_boundary",
    "original_brief_ref",
    "original_brief_sha256",
    "seat_slots",
    "dossiers",
    "anonymization_salt_sha256",
    "alias_map_ref",
    "alias_map_sha256",
    "review_refs",
    "review_sha256",
    "review_execution_sha256",
    "final_verdict_ref",
    "final_verdict_sha256",
    "final_execution_receipt_ref",
    "final_execution_receipt_sha256",
    "residual_trace_ref",
    "residual_trace_sha256",
    "agent_config_sha256",
    "agent_config_ref",
    "builder_config_sha256",
    "builder_config_ref",
    "runtime_sha256",
    "evidence_manifest_ref",
    "evidence_manifest_sha256",
    "evidence_coverage_ref",
    "evidence_coverage_sha256",
    "assignment_plan_ref",
    "assignment_plan_sha256",
    "residual_reduction_ref",
    "residual_reduction_sha256",
    "error",
}
STATUSES = {
    "awaiting_dossiers",
    "building_dossiers",
    "dossiers_frozen",
    "cross_reviewing",
    "cross_reviewed",
    "finalizing",
    "completed",
    "failed",
}
ACTION_BOUNDARIES = {"none", "reversible", "protected_write", "irreversible"}
PORTABLE_ID = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


class TrialRuntime:
    def __init__(self, trial_dir: Path, runner: CommandRunner | None = None) -> None:
        self.root = trial_dir.resolve()
        self.state_path = self.root / "trial.json"
        self.runner = runner or CommandRunner()

    @classmethod
    def initialize(
        cls,
        trial_dir: Path,
        *,
        trial_id: str,
        seat_slots: list[str],
        action_boundary: str,
        original_brief: Path,
    ) -> "TrialRuntime":
        if not _is_portable_id(trial_id):
            raise ContractError("trial_id must be a 1-128 character portable identifier")
        if action_boundary not in ACTION_BOUNDARIES:
            raise ContractError("action_boundary is invalid")
        if len(seat_slots) != 3 or len(set(seat_slots)) != 3 or not all(
            _is_portable_id(item) for item in seat_slots
        ):
            raise ContractError("seat_slots must contain three distinct portable IDs")
        runtime = cls(trial_dir)
        if runtime.state_path.exists():
            raise StateError(f"trial already exists: {runtime.state_path}")
        now = _now()
        runtime.root.mkdir(parents=True, exist_ok=True)
        source_brief = read_json(original_brief.resolve())
        _validate_original_brief(source_brief)
        original_copy = runtime.root / "input" / "original-brief.json"
        if original_copy.exists():
            raise StateError(f"trial input already exists: {original_copy}")
        atomic_write_json(original_copy, source_brief)
        state = {
            "trial_version": "1.0",
            "trial_id": trial_id,
            "created_at": now,
            "updated_at": now,
            "status": "awaiting_dossiers",
            "action_boundary": action_boundary,
            "original_brief_ref": _relative_or_absolute(original_copy, runtime.root),
            "original_brief_sha256": digest_file(original_copy),
            "seat_slots": seat_slots,
            "dossiers": {},
            "anonymization_salt_sha256": None,
            "alias_map_ref": None,
            "alias_map_sha256": None,
            "review_refs": [],
            "review_sha256": {},
            "review_execution_sha256": {},
            "final_verdict_ref": None,
            "final_verdict_sha256": None,
            "final_execution_receipt_ref": None,
            "final_execution_receipt_sha256": None,
            "residual_trace_ref": None,
            "residual_trace_sha256": None,
            "agent_config_sha256": None,
            "agent_config_ref": None,
            "builder_config_sha256": None,
            "builder_config_ref": None,
            "runtime_sha256": runtime_digest(),
            "evidence_manifest_ref": None,
            "evidence_manifest_sha256": None,
            "evidence_coverage_ref": None,
            "evidence_coverage_sha256": None,
            "assignment_plan_ref": None,
            "assignment_plan_sha256": None,
            "residual_reduction_ref": None,
            "residual_reduction_sha256": None,
            "error": None,
        }
        atomic_write_json(runtime.state_path, state)
        return runtime

    def register_dossier(self, seat_id: str, dossier_path: Path) -> dict[str, Any]:
        state = self.load_state()
        self._require_status(state, {"awaiting_dossiers", "building_dossiers"})
        if seat_id not in state["seat_slots"]:
            raise ContractError(f"seat_id is not a trial slot: {seat_id}")
        _reject_source_symlinks(dossier_path)
        seat = load_seat_dossier(dossier_path)
        self._validate_seat_assignment(state, seat)
        if seat.seat_id != seat_id:
            raise ContractError("registered seat ID does not match dossier")
        if seat.dossier["original_brief_sha256"] != state["original_brief_sha256"]:
            raise ContractError("dossier is not bound to this trial's original brief")
        original = read_json(_resolve_ref(self.root, state["original_brief_ref"]))
        _verify_original_fields(original, seat)
        dossiers = dict(state["dossiers"])
        frozen_dir = self.root / "dossiers" / seat_id
        frozen_dossier = frozen_dir / "dossier.json"
        existing = dossiers.get(seat_id)
        if existing is not None:
            existing_seat = load_seat_dossier(_resolve_ref(self.root, existing))
            if existing_seat.dossier != seat.dossier:
                raise StateError(f"seat {seat_id} already has a different frozen dossier")
            return state
        if frozen_dir.exists():
            # An atomic rename can complete immediately before state persistence. Adopt
            # that validated copy on resume instead of making the trial unrecoverable.
            frozen_seat = load_seat_dossier(frozen_dossier)
            if frozen_seat.dossier != seat.dossier:
                raise StateError(f"frozen dossier destination already exists: {frozen_dir}")
            _make_read_only(frozen_dir)
        else:
            frozen_dir.parent.mkdir(parents=True, exist_ok=True)
            temporary = Path(
                tempfile.mkdtemp(prefix=f".{seat_id}.freeze-", dir=frozen_dir.parent)
            )
            try:
                shutil.copytree(
                    seat.dossier_path.parent,
                    temporary,
                    symlinks=False,
                    ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
                    dirs_exist_ok=True,
                )
                frozen_seat = load_seat_dossier(temporary / "dossier.json")
                if frozen_seat.dossier != seat.dossier:
                    raise ContractError("frozen dossier copy differs from source dossier")
                os.replace(temporary, frozen_dir)
                _make_read_only(frozen_dir)
            finally:
                if temporary.exists():
                    _remove_tree(temporary)
        frozen_seat = load_seat_dossier(frozen_dossier)
        self._validate_seat_assignment(state, frozen_seat)
        if frozen_seat.dossier != seat.dossier:
            raise ContractError("frozen dossier copy differs from source dossier")
        ref = _relative_or_absolute(frozen_dossier, self.root)
        dossiers[seat_id] = ref
        state["dossiers"] = dossiers
        if len(dossiers) == 3:
            validate_trial_seats(self._load_seats(state))
            state["status"] = "dossiers_frozen"
        self.save_state(state)
        return state

    def build_dossiers(
        self, config_path: Path, assignment_plan_path: Path | None = None
    ) -> dict[str, Any]:
        state = self.load_state()
        self._require_status(state, {"awaiting_dossiers", "building_dossiers", "dossiers_frozen"})
        if state["status"] == "dossiers_frozen":
            return state
        config = _load_builder_config(config_path, set(state["seat_slots"]))
        self._require_evidence_binding(state)
        self._bind_assignment_plan(state, assignment_plan_path)
        config_digest = digest_value(read_json(config_path.resolve()))
        if state["builder_config_sha256"] is None:
            frozen = self.root / "private" / "builder-config.json"
            atomic_write_json(frozen, read_json(config_path))
            state["builder_config_sha256"] = config_digest
            state["builder_config_ref"] = _relative_or_absolute(frozen, self.root)
        elif state["builder_config_sha256"] != config_digest:
            raise StateError("seat builder config changed after dossier generation began")
        state["status"] = "building_dossiers"
        self.save_state(state)
        for seat_id in state["seat_slots"]:
            if seat_id in state["dossiers"]:
                continue
            output_dir = self.root / "seat-work" / seat_id
            dossier = output_dir / "dossier.json"
            if dossier.is_file():
                try:
                    self.register_dossier(seat_id, dossier)
                    continue
                except (ContractError, StateError):
                    pass
            if output_dir.exists() or output_dir.is_symlink():
                _archive_incomplete_seat_work(self.root, seat_id, output_dir)
        state = self.load_state()
        pending = [seat_id for seat_id in state["seat_slots"] if seat_id not in state["dossiers"]]
        if not pending:
            return state
        candidates: dict[str, Path] = {}
        errors: dict[str, Exception] = {}

        def build_one(seat_id: str) -> Path:
            output_dir = self.root / "seat-work" / seat_id
            payload = {
                "task": "magi_build_seat",
                "contract_version": "1.0",
                "trial_id": state["trial_id"],
                "trial_dir": str(self.root),
                "seat_id": seat_id,
                "original_brief_path": str(
                    _resolve_ref(self.root, state["original_brief_ref"])
                ),
                "original_brief_sha256": state["original_brief_sha256"],
                "seat_output_dir": str(output_dir),
                "evidence_manifest_path": (
                    str(_resolve_ref(self.root, state["evidence_manifest_ref"]))
                    if state["evidence_manifest_ref"] is not None
                    else None
                ),
                "evidence_manifest_sha256": state["evidence_manifest_sha256"],
                "assignment_plan_path": str(
                    _resolve_ref(self.root, state["assignment_plan_ref"])
                ),
                "assignment_plan_sha256": state["assignment_plan_sha256"],
            }
            result = self.runner.run(config["seat_builders"][seat_id], payload)
            if set(result) != {"seat_id", "dossier_path"}:
                raise ContractError("seat builder output must contain only seat_id and dossier_path")
            if result.get("seat_id") != seat_id:
                raise ContractError("seat builder output seat_id does not match assignment")
            dossier_path = result.get("dossier_path")
            if not isinstance(dossier_path, str) or not dossier_path.strip():
                raise ContractError("seat builder output dossier_path must be non-empty")
            candidate = Path(dossier_path)
            if not candidate.is_absolute():
                candidate = (self.root / candidate).resolve()
            output_root = output_dir.resolve()
            if candidate.resolve() != output_root and output_root not in candidate.resolve().parents:
                raise ContractError("seat builder dossier_path escapes assigned seat output directory")
            return candidate

        # Builders are independent model/container pipelines. Only their
        # immutable outputs are committed to trial state, in slot order, after
        # all subprocesses return.
        with ThreadPoolExecutor(max_workers=len(pending)) as executor:
            futures = {executor.submit(build_one, seat_id): seat_id for seat_id in pending}
            for future in as_completed(futures):
                seat_id = futures[future]
                try:
                    candidates[seat_id] = future.result()
                except Exception as exc:
                    errors[seat_id] = exc

        for seat_id in state["seat_slots"]:
            candidate = candidates.get(seat_id)
            if candidate is None:
                continue
            try:
                self.register_dossier(seat_id, candidate)
            except Exception as exc:
                errors[seat_id] = exc
        if errors:
            first_failed = next(seat_id for seat_id in state["seat_slots"] if seat_id in errors)
            raise errors[first_failed]
        return self.load_state()

    def run(self, config_path: Path) -> dict[str, Any]:
        state = self.load_state()
        if state["status"] == "completed":
            return self.verify_product()
        self._require_status(
            state, {"dossiers_frozen", "cross_reviewing", "cross_reviewed", "finalizing"}
        )
        config = _load_config(config_path, set(state["seat_slots"]), self.root)
        config_digest = digest_value(read_json(config_path.resolve()))
        if state["agent_config_sha256"] is None:
            frozen = self.root / "private" / "agent-config.json"
            atomic_write_json(frozen, read_json(config_path))
            state["agent_config_sha256"] = config_digest
            state["agent_config_ref"] = _relative_or_absolute(frozen, self.root)
            self.save_state(state)
        elif state["agent_config_sha256"] != config_digest:
            raise StateError("agent config changed after trial execution began")
        seats = self._load_seats(state)
        validate_trial_seats(seats)
        aliases = self._ensure_aliases(state, seats)
        seats_by_alias = {aliases[seat.seat_id]: seat for seat in seats}
        reviews = self._run_reviews(state, config, seats_by_alias)
        verdict = self._run_final_adjudicator(state, config, seats_by_alias, reviews)
        trace = build_highball_trace(
            verdict, seats_by_alias, reviews, action_boundary=state["action_boundary"]
        )
        trace_path = self.root / "final" / "residual-trace.json"
        atomic_write_json(trace_path, trace)
        state["residual_trace_ref"] = _relative_or_absolute(trace_path, self.root)
        state["residual_trace_sha256"] = digest_file(trace_path)
        reduction_path = self.root / "final" / "residual-reduction-receipt.json"
        atomic_write_json(
            reduction_path,
            build_residual_reduction_receipt(verdict, seats_by_alias, reviews),
        )
        state["residual_reduction_ref"] = _relative_or_absolute(reduction_path, self.root)
        state["residual_reduction_sha256"] = digest_file(reduction_path)
        self._build_evidence_coverage(state)
        state["status"] = "completed"
        state["error"] = None
        self.save_state(state)
        return self.verify_product()

    def _bind_evidence_manifest(self, state: dict[str, Any]) -> None:
        from .evidence import MANIFEST_REF, validate_evidence_manifest

        manifest_path = self.root / MANIFEST_REF
        if not manifest_path.is_file():
            return
        manifest = read_json(manifest_path)
        validate_evidence_manifest(
            manifest, trial_root=self.root, staged_root=manifest_path.parent
        )
        if manifest["original_brief_sha256"] != state["original_brief_sha256"]:
            raise ContractError("staged evidence does not bind the trial original brief")
        reference = _relative_or_absolute(manifest_path, self.root)
        sha256 = digest_file(manifest_path)
        if state["evidence_manifest_ref"] is None:
            state["evidence_manifest_ref"] = reference
            state["evidence_manifest_sha256"] = sha256
            self.save_state(state)
        elif (
            state["evidence_manifest_ref"] != reference
            or state["evidence_manifest_sha256"] != sha256
        ):
            raise StateError("evidence manifest changed after dossier generation began")

    def _bind_assignment_plan(
        self, state: dict[str, Any], assignment_plan_path: Path | None
    ) -> None:
        from .assignment import validate_assignment_plan

        if state["assignment_plan_ref"] is None:
            if assignment_plan_path is None:
                raise ContractError("dossier generation requires a frozen assignment plan")
            source = assignment_plan_path.resolve()
            plan = validate_assignment_plan(read_json(source))
            if plan["trial_id"] != state["trial_id"]:
                raise ContractError("assignment plan trial_id does not match the trial")
            if {item["seat_id"] for item in plan["seats"]} != set(state["seat_slots"]):
                raise ContractError("assignment plan seats do not match the trial")
            frozen = self.root / "private" / "assignment-plan.json"
            atomic_write_json(frozen, plan)
            state["assignment_plan_ref"] = _relative_or_absolute(frozen, self.root)
            state["assignment_plan_sha256"] = digest_file(frozen)
            self.save_state(state)
            return
        if assignment_plan_path is not None:
            candidate = validate_assignment_plan(read_json(assignment_plan_path.resolve()))
            if digest_value(candidate) != digest_value(
                read_json(_resolve_ref(self.root, state["assignment_plan_ref"]))
            ):
                raise StateError("assignment plan changed after dossier generation began")

    def _assignment_plan(self, state: dict[str, Any]) -> dict[str, Any]:
        reference = state.get("assignment_plan_ref")
        if reference is None:
            raise ContractError("trial has no frozen assignment plan")
        return validate_assignment_plan(read_json(_resolve_ref(self.root, reference)))

    def _validate_seat_assignment(
        self, state: dict[str, Any], seat: SeatProduct
    ) -> dict[str, Any]:
        plan = self._assignment_plan(state)
        matches = [item for item in plan["seats"] if item["seat_id"] == seat.seat_id]
        if len(matches) != 1:
            raise ContractError(f"assignment plan does not bind seat {seat.seat_id} exactly once")
        assigned = matches[0]
        actual = seat.result["seat_binding"]
        for field in ("family", "provider", "text_model", "multimodal_model"):
            if assigned[field] != actual[field]:
                raise ContractError(
                    f"seat {seat.seat_id} {field} does not match frozen assignment plan"
                )
        if assigned["profile_id"] != seat.dossier["profile_id"]:
            raise ContractError(
                f"seat {seat.seat_id} profile_id does not match frozen assignment plan"
            )
        if assigned["profile_source_sha256"] != seat.dossier["reviewer_profile_sha256"]:
            raise ContractError(
                f"seat {seat.seat_id} profile source does not match frozen assignment plan"
            )
        manifest = read_json(_resolve_ref(self.root, state["evidence_manifest_ref"]))
        known_evidence = {
            item["evidence_ref"]
            for item in [*manifest["source_files"], *manifest["derived_frames"]]
        }
        if not set(assigned["evidence_refs"]).issubset(known_evidence):
            raise ContractError(
                f"seat {seat.seat_id} assignment exposes evidence outside the frozen manifest"
            )
        # Validate only the seat's assigned subset so text-only carriers never
        # fail closed on unassigned multimodal items present in the same trial.
        check_carrier_capabilities(
            manifest,
            assigned["carrier_capabilities"],
            evidence_refs=list(assigned["evidence_refs"]),
        )
        return assigned

    def _build_evidence_coverage(self, state: dict[str, Any]) -> None:
        if state["evidence_manifest_ref"] is None:
            return
        from .evidence import build_coverage_receipt

        artifacts = [
            _resolve_ref(self.root, state["dossiers"][seat_id])
            for seat_id in state["seat_slots"]
        ] + [
            _resolve_ref(self.root, reference) for reference in state["review_refs"]
        ] + [
            _resolve_ref(self.root, state["final_verdict_ref"]),
            _resolve_ref(self.root, state["residual_trace_ref"]),
        ]
        output = self.root / "final" / "evidence-coverage-receipt.json"
        receipt = build_coverage_receipt(
            self.root,
            artifacts=artifacts,
            declared_limitations=(
                "Coverage records citations; it does not prove model perception.",
            ),
            output=output,
        )
        state["evidence_coverage_ref"] = _relative_or_absolute(output, self.root)
        state["evidence_coverage_sha256"] = digest_file(output)

    def _require_evidence_binding(self, state: dict[str, Any]) -> None:
        self._bind_evidence_manifest(state)
        if state["evidence_manifest_ref"] is None:
            raise ContractError(
                "dossier generation requires staged evidence or an explicit no-evidence manifest"
            )

    def status(self) -> dict[str, Any]:
        state = self.load_state()
        if state["status"] == "completed":
            return self.verify_product()
        return state

    def load_state(self) -> dict[str, Any]:
        state = read_json(self.state_path)
        unknown = sorted(set(state) - TRIAL_FIELDS)
        missing = sorted(TRIAL_FIELDS - set(state))
        if unknown or missing:
            details = []
            if unknown:
                details.append(f"unknown: {', '.join(unknown)}")
            if missing:
                details.append(f"missing: {', '.join(missing)}")
            raise ContractError("invalid trial state (" + "; ".join(details) + ")")
        if state.get("trial_version") != "1.0" or state.get("status") not in STATUSES:
            raise ContractError("unsupported trial state version or status")
        if state.get("action_boundary") not in ACTION_BOUNDARIES:
            raise ContractError("trial action_boundary is invalid")
        if state.get("runtime_sha256") != runtime_digest():
            raise ContractError("MAGI runtime changed since trial initialization")
        for field in ("trial_id", "created_at", "updated_at", "original_brief_ref"):
            if not isinstance(state.get(field), str) or not state[field].strip():
                raise ContractError(f"trial {field} must be a non-empty string")
        if not _is_portable_id(state["trial_id"]):
            raise ContractError("trial trial_id must be a portable identifier")
        for field in (
            "original_brief_sha256",
            "runtime_sha256",
            "anonymization_salt_sha256",
            "alias_map_sha256",
            "final_verdict_sha256",
            "final_execution_receipt_sha256",
            "residual_trace_sha256",
            "agent_config_sha256",
            "builder_config_sha256",
            "evidence_manifest_sha256",
            "evidence_coverage_sha256",
            "assignment_plan_sha256",
            "residual_reduction_sha256",
        ):
            value = state.get(field)
            if value is not None and (
                not isinstance(value, str)
                or len(value) != 71
                or not value.startswith("sha256:")
            ):
                raise ContractError(f"trial {field} is not a sha256 digest")
        if digest_file(_resolve_ref(self.root, state["original_brief_ref"])) != state["original_brief_sha256"]:
            raise ContractError("trial original brief digest does not match artifact")
        slots = state.get("seat_slots")
        if (
            not isinstance(slots, list)
            or len(slots) != 3
            or len(set(slots)) != 3
            or not all(_is_portable_id(item) for item in slots)
        ):
            raise ContractError("trial seat_slots are invalid")
        dossiers = state.get("dossiers")
        if not isinstance(dossiers, dict) or not set(dossiers).issubset(set(slots)):
            raise ContractError("trial dossiers must be an object")
        if not isinstance(state.get("review_refs"), list):
            raise ContractError("trial review_refs must be an array")
        if not isinstance(state.get("review_sha256"), dict):
            raise ContractError("trial review_sha256 must be an object")
        if not isinstance(state.get("review_execution_sha256"), dict):
            raise ContractError("trial review_execution_sha256 must be an object")
        _verify_state_artifact(self.root, state, "final_verdict_ref", "final_verdict_sha256")
        _verify_state_artifact(
            self.root,
            state,
            "final_execution_receipt_ref",
            "final_execution_receipt_sha256",
        )
        _verify_state_artifact(self.root, state, "residual_trace_ref", "residual_trace_sha256")
        _verify_state_artifact(self.root, state, "alias_map_ref", "alias_map_sha256")
        _verify_state_artifact(
            self.root, state, "evidence_manifest_ref", "evidence_manifest_sha256"
        )
        _verify_state_artifact(
            self.root, state, "evidence_coverage_ref", "evidence_coverage_sha256"
        )
        _verify_state_artifact(
            self.root, state, "assignment_plan_ref", "assignment_plan_sha256"
        )
        _verify_state_artifact(
            self.root, state, "residual_reduction_ref", "residual_reduction_sha256"
        )
        _verify_config_artifact(
            self.root, state, "agent_config_ref", "agent_config_sha256"
        )
        _verify_config_artifact(
            self.root, state, "builder_config_ref", "builder_config_sha256"
        )
        for reference in state["review_refs"]:
            expected = state["review_sha256"].get(reference)
            if expected is None or digest_file(_resolve_ref(self.root, reference)) != expected:
                raise ContractError(f"stored cross-review digest mismatch: {reference}")
            receipt_ref = _review_execution_ref(reference)
            receipt_digest = state["review_execution_sha256"].get(receipt_ref)
            if receipt_digest is None or digest_file(_resolve_ref(self.root, receipt_ref)) != receipt_digest:
                raise ContractError(f"stored reviewer execution receipt mismatch: {receipt_ref}")
            receipt = read_json(_resolve_ref(self.root, receipt_ref))
            _validate_execution_receipt(receipt, f"reviewer execution receipt {receipt_ref}")
            if receipt["output_artifact_sha256"] != expected:
                raise ContractError(f"reviewer execution receipt output mismatch: {receipt_ref}")
        if state["final_execution_receipt_ref"] is not None:
            final_receipt = read_json(
                _resolve_ref(self.root, state["final_execution_receipt_ref"])
            )
            _validate_execution_receipt(final_receipt, "final execution receipt")
            if final_receipt["output_artifact_sha256"] != state["final_verdict_sha256"]:
                raise ContractError("final execution receipt output does not match verdict")
        _validate_state_coherence(state)
        return state

    def verify_product(self) -> dict[str, Any]:
        state = self.load_state()
        if state["status"] != "completed":
            raise StateError("MAGI product is not completed")
        seats = self._load_seats(state)
        validate_trial_seats(seats)
        for seat in seats:
            self._validate_seat_assignment(state, seat)
        aliases = self._ensure_aliases(state, seats, allow_create=False)
        seats_by_alias = {aliases[seat.seat_id]: seat for seat in seats}
        reviews = self._load_completed_reviews(state, seats_by_alias)
        verdict = read_json(_resolve_ref(self.root, state["final_verdict_ref"]))
        verify_final(verdict, seats_by_alias, reviews)
        expected_trace = build_highball_trace(
            verdict,
            seats_by_alias,
            reviews,
            action_boundary=state["action_boundary"],
        )
        actual_trace = read_json(_resolve_ref(self.root, state["residual_trace_ref"]))
        if actual_trace != expected_trace:
            raise ContractError("stored residual trace does not match deterministic reconstruction")
        expected_reduction = build_residual_reduction_receipt(
            verdict, seats_by_alias, reviews
        )
        actual_reduction = validate_residual_reduction_receipt(
            read_json(_resolve_ref(self.root, state["residual_reduction_ref"]))
        )
        if actual_reduction != expected_reduction:
            raise ContractError(
                "stored residual-reduction receipt does not match deterministic reconstruction"
            )
        if state["evidence_coverage_ref"] is not None:
            from .evidence import validate_coverage_receipt

            validate_coverage_receipt(
                read_json(_resolve_ref(self.root, state["evidence_coverage_ref"])),
                trial_root=self.root,
                replay=True,
            )
        self._verify_seat_mappings(state, seats)
        original = read_json(_resolve_ref(self.root, state["original_brief_ref"]))
        identity = {
            "product_version": "1.0",
            "trial_id": state["trial_id"],
            "status": state["status"],
            "runtime_sha256": state["runtime_sha256"],
            "agent_config_sha256": state["agent_config_sha256"],
            "builder_config_sha256": state["builder_config_sha256"],
            "assignment_plan_ref": state["assignment_plan_ref"],
            "assignment_plan_sha256": state["assignment_plan_sha256"],
            "evidence_manifest_ref": state["evidence_manifest_ref"],
            "evidence_manifest_sha256": state["evidence_manifest_sha256"],
            "evidence_coverage_ref": state["evidence_coverage_ref"],
            "evidence_coverage_sha256": state["evidence_coverage_sha256"],
            "original_brief_sha256": state["original_brief_sha256"],
            "action_binding_sha256": original["action_binding_sha256"],
            "question": original["question"],
            "action_scope": original.get("action_scope"),
            "affected_paths": original.get("affected_paths", []),
            "final_decision": verdict["decision"],
            "final_dissent": verdict["dissent"],
            "final_verdict_ref": state["final_verdict_ref"],
            "final_verdict_sha256": state["final_verdict_sha256"],
            "residual_trace_ref": state["residual_trace_ref"],
            "residual_trace_sha256": state["residual_trace_sha256"],
            "residual_reduction_ref": state["residual_reduction_ref"],
            "residual_reduction_sha256": state["residual_reduction_sha256"],
            "seats": [
                {
                    "seat_id": seat.seat_id,
                    "family": seat.family,
                    "provider": seat.result["seat_binding"]["provider"],
                    "text_model": seat.result["seat_binding"]["text_model"],
                    "multimodal_model": seat.result["seat_binding"]["multimodal_model"],
                    "profile_sha256": seat.dossier["profile_sha256"],
                    "thesis_sha256": seat.dossier["thesis_sha256"],
                    "dossier_ref": state["dossiers"][seat.seat_id],
                    "dossier_sha256": digest_file(seat.dossier_path),
                    "quinte_run_id": seat.run_id,
                    "quinte_manifest_sha256": seat.dossier["quinte_manifest_sha256"],
                    "quinte_result_sha256": seat.result_sha256,
                    "assigned_evidence_refs": list(
                        seat.dossier.get("assigned_evidence_refs") or []
                    ),
                    "evidence_mapping_ref": (
                        (
                            Path(state["dossiers"][seat.seat_id]).parent
                            / Path(seat.dossier["evidence_mapping_ref"]).name
                        ).as_posix()
                        if seat.dossier.get("evidence_mapping_ref") is not None
                        else None
                    ),
                    "evidence_mapping_sha256": seat.dossier.get("evidence_mapping_sha256"),
                }
                for seat in sorted(seats, key=lambda item: item.seat_id)
            ],
            "cross_reviews": self._product_review_receipts(state),
            "final_adjudicator": self._product_final_adjudicator(state),
        }
        summary = {**identity, "product_sha256": digest_value(identity)}
        summary = validate_product_summary(summary)
        atomic_write_json(self.root / "final" / "product-summary.json", summary)
        return summary

    def _product_review_receipts(self, state: dict[str, Any]) -> list[dict[str, str]]:
        receipts: list[dict[str, str]] = []
        seats = self._load_seats(state)
        aliases = self._ensure_aliases(state, seats, allow_create=False)
        seats_by_id = {seat.seat_id: seat for seat in seats}
        config = _load_config(
            _resolve_ref(self.root, state["agent_config_ref"]),
            set(state["seat_slots"]),
            self.root,
        )
        for reference in state["review_refs"]:
            review = read_json(_resolve_ref(self.root, reference))
            binding = review["reviewer_profile_binding"]
            seat_id = next(
                seat_id for seat_id, alias in aliases.items() if alias == review["reviewer_alias"]
            )
            seat = seats_by_id[seat_id]
            command = config["seat_agents"][seat_id]
            execution_ref = _review_execution_ref(reference)
            receipts.append(
                {
                    "artifact_ref": reference,
                    "sha256": state["review_sha256"][reference],
                    "reviewer_seat_id": seat_id,
                    "reviewer_family": seat.result["seat_binding"]["family"],
                    "reviewer_provider": seat.result["seat_binding"]["provider"],
                    "reviewer_text_model": seat.result["seat_binding"]["text_model"],
                    "reviewer_multimodal_model": seat.result["seat_binding"]["multimodal_model"],
                    "reviewer_profile_id": binding["profile_id"],
                    "reviewer_profile_sha256": binding["profile_sha256"],
                    "reviewer_profile_source_sha256": binding["profile_source_sha256"],
                    "reviewer_agent_config_sha256": command.identity_sha256(),
                    "methodology_trace_sha256": digest_value(review["methodology_trace"]),
                    "reviewer_execution_receipt_ref": execution_ref,
                    "reviewer_execution_receipt_sha256": state["review_execution_sha256"][execution_ref],
                }
            )
        return receipts

    def _product_final_adjudicator(self, state: dict[str, Any]) -> dict[str, str]:
        config = _load_config(
            _resolve_ref(self.root, state["agent_config_ref"]),
            set(state["seat_slots"]),
            self.root,
        )
        command = config["final_adjudicator"]
        execution = _required_execution(command, "final_adjudicator")
        return {
            "family": execution["family"],
            "provider": execution["provider"],
            "text_model": execution["text_model"],
            "multimodal_model": execution["multimodal_model"],
            "agent_config_sha256": command.identity_sha256(),
            "execution_mode": execution["mode"],
            "execution_receipt_ref": state["final_execution_receipt_ref"],
            "execution_receipt_sha256": state["final_execution_receipt_sha256"],
        }

    def save_state(self, state: dict[str, Any]) -> None:
        state["updated_at"] = _now()
        atomic_write_json(self.state_path, state)

    def _load_seats(self, state: dict[str, Any]) -> list[SeatProduct]:
        dossiers = state["dossiers"]
        if set(dossiers) != set(state["seat_slots"]):
            raise StateError("all three frozen dossiers are required")
        return [load_seat_dossier(_resolve_ref(self.root, dossiers[slot])) for slot in state["seat_slots"]]

    def _verify_seat_mappings(
        self, state: dict[str, Any], seats: list[SeatProduct]
    ) -> None:
        """Replay mapping receipts against the frozen assignment plan when present."""

        from .mapping import replay_mapping_receipt, validate_mapping_receipt

        plan_ref = state.get("assignment_plan_ref")
        plan = None
        if plan_ref is not None:
            plan = self._assignment_plan(state)
        seats_by_id = {item["seat_id"]: item for item in (plan["seats"] if plan else [])}
        evidence_manifest = None
        evidence_sha = state.get("evidence_manifest_sha256")
        if state.get("evidence_manifest_ref") is not None:
            evidence_manifest = read_json(
                _resolve_ref(self.root, state["evidence_manifest_ref"])
            )
        for seat in seats:
            dossier = seat.dossier
            mapping_ref = dossier.get("evidence_mapping_ref")
            if mapping_ref is None:
                continue
            mapping_path = seat.dossier_path.parent / mapping_ref
            if not mapping_path.is_file():
                mapping_path = _resolve_ref(self.root, mapping_ref)
            receipt = validate_mapping_receipt(read_json(mapping_path))
            if plan is not None:
                assigned = seats_by_id.get(seat.seat_id)
                if assigned is None:
                    raise ContractError(
                        f"assignment plan missing seat {seat.seat_id} for mapping verify"
                    )
                if receipt["assigned_evidence_refs"] != list(assigned["evidence_refs"]):
                    raise ContractError(
                        f"seat {seat.seat_id} mapping assigned refs disagree with assignment plan"
                    )
                # Production seats bind the trial assignment plan digest into the
                # dossier/mapping. Fixture dossiers may leave it null until builders
                # rewrite them; only enforce when the dossier claims a plan digest.
                dossier_plan = dossier.get("assignment_plan_sha256")
                if dossier_plan is not None:
                    if dossier_plan != state.get("assignment_plan_sha256"):
                        raise ContractError(
                            f"seat {seat.seat_id} dossier assignment_plan_sha256 disagrees with trial"
                        )
                    if receipt["assignment_plan_sha256"] != state["assignment_plan_sha256"]:
                        raise ContractError(
                            f"seat {seat.seat_id} mapping assignment plan digest disagrees with trial"
                        )
            if evidence_manifest is not None and evidence_sha is not None:
                if receipt["evidence_manifest_sha256"] != evidence_sha:
                    # Production seats must bind the trial evidence set. Fixture
                    # dossiers may carry a placeholder empty mapping until builders
                    # rewrite them against the staged manifest.
                    if receipt["assigned_evidence_refs"]:
                        raise ContractError(
                            f"seat {seat.seat_id} mapping evidence_manifest_sha256 disagrees with trial"
                        )
                    continue
                snapshot = read_json(seat.run_dir / "input" / "snapshot-manifest.json")
                replay_mapping_receipt(
                    receipt,
                    evidence_manifest=evidence_manifest,
                    evidence_manifest_sha256=evidence_sha,
                    assignment_plan_sha256=receipt["assignment_plan_sha256"],
                    assigned_evidence_refs=list(receipt["assigned_evidence_refs"]),
                    quinte_snapshot_manifest=snapshot,
                    quinte_snapshot_manifest_sha256=receipt[
                        "quinte_snapshot_manifest_sha256"
                    ],
                )

    def _ensure_aliases(
        self,
        state: dict[str, Any],
        seats: list[SeatProduct],
        *,
        allow_create: bool = True,
    ) -> dict[str, str]:
        if state["alias_map_ref"] is not None:
            alias_doc = read_json(_resolve_ref(self.root, state["alias_map_ref"]))
            if set(alias_doc) != {"alias_map_version", "seat_to_alias", "seat_result_digests"}:
                raise ContractError("stored anonymous alias map has invalid fields")
            if alias_doc.get("alias_map_version") != "1.0":
                raise ContractError("stored anonymous alias map version is unsupported")
            aliases = alias_doc.get("seat_to_alias")
            if not isinstance(aliases, dict) or set(aliases) != {seat.seat_id for seat in seats}:
                raise ContractError("stored anonymous alias map is invalid")
            if set(aliases.values()) != {"Expert-1", "Expert-2", "Expert-3"}:
                raise ContractError("stored anonymous aliases are invalid")
            expected_results = {seat.seat_id: seat.result_sha256 for seat in seats}
            if alias_doc.get("seat_result_digests") != expected_results:
                raise ContractError("stored anonymous alias map does not match frozen dossiers")
            return aliases
        if not allow_create:
            raise ContractError("completed MAGI product is missing its frozen alias map")
        salt = secrets.token_bytes(32)
        ranked = sorted(seats, key=lambda seat: digest_value([salt.hex(), seat.result_sha256]))
        aliases = {seat.seat_id: f"Expert-{index}" for index, seat in enumerate(ranked, 1)}
        alias_doc = {
            "alias_map_version": "1.0",
            "seat_to_alias": aliases,
            "seat_result_digests": {seat.seat_id: seat.result_sha256 for seat in seats},
        }
        alias_path = self.root / "private" / "alias-map.json"
        atomic_write_json(alias_path, alias_doc)
        state["anonymization_salt_sha256"] = digest_value(salt.hex())
        state["alias_map_ref"] = _relative_or_absolute(alias_path, self.root)
        state["alias_map_sha256"] = digest_file(alias_path)
        state["status"] = "cross_reviewing"
        self.save_state(state)
        return aliases

    def _run_reviews(
        self,
        state: dict[str, Any],
        config: dict[str, Any],
        seats_by_alias: dict[str, SeatProduct],
    ) -> list[dict[str, Any]]:
        expected_pairs = list(itertools.permutations(sorted(seats_by_alias), 2))
        aliases_to_ids = {alias: seat.seat_id for alias, seat in seats_by_alias.items()}
        obligations = {
            (item["reviewer_seat_id"], item["subject_seat_id"]): item
            for item in self._assignment_plan(state)["cross_review_obligations"]
        }
        refs_by_pair: dict[tuple[str, str], str] = {}
        for ref in state["review_refs"]:
            review = read_json(_resolve_ref(self.root, ref))
            pair = (review.get("reviewer_alias"), review.get("subject_alias"))
            if pair in refs_by_pair or pair not in expected_pairs:
                raise ContractError("stored cross-review set has duplicate or invalid assignment")
            _validate_cross_review(review, pair[0], pair[1], seats_by_alias, stored=True)
            refs_by_pair[pair] = ref
        for reviewer, subject in expected_pairs:
            if (reviewer, subject) in refs_by_pair:
                continue
            reviewer_seat = seats_by_alias[reviewer]
            subject_view = seats_by_alias[subject].anonymous_view(subject)
            command = _seat_command(config, reviewer_seat.seat_id)
            if command.reviewer_profile_mode != "hermes_profile":
                raise ContractError(
                    f"seat agent {reviewer_seat.seat_id} must execute cross-review through its immutable Hermes profile"
                )
            if command.profile_source is None:
                raise ContractError("Hermes profile reviewer has no immutable profile source")
            configured_profile = Path(command.profile_source).expanduser().resolve()
            if configured_profile != reviewer_seat.reviewer_profile_path:
                raise ContractError(
                    f"seat agent {reviewer_seat.seat_id} is not bound to its frozen dossier profile"
                )
            reviewer_profile = reviewer_seat.reviewer_profile()
            reviewer_binding = reviewer_seat.reviewer_profile_binding()
            obligation = obligations[(aliases_to_ids[reviewer], aliases_to_ids[subject])]
            anonymous_obligation = {
                "review_kind": obligation["review_kind"],
                "required_checks": obligation["required_checks"],
                "evidence_refs": obligation["evidence_refs"],
                "limitations": obligation["limitations"],
            }
            packet = {
                "task": "magi_cross_review",
                "contract_version": "1.1",
                "reviewer_alias": reviewer,
                "subject_alias": subject,
                "original_question": reviewer_seat.result["question"],
                "reviewer_profile_binding": reviewer_binding,
                "reviewer_methodology": {
                    "discipline": reviewer_profile["discipline"],
                    "epistemic_lens": reviewer_profile["epistemic_lens"],
                    "methods": reviewer_profile["methods"],
                    "failure_checks": reviewer_profile["failure_checks"],
                    "instructions": reviewer_profile["instructions"],
                },
                "subject_dossier": subject_view,
                "review_obligation": anonymous_obligation,
                "assigned_source_ref_prefix": f"review:{reviewer}>{subject}:finding:",
                "instructions": _review_instructions(),
            }
            review = self.runner.run(command, packet)
            _validate_cross_review(review, reviewer, subject, seats_by_alias)
            path = self.root / "reviews" / f"{reviewer}--{subject}.json"
            atomic_write_json(path, review)
            refs_by_pair[(reviewer, subject)] = _relative_or_absolute(path, self.root)
            state["review_sha256"][refs_by_pair[(reviewer, subject)]] = digest_file(path)
            execution = _required_execution(command, f"seat agent {reviewer_seat.seat_id}")
            receipt_path = path.with_name(path.stem + "--execution.json")
            receipt = _execution_receipt(
                kind="cross_review",
                service=execution["service"],
                seat_id=reviewer_seat.seat_id,
                image_digest=execution["image_digest"],
                profile_sha256=reviewer_binding["profile_source_sha256"],
                agent_config_sha256=command.identity_sha256(),
                input_sha256=digest_value(packet),
                output_sha256=digest_file(path),
                execution_mode=execution["mode"],
            )
            atomic_write_json(receipt_path, receipt)
            receipt_ref = _relative_or_absolute(receipt_path, self.root)
            state["review_execution_sha256"][receipt_ref] = digest_file(receipt_path)
            state["review_refs"] = [refs_by_pair[pair] for pair in expected_pairs if pair in refs_by_pair]
            self.save_state(state)
        state["status"] = "cross_reviewed"
        self.save_state(state)
        return [read_json(_resolve_ref(self.root, refs_by_pair[pair])) for pair in expected_pairs]

    def _load_completed_reviews(
        self, state: dict[str, Any], seats_by_alias: dict[str, SeatProduct]
    ) -> list[dict[str, Any]]:
        expected_pairs = list(itertools.permutations(sorted(seats_by_alias), 2))
        refs_by_pair: dict[tuple[str, str], str] = {}
        for reference in state["review_refs"]:
            review = read_json(_resolve_ref(self.root, reference))
            pair = (review.get("reviewer_alias"), review.get("subject_alias"))
            if pair not in expected_pairs or pair in refs_by_pair:
                raise ContractError("completed cross-review set is invalid")
            _validate_cross_review(review, pair[0], pair[1], seats_by_alias, stored=True)
            refs_by_pair[pair] = reference
        if set(refs_by_pair) != set(expected_pairs):
            raise ContractError("completed MAGI product does not have all six cross-reviews")
        return [read_json(_resolve_ref(self.root, refs_by_pair[pair])) for pair in expected_pairs]

    def _run_final_adjudicator(
        self,
        state: dict[str, Any],
        config: dict[str, Any],
        seats_by_alias: dict[str, SeatProduct],
        reviews: list[dict[str, Any]],
    ) -> dict[str, Any]:
        if state["final_verdict_ref"] is not None:
            verdict = read_json(_resolve_ref(self.root, state["final_verdict_ref"]))
            return verify_final(verdict, seats_by_alias, reviews)
        state["status"] = "finalizing"
        self.save_state(state)
        packet = {
            "task": "magi_final_adjudication",
            "contract_version": "1.0",
            "question": next(iter(seats_by_alias.values())).result["question"],
            "action_boundary": state["action_boundary"],
            "dossiers": [
                seat.adjudicator_view(alias)
                for alias, seat in sorted(seats_by_alias.items())
            ],
            "cross_reviews": reviews,
            "canonical_seat_source_refs": {
                alias: [f"seat:{alias}:residual:{item['id']}" for item in seat.result["residuals"]]
                for alias, seat in sorted(seats_by_alias.items())
            },
            "required_dissent": sorted(
                {
                    dissent.strip()
                    for alias, seat in seats_by_alias.items()
                    for dissent in seat.anonymous_view(alias)["quinte_result"]["dissent"]
                    if dissent.strip()
                }
                | {
                    dissent.strip()
                    for review in reviews
                    for dissent in review["dissent"]
                    if dissent.strip()
                }
            ),
            "instructions": _final_adjudicator_instructions(),
        }
        verdict = self.runner.run(config["final_adjudicator"], packet)
        verify_final(verdict, seats_by_alias, reviews)
        verdict_path = self.root / "final" / "verdict.json"
        atomic_write_json(verdict_path, verdict)
        state["final_verdict_ref"] = _relative_or_absolute(verdict_path, self.root)
        state["final_verdict_sha256"] = digest_file(verdict_path)
        command = config["final_adjudicator"]
        execution = _required_execution(command, "final_adjudicator")
        receipt_path = self.root / "final" / "adjudicator-execution-receipt.json"
        receipt = _execution_receipt(
            kind="final_adjudication",
            service=execution["service"],
            seat_id=None,
            image_digest=execution["image_digest"],
            profile_sha256=None,
            agent_config_sha256=command.identity_sha256(),
            input_sha256=digest_value(packet),
            output_sha256=digest_file(verdict_path),
            execution_mode=execution["mode"],
        )
        atomic_write_json(receipt_path, receipt)
        state["final_execution_receipt_ref"] = _relative_or_absolute(receipt_path, self.root)
        state["final_execution_receipt_sha256"] = digest_file(receipt_path)
        self.save_state(state)
        return verdict

    @staticmethod
    def _require_status(state: dict[str, Any], allowed: set[str]) -> None:
        if state["status"] not in allowed:
            raise StateError(f"operation not allowed while trial is {state['status']}")


def _load_config(path: Path, seat_slots: set[str], trial_root: Path) -> dict[str, Any]:
    raw = read_json(path)
    fields = {"config_version", "seat_agents", "final_adjudicator"}
    unknown = sorted(set(raw) - fields)
    missing = sorted(fields - set(raw))
    if unknown or missing or raw.get("config_version") != "1.0":
        raise ContractError("agent config must be a closed version 1.0 contract")
    agents = raw.get("seat_agents")
    if not isinstance(agents, dict) or set(agents) != seat_slots:
        raise ContractError("agent config must bind exactly the three trial seat IDs")
    specs = {
        key: CommandSpec.from_value(value, f"seat_agents.{key}")
        for key, value in agents.items()
    }
    for seat_id, spec in specs.items():
        _required_execution(spec, f"seat_agents.{seat_id}")
        if spec.reviewer_profile_mode != "hermes_profile":
            raise ContractError(
                f"seat_agents.{seat_id} must use reviewer_profile_mode=hermes_profile"
            )
        expected = (trial_root / "dossiers" / seat_id / "reviewer-profile").resolve()
        if Path(spec.profile_source or "").expanduser().resolve() != expected:
            raise ContractError(
                f"seat_agents.{seat_id}.profile_source must be the frozen dossier profile"
            )
    final_adjudicator = CommandSpec.from_value(
        raw.get("final_adjudicator"), "final_adjudicator"
    )
    execution = _required_execution(final_adjudicator, "final_adjudicator")
    from .configuration import require_finale_container_execution

    require_finale_container_execution(execution)
    return {
        "config_version": "1.0",
        "seat_agents": specs,
        "final_adjudicator": final_adjudicator,
    }


def _load_builder_config(path: Path, seat_slots: set[str]) -> dict[str, Any]:
    raw = read_json(path)
    fields = {"builder_version", "seat_builders"}
    if set(raw) != fields or raw.get("builder_version") != "1.0":
        raise ContractError("seat builder config must be a closed version 1.0 contract")
    builders = raw.get("seat_builders")
    if not isinstance(builders, dict) or set(builders) != seat_slots:
        raise ContractError("seat builder config must bind exactly the three trial seat IDs")
    return {
        "builder_version": "1.0",
        "seat_builders": {
            key: CommandSpec.from_value(value, f"seat_builders.{key}")
            for key, value in builders.items()
        },
    }


def _seat_command(config: dict[str, Any], seat_id: str) -> CommandSpec:
    try:
        return config["seat_agents"][seat_id]
    except KeyError as exc:
        raise ContractError(f"agent config has no command for seat {seat_id}") from exc


def _review_instructions() -> dict[str, Any]:
    return {
        "independence": "Review only the anonymous subject dossier; do not infer identity.",
        "coverage": "Expose contradictions, omissions, evidence gaps, unsupported closures, and dissent.",
        "methodology": "Act through the supplied immutable reviewer methodology. Record at least one declared method and one declared failure check in methodology_trace, with how each affected this review.",
        "output": "Return exactly the closed cross-review 1.1 JSON contract, including the supplied reviewer_profile_binding verbatim.",
        "source_refs": "Each finding source_refs must contain its canonical review ref, supplied by the harness assignment.",
    }


def _final_adjudicator_instructions() -> dict[str, Any]:
    return {
        "authority": "Issue an actionable PASS, BLOCK, or ESCALATE final verdict.",
        "no_vote": "Synthesize evidence; do not hide dissent or use unqualified majority voting.",
        "coverage": "Every HIGH/CRITICAL/P0 seat residual and cross-review finding must appear through source_refs.",
        "dissent": "Copy the supplied canonical seat and cross-review dissent array exactly into verdict.dissent.",
        "closure": "Never claim closure without closure evidence and scope.",
        "output": "Return exactly the closed final-verdict 1.0 JSON contract.",
    }


def _relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def _required_execution(spec: CommandSpec, label: str) -> dict[str, str]:
    if spec.execution is None:
        raise ContractError(f"{label}.execution is required for provenance")
    return spec.execution


def _review_execution_ref(review_ref: str) -> str:
    path = Path(review_ref)
    return path.with_name(path.stem + "--execution.json").as_posix()


def _execution_receipt(
    *,
    kind: str,
    service: str,
    seat_id: str | None,
    image_digest: str,
    profile_sha256: str | None,
    agent_config_sha256: str,
    input_sha256: str,
    output_sha256: str,
    execution_mode: str,
) -> dict[str, Any]:
    return {
        "receipt_version": "1.0",
        "kind": kind,
        "service": service,
        "seat_id": seat_id,
        "image_digest": image_digest,
        "profile_sha256": profile_sha256,
        "agent_config_sha256": agent_config_sha256,
        "input_packet_sha256": input_sha256,
        "output_artifact_sha256": output_sha256,
        "execution_mode": execution_mode,
    }


def _validate_execution_receipt(value: dict[str, Any], label: str) -> None:
    fields = {
        "receipt_version", "kind", "service", "seat_id", "image_digest",
        "profile_sha256", "agent_config_sha256", "input_packet_sha256",
        "output_artifact_sha256", "execution_mode",
    }
    if set(value) != fields or value.get("receipt_version") != "1.0":
        raise ContractError(f"{label} has a closed-field/version mismatch")
    for field in ("kind", "service", "execution_mode"):
        if not isinstance(value.get(field), str) or not value[field].strip():
            raise ContractError(f"{label}.{field} must be a non-empty string")
    if value.get("seat_id") is not None and not _is_portable_id(value["seat_id"]):
        raise ContractError(f"{label}.seat_id is invalid")
    for field in (
        "image_digest", "agent_config_sha256", "input_packet_sha256",
        "output_artifact_sha256",
    ):
        candidate = value.get(field)
        if not isinstance(candidate, str) or len(candidate) != 71 or not candidate.startswith("sha256:"):
            raise ContractError(f"{label}.{field} is not a sha256 digest")
    profile = value.get("profile_sha256")
    if profile is not None and (
        not isinstance(profile, str) or len(profile) != 71 or not profile.startswith("sha256:")
    ):
        raise ContractError(f"{label}.profile_sha256 is not a sha256 digest")


def _resolve_ref(root: Path, reference: str) -> Path:
    if not isinstance(reference, str) or not reference.strip():
        raise ContractError("trial artifact reference must be a non-empty relative path")
    path = Path(reference)
    if path.is_absolute():
        raise ContractError(f"trial artifact reference must be relative: {reference}")
    candidate = (root / path).resolve()
    if candidate != root and root not in candidate.parents:
        raise ContractError(f"trial artifact reference escapes trial directory: {reference}")
    return candidate


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds").replace("+00:00", "Z")


def _is_portable_id(value: Any) -> bool:
    return isinstance(value, str) and PORTABLE_ID.fullmatch(value) is not None


def _verify_state_artifact(
    root: Path, state: dict[str, Any], ref_field: str, digest_field: str
) -> None:
    reference = state.get(ref_field)
    expected = state.get(digest_field)
    if reference is None and expected is None:
        return
    if not isinstance(reference, str) or not isinstance(expected, str):
        raise ContractError(f"trial {ref_field}/{digest_field} binding is incomplete")
    if digest_file(_resolve_ref(root, reference)) != expected:
        raise ContractError(f"stored artifact digest mismatch: {reference}")


def _verify_config_artifact(
    root: Path, state: dict[str, Any], ref_field: str, digest_field: str
) -> None:
    reference = state.get(ref_field)
    expected = state.get(digest_field)
    if reference is None and expected is None:
        return
    if not isinstance(reference, str) or not isinstance(expected, str):
        raise ContractError(f"trial {ref_field}/{digest_field} binding is incomplete")
    document = read_json(_resolve_ref(root, reference))
    # Config identity is semantic JSON, independent of host newline formatting.
    if digest_value(document) != expected:
        raise ContractError(f"stored configuration digest mismatch: {reference}")


def _validate_state_coherence(state: dict[str, Any]) -> None:
    status = state["status"]
    dossier_count = len(state["dossiers"])
    review_count = len(state["review_refs"])
    if set(state["review_sha256"]) != set(state["review_refs"]):
        raise ContractError("trial cross-review digest index does not match review refs")
    expected_execution_refs = {_review_execution_ref(ref) for ref in state["review_refs"]}
    if set(state["review_execution_sha256"]) != expected_execution_refs:
        raise ContractError("trial reviewer execution receipt index does not match review refs")
    if review_count != len(set(state["review_refs"])) or review_count > 6:
        raise ContractError("trial cross-review refs are duplicated or exceed six")
    if status == "building_dossiers" and state["builder_config_sha256"] is None:
        raise ContractError("trial dossier-building state lacks a frozen builder config")
    if status in {
        "dossiers_frozen",
        "cross_reviewing",
        "cross_reviewed",
        "finalizing",
        "completed",
    } and dossier_count != 3:
        raise ContractError(f"trial status {status} requires three dossiers")
    if status in {"cross_reviewing", "cross_reviewed", "finalizing", "completed"}:
        if state["agent_config_sha256"] is None or state["alias_map_ref"] is None:
            raise ContractError(f"trial status {status} lacks frozen execution identity")
    if status in {"cross_reviewed", "finalizing", "completed"} and review_count != 6:
        raise ContractError(f"trial status {status} requires six cross-reviews")
    if status == "completed":
        for field in (
            "final_verdict_ref",
            "final_verdict_sha256",
            "final_execution_receipt_ref",
            "final_execution_receipt_sha256",
            "residual_trace_ref",
            "residual_trace_sha256",
            "residual_reduction_ref",
            "residual_reduction_sha256",
        ):
            if state[field] is None:
                raise ContractError(f"completed trial is missing {field}")


def _validate_cross_review(
    review: dict[str, Any],
    reviewer: str,
    subject: str,
    seats_by_alias: dict[str, SeatProduct],
    *,
    stored: bool = False,
) -> None:
    reviewer_seat = seats_by_alias[reviewer]
    validate_review(
        review,
        reviewer,
        subject,
        expected_profile_binding=reviewer_seat.reviewer_profile_binding(),
        profile=reviewer_seat.reviewer_profile(),
    )
    valid_subject_evidence = all_evidence_refs({subject: seats_by_alias[subject]})
    valid_subject_sources = {
        f"seat:{subject}:residual:{item['id']}"
        for item in seats_by_alias[subject].result["residuals"]
    }
    source_severity = {
        f"seat:{subject}:residual:{item['id']}": item["severity"]
        for item in seats_by_alias[subject].result["residuals"]
    }
    source_evidence = {
        f"seat:{subject}:residual:{item['id']}": {
            f"seat:{subject}:evidence:{reference}"
            for reference in item["evidence_refs"] + item["closure_evidence"]
            if reference
        }
        for item in seats_by_alias[subject].result["residuals"]
    }
    source_closure_evidence = {
        f"seat:{subject}:residual:{item['id']}": {
            f"seat:{subject}:evidence:{reference}"
            for reference in item["closure_evidence"]
            if reference
        }
        for item in seats_by_alias[subject].result["residuals"]
    }
    prefix = "stored " if stored else ""
    for finding in review["findings"]:
        expected_ref = f"review:{reviewer}>{subject}:finding:{finding['id']}"
        if expected_ref not in finding["source_refs"]:
            raise ContractError(
                f"{prefix}cross-review finding {finding['id']} omits canonical source ref"
            )
        invalid_evidence = sorted(set(finding["evidence_refs"]) - valid_subject_evidence)
        if invalid_evidence:
            raise ContractError(
                f"{prefix}cross-review finding {finding['id']} cites invalid evidence refs"
            )
        invalid_sources = sorted(
            set(finding["source_refs"]) - {expected_ref, *valid_subject_sources}
        )
        if invalid_sources:
            raise ContractError(
                f"{prefix}cross-review finding {finding['id']} cites invalid source refs"
            )
        cited_subject_sources = set(finding["source_refs"]) & valid_subject_sources
        if finding["evidence_refs"] and not cited_subject_sources:
            raise ContractError(
                f"{prefix}cross-review finding {finding['id']} cites evidence without a subject source"
            )
        supported_evidence = set().union(
            *(source_evidence[reference] for reference in cited_subject_sources)
        ) if cited_subject_sources else set()
        if set(finding["evidence_refs"]) - supported_evidence:
            raise ContractError(
                f"{prefix}cross-review finding {finding['id']} cites evidence unrelated to its subject sources"
            )
        invalid_closure_evidence = sorted(
            set(finding["closure_evidence"]) - valid_subject_evidence
        )
        if invalid_closure_evidence:
            raise ContractError(
                f"{prefix}cross-review finding {finding['id']} cites invalid closure evidence"
            )
        supported_closure_evidence = (
            set().union(
                *(source_closure_evidence[reference] for reference in cited_subject_sources)
            )
            if cited_subject_sources
            else set()
        )
        if set(finding["closure_evidence"]) - supported_closure_evidence:
            raise ContractError(
                f"{prefix}cross-review finding {finding['id']} invents closure evidence"
            )
        severity_rank = {"LOW": 0, "MEDIUM": 1, "HIGH": 2, "CRITICAL": 3, "P0": 4}
        highest_cited = max(
            (source_severity[reference] for reference in cited_subject_sources),
            key=severity_rank.__getitem__,
            default=None,
        )
        if highest_cited is not None and severity_rank[finding["severity"]] < severity_rank[highest_cited]:
            raise ContractError(
                f"{prefix}cross-review finding {finding['id']} downgrades a high-risk subject source"
            )
        if finding["closure_state"] in {"closed", "blocked", "waived", "not_applicable"}:
            if not finding["closure_evidence"]:
                raise ContractError(
                    f"{prefix}cross-review finding {finding['id']} claims closure without evidence"
                )
            if not finding["scope"].strip():
                raise ContractError(
                    f"{prefix}cross-review finding {finding['id']} claims closure without scope"
                )


def _reject_source_symlinks(dossier_path: Path) -> None:
    try:
        lexical = dossier_path.absolute()
        root = lexical.parent
        if root.is_symlink() or lexical.is_symlink():
            raise ContractError(f"dossier source contains a symlink: {lexical}")
        for path in root.rglob("*"):
            if path.is_symlink():
                raise ContractError(f"dossier source contains a symlink: {path}")
    except OSError as exc:
        raise ContractError(f"cannot inspect dossier source {dossier_path}: {exc}") from exc


def _remove_tree(root: Path) -> None:
    for directory, directories, files in os.walk(root):
        for name in directories:
            path = Path(directory) / name
            try:
                path.chmod(path.stat().st_mode | 0o700)
            except OSError:
                pass
        for name in files:
            path = Path(directory) / name
            try:
                path.chmod(path.stat().st_mode | 0o200)
            except OSError:
                pass
    try:
        root.chmod(root.stat().st_mode | 0o700)
    except OSError:
        pass
    shutil.rmtree(root, ignore_errors=True)


def _archive_incomplete_seat_work(root: Path, seat_id: str, output_dir: Path) -> None:
    recovery = root / "private" / "failed-seat-work"
    recovery.mkdir(parents=True, exist_ok=True)
    destination = recovery / f"{seat_id}-{secrets.token_hex(8)}"
    try:
        os.replace(output_dir, destination)
    except OSError as exc:
        raise StateError(
            f"cannot archive incomplete seat work {output_dir}: {exc}"
        ) from exc


def _make_read_only(root: Path) -> None:
    directories: list[Path] = []
    for directory, _, files in os.walk(root):
        directories.append(Path(directory))
        for name in files:
            path = Path(directory) / name
            try:
                path.chmod(path.stat().st_mode & ~0o222)
            except OSError as exc:
                raise ContractError(f"cannot freeze dossier artifact {path}: {exc}") from exc
    for path in reversed(directories):
        try:
            path.chmod(path.stat().st_mode & ~0o222)
        except OSError as exc:
            raise ContractError(f"cannot freeze dossier directory {path}: {exc}") from exc


def _validate_original_brief(value: dict[str, Any]) -> None:
    allowed = {
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
    unknown = sorted(set(value) - allowed)
    if unknown:
        raise ContractError(f"original brief has unknown fields: {', '.join(unknown)}")
    missing = sorted({"brief_version", "question", "action_binding_sha256"} - set(value))
    if missing:
        raise ContractError(f"original brief is missing fields: {', '.join(missing)}")
    if value.get("brief_version") != "1.1":
        raise ContractError("original brief version must be 1.1")
    if not isinstance(value.get("question"), str) or not value["question"].strip():
        raise ContractError("original brief question must be non-empty")
    for field in ("evidence_roots", "snapshot_ignore", "attachments", "affected_paths"):
        if field in value and (
            not isinstance(value[field], list)
            or not all(isinstance(item, str) and item for item in value[field])
        ):
            raise ContractError(f"original brief {field} must be a string array")
    if "context" in value and value["context"] is not None and not isinstance(value["context"], str):
        raise ContractError("original brief context must be a string or null")
    if "action_scope" in value and value["action_scope"] is not None and not isinstance(
        value["action_scope"], str
    ):
        raise ContractError("original brief action_scope must be a string or null")
    binding = value.get("action_binding_sha256")
    if not isinstance(binding, str) or re.fullmatch(r"sha256:[a-f0-9]{64}", binding) is None:
        raise ContractError("original brief requires a sha256 action binding")


def _verify_original_fields(original: dict[str, Any], seat: SeatProduct) -> None:
    expected = {
        "question": original["question"],
        "action_scope": original.get("action_scope"),
        "affected_paths": original.get("affected_paths", []),
        "action_binding_sha256": original.get("action_binding_sha256"),
    }
    for field, value in expected.items():
        if seat.brief.get(field) != value:
            raise ContractError(f"seat derived QUINTE brief changed original {field}")
