"""MAGI canonical ↔ QUINTE-local evidence mapping receipt tests."""

from __future__ import annotations

import copy
import unittest

from magi.errors import ContractError
from magi.mapping import build_mapping_receipt, replay_mapping_receipt, validate_mapping_receipt


def _canonical_doc() -> dict:
    return {
        "evidence_ref": "snapshot://source/source-0001.txt",
        "staged_ref": "snapshot/source/source-0001.txt",
        "sha256": "sha256:" + "1" * 64,
        "size_bytes": 12,
        "media_type": "text/plain",
        "media_class": "document",
        "exposure_modes": ["snapshot"],
    }


def _canonical_image() -> dict:
    return {
        "evidence_ref": "snapshot://source/source-0002.png",
        "staged_ref": "snapshot/source/source-0002.png",
        "sha256": "sha256:" + "2" * 64,
        "size_bytes": 64,
        "media_type": "image/png",
        "media_class": "image",
        "exposure_modes": ["multimodal_attachment", "snapshot"],
    }


def _evidence_manifest(*items: dict) -> dict:
    return {
        "evidence_manifest_version": "1.0",
        "source_files": list(items),
        "derived_frames": [],
    }


def _quinte_manifest(*, entries=None, attachments=None) -> dict:
    return {
        "snapshot_version": "1.0",
        "created_at": "2026-07-31T00:00:00Z",
        "entries": entries or [],
        "attachments": attachments or [],
        "total_bytes": 0,
    }


