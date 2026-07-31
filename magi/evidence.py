"""Private evidence staging and citation-coverage receipts.

The staging boundary copies explicitly selected regular files into a trial-owned,
read-only tree.  It never treats a mount as proof that an agent read the bytes.
"""

from __future__ import annotations

import hashlib
import json
import mimetypes
import os
import re
import shutil
import stat
import subprocess
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Callable, Iterable, Sequence

from .errors import ContractError, StateError
from .io import atomic_write_json, canonical_json_bytes, digest_file, digest_value, read_json


MANIFEST_VERSION = "1.0"
RECEIPT_VERSION = "1.0"
STAGED_ROOT_REF = "trial-private/evidence"
MANIFEST_REF = f"{STAGED_ROOT_REF}/evidence-manifest.json"
EXPOSURE_MODES = {"snapshot", "multimodal_attachment"}
MULTIMODAL_IMAGE_TYPES = {"image/png", "image/jpeg", "image/webp", "image/gif"}

MANIFEST_FIELDS = {
    "evidence_manifest_version",
    "original_brief_ref",
    "original_brief_sha256",
    "source_root",
    "staged_root_ref",
    "source_files",
    "derived_frames",
    "evidence_set_sha256",
    "limitations",
}
SOURCE_FIELDS = {
    "id",
    "source_path",
    "source_relative_path",
    "staged_ref",
    "evidence_ref",
    "sha256",
    "size_bytes",
    "media_type",
    "media_class",
    "exposure_modes",
}
FRAME_FIELDS = {
    "id",
    "source_id",
    "source_evidence_ref",
    "timestamp_ms",
    "staged_ref",
    "evidence_ref",
    "sha256",
    "size_bytes",
    "media_type",
    "media_class",
    "exposure_modes",
    "derivation_tool",
    "derivation_command",
    "derivation_command_sha256",
}
RECEIPT_FIELDS = {
    "coverage_receipt_version",
    "coverage_status",
    "coverage_scope",
    "original_brief_sha256",
    "evidence_manifest_ref",
    "evidence_manifest_sha256",
    "artifacts",
    "exposed_evidence",
    "cited_evidence",
    "exposed_but_uncited",
    "unknown_citations",
    "unreviewed_media",
    "declared_limitations",
    "limitations",
    "receipt_binding_sha256",
}
ARTIFACT_FIELDS = {"artifact_ref", "sha256", "evidence_refs"}
CARRIER_FIELDS = {
    "carrier_id",
    "snapshot_media_classes",
    "multimodal_media_types",
    "allow_sampled_video",
}

_SECRET_COMPONENTS = {".aws", ".azure", ".git", ".gnupg", ".kube", ".ssh"}
_SECRET_NAMES = {
    ".env",
    ".netrc",
    ".npmrc",
    ".pypirc",
    "auth.json",
    "credentials.json",
    "id_dsa",
    "id_ed25519",
    "id_rsa",
    "secrets.json",
}
_SECRET_SUFFIXES = {".jks", ".key", ".keystore", ".p12", ".pem", ".pfx"}
_SECRET_NAME_TOKEN = re.compile(
    r"(?:^|[._-])(api[._-]?key|access[._-]?token|client[._-]?secret|credentials?|"
    r"private[._-]?key|refresh[._-]?token|secrets?)(?:$|[._-])",
    re.IGNORECASE,
)
_STRONG_SECRET_BYTES = (
    re.compile(br"-----BEGIN (?:[A-Z0-9 ]+ )?PRIVATE KEY-----"),
    re.compile(br"AKIA[0-9A-Z]{16}"),
    re.compile(br"gh[pousr]_[A-Za-z0-9]{20,}"),
    re.compile(br"sk-[A-Za-z0-9_-]{20,}"),
)
_ASSIGNED_SECRET = re.compile(
    r"(?im)^\s*(?:export\s+)?(?:api[_-]?key|access[_-]?token|client[_-]?secret|"
    r"password|private[_-]?key|refresh[_-]?token)\s*[:=]\s*[\"']?"
    r"(?!example\b|placeholder\b|redacted\b|changeme\b)[A-Za-z0-9/+_.=-]{8,}",
)
_CITATION_KEYS = {"evidence_refs", "closure_evidence", "source_refs"}
_URI_MARKERS = ("snapshot://", "attachment://")


@dataclass(frozen=True)
class EvidenceSelection:
    """One source-root-relative file and its requested carrier exposure."""

    relative_path: str
    exposure_modes: tuple[str, ...] = ("snapshot",)
    frame_times_ms: tuple[int, ...] = ()


FrameRunner = Callable[[list[str]], None]


