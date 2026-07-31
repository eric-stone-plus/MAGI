"""Digest-bound mapping between MAGI canonical evidence refs and QUINTE-local refs.

MAGI stages evidence as ``snapshot://source/...`` / ``snapshot://derived/...``.
QUINTE re-snapshots under ``snapshot://root-N/...`` and copies images as
``attachment://attachment-N.*``. This module reconciles the two by staged
bytes (sha256) and exposure mode, fail-closed on missing, duplicate, ambiguous,
or drifted mappings.
"""

from __future__ import annotations

from typing import Any

from .errors import ContractError
from .io import digest_value


RECEIPT_VERSION = "1.0"
RECEIPT_FIELDS = {
    "mapping_receipt_version",
    "seat_id",
    "evidence_manifest_sha256",
    "assignment_plan_sha256",
    "assigned_evidence_refs",
    "quinte_run_id",
    "quinte_snapshot_manifest_ref",
    "quinte_snapshot_manifest_sha256",
    "mappings",
    "unmapped_canonical_refs",
    "unmapped_quinte_local_refs",
    "limitations",
    "receipt_binding_sha256",
}
MAPPING_FIELDS = {
    "canonical_ref",
    "staged_ref",
    "staged_sha256",
    "size_bytes",
    "media_type",
    "media_class",
    "exposure_modes",
    "quinte_local_refs",
    "quinte_entries",
}
QUINTE_ENTRY_FIELDS = {
    "local_ref",
    "kind",
    "source_name",
    "sha256",
    "bytes",
    "media_type",
}


