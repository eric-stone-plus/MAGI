from __future__ import annotations

import json
import os
import tempfile
import unittest
from pathlib import Path

from magi.cli import main
from magi.evidence import (
    EvidenceSelection,
    build_coverage_receipt,
    check_carrier_capabilities,
    deterministic_ffmpeg_command,
    evidence_brief_inputs,
    stage_evidence,
    stage_empty_evidence,
    validate_coverage_receipt,
    validate_evidence_manifest,
)
from magi.errors import ContractError, StateError
from magi.io import atomic_write_json

from tests.helpers import original_brief


PNG = b"\x89PNG\r\n\x1a\n" + b"deterministic-test-frame"


class EvidenceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.trial = self.base / "trial"
        self.source = self.base / "source"
        (self.trial / "input").mkdir(parents=True)
        self.source.mkdir()
        self.brief = self.trial / "input" / "original-brief.json"
        atomic_write_json(self.brief, original_brief())

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_explicit_no_evidence_boundary_is_closed_and_replayable(self) -> None:
        manifest = stage_empty_evidence(self.trial, original_brief=self.brief)
        self.assertEqual(manifest["source_files"], [])
        self.assertEqual(manifest["source_root"], "none://no-external-evidence")
        validate_evidence_manifest(
            manifest,
            trial_root=self.trial,
            staged_root=self.trial / "trial-private" / "evidence",
        )

    def write_source(self, relative: str, raw: bytes, mode: int = 0o600) -> Path:
        path = self.source / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
        os.chmod(path, mode)
        return path

    def stage(self, *selections: EvidenceSelection, frame_runner=None) -> dict:
        return stage_evidence(
            self.trial,
            original_brief=self.brief,
            source_root=self.source,
            selections=list(selections),
            frame_runner=frame_runner,
        )

    def test_stage_binds_source_bytes_paths_and_brief(self) -> None:
        source = self.write_source("reports/case.txt", b"bounded evidence\n")
        manifest = self.stage(EvidenceSelection("reports/case.txt"))
        record = manifest["source_files"][0]
        self.assertEqual(record["source_path"], str(source.resolve()))
        self.assertEqual(record["source_relative_path"], "reports/case.txt")
        self.assertEqual(record["size_bytes"], len(b"bounded evidence\n"))
        self.assertRegex(record["sha256"], r"^sha256:[0-9a-f]{64}$")
        self.assertEqual(record["evidence_ref"], "snapshot://source/source-0001.txt")
        staged = self.trial / "trial-private" / "evidence" / record["staged_ref"]
        self.assertEqual(staged.read_bytes(), source.read_bytes())
        self.assertEqual(staged.stat().st_mode & 0o777, 0o400)
        validate_evidence_manifest(
            manifest,
            trial_root=self.trial,
            staged_root=self.trial / "trial-private" / "evidence",
        )
        rendered = evidence_brief_inputs(manifest)
        self.assertEqual(rendered["evidence_roots"], ["/evidence/snapshot"])
        self.assertEqual(rendered["attachments"], [])

    def test_stage_rejects_escape_symlink_non_regular_and_duplicates(self) -> None:
        self.write_source("safe.txt", b"safe")
        outside = self.base / "outside.txt"
        outside.write_text("outside")
        os.symlink(outside, self.source / "link.txt")
        (self.source / "directory").mkdir()
        for selection, message in (
            (EvidenceSelection("../outside.txt"), "escape"),
            (EvidenceSelection("link.txt"), "symlink"),
            (EvidenceSelection("directory"), "regular"),
        ):
            with self.subTest(selection=selection), self.assertRaisesRegex(ContractError, message):
                self.stage(selection)
        os.link(self.source / "safe.txt", self.source / "same-bytes.txt")
        with self.assertRaisesRegex(ContractError, "selected more than once"):
            self.stage(EvidenceSelection("safe.txt"), EvidenceSelection("same-bytes.txt"))

    @unittest.skipIf(os.name == "nt", "POSIX mode contract")
    def test_stage_rejects_unsafe_source_permissions(self) -> None:
        self.write_source("world-writable.txt", b"unsafe", 0o622)
        with self.assertRaisesRegex(ContractError, "unsafe permissions"):
            self.stage(EvidenceSelection("world-writable.txt"))

    def test_stage_rejects_secret_like_names_and_content_atomically(self) -> None:
        self.write_source("credentials.json", b"{}")
        with self.assertRaisesRegex(ContractError, "secret-like evidence path"):
            self.stage(EvidenceSelection("credentials.json"))
        self.write_source("report.txt", b"OPENAI_API_KEY=sk-test-secret-value-123456789\n")
        with self.assertRaisesRegex(ContractError, "secret-like"):
            self.stage(EvidenceSelection("report.txt"))
        self.assertFalse((self.trial / "trial-private" / "evidence").exists())
        self.assertEqual(list((self.trial / "trial-private").glob(".evidence-stage-*")), [])

    def test_deterministic_video_frames_and_unreviewed_limitation(self) -> None:
        self.write_source("clip.mp4", b"not-real-video")
        commands: list[list[str]] = []

        def fake_ffmpeg(command: list[str]) -> None:
            commands.append(command)
            Path(command[-1]).write_bytes(PNG)

        manifest = self.stage(
            EvidenceSelection("clip.mp4", ("snapshot",), (2000, 0, 2000)),
            frame_runner=fake_ffmpeg,
        )
        self.assertEqual([item["timestamp_ms"] for item in manifest["derived_frames"]], [0, 2000])
        self.assertEqual(len(commands), 2)
        self.assertEqual(commands[0][-4:-2], ["-pred", "mixed"])
        expected = deterministic_ffmpeg_command(
            "ffmpeg", Path("source.mp4"), Path("frame.png"), 23
        )
        self.assertIn("0.023", expected)
        self.assertIn("+bitexact", expected)
        self.assertIn("-threads", expected)
        self.assertTrue(any("intervals and audio" in item for item in manifest["limitations"]))
        attachments = evidence_brief_inputs(manifest)["attachments"]
        self.assertEqual(len(attachments), 2)
        self.assertTrue(all(path.endswith(".png") for path in attachments))

    def test_attachment_input_is_limited_to_supported_image_types(self) -> None:
        self.write_source("photo.jpg", b"fake-jpeg")
        manifest = self.stage(
            EvidenceSelection("photo.jpg", ("multimodal_attachment",))
        )
        item = manifest["source_files"][0]
        self.assertEqual(item["exposure_modes"], ["multimodal_attachment", "snapshot"])
        self.assertEqual(
            evidence_brief_inputs(manifest)["attachments"],
            ["/evidence/" + item["staged_ref"]],
        )

        other_trial = self.base / "other-trial"
        (other_trial / "input").mkdir(parents=True)
        other_brief = other_trial / "input" / "original-brief.json"
        atomic_write_json(other_brief, original_brief())
        self.write_source("manual.pdf", b"fake-pdf")
        with self.assertRaisesRegex(ContractError, "must be PNG/JPEG/WebP/GIF"):
            stage_evidence(
                other_trial,
                original_brief=other_brief,
                source_root=self.source,
                selections=[EvidenceSelection("manual.pdf", ("multimodal_attachment",))],
            )

    def test_carrier_capabilities_fail_closed(self) -> None:
        self.write_source("photo.png", PNG)
        manifest = self.stage(
            EvidenceSelection("photo.png", ("multimodal_attachment",))
        )
        with self.assertRaisesRegex(ContractError, "cannot inspect"):
            check_carrier_capabilities(
                manifest,
                {
                    "carrier_id": "text-only",
                    "snapshot_media_classes": ["document"],
                    "multimodal_media_types": [],
                    "allow_sampled_video": False,
                },
            )
        receipt = check_carrier_capabilities(
            manifest,
            {
                "carrier_id": "image-carrier",
                "snapshot_media_classes": ["image"],
                "multimodal_media_types": ["image/png"],
                "allow_sampled_video": False,
            },
        )
        self.assertTrue(receipt["inspectable"])

    def test_coverage_distinguishes_cited_uncited_unknown_and_unreviewed(self) -> None:
        self.write_source("report.txt", b"report")
        self.write_source("clip.mp4", b"video")

        def fake_ffmpeg(command: list[str]) -> None:
            Path(command[-1]).write_bytes(PNG)

        manifest = self.stage(
            EvidenceSelection("report.txt"),
            EvidenceSelection("clip.mp4", frame_times_ms=(1000,)),
            frame_runner=fake_ffmpeg,
        )
        cited_ref = manifest["source_files"][0]["evidence_ref"]
        result = self.trial / "result.json"
        atomic_write_json(
            result,
            {
                "residuals": [
                    {
                        "evidence_refs": [cited_ref, "snapshot://invented"],
                        "finding": "bounded finding",
                    }
                ]
            },
        )
        receipt_path = self.trial / "trial-private" / "coverage.json"
        receipt = build_coverage_receipt(
            self.trial,
            artifacts=[result],
            declared_limitations=["OCR was not independently validated."],
            output=receipt_path,
        )
        self.assertEqual(receipt["coverage_status"], "limited")
        self.assertEqual(receipt["cited_evidence"][0]["evidence_ref"], cited_ref)
        self.assertEqual(len(receipt["exposed_but_uncited"]), 2)
        self.assertEqual(receipt["unknown_citations"][0]["evidence_ref"], "snapshot://invented")
        self.assertEqual(receipt["unreviewed_media"][0]["media_class"], "video")
        self.assertTrue(any("not equivalent" in item for item in receipt["limitations"]))
        validate_coverage_receipt(json.loads(receipt_path.read_text()), trial_root=self.trial)

    def test_coverage_replay_rejects_artifact_and_staged_byte_tamper(self) -> None:
        self.write_source("report.txt", b"report")
        manifest = self.stage(EvidenceSelection("report.txt"))
        result = self.trial / "result.json"
        atomic_write_json(result, {"evidence_refs": [manifest["source_files"][0]["evidence_ref"]]})
        receipt = build_coverage_receipt(self.trial, artifacts=[result])
        result.write_text("{}\n")
        with self.assertRaisesRegex(ContractError, "does not replay"):
            validate_coverage_receipt(receipt, trial_root=self.trial)

        atomic_write_json(result, {"evidence_refs": [manifest["source_files"][0]["evidence_ref"]]})
        staged = self.trial / "trial-private" / "evidence" / manifest["source_files"][0]["staged_ref"]
        os.chmod(staged, 0o600)
        staged.write_bytes(b"tampered")
        os.chmod(staged, 0o400)
        with self.assertRaisesRegex(ContractError, "digest/size mismatch"):
            validate_evidence_manifest(
                manifest,
                trial_root=self.trial,
                staged_root=staged.parents[2],
            )

    def test_stage_is_immutable_and_cli_selection_is_closed(self) -> None:
        self.write_source("report.txt", b"report")
        self.stage(EvidenceSelection("report.txt"))
        with self.assertRaises(StateError):
            self.stage(EvidenceSelection("report.txt"))

        other = self.base / "cli-trial"
        (other / "input").mkdir(parents=True)
        other_brief = other / "input" / "original-brief.json"
        atomic_write_json(other_brief, original_brief())
        selection = self.base / "selection.json"
        atomic_write_json(
            selection,
            {
                "selection_version": "1.0",
                "source_root": str(self.source),
                "files": [{"path": "report.txt"}],
            },
        )
        self.assertEqual(
            main(
                [
                    "stage-evidence",
                    str(other),
                    "--brief",
                    str(other_brief),
                    "--selection",
                    str(selection),
                ]
            ),
            0,
        )


if __name__ == "__main__":
    unittest.main()