def stage_evidence(
    trial_dir: Path,
    *,
    original_brief: Path,
    source_root: Path,
    selections: Sequence[EvidenceSelection],
    ffmpeg: str = "ffmpeg",
    frame_runner: FrameRunner | None = None,
) -> dict[str, Any]:
    """Stage a closed selection into ``trial-private/evidence``.

    The operation is all-or-nothing and refuses to replace an existing evidence
    tree.  Run it once per immutable trial.
    """

    if not selections:
        raise ContractError("at least one evidence file must be selected")
    trial = _existing_directory(trial_dir, "trial directory")
    brief = _regular_below_trial(original_brief, trial, "original brief")
    source = _source_root(source_root)
    normalized = _normalize_selections(selections)
    private_root = _private_root(trial)
    final_root = private_root / "evidence"
    if final_root.exists() or final_root.is_symlink():
        raise StateError(f"trial evidence already exists: {final_root}")

    temporary = private_root / f".evidence-stage-{uuid.uuid4().hex}"
    temporary.mkdir(mode=0o700)
    runner = frame_runner or _run_frame_command
    try:
        source_records: list[dict[str, Any]] = []
        frame_records: list[dict[str, Any]] = []
        resolved_seen: set[tuple[int, int]] = set()
        for index, selection in enumerate(normalized, start=1):
            relative, source_path, source_stat = _resolve_source(source, selection.relative_path)
            inode = (source_stat.st_dev, source_stat.st_ino)
            if inode in resolved_seen:
                raise ContractError(f"the same source file was selected more than once: {relative}")
            resolved_seen.add(inode)
            media_type, media_class = _classify_media(relative)
            modes = set(selection.exposure_modes)
            if "multimodal_attachment" in modes and media_type not in MULTIMODAL_IMAGE_TYPES:
                raise ContractError(
                    f"multimodal attachment must be PNG/JPEG/WebP/GIF: {relative} ({media_type})"
                )
            if selection.frame_times_ms and media_class != "video":
                raise ContractError(f"frame extraction requires a video source: {relative}")
            source_id = f"source-{index:04d}"
            staged_ref = f"snapshot/source/{source_id}{_safe_suffix(relative)}"
            destination = temporary / staged_ref
            sha256, size = _copy_checked(source_path, destination, source_stat)
            source_record = {
                "id": source_id,
                "source_path": str(source_path),
                "source_relative_path": relative.as_posix(),
                "staged_ref": staged_ref,
                "evidence_ref": f"snapshot://source/{source_id}{_safe_suffix(relative)}",
                "sha256": sha256,
                "size_bytes": size,
                "media_type": media_type,
                "media_class": media_class,
                "exposure_modes": sorted(modes),
            }
            source_records.append(source_record)

            for frame_index, timestamp_ms in enumerate(selection.frame_times_ms, start=1):
                frame_id = f"{source_id}-frame-{frame_index:04d}"
                frame_ref = (
                    f"snapshot/derived/{source_id}/frame-{frame_index:04d}-"
                    f"{timestamp_ms:012d}ms.png"
                )
                frame_destination = temporary / frame_ref
                frame_destination.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
                template = deterministic_ffmpeg_command(
                    ffmpeg, Path("{source}"), Path("{destination}"), timestamp_ms
                )
                command = deterministic_ffmpeg_command(
                    ffmpeg, destination, frame_destination, timestamp_ms
                )
                try:
                    runner(command)
                except (OSError, subprocess.SubprocessError) as exc:
                    raise ContractError(
                        f"deterministic frame extraction failed for {relative} at {timestamp_ms}ms: {exc}"
                    ) from exc
                frame_sha, frame_size = _validate_generated_frame(frame_destination)
                frame_records.append(
                    {
                        "id": frame_id,
                        "source_id": source_id,
                        "source_evidence_ref": source_record["evidence_ref"],
                        "timestamp_ms": timestamp_ms,
                        "staged_ref": frame_ref,
                        "evidence_ref": f"snapshot://{frame_ref.removeprefix('snapshot/')}",
                        "sha256": frame_sha,
                        "size_bytes": frame_size,
                        "media_type": "image/png",
                        "media_class": "image",
                        "exposure_modes": ["multimodal_attachment", "snapshot"],
                        "derivation_tool": "ffmpeg",
                        "derivation_command": template,
                        "derivation_command_sha256": digest_value(template),
                    }
                )

        limitations = _manifest_limitations(source_records, frame_records)
        original_ref = brief.relative_to(trial).as_posix()
        manifest = {
            "evidence_manifest_version": MANIFEST_VERSION,
            "original_brief_ref": original_ref,
            "original_brief_sha256": digest_file(brief),
            "source_root": str(source),
            "staged_root_ref": STAGED_ROOT_REF,
            "source_files": source_records,
            "derived_frames": frame_records,
            "evidence_set_sha256": "",
            "limitations": limitations,
        }
        manifest["evidence_set_sha256"] = _evidence_set_digest(manifest)
        atomic_write_json(temporary / "evidence-manifest.json", manifest)
        os.chmod(temporary / "evidence-manifest.json", 0o400)
        validate_evidence_manifest(manifest, trial_root=trial, staged_root=temporary)
        os.replace(temporary, final_root)
        return manifest
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def stage_empty_evidence(trial_dir: Path, *, original_brief: Path) -> dict[str, Any]:
    """Freeze an explicit no-external-evidence boundary for one trial."""

    trial = _existing_directory(trial_dir, "trial directory")
    brief = _regular_below_trial(original_brief, trial, "original brief")
    private_root = _private_root(trial)
    final_root = private_root / "evidence"
    if final_root.exists() or final_root.is_symlink():
        raise StateError(f"trial evidence already exists: {final_root}")
    temporary = private_root / f".evidence-stage-{uuid.uuid4().hex}"
    temporary.mkdir(mode=0o700)
    try:
        manifest = {
            "evidence_manifest_version": MANIFEST_VERSION,
            "original_brief_ref": brief.relative_to(trial).as_posix(),
            "original_brief_sha256": digest_file(brief),
            "source_root": "none://no-external-evidence",
            "staged_root_ref": STAGED_ROOT_REF,
            "source_files": [],
            "derived_frames": [],
            "evidence_set_sha256": "",
            "limitations": [
                "No external evidence was staged; conclusions are limited to the original brief."
            ],
        }
        manifest["evidence_set_sha256"] = _evidence_set_digest(manifest)
        atomic_write_json(temporary / "evidence-manifest.json", manifest)
        os.chmod(temporary / "evidence-manifest.json", 0o400)
        validate_evidence_manifest(manifest, trial_root=trial, staged_root=temporary)
        os.replace(temporary, final_root)
        return manifest
    except BaseException:
        shutil.rmtree(temporary, ignore_errors=True)
        raise