class MappingReceiptTests(unittest.TestCase):
    def test_snapshot_and_attachment_one_to_many(self) -> None:
        image = _canonical_image()
        quinte = _quinte_manifest(
            entries=[
                {
                    "snapshot_ref": "snapshot://root-0/source-0002.png",
                    "source_name": "source-0002.png",
                    "sha256": image["sha256"],
                    "bytes": image["size_bytes"],
                    "media_type": "image/png",
                }
            ],
            attachments=[
                {
                    "attachment_ref": "attachment://attachment-0.png",
                    "source_name": "source-0002.png",
                    "sha256": image["sha256"],
                    "bytes": image["size_bytes"],
                    "media_type": "image/png",
                }
            ],
        )
        receipt = build_mapping_receipt(
            seat_id="seat-m",
            evidence_manifest=_evidence_manifest(image),
            evidence_manifest_sha256="sha256:" + "a" * 64,
            assignment_plan_sha256="sha256:" + "b" * 64,
            assigned_evidence_refs=[image["evidence_ref"]],
            quinte_run_id="run-1",
            quinte_snapshot_manifest=quinte,
            quinte_snapshot_manifest_ref="quinte-run/input/snapshot-manifest.json",
            quinte_snapshot_manifest_sha256="sha256:" + "c" * 64,
        )
        self.assertEqual(
            receipt["mappings"][0]["quinte_local_refs"],
            [
                "attachment://attachment-0.png",
                "snapshot://root-0/source-0002.png",
            ],
        )
        validate_mapping_receipt(receipt)

    def test_missing_mapping_fails_closed(self) -> None:
        doc = _canonical_doc()
        with self.assertRaisesRegex(ContractError, "no QUINTE-local entry"):
            build_mapping_receipt(
                seat_id="seat-d",
                evidence_manifest=_evidence_manifest(doc),
                evidence_manifest_sha256="sha256:" + "a" * 64,
                assignment_plan_sha256="sha256:" + "b" * 64,
                assigned_evidence_refs=[doc["evidence_ref"]],
                quinte_run_id="run-1",
                quinte_snapshot_manifest=_quinte_manifest(),
                quinte_snapshot_manifest_ref="quinte-run/input/snapshot-manifest.json",
                quinte_snapshot_manifest_sha256="sha256:" + "c" * 64,
            )

    def test_digest_drift_fails_closed(self) -> None:
        doc = _canonical_doc()
        quinte = _quinte_manifest(
            entries=[
                {
                    "snapshot_ref": "snapshot://root-0/source-0001.txt",
                    "source_name": "source-0001.txt",
                    "sha256": doc["sha256"],
                    "bytes": doc["size_bytes"],
                    "media_type": "text/plain",
                }
            ]
        )
        receipt = build_mapping_receipt(
            seat_id="seat-d",
            evidence_manifest=_evidence_manifest(doc),
            evidence_manifest_sha256="sha256:" + "a" * 64,
            assignment_plan_sha256="sha256:" + "b" * 64,
            assigned_evidence_refs=[doc["evidence_ref"]],
            quinte_run_id="run-1",
            quinte_snapshot_manifest=quinte,
            quinte_snapshot_manifest_ref="quinte-run/input/snapshot-manifest.json",
            quinte_snapshot_manifest_sha256="sha256:" + "c" * 64,
        )
        tampered = copy.deepcopy(receipt)
        tampered["mappings"][0]["quinte_entries"][0]["sha256"] = "sha256:" + "9" * 64
        with self.assertRaisesRegex(ContractError, "drifted|binding"):
            validate_mapping_receipt(tampered)

    def test_duplicate_local_ref_fails_closed(self) -> None:
        doc = _canonical_doc()
        image = _canonical_image()
        # Force both digests identical so two canonical items compete for same locals.
        image = dict(image)
        image["sha256"] = doc["sha256"]
        quinte = _quinte_manifest(
            entries=[
                {
                    "snapshot_ref": "snapshot://root-0/shared.bin",
                    "source_name": "shared.bin",
                    "sha256": doc["sha256"],
                    "bytes": 12,
                    "media_type": "application/octet-stream",
                }
            ]
        )
        with self.assertRaisesRegex(ContractError, "already mapped"):
            build_mapping_receipt(
                seat_id="seat-m",
                evidence_manifest=_evidence_manifest(doc, image),
                evidence_manifest_sha256="sha256:" + "a" * 64,
                assignment_plan_sha256="sha256:" + "b" * 64,
                assigned_evidence_refs=sorted(
                    [doc["evidence_ref"], image["evidence_ref"]]
                ),
                quinte_run_id="run-1",
                quinte_snapshot_manifest=quinte,
                quinte_snapshot_manifest_ref="quinte-run/input/snapshot-manifest.json",
                quinte_snapshot_manifest_sha256="sha256:" + "c" * 64,
            )

    def test_empty_assignment_receipt_is_valid(self) -> None:
        receipt = build_mapping_receipt(
            seat_id="seat-g",
            evidence_manifest=_evidence_manifest(_canonical_doc()),
            evidence_manifest_sha256="sha256:" + "a" * 64,
            assignment_plan_sha256="sha256:" + "b" * 64,
            assigned_evidence_refs=[],
            quinte_run_id="run-1",
            quinte_snapshot_manifest=_quinte_manifest(
                entries=[
                    {
                        "snapshot_ref": "snapshot://root-0/x.txt",
                        "source_name": "x.txt",
                        "sha256": "sha256:" + "1" * 64,
                        "bytes": 1,
                        "media_type": "text/plain",
                    }
                ]
            ),
            quinte_snapshot_manifest_ref="quinte-run/input/snapshot-manifest.json",
            quinte_snapshot_manifest_sha256="sha256:" + "c" * 64,
        )
        self.assertEqual(receipt["mappings"], [])
        self.assertEqual(
            receipt["unmapped_quinte_local_refs"], ["snapshot://root-0/x.txt"]
        )

    def test_replay_after_resume(self) -> None:
        doc = _canonical_doc()
        evidence = _evidence_manifest(doc)
        quinte = _quinte_manifest(
            entries=[
                {
                    "snapshot_ref": "snapshot://root-0/source-0001.txt",
                    "source_name": "source-0001.txt",
                    "sha256": doc["sha256"],
                    "bytes": doc["size_bytes"],
                    "media_type": "text/plain",
                }
            ]
        )
        kwargs = dict(
            seat_id="seat-d",
            evidence_manifest=evidence,
            evidence_manifest_sha256="sha256:" + "a" * 64,
            assignment_plan_sha256="sha256:" + "b" * 64,
            assigned_evidence_refs=[doc["evidence_ref"]],
            quinte_run_id="run-1",
            quinte_snapshot_manifest=quinte,
            quinte_snapshot_manifest_ref="quinte-run/input/snapshot-manifest.json",
            quinte_snapshot_manifest_sha256="sha256:" + "c" * 64,
        )
        receipt = build_mapping_receipt(**kwargs)
        replay_mapping_receipt(
            receipt,
            evidence_manifest=evidence,
            evidence_manifest_sha256=kwargs["evidence_manifest_sha256"],
            assignment_plan_sha256=kwargs["assignment_plan_sha256"],
            assigned_evidence_refs=kwargs["assigned_evidence_refs"],
            quinte_snapshot_manifest=quinte,
            quinte_snapshot_manifest_sha256=kwargs["quinte_snapshot_manifest_sha256"],
        )
        tampered_quinte = copy.deepcopy(quinte)
        tampered_quinte["entries"][0]["sha256"] = "sha256:" + "8" * 64
        with self.assertRaisesRegex(ContractError, "does not replay|no QUINTE-local"):
            replay_mapping_receipt(
                receipt,
                evidence_manifest=evidence,
                evidence_manifest_sha256=kwargs["evidence_manifest_sha256"],
                assignment_plan_sha256=kwargs["assignment_plan_sha256"],
                assigned_evidence_refs=kwargs["assigned_evidence_refs"],
                quinte_snapshot_manifest=tampered_quinte,
                quinte_snapshot_manifest_sha256=kwargs["quinte_snapshot_manifest_sha256"],
            )


if __name__ == "__main__":
    unittest.main()
