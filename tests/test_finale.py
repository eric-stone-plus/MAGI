"""Finale container contract, image pin, and product-replay tamper tests."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from magi.configuration import (
    generate_production_config,
    require_finale_container_execution,
)
from magi.errors import ContractError
from magi.io import atomic_write_json, digest_file
from magi.oci import reconcile_declared_and_observed
from magi.runner import FunctionRunner
from magi.runtime import TrialRuntime
from magi.evidence import stage_empty_evidence

from tests.helpers import original_brief
from tests.test_configuration import IMAGE_DIGEST, SEAT_CONFIGS, _write_profile
from tests.test_runtime import RuntimeTests


ROOT = Path(__file__).resolve().parents[1]


class FinaleContractTests(unittest.TestCase):
    def test_compose_defines_final_adjudicator_service(self) -> None:
        text = (ROOT / "container" / "compose.yml").read_text(encoding="utf-8")
        self.assertIn("\n  final-adjudicator:\n", text)
        self.assertIn("final-adjudicator-private", text)
        self.assertIn("final-adjudicator-egress", text)
        self.assertIn("MAGI_SEAT_MODE: final", text)
        self.assertIn("MAGI_FINAL_PACKET", text)
        self.assertIn("MAGI_FINAL_OUTPUT", text)
        proxy = (ROOT / "container" / "proxy" / "final-adjudicator.cfg").read_text(
            encoding="utf-8"
        )
        self.assertIn("apinebula.com", proxy)

    def test_require_finale_container_execution_rejects_host(self) -> None:
        with self.assertRaisesRegex(ContractError, "must be container"):
            require_finale_container_execution(
                {
                    "family": "openai",
                    "provider": "openai-api",
                    "text_model": "x",
                    "multimodal_model": "x",
                    "mode": "host",
                    "service": "final-adjudicator",
                    "image_digest": "sha256:" + "a" * 64,
                }
            )
        with self.assertRaisesRegex(ContractError, "final-adjudicator"):
            require_finale_container_execution(
                {
                    "family": "openai",
                    "provider": "openai-api",
                    "text_model": "x",
                    "multimodal_model": "x",
                    "mode": "container",
                    "service": "seat-g",
                    "image_digest": "sha256:" + "a" * 64,
                }
            )

    def test_production_configure_emits_container_finale(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            trial = base / "trial"
            (trial / "input").mkdir(parents=True)
            brief = trial / "input" / "original-brief.json"
            atomic_write_json(brief, original_brief())
            stage_empty_evidence(trial, original_brief=brief)
            repo = base / "repo"
            (repo / "container" / "seats").mkdir(parents=True)
            (repo / "scripts" / "host").mkdir(parents=True)
            (repo / "bin").mkdir(parents=True)
            for seat_id, config in SEAT_CONFIGS.items():
                atomic_write_json(repo / "container" / "seats" / f"{seat_id}.json", config)
            launcher = repo / "scripts" / "host" / "magi-seat.sh"
            launcher.write_text("#!/bin/sh\n", encoding="utf-8")
            launcher.chmod(0o755)
            profiles = {
                seat_id: _write_profile(base / "profiles", seat_id, config["profile_id"])
                for seat_id, config in SEAT_CONFIGS.items()
            }
            paths = generate_production_config(
                repo_root=repo,
                trial_dir=trial,
                trial_id="finale-contract-1",
                evidence_manifest=trial
                / "trial-private"
                / "evidence"
                / "evidence-manifest.json",
                profile_sources=profiles,
                image_digest=IMAGE_DIGEST,
                output_dir=base / "out",
            )
            agents = json.loads(paths["agents"].read_text(encoding="utf-8"))
            execution = agents["final_adjudicator"]["execution"]
            self.assertEqual(execution["mode"], "container")
            self.assertEqual(execution["service"], "final-adjudicator")
            self.assertEqual(execution["image_digest"], IMAGE_DIGEST)
            require_finale_container_execution(execution)

    def test_image_override_pin_mismatch_fails_closed(self) -> None:
        with self.assertRaisesRegex(ContractError, "does not match declared"):
            reconcile_declared_and_observed(
                declared_digest="sha256:" + "1" * 64,
                observed_digest="sha256:" + "2" * 64,
            )

    def test_command_runner_injects_pin_for_final_agent_path(self) -> None:
        """Production final-agent pass_env receives the frozen image pin."""

        from magi.runner import CommandRunner, CommandSpec
        import os

        pin = "sha256:" + "d" * 64
        spec = CommandSpec.from_value(
            {
                "argv": [str(ROOT / "scripts" / "host" / "magi-seat.sh"), "final-agent"],
                "timeout_seconds": 30,
                "pass_env": [
                    "MAGI_FINAL_CONFIG",
                    "MAGI_FINAL_SECRET_FILE",
                    "MAGI_REQUIRED_IMAGE_DIGEST",
                    "MAGI_SEAT_IMAGE",
                ],
                "execution": {
                    "family": "openai",
                    "provider": "openai-api",
                    "text_model": "gpt-5.6-sol",
                    "multimodal_model": "gpt-5.6-sol",
                    "mode": "container",
                    "service": "final-adjudicator",
                    "image_digest": pin,
                },
            },
            "final",
        )
        old = os.environ.pop("MAGI_REQUIRED_IMAGE_DIGEST", None)
        try:
            env = CommandRunner().environment_for(spec)
            self.assertEqual(env.get("MAGI_REQUIRED_IMAGE_DIGEST"), pin)
        finally:
            if old is not None:
                os.environ["MAGI_REQUIRED_IMAGE_DIGEST"] = old


class FinaleProductTamperTests(unittest.TestCase):
    """Uses RuntimeTests fixture without inheriting its entire suite."""

    def setUp(self) -> None:
        self._fixture = RuntimeTests("setUp")
        self._fixture.setUp()
        self.trial = self._fixture.trial
        self.config = self._fixture.config
        self.agent = self._fixture.agent

    def tearDown(self) -> None:
        self._fixture.tearDown()

    def test_product_summary_finale_is_container_service(self) -> None:
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        product = runtime.run(self.config)
        self.assertEqual(product["final_adjudicator"]["execution_mode"], "container")
        receipt = json.loads(
            (self.trial / "final" / "adjudicator-execution-receipt.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(receipt["execution_mode"], "container")
        self.assertEqual(receipt["service"], "final-adjudicator")
        self.assertEqual(receipt["kind"], "final_adjudication")

    def test_tampered_finale_execution_receipt_fails_replay(self) -> None:
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        runtime.run(self.config)
        path = self.trial / "final" / "adjudicator-execution-receipt.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["service"] = "host-magi-agent"
        atomic_write_json(path, value)
        with self.assertRaisesRegex(
            ContractError, "execution receipt mismatch|stored artifact digest mismatch"
        ):
            runtime.status()

    def test_tampered_finale_verdict_fails_replay(self) -> None:
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        runtime.run(self.config)
        path = self.trial / "final" / "verdict.json"
        value = json.loads(path.read_text(encoding="utf-8"))
        value["summary"] = value["summary"] + " tampered"
        atomic_write_json(path, value)
        with self.assertRaisesRegex(
            ContractError, "digest does not match|final verdict|stored artifact digest mismatch"
        ):
            runtime.status()

    def test_load_config_rejects_host_finale(self) -> None:
        config = json.loads(self.config.read_text(encoding="utf-8"))
        config["final_adjudicator"]["execution"]["mode"] = "host"
        atomic_write_json(self.config, config)
        with self.assertRaisesRegex(ContractError, "must be container"):
            TrialRuntime(self.trial, FunctionRunner(self.agent)).run(self.config)


if __name__ == "__main__":
    unittest.main()