def deterministic_ffmpeg_command(
    executable: str, source: Path, destination: Path, timestamp_ms: int
) -> list[str]:
    """Return the metadata-free, single-thread PNG extraction command."""

    if not isinstance(timestamp_ms, int) or isinstance(timestamp_ms, bool) or timestamp_ms < 0:
        raise ContractError("video frame timestamps must be non-negative integer milliseconds")
    timestamp = f"{timestamp_ms // 1000}.{timestamp_ms % 1000:03d}"
    return [
        executable,
        "-nostdin",
        "-hide_banner",
        "-loglevel",
        "error",
        "-i",
        str(source),
        "-ss",
        timestamp,
        "-map",
        "0:v:0",
        "-frames:v",
        "1",
        "-an",
        "-sn",
        "-dn",
        "-vf",
        "format=rgb24",
        "-map_metadata",
        "-1",
        "-fflags",
        "+bitexact",
        "-flags:v",
        "+bitexact",
        "-threads",
        "1",
        "-c:v",
        "png",
        "-compression_level",
        "9",
        "-pred",
        "mixed",
        "-y",
        str(destination),
    ]


def evidence_brief_inputs(
    manifest: dict[str, Any],
    *,
    container_root: str = "/evidence",
    evidence_refs: Sequence[str] | None = None,
) -> dict[str, list[str]]:
    """Render the evidence-only QUINTE brief fields for a read-only mount.

    When ``evidence_refs`` is set, only that assigned subset is exposed via
    attachments, and unassigned snapshot paths are listed in ``snapshot_ignore``.
    """

    validate_evidence_manifest(manifest)
    root = container_root.rstrip("/")
    all_items = list(_all_evidence(manifest))
    known = {item["evidence_ref"] for item in all_items}
    if evidence_refs is None:
        selected = all_items
        allowed = known
    else:
        refs = list(evidence_refs)
        if not all(isinstance(item, str) and item.strip() for item in refs):
            raise ContractError("evidence_refs must be non-empty strings")
        if len(set(refs)) != len(refs):
            raise ContractError("evidence_refs must be unique")
        unknown = sorted(set(refs) - known)
        if unknown:
            raise ContractError(
                "evidence_refs outside the frozen manifest: " + ", ".join(unknown)
            )
        allowed = set(refs)
        selected = [item for item in all_items if item["evidence_ref"] in allowed]
    snapshot_assigned = any(
        "snapshot" in set(item["exposure_modes"]) for item in selected
    )
    attachments = sorted(
        f"{root}/{item['staged_ref']}"
        for item in selected
        if "multimodal_attachment" in item["exposure_modes"]
    )
    ignore = sorted(
        {
            item["staged_ref"][len("snapshot/") :]
            for item in all_items
            if item["evidence_ref"] not in allowed
            and isinstance(item.get("staged_ref"), str)
            and item["staged_ref"].startswith("snapshot/")
            and item["staged_ref"][len("snapshot/") :]
        }
    )
    return {
        "evidence_roots": [f"{root}/snapshot"] if snapshot_assigned else [],
        "snapshot_ignore": ignore,
        "attachments": attachments,
    }


def check_carrier_capabilities(
    manifest: dict[str, Any],
    capabilities: dict[str, Any],
    *,
    evidence_refs: Sequence[str] | None = None,
) -> dict[str, Any]:
    """Fail closed when a carrier cannot inspect a requested evidence exposure.

    When ``evidence_refs`` is provided, only that assigned subset is validated.
    When it is ``None``, the full staged manifest is validated (legacy full-set
    check). An empty sequence means no original evidence was assigned.
    """

    validate_evidence_manifest(manifest)
    _closed(capabilities, CARRIER_FIELDS, "carrier capabilities")
    carrier_id = _text(capabilities.get("carrier_id"), "carrier.carrier_id")
    snapshot_classes = _string_set(
        capabilities.get("snapshot_media_classes"), "carrier.snapshot_media_classes"
    )
    multimodal_types = _string_set(
        capabilities.get("multimodal_media_types"), "carrier.multimodal_media_types"
    )
    sampled_video = capabilities.get("allow_sampled_video")
    if not isinstance(sampled_video, bool):
        raise ContractError("carrier.allow_sampled_video must be boolean")
    known = {
        item["evidence_ref"]
        for item in [*manifest["source_files"], *manifest["derived_frames"]]
    }
    if evidence_refs is not None:
        refs = list(evidence_refs)
        if not all(isinstance(item, str) and item.strip() for item in refs):
            raise ContractError("assigned evidence_refs must be non-empty strings")
        if len(set(refs)) != len(refs):
            raise ContractError("assigned evidence_refs must be unique")
        unknown = sorted(set(refs) - known)
        if unknown:
            raise ContractError(
                "assigned evidence_refs outside the frozen manifest: " + ", ".join(unknown)
            )
        allowed = set(refs)
    else:
        allowed = known
    by_source = _frames_by_source(manifest)
    failures: list[str] = []
    for item in manifest["source_files"]:
        if item["evidence_ref"] not in allowed and not (
            item["media_class"] == "video"
            and sampled_video
            and any(frame["evidence_ref"] in allowed for frame in by_source.get(item["id"], []))
        ):
            continue
        modes = set(item["exposure_modes"])
        assigned_frames = [
            frame
            for frame in by_source.get(item["id"], [])
            if frame["evidence_ref"] in allowed
        ]
        if item["media_class"] == "video" and sampled_video and assigned_frames:
            for frame in assigned_frames:
                if frame["media_type"] not in multimodal_types:
                    failures.append(
                        f"{frame['evidence_ref']}: derived frame type {frame['media_type']} unsupported"
                    )
            if item["evidence_ref"] not in allowed:
                continue
        if item["evidence_ref"] not in allowed:
            continue
        if "snapshot" in modes and item["media_class"] not in snapshot_classes:
            failures.append(
                f"{item['evidence_ref']}: snapshot media class {item['media_class']} unsupported"
            )
        if (
            "multimodal_attachment" in modes
            and item["media_type"] not in multimodal_types
        ):
            failures.append(
                f"{item['evidence_ref']}: attachment type {item['media_type']} unsupported"
            )
    for frame in manifest["derived_frames"]:
        if frame["evidence_ref"] not in allowed:
            continue
        if frame["media_type"] not in multimodal_types:
            failures.append(
                f"{frame['evidence_ref']}: derived frame type {frame['media_type']} unsupported"
            )
    if failures:
        raise ContractError(
            f"carrier {carrier_id} cannot inspect requested evidence: " + "; ".join(sorted(set(failures)))
        )
    return {
        "carrier_id": carrier_id,
        "evidence_set_sha256": manifest["evidence_set_sha256"],
        "assigned_evidence_refs": sorted(allowed),
        "inspectable": True,
        "sampled_video": bool(by_source) and sampled_video and any(
            frame["evidence_ref"] in allowed
            for frames in by_source.values()
            for frame in frames
        ),
    }


