"""Command-line interface for the MAGI production runtime."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from . import __version__
from .errors import AgentError, ContractError, MagiError, StateError
from .evidence import (
    EvidenceSelection,
    build_coverage_receipt,
    stage_empty_evidence,
    stage_evidence,
    validate_coverage_receipt,
    validate_evidence_manifest,
)
from .io import read_json
from .runtime import TrialRuntime
from .configuration import generate_production_config


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(prog="magi", description="Triadic cross-family verification runtime")
    root.add_argument("--version", action="version", version=f"magi {__version__}")
    commands = root.add_subparsers(dest="command", required=True)

    init = commands.add_parser("init", help="initialize an immutable trial")
    init.add_argument("trial_dir", type=Path)
    init.add_argument("--trial-id", required=True)
    init.add_argument("--brief", required=True, type=Path)
    init.add_argument("--seat", action="append", required=True, dest="seats")
    init.add_argument(
        "--action-boundary",
        choices=("none", "reversible", "protected_write", "irreversible"),
        required=True,
    )

    evidence = commands.add_parser(
        "stage-evidence", help="copy an explicit evidence selection into an immutable trial tree"
    )
    evidence.add_argument("trial_dir", type=Path)
    evidence.add_argument("--brief", required=True, type=Path)
    evidence.add_argument("--selection", required=True, type=Path)
    evidence.add_argument("--ffmpeg", default="ffmpeg")

    no_evidence = commands.add_parser(
        "stage-no-evidence",
        help="freeze an explicit no-external-evidence boundary for the trial",
    )
    no_evidence.add_argument("trial_dir", type=Path)
    no_evidence.add_argument("--brief", required=True, type=Path)

    coverage = commands.add_parser(
        "evidence-coverage", help="bind staged evidence exposures to result-artifact citations"
    )
    coverage.add_argument("trial_dir", type=Path)
    coverage.add_argument("--artifact", action="append", required=True, type=Path, dest="artifacts")
    coverage.add_argument("--limitation", action="append", default=[], dest="limitations")
    coverage.add_argument("--out", type=Path)

    evidence_verify = commands.add_parser(
        "verify-evidence", help="verify staged bytes and optionally replay a coverage receipt"
    )
    evidence_verify.add_argument("trial_dir", type=Path)
    evidence_verify.add_argument("--receipt", type=Path)

    register = commands.add_parser("register-dossier", help="freeze one completed seat dossier")
    register.add_argument("trial_dir", type=Path)
    register.add_argument("--seat", required=True)
    register.add_argument("--dossier", required=True, type=Path)

    build = commands.add_parser(
        "build-dossiers", help="resume isolated thesis, QUINTE, and dossier generation"
    )
    build.add_argument("trial_dir", type=Path)
    build.add_argument("--config", required=True, type=Path)
    build.add_argument("--assignment-plan", required=True, type=Path)

    run = commands.add_parser(
        "run", help="resume exchange, final adjudication, and deterministic verification"
    )
    run.add_argument("trial_dir", type=Path)
    run.add_argument("--config", required=True, type=Path)

    configure = commands.add_parser(
        "configure", help="generate assignment, builder, and agent contracts"
    )
    configure.add_argument("trial_dir", type=Path)
    configure.add_argument("--trial-id", required=True)
    configure.add_argument("--evidence-manifest", required=True, type=Path)
    configure.add_argument("--image-digest", required=True)
    configure.add_argument("--profile", action="append", required=True)
    configure.add_argument("--out", required=True, type=Path)

    status = commands.add_parser("status", help="print the closed trial state")
    status.add_argument("trial_dir", type=Path)
    verify = commands.add_parser(
        "verify-product", help="revalidate and summarize one completed atomic MAGI product"
    )
    verify.add_argument("trial_dir", type=Path)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        if args.command == "init":
            runtime = TrialRuntime.initialize(
                args.trial_dir,
                trial_id=args.trial_id,
                seat_slots=args.seats,
                action_boundary=args.action_boundary,
                original_brief=args.brief,
            )
            state = runtime.load_state()
        elif args.command == "stage-evidence":
            selection = _load_evidence_selection(args.selection)
            state = stage_evidence(
                args.trial_dir,
                original_brief=args.brief,
                source_root=Path(selection["source_root"]),
                selections=selection["files"],
                ffmpeg=args.ffmpeg,
            )
        elif args.command == "stage-no-evidence":
            state = stage_empty_evidence(args.trial_dir, original_brief=args.brief)
        elif args.command == "evidence-coverage":
            output = args.out or args.trial_dir / "trial-private" / "evidence-coverage-receipt.json"
            state = build_coverage_receipt(
                args.trial_dir,
                artifacts=args.artifacts,
                declared_limitations=args.limitations,
                output=output,
            )
        elif args.command == "verify-evidence":
            manifest_path = args.trial_dir / "trial-private" / "evidence" / "evidence-manifest.json"
            state = validate_evidence_manifest(
                read_json(manifest_path),
                trial_root=args.trial_dir,
                staged_root=manifest_path.parent,
            )
            if args.receipt is not None:
                state = validate_coverage_receipt(
                    read_json(args.receipt), trial_root=args.trial_dir
                )
        elif args.command == "register-dossier":
            state = TrialRuntime(args.trial_dir).register_dossier(args.seat, args.dossier)
        elif args.command == "build-dossiers":
            state = TrialRuntime(args.trial_dir).build_dossiers(
                args.config, args.assignment_plan
            )
        elif args.command == "run":
            state = TrialRuntime(args.trial_dir).run(args.config)
        elif args.command == "configure":
            profiles = _load_profiles(args.profile)
            paths = generate_production_config(
                repo_root=Path(__file__).resolve().parents[1],
                trial_dir=args.trial_dir,
                trial_id=args.trial_id,
                evidence_manifest=args.evidence_manifest,
                profile_sources=profiles,
                image_digest=args.image_digest,
                output_dir=args.out,
            )
            state = {key: str(value) for key, value in paths.items()}
        elif args.command == "verify-product":
            state = TrialRuntime(args.trial_dir).verify_product()
        else:
            state = TrialRuntime(args.trial_dir).status()
        print(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except (ContractError, StateError) as exc:
        print(f"magi: contract error: {exc}", file=sys.stderr)
        return 2
    except AgentError as exc:
        print(f"magi: agent error: {exc}", file=sys.stderr)
        return 3
    except (OSError, ValueError) as exc:
        print(f"magi: runtime error: {exc}", file=sys.stderr)
        return 4


def _load_evidence_selection(path: Path) -> dict[str, object]:
    value = read_json(path)
    expected = {"selection_version", "source_root", "files"}
    unknown = sorted(set(value) - expected)
    missing = sorted(expected - set(value))
    if unknown or missing:
        raise ContractError(
            f"evidence selection closed-field mismatch; unknown={unknown}, missing={missing}"
        )
    if value.get("selection_version") != "1.0":
        raise ContractError("evidence selection_version must be 1.0")
    if not isinstance(value.get("source_root"), str) or not value["source_root"]:
        raise ContractError("evidence selection source_root must be a non-empty string")
    files = value.get("files")
    if not isinstance(files, list) or not files:
        raise ContractError("evidence selection files must be a non-empty array")
    rendered: list[EvidenceSelection] = []
    for index, item in enumerate(files):
        if not isinstance(item, dict):
            raise ContractError(f"evidence selection files[{index}] must be an object")
        allowed = {"path", "exposure_modes", "frame_times_ms"}
        if set(item) - allowed or "path" not in item:
            raise ContractError(f"evidence selection files[{index}] has invalid fields")
        modes = item.get("exposure_modes", ["snapshot"])
        times = item.get("frame_times_ms", [])
        if not isinstance(item["path"], str) or not isinstance(modes, list) or not isinstance(times, list):
            raise ContractError(f"evidence selection files[{index}] has invalid value types")
        rendered.append(EvidenceSelection(item["path"], tuple(modes), tuple(times)))
    return {"source_root": value["source_root"], "files": rendered}


def _load_profiles(values: list[str]) -> dict[str, Path]:
    profiles: dict[str, Path] = {}
    for value in values:
        if "=" not in value:
            raise ContractError("--profile must use seat-id=/absolute/path")
        seat, path = value.split("=", 1)
        if seat not in {"seat-m", "seat-d", "seat-g"} or seat in profiles:
            raise ContractError("--profile must bind each production seat exactly once")
        profiles[seat] = Path(path)
    if set(profiles) != {"seat-m", "seat-d", "seat-g"}:
        raise ContractError("--profile must bind all three production seats")
    return profiles


if __name__ == "__main__":
    raise SystemExit(main())
