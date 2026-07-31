"""Capability-aware assignment and production-config policy tests."""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

from magi.assignment import validate_assignment_plan
from magi.configuration import (
    GLOBAL_CHECKS,
    assign_evidence_for_seat,
    carrier_capabilities_for_seat,
    generate_production_config,
)
from magi.errors import ContractError
from magi.evidence import (
    EvidenceSelection,
    check_carrier_capabilities,
    evidence_brief_inputs,
    stage_evidence,
)
from magi.io import atomic_write_json, digest_file

from tests.helpers import original_brief


PNG = b"\x89PNG\r\n\x1a\n" + b"deterministic-test-frame"
IMAGE_DIGEST = "sha256:" + "a" * 64

SEAT_CONFIGS = {
    "seat-m": {
        "seat_config_version": "1.0",
        "seat_id": "seat-m",
        "model_family": "mimo",
        "provider": "xiaomi",
        "text_model": "mimo-v2.5-pro",
        "multimodal_model": "mimo-v2.5",
        "profile_id": "formalist",
        "provider_key_env": "XIAOMI_API_KEY",
        "provider_base_url_env": "XIAOMI_BASE_URL",
        "provider_base_url": "https://example.invalid/mimo",
    },
    "seat-d": {
        "seat_config_version": "1.0",
        "seat_id": "seat-d",
        "model_family": "deepseek",
        "provider": "deepseek",
        "text_model": "deepseek-v4-pro",
        "multimodal_model": "deepseek-v4-pro",
        "profile_id": "adversarial",
        "provider_key_env": "DEEPSEEK_API_KEY",
        "provider_base_url_env": "DEEPSEEK_BASE_URL",
        "provider_base_url": "https://example.invalid/deepseek",
    },
    "seat-g": {
        "seat_config_version": "1.0",
        "seat_id": "seat-g",
        "model_family": "openai",
        "provider": "openai-api",
        "text_model": "gpt-5.6-sol",
        "multimodal_model": "gpt-5.6-sol",
        "profile_id": "empirical",
        "provider_key_env": "OPENAI_API_KEY",
        "provider_base_url_env": "OPENAI_BASE_URL",
        "provider_base_url": "https://example.invalid/openai",
    },
}


def _write_profile(root: Path, seat_id: str, profile_id: str) -> Path:
    profile = root / seat_id
    profile.mkdir(parents=True)
    (profile / "SOUL.md").write_text(f"soul for {profile_id}\n", encoding="utf-8")
    (profile / "AGENTS.md").write_text("agents\n", encoding="utf-8")
    (profile / "config.yaml").write_text("memory:\n  memory_enabled: false\n", encoding="utf-8")
    atomic_write_json(
        profile / "profile.json",
        {
            "profile_id": profile_id,
            "discipline": "engineering",
            "epistemic_lens": "test",
            "methods": ["method-a"],
            "failure_checks": ["fail-a"],
            "instructions": "test profile",
        },
    )
    # Composition receipt must match content digest rules used by configuration.
    hasher = hashlib.sha256()
    for path in sorted(item for item in profile.rglob("*") if item.is_file()):
        relative = path.relative_to(profile).as_posix().encode()
        raw = path.read_bytes()
        hasher.update(len(relative).to_bytes(8, "big"))
        hasher.update(relative)
        hasher.update(len(raw).to_bytes(8, "big"))
        hasher.update(raw)
    content = "sha256:" + hasher.hexdigest()
    atomic_write_json(
        profile / "COMPOSITION.json",
        {
            "composition_version": "1.0",
            "seat_id": seat_id,
            "profile_id": profile_id,
            "base_sha256": "sha256:" + "b" * 64,
            "overlay_sha256": "sha256:" + "c" * 64,
            "composed_content_sha256": content,
        },
    )
    # Recompute including COMPOSITION.json (runtime digests the full tree).
    hasher = hashlib.sha256()
    for path in sorted(item for item in profile.rglob("*") if item.is_file()):
        relative = path.relative_to(profile).as_posix().encode()
        raw = path.read_bytes()
        hasher.update(len(relative).to_bytes(8, "big"))
        hasher.update(relative)
        hasher.update(len(raw).to_bytes(8, "big"))
        hasher.update(raw)
    # COMPOSITION composed_content_sha256 historically excludes itself in entrypoint;
    # configuration._profile_tree_digest hashes every file including COMPOSITION.json.
    return profile


class ConfigurationAssignmentTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.base = Path(self.temporary.name)
        self.trial = self.base / "trial"
        self.source = self.base / "source"
        (self.trial / "input").mkdir(parents=True)
        self.source.mkdir()
        self.brief = self.trial / "input" / "original-brief.json"
        atomic_write_json(self.brief, original_brief())
        self.repo = self.base / "repo"
        (self.repo / "container" / "seats").mkdir(parents=True)
        (self.repo / "scripts" / "host").mkdir(parents=True)
        (self.repo / "bin").mkdir(parents=True)
        for seat_id, config in SEAT_CONFIGS.items():
            atomic_write_json(self.repo / "container" / "seats" / f"{seat_id}.json", config)
        # Minimal host launcher stubs so argv paths exist.
        launcher = self.repo / "scripts" / "host" / "magi-seat.sh"
        launcher.write_text("#!/bin/sh\n", encoding="utf-8")
        launcher.chmod(0o755)
        self.profiles = {
            seat_id: _write_profile(
                self.base / "profiles", seat_id, config["profile_id"]
            )
            for seat_id, config in SEAT_CONFIGS.items()
        }

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _stage_mixed(self) -> dict:
        (self.source / "report.txt").write_bytes(b"report body")
        (self.source / "photo.png").write_bytes(PNG)
        return stage_evidence(
            self.trial,
            original_brief=self.brief,
            source_root=self.source,
            selections=[
                EvidenceSelection("report.txt"),
                EvidenceSelection("photo.png", ("multimodal_attachment", "snapshot")),
            ],
        )

    def test_mixed_text_image_allocation_by_seat_policy(self) -> None:
        manifest = self._stage_mixed()
        items = [*manifest["source_files"], *manifest["derived_frames"]]
        by_class = {item["media_class"]: item for item in items}
        doc_ref = by_class["document"]["evidence_ref"]
        image_ref = by_class["image"]["evidence_ref"]

        mimo = assign_evidence_for_seat("seat-m", SEAT_CONFIGS["seat-m"], items)
        deepseek = assign_evidence_for_seat("seat-d", SEAT_CONFIGS["seat-d"], items)
        codex = assign_evidence_for_seat("seat-g", SEAT_CONFIGS["seat-g"], items)

        mimo_refs = {item["evidence_ref"] for item in mimo}
        deepseek_refs = {item["evidence_ref"] for item in deepseek}
        codex_refs = {item["evidence_ref"] for item in codex}

        self.assertIn(doc_ref, mimo_refs)
        self.assertIn(image_ref, mimo_refs)
        self.assertEqual(deepseek_refs, {doc_ref})
        self.assertNotIn(image_ref, deepseek_refs)
        self.assertEqual(codex_refs, set())

    def test_deepseek_never_receives_image_or_frame_attachments(self) -> None:
        (self.source / "clip.mp4").write_bytes(b"video")
        (self.source / "note.txt").write_bytes(b"note")

        def fake_ffmpeg(command: list[str]) -> None:
            Path(command[-1]).write_bytes(PNG)

        manifest = stage_evidence(
            self.trial,
            original_brief=self.brief,
            source_root=self.source,
            selections=[
                EvidenceSelection("note.txt"),
                EvidenceSelection("clip.mp4", frame_times_ms=(1000,)),
            ],
            frame_runner=fake_ffmpeg,
        )
        items = [*manifest["source_files"], *manifest["derived_frames"]]
        assigned = assign_evidence_for_seat("seat-d", SEAT_CONFIGS["seat-d"], items)
        for item in assigned:
            self.assertEqual(item["media_class"], "document")
            self.assertFalse(item["evidence_ref"].startswith("snapshot://derived/"))
        carrier = carrier_capabilities_for_seat(SEAT_CONFIGS["seat-d"], assigned)
        self.assertEqual(carrier["multimodal_media_types"], [])
        self.assertFalse(carrier["allow_sampled_video"])
        # Subset validation succeeds; full-manifest validation would fail.
        check_carrier_capabilities(
            manifest,
            carrier,
            evidence_refs=[item["evidence_ref"] for item in assigned],
        )
        with self.assertRaisesRegex(ContractError, "cannot inspect"):
            check_carrier_capabilities(manifest, carrier)

    def test_codex_gets_no_original_media(self) -> None:
        manifest = self._stage_mixed()
        items = [*manifest["source_files"], *manifest["derived_frames"]]
        assigned = assign_evidence_for_seat("seat-g", SEAT_CONFIGS["seat-g"], items)
        self.assertEqual(assigned, [])
        carrier = carrier_capabilities_for_seat(SEAT_CONFIGS["seat-g"], assigned)
        self.assertEqual(carrier["multimodal_media_types"], [])
        check_carrier_capabilities(manifest, carrier, evidence_refs=[])

    def test_all_seats_retain_complete_global_checks(self) -> None:
        manifest = self._stage_mixed()
        manifest_path = self.trial / "trial-private" / "evidence" / "evidence-manifest.json"
        output = self.base / "config-out"
        paths = generate_production_config(
            repo_root=self.repo,
            trial_dir=self.trial,
            trial_id="trial-mixed-1",
            evidence_manifest=manifest_path,
            profile_sources=self.profiles,
            image_digest=IMAGE_DIGEST,
            output_dir=output,
        )
        plan = validate_assignment_plan(json.loads(paths["assignment_plan"].read_text()))
        for seat in plan["seats"]:
            self.assertEqual(seat["mandatory_global_checks"], GLOBAL_CHECKS)
            self.assertEqual(plan["global_checks"], GLOBAL_CHECKS)

    def test_generate_plan_mixed_media_does_not_fail_deepseek(self) -> None:
        self._stage_mixed()
        manifest_path = self.trial / "trial-private" / "evidence" / "evidence-manifest.json"
        paths = generate_production_config(
            repo_root=self.repo,
            trial_dir=self.trial,
            trial_id="trial-mixed-2",
            evidence_manifest=manifest_path,
            profile_sources=self.profiles,
            image_digest=IMAGE_DIGEST,
            output_dir=self.base / "config-out-2",
        )
        plan = validate_assignment_plan(json.loads(paths["assignment_plan"].read_text()))
        by_seat = {seat["seat_id"]: seat for seat in plan["seats"]}
        self.assertTrue(any("photo" in ref or "source-" in ref for ref in by_seat["seat-m"]["evidence_refs"]))
        self.assertTrue(
            all(
                "image" not in ref and "png" not in ref
                for ref in by_seat["seat-d"]["evidence_refs"]
            )
            or by_seat["seat-d"]["evidence_refs"]
        )
        # DeepSeek refs must only be document snapshots from this fixture.
        for ref in by_seat["seat-d"]["evidence_refs"]:
            self.assertTrue(ref.startswith("snapshot://source/"))
            self.assertFalse(ref.endswith(".png"))
        self.assertEqual(by_seat["seat-g"]["evidence_refs"], [])
        for review in plan["cross_review_obligations"]:
            self.assertEqual(review["review_kind"], "artifact_review")
            self.assertEqual(review["evidence_refs"], [])

    def test_assigned_subset_carrier_validation_and_brief_ignore(self) -> None:
        manifest = self._stage_mixed()
        items = [*manifest["source_files"], *manifest["derived_frames"]]
        deepseek = assign_evidence_for_seat("seat-d", SEAT_CONFIGS["seat-d"], items)
        refs = [item["evidence_ref"] for item in deepseek]
        rendered = evidence_brief_inputs(manifest, evidence_refs=refs)
        self.assertEqual(rendered["evidence_roots"], ["/evidence/snapshot"])
        self.assertEqual(rendered["attachments"], [])
        self.assertTrue(any(path.endswith(".png") for path in rendered["snapshot_ignore"]))

    def test_invalid_image_digest_fails_closed(self) -> None:
        self._stage_mixed()
        manifest_path = self.trial / "trial-private" / "evidence" / "evidence-manifest.json"
        with self.assertRaisesRegex(ContractError, "image_digest"):
            generate_production_config(
                repo_root=self.repo,
                trial_dir=self.trial,
                trial_id="trial-bad-digest",
                evidence_manifest=manifest_path,
                profile_sources=self.profiles,
                image_digest="not-a-digest",
                output_dir=self.base / "bad",
            )

    def test_invalid_profile_composition_fails_closed(self) -> None:
        self._stage_mixed()
        manifest_path = self.trial / "trial-private" / "evidence" / "evidence-manifest.json"
        broken = self.profiles["seat-m"]
        atomic_write_json(
            broken / "COMPOSITION.json",
            {
                "composition_version": "1.0",
                "seat_id": "seat-m",
                "profile_id": "formalist",
                "base_sha256": "sha256:" + "b" * 64,
                "overlay_sha256": "sha256:" + "c" * 64,
                "composed_content_sha256": "not-valid",
            },
        )
        with self.assertRaisesRegex(ContractError, "profile composition"):
            generate_production_config(
                repo_root=self.repo,
                trial_dir=self.trial,
                trial_id="trial-bad-profile",
                evidence_manifest=manifest_path,
                profile_sources=self.profiles,
                image_digest=IMAGE_DIGEST,
                output_dir=self.base / "bad-profile",
            )


if __name__ == "__main__":
    unittest.main()