def build_coverage_receipt(
    trial_dir: Path,
    *,
    artifacts: Sequence[Path],
    declared_limitations: Sequence[str] = (),
    output: Path | None = None,
) -> dict[str, Any]:
    """Bind staged exposures to citations made by concrete JSON artifacts."""

    trial = _existing_directory(trial_dir, "trial directory")
    manifest_path = trial / MANIFEST_REF
    manifest = read_json(manifest_path)
    validate_evidence_manifest(manifest, trial_root=trial, staged_root=manifest_path.parent)
    limitations_input = _unique_text(declared_limitations, "declared limitations")
    artifact_records = _artifact_records(trial, artifacts)
    cited_by: dict[str, list[str]] = {}
    for artifact in artifact_records:
        for reference in artifact["evidence_refs"]:
            cited_by.setdefault(reference, []).append(artifact["artifact_ref"])

    exposed_records = [_exposure_record(item) for item in _all_evidence(manifest)]
    exposed_by_ref = {item["evidence_ref"]: item for item in exposed_records}
    cited = [
        {**exposed_by_ref[reference], "artifact_refs": sorted(set(cited_by[reference]))}
        for reference in sorted(set(cited_by) & set(exposed_by_ref))
    ]
    uncited = [
        exposed_by_ref[reference]
        for reference in sorted(set(exposed_by_ref) - set(cited_by))
    ]
    unknown = [
        {"evidence_ref": reference, "artifact_refs": sorted(set(cited_by[reference]))}
        for reference in sorted(set(cited_by) - set(exposed_by_ref))
    ]
    unreviewed = _unreviewed_media(manifest)
    limitations = _coverage_limitations(limitations_input, uncited, unknown, unreviewed)
    receipt = {
        "coverage_receipt_version": RECEIPT_VERSION,
        "coverage_status": "bounded" if not (uncited or unknown or unreviewed) else "limited",
        "coverage_scope": "artifact citation coverage; not proof of model perception or review",
        "original_brief_sha256": manifest["original_brief_sha256"],
        "evidence_manifest_ref": MANIFEST_REF,
        "evidence_manifest_sha256": digest_file(manifest_path),
        "artifacts": artifact_records,
        "exposed_evidence": exposed_records,
        "cited_evidence": cited,
        "exposed_but_uncited": uncited,
        "unknown_citations": unknown,
        "unreviewed_media": unreviewed,
        "declared_limitations": limitations_input,
        "limitations": limitations,
        "receipt_binding_sha256": "",
    }
    receipt["receipt_binding_sha256"] = _receipt_digest(receipt)
    validate_coverage_receipt(receipt, trial_root=trial, replay=False)
    if output is not None:
        output_path = _output_below_trial(output, trial)
        atomic_write_json(output_path, receipt)
        os.chmod(output_path, 0o400)
    return receipt


def validate_coverage_receipt(
    receipt: dict[str, Any], *, trial_root: Path, replay: bool = True
) -> dict[str, Any]:
    """Validate receipt closure, binding, staged bytes, and optionally replay it."""

    _closed(receipt, RECEIPT_FIELDS, "coverage receipt")
    if receipt.get("coverage_receipt_version") != RECEIPT_VERSION:
        raise ContractError(f"coverage_receipt_version must be {RECEIPT_VERSION}")
    if receipt.get("coverage_status") not in {"bounded", "limited"}:
        raise ContractError("coverage_status must be bounded or limited")
    _text(receipt.get("coverage_scope"), "coverage_scope")
    _digest(receipt.get("original_brief_sha256"), "original_brief_sha256")
    _digest(receipt.get("evidence_manifest_sha256"), "evidence_manifest_sha256")
    _digest(receipt.get("receipt_binding_sha256"), "receipt_binding_sha256")
    if receipt["evidence_manifest_ref"] != MANIFEST_REF:
        raise ContractError("coverage receipt uses an unexpected evidence manifest reference")
    if receipt["receipt_binding_sha256"] != _receipt_digest(receipt):
        raise ContractError("coverage receipt binding digest mismatch")
    for field in (
        "artifacts",
        "exposed_evidence",
        "cited_evidence",
        "exposed_but_uncited",
        "unknown_citations",
        "unreviewed_media",
        "declared_limitations",
        "limitations",
    ):
        if not isinstance(receipt.get(field), list):
            raise ContractError(f"coverage receipt {field} must be an array")
    for index, artifact in enumerate(receipt["artifacts"]):
        if not isinstance(artifact, dict):
            raise ContractError(f"coverage receipt artifacts[{index}] must be an object")
        _closed(artifact, ARTIFACT_FIELDS, f"coverage receipt artifacts[{index}]")
        _digest(artifact.get("sha256"), f"coverage receipt artifacts[{index}].sha256")
    trial = _existing_directory(trial_root, "trial directory")
    manifest_path = trial / MANIFEST_REF
    if digest_file(manifest_path) != receipt["evidence_manifest_sha256"]:
        raise ContractError("coverage receipt evidence manifest digest mismatch")
    manifest = read_json(manifest_path)
    validate_evidence_manifest(manifest, trial_root=trial, staged_root=manifest_path.parent)
    if manifest["original_brief_sha256"] != receipt["original_brief_sha256"]:
        raise ContractError("coverage receipt original brief digest mismatch")
    if replay:
        paths = [trial / artifact["artifact_ref"] for artifact in receipt["artifacts"]]
        rebuilt = build_coverage_receipt(
            trial,
            artifacts=paths,
            declared_limitations=receipt["declared_limitations"],
        )
        if rebuilt != receipt:
            raise ContractError("coverage receipt does not replay from bound artifacts")
    return receipt