def build_mapping_receipt(
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
    """Build a closed mapping receipt for one seat's assigned evidence."""

    _text(seat_id, "seat_id")
    _digest(evidence_manifest_sha256, "evidence_manifest_sha256")
    _digest(assignment_plan_sha256, "assignment_plan_sha256")
    _digest(quinte_snapshot_manifest_sha256, "quinte_snapshot_manifest_sha256")
    _text(quinte_run_id, "quinte_run_id")
    _text(quinte_snapshot_manifest_ref, "quinte_snapshot_manifest_ref")
    assigned = _sorted_unique_strings(assigned_evidence_refs, "assigned_evidence_refs")
    items = {
        item["evidence_ref"]: item
        for item in [
            *evidence_manifest.get("source_files", []),
            *evidence_manifest.get("derived_frames", []),
        ]
        if isinstance(item, dict) and isinstance(item.get("evidence_ref"), str)
    }
    missing_assigned = sorted(set(assigned) - set(items))
    if missing_assigned:
        raise ContractError(
            "assigned evidence missing from MAGI manifest: " + ", ".join(missing_assigned)
        )

    quinte_by_digest = _index_quinte_by_digest(quinte_snapshot_manifest)
    mappings: list[dict[str, Any]] = []
    used_local: set[str] = set()
    for reference in assigned:
        item = items[reference]
        digest = item.get("sha256")
        _digest(digest, f"canonical {reference}.sha256")
        candidates = list(quinte_by_digest.get(digest, []))
        if not candidates:
            # Empty assignment is fine; non-empty must map unless no original media path.
            raise ContractError(
                f"no QUINTE-local entry matches staged digest for {reference}"
            )
        local_refs = sorted({entry["local_ref"] for entry in candidates})
        overlap = used_local & set(local_refs)
        if overlap:
            raise ContractError(
                "QUINTE-local ref already mapped to another canonical item: "
                + ", ".join(sorted(overlap))
            )
        used_local.update(local_refs)
        # One-to-many is allowed (snapshot + attachment of the same bytes).
        # Ambiguous competing digests for different staged items are blocked above.
        mappings.append(
            {
                "canonical_ref": reference,
                "staged_ref": item["staged_ref"],
                "staged_sha256": digest,
                "size_bytes": item["size_bytes"],
                "media_type": item["media_type"],
                "media_class": item["media_class"],
                "exposure_modes": list(item["exposure_modes"]),
                "quinte_local_refs": local_refs,
                "quinte_entries": sorted(candidates, key=lambda value: value["local_ref"]),
            }
        )

    all_quinte_locals = {
        entry["local_ref"] for entries in quinte_by_digest.values() for entry in entries
    }
    unmapped_local = sorted(all_quinte_locals - used_local)
    # Unmapped QUINTE locals are recorded, not hard-failed: ignore patterns and
    # empty-assignment seats may legitimately leave extras when policy is loose.
    # Fail closed only when assigned canonical refs cannot be joined (above).
    receipt: dict[str, Any] = {
        "mapping_receipt_version": RECEIPT_VERSION,
        "seat_id": seat_id,
        "evidence_manifest_sha256": evidence_manifest_sha256,
        "assignment_plan_sha256": assignment_plan_sha256,
        "assigned_evidence_refs": assigned,
        "quinte_run_id": quinte_run_id,
        "quinte_snapshot_manifest_ref": quinte_snapshot_manifest_ref,
        "quinte_snapshot_manifest_sha256": quinte_snapshot_manifest_sha256,
        "mappings": mappings,
        "unmapped_canonical_refs": [],
        "unmapped_quinte_local_refs": unmapped_local,
        "limitations": sorted(
            {
                "Mapping joins staged digests to QUINTE snapshot/attachment entries; it does not prove model perception.",
                "Unmapped QUINTE-local refs are reported when the snapshot tree contains extra files.",
            }
        ),
        "receipt_binding_sha256": "",
    }
    receipt["receipt_binding_sha256"] = _binding(receipt)
    return validate_mapping_receipt(receipt)


def validate_mapping_receipt(value: Any) -> dict[str, Any]:
    receipt = _object(value, "mapping receipt")
    _closed(receipt, RECEIPT_FIELDS, "mapping receipt")
    if receipt.get("mapping_receipt_version") != RECEIPT_VERSION:
        raise ContractError("mapping receipt version must be 1.0")
    _text(receipt.get("seat_id"), "mapping receipt.seat_id")
    for field in (
        "evidence_manifest_sha256",
        "assignment_plan_sha256",
        "quinte_snapshot_manifest_sha256",
        "receipt_binding_sha256",
    ):
        _digest(receipt.get(field), f"mapping receipt.{field}")
    _text(receipt.get("quinte_run_id"), "mapping receipt.quinte_run_id")
    _text(
        receipt.get("quinte_snapshot_manifest_ref"),
        "mapping receipt.quinte_snapshot_manifest_ref",
    )
    assigned = _sorted_unique_strings(
        receipt.get("assigned_evidence_refs"), "mapping receipt.assigned_evidence_refs"
    )
    unmapped_canonical = _sorted_unique_strings(
        receipt.get("unmapped_canonical_refs"), "mapping receipt.unmapped_canonical_refs"
    )
    unmapped_local = _sorted_unique_strings(
        receipt.get("unmapped_quinte_local_refs"),
        "mapping receipt.unmapped_quinte_local_refs",
    )
    mappings = receipt.get("mappings")
    if not isinstance(mappings, list):
        raise ContractError("mapping receipt.mappings must be an array")
    seen_canonical: set[str] = set()
    seen_local: set[str] = set()
    for index, raw in enumerate(mappings):
        label = f"mapping receipt.mappings[{index}]"
        mapping = _object(raw, label)
        _closed(mapping, MAPPING_FIELDS, label)
        canonical = _text(mapping.get("canonical_ref"), f"{label}.canonical_ref")
        if canonical in seen_canonical:
            raise ContractError(f"duplicate canonical mapping: {canonical}")
        seen_canonical.add(canonical)
        _text(mapping.get("staged_ref"), f"{label}.staged_ref")
        _digest(mapping.get("staged_sha256"), f"{label}.staged_sha256")
        if not isinstance(mapping.get("size_bytes"), int) or mapping["size_bytes"] < 0:
            raise ContractError(f"{label}.size_bytes must be a non-negative integer")
        _text(mapping.get("media_type"), f"{label}.media_type")
        _text(mapping.get("media_class"), f"{label}.media_class")
        modes = mapping.get("exposure_modes")
        if (
            not isinstance(modes, list)
            or not modes
            or modes != sorted(set(modes))
            or not all(isinstance(item, str) and item.strip() for item in modes)
        ):
            raise ContractError(f"{label}.exposure_modes must be a sorted unique non-empty string array")
        local_refs = _sorted_unique_strings(
            mapping.get("quinte_local_refs"), f"{label}.quinte_local_refs", nonempty=True
        )
        overlap = seen_local & set(local_refs)
        if overlap:
            raise ContractError(
                "duplicate QUINTE-local mapping: " + ", ".join(sorted(overlap))
            )
        seen_local.update(local_refs)
        entries = mapping.get("quinte_entries")
        if not isinstance(entries, list) or not entries:
            raise ContractError(f"{label}.quinte_entries must be a non-empty array")
        entry_refs: list[str] = []
        for entry_index, entry_raw in enumerate(entries):
            entry_label = f"{label}.quinte_entries[{entry_index}]"
            entry = _object(entry_raw, entry_label)
            _closed(entry, QUINTE_ENTRY_FIELDS, entry_label)
            local_ref = _text(entry.get("local_ref"), f"{entry_label}.local_ref")
            entry_refs.append(local_ref)
            kind = _text(entry.get("kind"), f"{entry_label}.kind")
            if kind not in {"snapshot", "attachment"}:
                raise ContractError(f"{entry_label}.kind must be snapshot or attachment")
            _text(entry.get("source_name"), f"{entry_label}.source_name")
            _digest(entry.get("sha256"), f"{entry_label}.sha256")
            if entry["sha256"] != mapping["staged_sha256"]:
                raise ContractError(
                    f"{entry_label}.sha256 drifted from staged digest for {canonical}"
                )
            if not isinstance(entry.get("bytes"), int) or entry["bytes"] < 0:
                raise ContractError(f"{entry_label}.bytes must be a non-negative integer")
            _text(entry.get("media_type"), f"{entry_label}.media_type")
        if sorted(set(entry_refs)) != local_refs:
            raise ContractError(f"{label} quinte_local_refs do not match quinte_entries")
    if seen_canonical != set(assigned):
        raise ContractError(
            "mapping receipt mappings must cover assigned_evidence_refs exactly once"
        )
    if unmapped_canonical:
        raise ContractError(
            "mapping receipt must not leave assigned canonical refs unmapped: "
            + ", ".join(unmapped_canonical)
        )
    # unmapped_local may be non-empty; no extra structural check beyond uniqueness
    _sorted_unique_strings(receipt.get("limitations"), "mapping receipt.limitations", True)
    if receipt["receipt_binding_sha256"] != _binding(receipt):
        raise ContractError("mapping receipt binding digest does not match")
    return receipt


def replay_mapping_receipt(
    receipt: dict[str, Any],
    *,
    evidence_manifest: dict[str, Any],
    evidence_manifest_sha256: str,
    assignment_plan_sha256: str,
    assigned_evidence_refs: list[str],
    quinte_snapshot_manifest: dict[str, Any],
    quinte_snapshot_manifest_sha256: str,
) -> dict[str, Any]:
    """Rebuild the receipt from inputs and require byte-identical equality."""

    validate_mapping_receipt(receipt)
    rebuilt = build_mapping_receipt(
        seat_id=receipt["seat_id"],
        evidence_manifest=evidence_manifest,
        evidence_manifest_sha256=evidence_manifest_sha256,
        assignment_plan_sha256=assignment_plan_sha256,
        assigned_evidence_refs=assigned_evidence_refs,
        quinte_run_id=receipt["quinte_run_id"],
        quinte_snapshot_manifest=quinte_snapshot_manifest,
        quinte_snapshot_manifest_ref=receipt["quinte_snapshot_manifest_ref"],
        quinte_snapshot_manifest_sha256=quinte_snapshot_manifest_sha256,
    )
    if rebuilt != receipt:
        raise ContractError("mapping receipt does not replay from bound inputs")
    return rebuilt


def _index_quinte_by_digest(manifest: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    if not isinstance(manifest, dict):
        raise ContractError("QUINTE snapshot manifest must be an object")
    if manifest.get("snapshot_version") not in {"1.0", "1", 1, "1.0.0"} and not isinstance(
        manifest.get("snapshot_version"), str
    ):
        # Accept any non-empty string version; QUINTE pins its own constant.
        if not isinstance(manifest.get("snapshot_version"), str) or not manifest["snapshot_version"]:
            raise ContractError("QUINTE snapshot_version is invalid")
    entries = manifest.get("entries")
    attachments = manifest.get("attachments")
    if not isinstance(entries, list) or not isinstance(attachments, list):
        raise ContractError("QUINTE snapshot manifest entries/attachments must be arrays")
    by_digest: dict[str, list[dict[str, Any]]] = {}
    seen_refs: set[str] = set()
    for index, raw in enumerate(entries):
        label = f"QUINTE snapshot entries[{index}]"
        entry = _object(raw, label)
        local_ref = _text(entry.get("snapshot_ref"), f"{label}.snapshot_ref")
        if local_ref in seen_refs:
            raise ContractError(f"duplicate QUINTE-local ref: {local_ref}")
        seen_refs.add(local_ref)
        digest = _digest(entry.get("sha256"), f"{label}.sha256")
        record = {
            "local_ref": local_ref,
            "kind": "snapshot",
            "source_name": _text(entry.get("source_name"), f"{label}.source_name"),
            "sha256": digest,
            "bytes": entry.get("bytes"),
            "media_type": _text(entry.get("media_type"), f"{label}.media_type"),
        }
        if not isinstance(record["bytes"], int) or record["bytes"] < 0:
            raise ContractError(f"{label}.bytes must be a non-negative integer")
        by_digest.setdefault(digest, []).append(record)
    for index, raw in enumerate(attachments):
        label = f"QUINTE snapshot attachments[{index}]"
        entry = _object(raw, label)
        local_ref = _text(entry.get("attachment_ref"), f"{label}.attachment_ref")
        if local_ref in seen_refs:
            raise ContractError(f"duplicate QUINTE-local ref: {local_ref}")
        seen_refs.add(local_ref)
        digest = _digest(entry.get("sha256"), f"{label}.sha256")
        record = {
            "local_ref": local_ref,
            "kind": "attachment",
            "source_name": _text(entry.get("source_name"), f"{label}.source_name"),
            "sha256": digest,
            "bytes": entry.get("bytes"),
            "media_type": _text(entry.get("media_type"), f"{label}.media_type"),
        }
        if not isinstance(record["bytes"], int) or record["bytes"] < 0:
            raise ContractError(f"{label}.bytes must be a non-negative integer")
        by_digest.setdefault(digest, []).append(record)
    return by_digest


def _binding(receipt: dict[str, Any]) -> str:
    return digest_value(
        {key: value for key, value in receipt.items() if key != "receipt_binding_sha256"}
    )


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


def _digest(value: Any, label: str) -> str:
    if not isinstance(value, str) or len(value) != 71 or not value.startswith("sha256:"):
        raise ContractError(f"{label} must be a sha256 digest")
    try:
        int(value[7:], 16)
    except ValueError as exc:
        raise ContractError(f"{label} must be a sha256 digest") from exc
    return value


def _sorted_unique_strings(
    value: Any, label: str, nonempty: bool = False
) -> list[str]:
    if (
        not isinstance(value, list)
        or (nonempty and not value)
        or not all(isinstance(item, str) and item.strip() for item in value)
        or value != sorted(set(value))
    ):
        raise ContractError(f"{label} must be a sorted unique string array")
    return value