def validate_evidence_manifest(
    manifest: dict[str, Any], *, trial_root: Path | None = None, staged_root: Path | None = None
) -> dict[str, Any]:
    """Validate a closed manifest and, when given, its staged bytes."""

    _closed(manifest, MANIFEST_FIELDS, "evidence manifest")
    if manifest.get("evidence_manifest_version") != MANIFEST_VERSION:
        raise ContractError(f"evidence_manifest_version must be {MANIFEST_VERSION}")
    if manifest.get("staged_root_ref") != STAGED_ROOT_REF:
        raise ContractError("evidence manifest staged_root_ref is invalid")
    _text(manifest.get("original_brief_ref"), "manifest.original_brief_ref")
    _digest(manifest.get("original_brief_sha256"), "manifest.original_brief_sha256")
    _text(manifest.get("source_root"), "manifest.source_root")
    _digest(manifest.get("evidence_set_sha256"), "manifest.evidence_set_sha256")
    if manifest["evidence_set_sha256"] != _evidence_set_digest(manifest):
        raise ContractError("evidence manifest set digest mismatch")
    source_files = manifest.get("source_files")
    frames = manifest.get("derived_frames")
    if not isinstance(source_files, list):
        raise ContractError("evidence manifest source_files must be an array")
    if not isinstance(frames, list) or not isinstance(manifest.get("limitations"), list):
        raise ContractError("evidence manifest derived_frames/limitations must be arrays")
    if not source_files:
        if manifest["source_root"] != "none://no-external-evidence" or frames:
            raise ContractError("empty evidence must use the explicit no-evidence boundary")
        if not any(
            isinstance(item, str) and "No external evidence" in item
            for item in manifest["limitations"]
        ):
            raise ContractError("empty evidence must declare its external-evidence limitation")
    seen_ids: set[str] = set()
    seen_refs: set[str] = set()
    expected_files = {"evidence-manifest.json"}
    for label, values, fields in (
        ("source_files", source_files, SOURCE_FIELDS),
        ("derived_frames", frames, FRAME_FIELDS),
    ):
        for index, item in enumerate(values):
            if not isinstance(item, dict):
                raise ContractError(f"manifest.{label}[{index}] must be an object")
            _closed(item, fields, f"manifest.{label}[{index}]")
            item_id = _text(item.get("id"), f"manifest.{label}[{index}].id")
            if item_id in seen_ids:
                raise ContractError(f"duplicate evidence item ID: {item_id}")
            seen_ids.add(item_id)
            reference = _text(
                item.get("evidence_ref"), f"manifest.{label}[{index}].evidence_ref"
            )
            if not reference.startswith("snapshot://") or reference in seen_refs:
                raise ContractError(f"invalid or duplicate evidence reference: {reference}")
            seen_refs.add(reference)
            staged_ref = _safe_relative(
                _text(item.get("staged_ref"), f"manifest.{label}[{index}].staged_ref")
            )
            if not staged_ref.as_posix().startswith("snapshot/"):
                raise ContractError("staged evidence must be below snapshot/")
            expected_files.add(staged_ref.as_posix())
            _digest(item.get("sha256"), f"manifest.{label}[{index}].sha256")
            if not isinstance(item.get("size_bytes"), int) or item["size_bytes"] < 0:
                raise ContractError(f"manifest.{label}[{index}].size_bytes must be non-negative")
            modes = _string_set(
                item.get("exposure_modes"), f"manifest.{label}[{index}].exposure_modes"
            )
            if not modes or not modes <= EXPOSURE_MODES:
                raise ContractError(f"manifest.{label}[{index}] has invalid exposure modes")
    source_ids = {item["id"] for item in source_files}
    for index, frame in enumerate(frames):
        if frame["source_id"] not in source_ids:
            raise ContractError(f"manifest.derived_frames[{index}] has unknown source_id")
        if not isinstance(frame["timestamp_ms"], int) or frame["timestamp_ms"] < 0:
            raise ContractError(f"manifest.derived_frames[{index}].timestamp_ms is invalid")
        _digest(
            frame.get("derivation_command_sha256"),
            f"manifest.derived_frames[{index}].derivation_command_sha256",
        )
        if frame["derivation_command_sha256"] != digest_value(frame["derivation_command"]):
            raise ContractError(f"manifest.derived_frames[{index}] command digest mismatch")
    if trial_root is not None:
        trial = _existing_directory(trial_root, "trial directory")
        brief = _resolve_trial_ref(trial, manifest["original_brief_ref"], "original brief")
        if digest_file(brief) != manifest["original_brief_sha256"]:
            raise ContractError("evidence manifest original brief digest mismatch")
    if staged_root is not None:
        root = _existing_directory(staged_root, "staged evidence root")
        actual_files: set[str] = set()
        for path in root.rglob("*"):
            if path.is_symlink():
                raise ContractError(f"staged evidence contains a symlink: {path}")
            if path.is_file():
                actual_files.add(path.relative_to(root).as_posix())
            elif not path.is_dir():
                raise ContractError(f"staged evidence contains a non-regular entry: {path}")
        if actual_files != expected_files:
            raise ContractError("staged evidence file set does not match manifest")
        for item in _all_evidence(manifest):
            path = _resolve_below(root, item["staged_ref"], "staged evidence")
            file_stat = path.stat()
            if not stat.S_ISREG(file_stat.st_mode):
                raise ContractError(f"staged evidence is not regular: {path}")
            if file_stat.st_size != item["size_bytes"] or digest_file(path) != item["sha256"]:
                raise ContractError(f"staged evidence digest/size mismatch: {item['evidence_ref']}")
            if os.name != "nt" and stat.S_IMODE(file_stat.st_mode) & 0o277:
                raise ContractError(f"staged evidence permissions are not read-only/private: {path}")
    return manifest


def _normalize_selections(
    selections: Sequence[EvidenceSelection],
) -> list[EvidenceSelection]:
    merged: dict[str, tuple[set[str], set[int]]] = {}
    spelling: dict[str, str] = {}
    for selection in selections:
        if not isinstance(selection, EvidenceSelection):
            raise ContractError("evidence selections must be EvidenceSelection values")
        relative = _safe_relative(selection.relative_path).as_posix()
        collision_key = relative.casefold()
        if collision_key in spelling and spelling[collision_key] != relative:
            raise ContractError(
                f"case-insensitive evidence path collision: {spelling[collision_key]} / {relative}"
            )
        spelling[collision_key] = relative
        modes = set(selection.exposure_modes)
        if not modes or not modes <= EXPOSURE_MODES:
            raise ContractError(f"invalid evidence exposure modes for {relative}")
        # Attachments are also snapshotted so their final claims can use snapshot:// refs.
        if "multimodal_attachment" in modes:
            modes.add("snapshot")
        times: set[int] = set()
        for value in selection.frame_times_ms:
            if not isinstance(value, int) or isinstance(value, bool) or value < 0:
                raise ContractError(f"invalid video frame timestamp for {relative}")
            times.add(value)
        entry = merged.setdefault(relative, (set(), set()))
        entry[0].update(modes)
        entry[1].update(times)
    return [
        EvidenceSelection(path, tuple(sorted(modes)), tuple(sorted(times)))
        for path, (modes, times) in sorted(merged.items())
    ]


def _source_root(path: Path) -> Path:
    raw = path.expanduser()
    if raw.is_symlink():
        raise ContractError(f"source root must not be a symlink: {raw}")
    return _existing_directory(raw, "source root")


def _resolve_source(root: Path, relative_value: str) -> tuple[Path, Path, os.stat_result]:
    relative = _safe_relative(relative_value)
    if _secret_like(relative):
        raise ContractError(f"secret-like evidence path is forbidden: {relative}")
    candidate = root / relative
    current = root
    for component in relative.parts:
        current = current / component
        try:
            item_stat = current.lstat()
        except OSError as exc:
            raise ContractError(f"cannot inspect selected evidence {relative}: {exc}") from exc
        if stat.S_ISLNK(item_stat.st_mode):
            raise ContractError(f"selected evidence path contains a symlink: {relative}")
    resolved = candidate.resolve(strict=True)
    if resolved != root and root not in resolved.parents:
        raise ContractError(f"selected evidence escapes source root: {relative}")
    item_stat = candidate.lstat()
    if not stat.S_ISREG(item_stat.st_mode):
        raise ContractError(f"selected evidence is not a regular file: {relative}")
    _safe_source_mode(item_stat.st_mode, relative)
    return relative, resolved, item_stat


def _copy_checked(
    source: Path, destination: Path, expected_stat: os.stat_result
) -> tuple[str, int]:
    destination.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    source_fd = os.open(source, flags)
    destination_fd: int | None = None
    try:
        opened_stat = os.fstat(source_fd)
        if not stat.S_ISREG(opened_stat.st_mode):
            raise ContractError(f"selected evidence changed to a non-regular file: {source}")
        if (opened_stat.st_dev, opened_stat.st_ino) != (expected_stat.st_dev, expected_stat.st_ino):
            raise ContractError(f"selected evidence changed during staging: {source}")
        _safe_source_mode(opened_stat.st_mode, source)
        destination_fd = os.open(destination, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o400)
        hasher = hashlib.sha256()
        size = 0
        text_sample = bytearray()
        overlap = b""
        while True:
            chunk = os.read(source_fd, 1024 * 1024)
            if not chunk:
                break
            probe = overlap + chunk
            for pattern in _STRONG_SECRET_BYTES:
                if pattern.search(probe):
                    raise ContractError(f"secret-like content is forbidden in evidence: {source}")
            overlap = probe[-128:]
            if len(text_sample) < 2 * 1024 * 1024:
                text_sample.extend(chunk[: 2 * 1024 * 1024 - len(text_sample)])
            view = memoryview(chunk)
            while view:
                written = os.write(destination_fd, view)
                view = view[written:]
            hasher.update(chunk)
            size += len(chunk)
        if _contains_assigned_secret(bytes(text_sample)):
            raise ContractError(f"secret-like assignment is forbidden in evidence: {source}")
        final_stat = os.fstat(source_fd)
        if (
            final_stat.st_size != opened_stat.st_size
            or final_stat.st_mtime_ns != opened_stat.st_mtime_ns
            or size != opened_stat.st_size
        ):
            raise ContractError(f"selected evidence changed while being staged: {source}")
        os.fsync(destination_fd)
        os.fchmod(destination_fd, 0o400)
        return f"sha256:{hasher.hexdigest()}", size
    finally:
        os.close(source_fd)
        if destination_fd is not None:
            os.close(destination_fd)


def _contains_assigned_secret(raw: bytes) -> bool:
    if b"\x00" in raw[:4096]:
        return False
    try:
        text_value = raw.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return _ASSIGNED_SECRET.search(text_value) is not None


def _validate_generated_frame(path: Path) -> tuple[str, int]:
    try:
        item_stat = path.lstat()
    except OSError as exc:
        raise ContractError(f"ffmpeg produced no frame at {path}: {exc}") from exc
    if not stat.S_ISREG(item_stat.st_mode) or item_stat.st_size == 0:
        raise ContractError(f"ffmpeg output is not a non-empty regular file: {path}")
    if path.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        raise ContractError(f"ffmpeg output is not a PNG frame: {path}")
    os.chmod(path, 0o400)
    return digest_file(path), item_stat.st_size


def _run_frame_command(command: list[str]) -> None:
    subprocess.run(command, check=True, stdin=subprocess.DEVNULL, capture_output=True)


def _artifact_records(trial: Path, artifacts: Sequence[Path]) -> list[dict[str, Any]]:
    expanded: list[Path] = []
    for raw in artifacts:
        path = raw.expanduser()
        if path.is_dir() and not path.is_symlink():
            expanded.extend(sorted(path.rglob("*.json")))
        else:
            expanded.append(path)
    if not expanded:
        raise ContractError("at least one result artifact is required for coverage")
    records: list[dict[str, Any]] = []
    seen: set[str] = set()
    for raw in expanded:
        path = _regular_below_trial(raw, trial, "coverage artifact")
        reference = path.relative_to(trial).as_posix()
        if reference in seen or reference in {MANIFEST_REF, "trial-private/evidence-coverage-receipt.json"}:
            continue
        seen.add(reference)
        value = read_json(path)
        records.append(
            {
                "artifact_ref": reference,
                "sha256": digest_file(path),
                "evidence_refs": sorted(_collect_citations(value)),
            }
        )
    if not records:
        raise ContractError("coverage selection contains no result JSON artifacts")
    return sorted(records, key=lambda item: item["artifact_ref"])


def _collect_citations(value: Any, active: bool = False) -> set[str]:
    found: set[str] = set()
    if isinstance(value, dict):
        for key, item in value.items():
            found.update(_collect_citations(item, active or key in _CITATION_KEYS))
    elif isinstance(value, list):
        for item in value:
            found.update(_collect_citations(item, active))
    elif active and isinstance(value, str):
        for marker in _URI_MARKERS:
            offset = value.find(marker)
            if offset >= 0:
                reference = value[offset:].strip()
                if reference:
                    found.add(reference)
    return found


def _manifest_limitations(
    sources: Sequence[dict[str, Any]], frames: Sequence[dict[str, Any]]
) -> list[str]:
    limitations = [
        "Staging and carrier exposure do not prove that a model read, decoded, or reviewed evidence."
    ]
    frames_by_source: dict[str, list[int]] = {}
    for frame in frames:
        frames_by_source.setdefault(frame["source_id"], []).append(frame["timestamp_ms"])
    for source in sources:
        if source["media_class"] == "video":
            timestamps = sorted(frames_by_source.get(source["id"], []))
            if timestamps:
                limitations.append(
                    f"{source['evidence_ref']} is sampled only at millisecond timestamps "
                    + ", ".join(str(value) for value in timestamps)
                    + "; intervals and audio remain unreviewed."
                )
            else:
                limitations.append(
                    f"{source['evidence_ref']} has no derived frames; video content remains unreviewed."
                )
        elif source["media_class"] == "audio":
            limitations.append(
                f"{source['evidence_ref']} has no deterministic transcription; audio remains unreviewed."
            )
    return limitations


def _coverage_limitations(
    declared: list[str], uncited: list[dict[str, Any]], unknown: list[dict[str, Any]], unreviewed: list[dict[str, Any]]
) -> list[str]:
    limitations = [
        "Mounted or exposed evidence is not equivalent to evidence read or reviewed.",
        "A citation is an artifact claim and does not attest model perception or semantic correctness.",
    ]
    if uncited:
        limitations.append(f"{len(uncited)} exposed evidence item(s) are not cited by bound artifacts.")
    if unknown:
        limitations.append(f"{len(unknown)} citation(s) do not resolve to the staged evidence manifest.")
    if unreviewed:
        limitations.append(f"{len(unreviewed)} media item(s) remain wholly or partially unreviewed.")
    return _unique_text([*limitations, *declared], "coverage limitations")


def _unreviewed_media(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    frames = _frames_by_source(manifest)
    records: list[dict[str, Any]] = []
    for source in manifest["source_files"]:
        if source["media_class"] == "video":
            derived = frames.get(source["id"], [])
            records.append(
                {
                    "evidence_ref": source["evidence_ref"],
                    "media_class": "video",
                    "reason": (
                        "only deterministic still frames were exposed; intervals and audio were not"
                        if derived
                        else "no decoded video representation was exposed"
                    ),
                    "derived_frame_refs": [item["evidence_ref"] for item in derived],
                }
            )
        elif source["media_class"] == "audio":
            records.append(
                {
                    "evidence_ref": source["evidence_ref"],
                    "media_class": "audio",
                    "reason": "no deterministic transcription was exposed",
                    "derived_frame_refs": [],
                }
            )
    return records


def _all_evidence(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    return [*manifest["source_files"], *manifest["derived_frames"]]


def _exposure_record(item: dict[str, Any]) -> dict[str, Any]:
    return {
        "evidence_ref": item["evidence_ref"],
        "staged_ref": item["staged_ref"],
        "sha256": item["sha256"],
        "size_bytes": item["size_bytes"],
        "media_type": item["media_type"],
        "media_class": item["media_class"],
        "exposure_modes": item["exposure_modes"],
    }


def _frames_by_source(manifest: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    values: dict[str, list[dict[str, Any]]] = {}
    for frame in manifest["derived_frames"]:
        values.setdefault(frame["source_id"], []).append(frame)
    for frames in values.values():
        frames.sort(key=lambda item: (item["timestamp_ms"], item["id"]))
    return values


def _receipt_digest(receipt: dict[str, Any]) -> str:
    return digest_value({key: value for key, value in receipt.items() if key != "receipt_binding_sha256"})


def _evidence_set_digest(manifest: dict[str, Any]) -> str:
    return digest_value(
        {
            "evidence_manifest_version": manifest["evidence_manifest_version"],
            "original_brief_ref": manifest["original_brief_ref"],
            "original_brief_sha256": manifest["original_brief_sha256"],
            "source_root": manifest["source_root"],
            "staged_root_ref": manifest["staged_root_ref"],
            "source_files": manifest["source_files"],
            "derived_frames": manifest["derived_frames"],
            "limitations": manifest["limitations"],
        }
    )


def _classify_media(path: Path) -> tuple[str, str]:
    media_type = mimetypes.guess_type(path.name, strict=False)[0] or "application/octet-stream"
    if media_type.startswith("image/"):
        media_class = "image"
    elif media_type.startswith("video/"):
        media_class = "video"
    elif media_type.startswith("audio/"):
        media_class = "audio"
    elif media_type.startswith("text/") or media_type in {
        "application/json",
        "application/pdf",
        "application/rtf",
        "application/xml",
        "application/vnd.ms-excel",
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    }:
        media_class = "document"
    else:
        media_class = "binary"
    return media_type, media_class


def _safe_suffix(path: Path) -> str:
    suffix = path.suffix.lower()
    return suffix if re.fullmatch(r"\.[a-z0-9]{1,10}", suffix) else ".bin"


def _secret_like(path: Path) -> bool:
    parts = [part.casefold() for part in path.parts]
    name = parts[-1]
    return (
        any(part in _SECRET_COMPONENTS for part in parts[:-1])
        or name in _SECRET_NAMES
        or any(name.endswith(suffix) for suffix in _SECRET_SUFFIXES)
        or _SECRET_NAME_TOKEN.search(name) is not None
        or name.startswith(".env.")
    )


def _safe_source_mode(mode: int, label: object) -> None:
    if os.name != "nt" and (stat.S_IMODE(mode) & 0o7022):
        raise ContractError(f"selected evidence has unsafe permissions: {label}")


def _safe_relative(value: str) -> Path:
    if not isinstance(value, str) or not value or "\x00" in value:
        raise ContractError("evidence path must be a non-empty relative path")
    path = Path(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ContractError(f"evidence path must not escape its root: {value}")
    return path


def _private_root(trial: Path) -> Path:
    private = trial / "trial-private"
    if private.is_symlink():
        raise ContractError(f"trial-private must not be a symlink: {private}")
    private.mkdir(mode=0o700, exist_ok=True)
    if not private.is_dir():
        raise ContractError(f"trial-private is not a directory: {private}")
    os.chmod(private, 0o700)
    return private


def _existing_directory(path: Path, label: str) -> Path:
    raw = path.expanduser()
    if raw.is_symlink():
        raise ContractError(f"{label} must not be a symlink: {raw}")
    try:
        resolved = raw.resolve(strict=True)
    except OSError as exc:
        raise ContractError(f"cannot resolve {label} {raw}: {exc}") from exc
    if not resolved.is_dir():
        raise ContractError(f"{label} is not a directory: {resolved}")
    return resolved


def _regular_below_trial(path: Path, trial: Path, label: str) -> Path:
    raw = path.expanduser()
    if raw.is_symlink():
        raise ContractError(f"{label} must not be a symlink: {raw}")
    try:
        resolved = raw.resolve(strict=True)
    except OSError as exc:
        raise ContractError(f"cannot resolve {label} {raw}: {exc}") from exc
    if resolved == trial or trial not in resolved.parents:
        raise ContractError(f"{label} must resolve below the trial directory")
    relative = resolved.relative_to(trial)
    current = trial
    for component in relative.parts:
        current = current / component
        if current.is_symlink():
            raise ContractError(f"{label} path contains a symlink: {current}")
    if not resolved.is_file() or not stat.S_ISREG(resolved.stat().st_mode):
        raise ContractError(f"{label} must be a regular file: {resolved}")
    return resolved


def _resolve_trial_ref(trial: Path, reference: str, label: str) -> Path:
    return _regular_below_trial(trial / _safe_relative(reference), trial, label)


def _resolve_below(root: Path, reference: str, label: str) -> Path:
    relative = _safe_relative(reference)
    candidate = root / relative
    if candidate.is_symlink():
        raise ContractError(f"{label} must not be a symlink: {candidate}")
    resolved = candidate.resolve(strict=True)
    if resolved == root or root not in resolved.parents:
        raise ContractError(f"{label} escapes its root: {reference}")
    return resolved


def _output_below_trial(path: Path, trial: Path) -> Path:
    raw = path.expanduser()
    parent = raw.parent.resolve(strict=True)
    if parent != trial and trial not in parent.parents:
        raise ContractError("coverage receipt output must be below the trial directory")
    if raw.exists() or raw.is_symlink():
        raise StateError(f"coverage receipt output already exists: {raw}")
    return raw


def _closed(value: dict[str, Any], fields: set[str], label: str) -> None:
    if not isinstance(value, dict):
        raise ContractError(f"{label} must be an object")
    unknown = sorted(set(value) - fields)
    missing = sorted(fields - set(value))
    if unknown or missing:
        raise ContractError(f"{label} closed-field mismatch; unknown={unknown}, missing={missing}")


def _text(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ContractError(f"{label} must be a non-empty string")
    return value


def _digest(value: Any, label: str) -> str:
    candidate = _text(value, label)
    if re.fullmatch(r"sha256:[a-f0-9]{64}", candidate) is None:
        raise ContractError(f"{label} must be a sha256 digest")
    return candidate


def _string_set(value: Any, label: str) -> set[str]:
    if not isinstance(value, list) or not all(isinstance(item, str) and item for item in value):
        raise ContractError(f"{label} must be a string array")
    if len(value) != len(set(value)):
        raise ContractError(f"{label} must not contain duplicates")
    return set(value)


def _unique_text(values: Iterable[str], label: str) -> list[str]:
    rendered: list[str] = []
    seen: set[str] = set()
    for value in values:
        text_value = _text(value, label)
        if text_value not in seen:
            rendered.append(text_value)
            seen.add(text_value)
    return rendered
