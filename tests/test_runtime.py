from __future__ import annotations

import json
import tempfile
import unittest
import subprocess
import threading
import time
from pathlib import Path

from magi.io import atomic_write_json
from magi.errors import ContractError, StateError
from magi.runner import CommandSpec, FunctionRunner
from magi.runtime import TrialRuntime
from tests.helpers import assignment_plan, finding, make_fixture, profiled_review_fields
from magi.evidence import stage_empty_evidence


class RuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.fixture = self.root / "fixture"
        self.paths = make_fixture(self.fixture)
        self.trial = self.root / "trial"
        runtime = TrialRuntime.initialize(
            self.trial,
            trial_id="trial-1",
            seat_slots=["seat-m", "seat-d", "seat-g"],
            action_boundary="protected_write",
            original_brief=self.fixture / "original-brief.json",
        )
        stage_empty_evidence(
            self.trial, original_brief=self.trial / "input" / "original-brief.json"
        )
        plan = assignment_plan(self.fixture, trial_id="trial-1")
        runtime._bind_evidence_manifest(runtime.load_state())
        runtime._bind_assignment_plan(runtime.load_state(), plan)
        for seat, dossier in zip(["seat-m", "seat-d", "seat-g"], self.paths):
            runtime.register_dossier(seat, dossier)
        self.config = self.root / "agents.json"
        specs = {
            seat: {
                "argv": ["unused"],
                "timeout_seconds": 30,
                "pass_env": [],
                "reviewer_profile_mode": "hermes_profile",
                "profile_source": str(
                    self.trial / "dossiers" / seat / "reviewer-profile"
                ),
                "execution": {
                    "family": family,
                    "provider": f"provider-{family}",
                    "text_model": f"model-{family}",
                    "multimodal_model": f"model-{family}",
                    "mode": "test_function",
                    "service": seat,
                    "image_digest": "sha256:" + "a" * 64,
                },
            }
            for seat, family in (
                ("seat-m", "mimo"),
                ("seat-d", "deepseek"),
                ("seat-g", "openai"),
            )
        }
        final_spec = {
            "argv": ["unused"],
            "timeout_seconds": 30,
            "pass_env": [],
            "execution": {
                "family": "openai",
                "provider": "openai-api",
                "text_model": "gpt-5.6-sol",
                "multimodal_model": "gpt-5.6-sol",
                "mode": "container",
                "service": "final-adjudicator",
                "image_digest": "sha256:" + "b" * 64,
            },
        }
        atomic_write_json(
            self.config,
            {
                "config_version": "1.0",
                "seat_agents": specs,
                "final_adjudicator": final_spec,
            },
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_initialize_rejects_nonportable_trial_id_before_writing(self) -> None:
        trial = self.root / "bad-trial"
        with self.assertRaisesRegex(ContractError, "portable identifier"):
            TrialRuntime.initialize(
                trial,
                trial_id="../escape",
                seat_slots=["seat-m", "seat-d", "seat-g"],
                action_boundary="none",
                original_brief=self.fixture / "original-brief.json",
            )
        self.assertFalse(trial.exists())

    def test_run_requires_all_frozen_dossiers_before_config_freeze(self) -> None:
        trial = self.root / "empty-trial"
        runtime = TrialRuntime.initialize(
            trial,
            trial_id="empty-trial",
            seat_slots=["seat-m", "seat-d", "seat-g"],
            action_boundary="none",
            original_brief=self.fixture / "original-brief.json",
        )
        with self.assertRaisesRegex(StateError, "awaiting_dossiers"):
            runtime.run(self.config)
        self.assertIsNone(runtime.load_state()["agent_config_sha256"])

    @staticmethod
    def agent(_: CommandSpec, payload: dict) -> dict:
        if payload["task"] == "magi_cross_review":
            reviewer = payload["reviewer_alias"]
            subject = payload["subject_alias"]
            identifier = "review-risk"
            return {
                "review_version": "1.1",
                "reviewer_alias": reviewer,
                "subject_alias": subject,
                **profiled_review_fields(payload),
                "summary": "Review found a high risk.",
                "findings": [
                    finding(
                        identifier,
                        f"review:{reviewer}>{subject}:finding:{identifier}",
                    )
                ],
                "dissent": [],
            }
        seat_refs = [ref for refs in payload["canonical_seat_source_refs"].values() for ref in refs]
        review_refs = [
            item["source_refs"][0]
            for review in payload["cross_reviews"]
            for item in review["findings"]
        ]
        return {
            "verdict_version": "1.0",
            "decision": "BLOCK",
            "summary": "High-risk evidence blocks release.",
            "recommendation": "Resolve every risk.",
            "findings": [
                finding(f"ALL-HIGH-RISK-{index}", source_ref)
                for index, source_ref in enumerate(seat_refs + review_refs)
            ],
            "dissent": [],
        }

    def test_full_six_review_final_adjudication_pipeline_and_resume(self) -> None:
        calls: list[str] = []

        def counting(spec: CommandSpec, payload: dict) -> dict:
            calls.append(payload["task"])
            value = self.agent(spec, payload)
            return value

        runtime = TrialRuntime(self.trial, FunctionRunner(counting))
        product = runtime.run(self.config)
        self.assertEqual(product["status"], "completed")
        self.assertEqual(calls.count("magi_cross_review"), 6)
        self.assertEqual(calls.count("magi_final_adjudication"), 1)
        trace = json.loads((self.trial / "final" / "residual-trace.json").read_text())
        self.assertEqual(trace["highball_decision"], "block")
        product = runtime.verify_product()
        self.assertEqual(product["product_version"], "1.0")
        self.assertTrue(product["product_sha256"].startswith("sha256:"))
        self.assertEqual(product["final_decision"], "BLOCK")
        self.assertEqual(len(product["seats"]), 3)
        self.assertEqual(len(product["cross_reviews"]), 6)
        for review in product["cross_reviews"]:
            self.assertIn(review["reviewer_seat_id"], {"seat-m", "seat-d", "seat-g"})
            self.assertTrue(review["reviewer_profile_source_sha256"].startswith("sha256:"))
            self.assertTrue(review["methodology_trace_sha256"].startswith("sha256:"))
            self.assertTrue(review["reviewer_execution_receipt_sha256"].startswith("sha256:"))
        self.assertEqual(product["final_adjudicator"]["family"], "openai")
        self.assertTrue(
            product["final_adjudicator"]["execution_receipt_sha256"].startswith("sha256:")
        )
        resumed = runtime.run(self.config)
        self.assertEqual(resumed["product_sha256"], product["product_sha256"])

    def test_frozen_assignment_is_reconciled_with_dossier_identity(self) -> None:
        plan_path = self.trial / "private" / "assignment-plan.json"
        plan = json.loads(plan_path.read_text())
        plan["seats"][0]["text_model"] = "model-drift"
        from magi.assignment import bind_assignment_plan
        from magi.io import digest_file

        atomic_write_json(plan_path, bind_assignment_plan(plan))
        state = json.loads((self.trial / "trial.json").read_text())
        state["assignment_plan_sha256"] = digest_file(plan_path)
        atomic_write_json(self.trial / "trial.json", state)
        with self.assertRaisesRegex(ContractError, "text_model.*assignment"):
            TrialRuntime(self.trial)._validate_seat_assignment(
                TrialRuntime(self.trial).load_state(),
                TrialRuntime(self.trial)._load_seats(TrialRuntime(self.trial).load_state())[0],
            )

    def test_status_returns_verified_product_after_completion(self) -> None:
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        product = runtime.run(self.config)
        status = runtime.status()
        self.assertEqual(status["product_version"], "1.0")
        self.assertEqual(status["product_sha256"], product["product_sha256"])

    def test_tampered_execution_receipt_fails_replay(self) -> None:
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        runtime.run(self.config)
        receipt = next((self.trial / "reviews").glob("*--execution.json"))
        value = json.loads(receipt.read_text())
        value["service"] = "changed"
        atomic_write_json(receipt, value)
        with self.assertRaisesRegex(ContractError, "execution receipt mismatch"):
            runtime.status()

    def test_tampered_mapping_receipt_fails_verify_product(self) -> None:
        """Product verification must not trust a mapping whose binding digest drifted."""
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        runtime.run(self.config)
        paths = list((self.trial / "dossiers").rglob("evidence-mapping-receipt.json"))
        self.assertTrue(paths, "expected mapping receipts after product run")
        target = paths[0]
        # Dossier trees are frozen read-only after registration; attacker-side
        # tamper must still be detectable when the product is re-verified.
        target.chmod(target.stat().st_mode | 0o200)
        target.parent.chmod(target.parent.stat().st_mode | 0o700)
        value = json.loads(target.read_text(encoding="utf-8"))
        value["receipt_binding_sha256"] = "sha256:" + "f" * 64
        atomic_write_json(target, value)
        with self.assertRaisesRegex(
            ContractError,
            "mapping digest does not match|binding digest does not match|mapping receipt",
        ):
            runtime.verify_product()

    def test_tampered_residual_reduction_receipt_fails_replay(self) -> None:
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        runtime.run(self.config)
        path = self.trial / "final" / "residual-reduction-receipt.json"
        value = json.loads(path.read_text())
        value["counts"]["cross_review_findings"] += 1
        atomic_write_json(path, value)
        state_path = self.trial / "trial.json"
        state = json.loads(state_path.read_text())
        from magi.io import digest_file

        state["residual_reduction_sha256"] = digest_file(path)
        atomic_write_json(state_path, state)
        with self.assertRaisesRegex(
            ContractError, "counts do not match|deterministic reconstruction"
        ):
            runtime.status()

    def test_product_summary_binds_final_dissent(self) -> None:
        dissent = "A cross-review assumption remains contested."

        def dissenting(spec: CommandSpec, payload: dict) -> dict:
            value = self.agent(spec, payload)
            if payload["task"] == "magi_cross_review" and payload["reviewer_alias"] == "Expert-1":
                value["dissent"] = [dissent]
            elif payload["task"] == "magi_final_adjudication":
                value["decision"] = "ESCALATE"
                value["dissent"] = payload["required_dissent"]
            return value

        product = TrialRuntime(self.trial, FunctionRunner(dissenting)).run(self.config)
        self.assertEqual(product["final_dissent"], [dissent])

    def test_final_dissent_is_trimmed_deduplicated_and_sorted(self) -> None:
        def dissenting(spec: CommandSpec, payload: dict) -> dict:
            value = self.agent(spec, payload)
            if payload["task"] == "magi_cross_review":
                value["dissent"] = ["  zeta dissent  ", "alpha dissent"]
            elif payload["task"] == "magi_final_adjudication":
                value["decision"] = "ESCALATE"
                value["dissent"] = payload["required_dissent"]
            return value

        product = TrialRuntime(self.trial, FunctionRunner(dissenting)).run(self.config)
        self.assertEqual(product["final_dissent"], ["alpha dissent", "zeta dissent"])

    def test_final_packet_includes_seat_and_review_dissent(self) -> None:
        seat_dissent = "Seat-m model identity remains disputed."
        review_dissent = "A review assumption remains contested."
        seat = self.trial / "dossiers" / "seat-m" / "quinte-run" / "result.json"
        # Frozen fixtures are read-only by contract; fault injection changes a
        # loaded seat below through the normal final packet construction path.
        packets: list[dict] = []

        def capturing(spec: CommandSpec, payload: dict) -> dict:
            value = self.agent(spec, payload)
            if payload["task"] == "magi_cross_review" and payload["reviewer_alias"] == "Expert-1":
                value["dissent"] = [review_dissent]
            elif payload["task"] == "magi_final_adjudication":
                packets.append(payload)
                value["decision"] = "ESCALATE"
                value["dissent"] = payload["required_dissent"]
            return value

        runtime = TrialRuntime(self.trial, FunctionRunner(capturing))
        original_loader = runtime._load_seats

        def seats_with_dissent(state: dict) -> list:
            seats = original_loader(state)
            target = next(item for item in seats if item.seat_id == "seat-m")
            target.result["dissent"] = [seat_dissent]
            return seats

        runtime._load_seats = seats_with_dissent  # type: ignore[method-assign]
        runtime.run(self.config)
        self.assertEqual(len(packets), 1)
        required = packets[0]["required_dissent"]
        self.assertIn(review_dissent, required)
        self.assertTrue(any("identity remains disputed" in item for item in required))

    def test_completed_state_requires_all_six_review_refs(self) -> None:
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        runtime.run(self.config)
        state_path = self.trial / "trial.json"
        state = json.loads(state_path.read_text())
        removed = state["review_refs"].pop()
        state["review_sha256"].pop(removed)
        state["review_execution_sha256"].pop(
            str(Path(removed).with_name(Path(removed).stem + "--execution.json"))
        )
        atomic_write_json(state_path, state)
        with self.assertRaisesRegex(ContractError, "requires six cross-reviews"):
            runtime.load_state()

    def test_state_rejects_artifact_reference_escape(self) -> None:
        state_path = self.trial / "trial.json"
        state = json.loads(state_path.read_text())
        state["original_brief_ref"] = "../fixture/original-brief.json"
        atomic_write_json(state_path, state)
        with self.assertRaisesRegex(ContractError, "escapes trial directory"):
            TrialRuntime(self.trial).load_state()

    def test_status_replays_full_completed_product_verification(self) -> None:
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        runtime.run(self.config)
        review = next(
            path
            for path in (self.trial / "reviews").glob("*.json")
            if not path.name.endswith("--execution.json")
        )
        value = json.loads(review.read_text())
        value["findings"][0]["source_refs"].append("seat:Expert-3:residual:foreign")
        atomic_write_json(review, value)
        state = json.loads((self.trial / "trial.json").read_text())
        from magi.io import digest_file

        reference = review.relative_to(self.trial).as_posix()
        state["review_sha256"][reference] = digest_file(review)
        receipt_ref = str(Path(reference).with_name(Path(reference).stem + "--execution.json"))
        receipt_path = self.trial / receipt_ref
        receipt = json.loads(receipt_path.read_text())
        receipt["output_artifact_sha256"] = digest_file(review)
        atomic_write_json(receipt_path, receipt)
        state["review_execution_sha256"][receipt_ref] = digest_file(receipt_path)
        atomic_write_json(self.trial / "trial.json", state)
        with self.assertRaisesRegex(ContractError, "invalid source refs"):
            runtime.status()

    def test_review_packets_do_not_disclose_family(self) -> None:
        packets: list[dict] = []

        def capturing(spec: CommandSpec, payload: dict) -> dict:
            packets.append(payload)
            return self.agent(spec, payload)

        runtime = TrialRuntime(self.trial, FunctionRunner(capturing))
        runtime.run(self.config)
        reviews = [packet for packet in packets if packet["task"] == "magi_cross_review"]
        encoded = json.dumps(reviews)
        for secret in ("mimo", "deepseek", "openai", "seat-m", "seat-d", "seat-g"):
            self.assertNotIn(secret, encoded)

    def test_cross_review_packet_binds_full_profile_methodology(self) -> None:
        packets: list[dict] = []

        def capturing(spec: CommandSpec, payload: dict) -> dict:
            if payload["task"] == "magi_cross_review":
                packets.append(payload)
            return self.agent(spec, payload)

        TrialRuntime(self.trial, FunctionRunner(capturing)).run(self.config)
        self.assertEqual(len(packets), 6)
        for packet in packets:
            binding = packet["reviewer_profile_binding"]
            methodology = packet["reviewer_methodology"]
            self.assertEqual(packet["contract_version"], "1.1")
            self.assertTrue(binding["profile_source_sha256"].startswith("sha256:"))
            self.assertTrue(methodology["methods"])
            self.assertTrue(methodology["failure_checks"])
            self.assertTrue(methodology["epistemic_lens"])
            self.assertTrue(methodology["instructions"])

    def test_cross_review_rejects_unprofiled_native_agent(self) -> None:
        config = json.loads(self.config.read_text())
        config["seat_agents"]["seat-m"].pop("reviewer_profile_mode")
        config["seat_agents"]["seat-m"].pop("profile_source")
        atomic_write_json(self.config, config)
        with self.assertRaisesRegex(ContractError, "reviewer_profile_mode=hermes_profile"):
            TrialRuntime(self.trial, FunctionRunner(self.agent)).run(self.config)

    def test_cross_review_rejects_profile_source_not_frozen_in_dossier(self) -> None:
        config = json.loads(self.config.read_text())
        config["seat_agents"]["seat-m"]["profile_source"] = str(
            self.fixture / "seat-m" / "reviewer-profile"
        )
        atomic_write_json(self.config, config)
        with self.assertRaisesRegex(ContractError, "profile_source must be the frozen dossier"):
            TrialRuntime(self.trial, FunctionRunner(self.agent)).run(self.config)

    def test_cross_review_rejects_profile_binding_drift(self) -> None:
        def drifted(spec: CommandSpec, payload: dict) -> dict:
            value = self.agent(spec, payload)
            if payload["task"] == "magi_cross_review":
                value["reviewer_profile_binding"]["profile_source_sha256"] = (
                    "sha256:" + "0" * 64
                )
            return value

        with self.assertRaisesRegex(ContractError, "profile binding does not match"):
            TrialRuntime(self.trial, FunctionRunner(drifted)).run(self.config)

    def test_cross_review_rejects_undeclared_methodology(self) -> None:
        def drifted(spec: CommandSpec, payload: dict) -> dict:
            value = self.agent(spec, payload)
            if payload["task"] == "magi_cross_review":
                value["methodology_trace"][0]["method"] = "generic reviewer intuition"
            return value

        with self.assertRaisesRegex(ContractError, "not declared by the assigned reviewer"):
            TrialRuntime(self.trial, FunctionRunner(drifted)).run(self.config)

    def test_registered_dossier_rejects_tampered_reviewer_profile_tree(self) -> None:
        trial = self.root / "profile-tamper-trial"
        runtime = TrialRuntime.initialize(
            trial,
            trial_id="profile-tamper-trial",
            seat_slots=["seat-m", "seat-d", "seat-g"],
            action_boundary="none",
            original_brief=self.fixture / "original-brief.json",
        )
        profile_rule = self.fixture / "seat-m" / "reviewer-profile" / "SOUL.md"
        profile_rule.write_text(profile_rule.read_text() + "tampered\n", encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "reviewer profile tree digest"):
            runtime.register_dossier("seat-m", self.paths[0])

    def test_cross_review_rejects_evidence_without_subject_source(self) -> None:
        def invalid_review(spec: CommandSpec, payload: dict) -> dict:
            value = self.agent(spec, payload)
            if payload["task"] == "magi_cross_review":
                subject = payload["subject_alias"]
                seat = payload["subject_dossier"]["quinte_result"]["residuals"][0]
                seat["evidence_refs"] = [f"seat:{subject}:evidence:snapshot://proof"]
                value["findings"][0]["evidence_refs"] = seat["evidence_refs"]
            return value

        runtime = TrialRuntime(self.trial, FunctionRunner(invalid_review))
        original_loader = runtime._load_seats

        def seats_with_evidence(state: dict) -> list:
            seats = original_loader(state)
            for seat in seats:
                seat.result["residuals"][0]["evidence_refs"] = ["snapshot://proof"]
            return seats

        runtime._load_seats = seats_with_evidence  # type: ignore[method-assign]
        with self.assertRaisesRegex(ContractError, "evidence without a subject source"):
            runtime.run(self.config)

    def test_cross_review_rejects_invented_closure_evidence(self) -> None:
        def invalid_review(spec: CommandSpec, payload: dict) -> dict:
            value = self.agent(spec, payload)
            if payload["task"] == "magi_cross_review":
                value["findings"][0]["closure_state"] = "blocked"
                value["findings"][0]["closure_evidence"] = [
                    f"seat:{payload['subject_alias']}:evidence:snapshot://invented"
                ]
            return value

        with self.assertRaisesRegex(ContractError, "invalid closure evidence"):
            TrialRuntime(self.trial, FunctionRunner(invalid_review)).run(self.config)

    def test_resume_rejects_changed_agent_config(self) -> None:
        fail_once = True

        def interrupted(spec: CommandSpec, payload: dict) -> dict:
            nonlocal fail_once
            if payload["task"] == "magi_cross_review" and fail_once:
                fail_once = False
                raise RuntimeError("simulated interruption")
            return self.agent(spec, payload)

        runtime = TrialRuntime(self.trial, FunctionRunner(interrupted))
        with self.assertRaises(RuntimeError):
            runtime.run(self.config)
        config = json.loads(self.config.read_text())
        config["final_adjudicator"]["timeout_seconds"] = 31
        atomic_write_json(self.config, config)
        with self.assertRaisesRegex(StateError, "agent config changed"):
            runtime.run(self.config)

    def test_resume_reuses_cross_reviews_completed_before_fault(self) -> None:
        attempts: list[tuple[str, str]] = []
        failed = False

        def interrupted(spec: CommandSpec, payload: dict) -> dict:
            nonlocal failed
            if payload["task"] == "magi_cross_review":
                pair = (payload["reviewer_alias"], payload["subject_alias"])
                attempts.append(pair)
                if len(attempts) == 3 and not failed:
                    failed = True
                    raise RuntimeError("simulated review fault")
            return self.agent(spec, payload)

        runtime = TrialRuntime(self.trial, FunctionRunner(interrupted))
        with self.assertRaisesRegex(RuntimeError, "simulated review fault"):
            runtime.run(self.config)
        saved = runtime.load_state()["review_refs"]
        self.assertEqual(len(saved), 2)

        product = runtime.run(self.config)
        self.assertEqual(product["status"], "completed")
        self.assertEqual(len(attempts), 7)
        self.assertEqual(attempts.count(attempts[0]), 1)
        self.assertEqual(attempts.count(attempts[1]), 1)

    def test_rejects_agent_config_for_wrong_seat_ids_before_freeze(self) -> None:
        config = json.loads(self.config.read_text())
        config["seat_agents"]["seat-x"] = config["seat_agents"].pop("seat-g")
        atomic_write_json(self.config, config)
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        with self.assertRaisesRegex(ContractError, "three trial seat IDs"):
            runtime.run(self.config)
        self.assertIsNone(runtime.load_state()["agent_config_sha256"])

    def test_resume_rejects_tampered_review(self) -> None:
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        runtime.run(self.config)
        state = runtime.load_state()
        review = self.trial / state["review_refs"][0]
        review.write_text(review.read_text() + " ", encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "cross-review digest mismatch"):
            runtime.load_state()

    def test_verify_product_reconstructs_trace(self) -> None:
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        runtime.run(self.config)
        trace = self.trial / "final" / "residual-trace.json"
        value = json.loads(trace.read_text())
        value["question"] = "tampered"
        atomic_write_json(trace, value)
        state = json.loads((self.trial / "trial.json").read_text())
        from magi.io import digest_file

        state["residual_trace_sha256"] = digest_file(trace)
        atomic_write_json(self.trial / "trial.json", state)
        with self.assertRaisesRegex(ContractError, "deterministic reconstruction"):
            runtime.verify_product()

    def test_emitted_trace_passes_highball_shape_validator(self) -> None:
        runtime = TrialRuntime(self.trial, FunctionRunner(self.agent))
        runtime.run(self.config)
        validator = Path("/Users/ericstone/Public/HIGHBALL/bin/validate-residual-trace.py")
        if not validator.exists():
            self.skipTest("HIGHBALL checkout is not available")
        completed = subprocess.run(
            [str(validator), str(self.trial / "final" / "residual-trace.json")],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertNotIn("ERROR", completed.stderr)
        self.assertIn("high-risk and open", completed.stderr)


class BuilderRuntimeTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.fixture = self.root / "fixture"
        self.paths = make_fixture(self.fixture)
        self.trial = self.root / "trial"
        TrialRuntime.initialize(
            self.trial,
            trial_id="builder-trial",
            seat_slots=["seat-m", "seat-d", "seat-g"],
            action_boundary="reversible",
            original_brief=self.fixture / "original-brief.json",
        )
        stage_empty_evidence(
            self.trial, original_brief=self.trial / "input" / "original-brief.json"
        )
        self.plan = assignment_plan(self.fixture, trial_id="builder-trial")
        TrialRuntime(self.trial)._bind_evidence_manifest(
            TrialRuntime(self.trial).load_state()
        )
        spec = {"argv": ["unused"], "timeout_seconds": 30, "pass_env": []}
        self.config = self.root / "builders.json"
        atomic_write_json(
            self.config,
            {
                "builder_version": "1.0",
                "seat_builders": {seat: spec for seat in ("seat-m", "seat-d", "seat-g")},
            },
        )

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def builder(self, _: CommandSpec, payload: dict) -> dict:
        seat = payload["seat_id"]
        source = self.fixture / seat
        destination = Path(payload["seat_output_dir"])
        import shutil

        shutil.copytree(source, destination)
        return {"seat_id": seat, "dossier_path": str(destination / "dossier.json")}

    def test_builds_and_freezes_all_three_dossiers(self) -> None:
        runtime = TrialRuntime(self.trial, FunctionRunner(self.builder))
        state = runtime.build_dossiers(self.config, self.plan)
        self.assertEqual(state["status"], "dossiers_frozen")
        self.assertEqual(set(state["dossiers"]), {"seat-m", "seat-d", "seat-g"})

    def test_builders_run_concurrently(self) -> None:
        active = 0
        peak = 0
        lock = threading.Lock()

        def delayed(spec: CommandSpec, payload: dict) -> dict:
            nonlocal active, peak
            with lock:
                active += 1
                peak = max(peak, active)
            try:
                time.sleep(0.05)
                return self.builder(spec, payload)
            finally:
                with lock:
                    active -= 1

        state = TrialRuntime(self.trial, FunctionRunner(delayed)).build_dossiers(self.config, self.plan)
        self.assertEqual(state["status"], "dossiers_frozen")
        self.assertEqual(peak, 3)

    def test_builder_resume_skips_registered_seat(self) -> None:
        calls: list[str] = []
        failed = False
        lock = threading.Lock()

        def interrupted(spec: CommandSpec, payload: dict) -> dict:
            nonlocal failed
            with lock:
                calls.append(payload["seat_id"])
                should_fail = payload["seat_id"] == "seat-d" and not failed
                if should_fail:
                    failed = True
            if should_fail:
                raise RuntimeError("interrupt")
            return self.builder(spec, payload)

        runtime = TrialRuntime(self.trial, FunctionRunner(interrupted))
        with self.assertRaises(RuntimeError):
            runtime.build_dossiers(self.config, self.plan)
        runtime.build_dossiers(self.config, self.plan)
        self.assertEqual(calls.count("seat-m"), 1)
        self.assertEqual(calls.count("seat-d"), 2)
        self.assertEqual(calls.count("seat-g"), 1)

    def test_builder_resume_adopts_valid_unregistered_seat_work(self) -> None:
        import shutil

        shutil.copytree(self.fixture / "seat-m", self.trial / "seat-work" / "seat-m")
        calls: list[str] = []

        def counting(spec: CommandSpec, payload: dict) -> dict:
            calls.append(payload["seat_id"])
            return self.builder(spec, payload)

        state = TrialRuntime(self.trial, FunctionRunner(counting)).build_dossiers(self.config, self.plan)
        self.assertEqual(state["status"], "dossiers_frozen")
        self.assertNotIn("seat-m", calls)
        self.assertEqual(sorted(calls), ["seat-d", "seat-g"])

    def test_builder_archives_incomplete_seat_work_before_rebuild(self) -> None:
        incomplete = self.trial / "seat-work" / "seat-m"
        incomplete.mkdir(parents=True)
        marker = incomplete / "partial-output.txt"
        marker.write_text("recoverable partial output", encoding="utf-8")

        state = TrialRuntime(self.trial, FunctionRunner(self.builder)).build_dossiers(self.config, self.plan)
        self.assertEqual(state["status"], "dossiers_frozen")
        archived = list((self.trial / "private" / "failed-seat-work").glob("seat-m-*"))
        self.assertEqual(len(archived), 1)
        self.assertEqual(
            (archived[0] / "partial-output.txt").read_text(encoding="utf-8"),
            "recoverable partial output",
        )

    def test_builder_fault_preserves_other_completed_seats_for_resume(self) -> None:
        failed = False
        calls: list[str] = []
        lock = threading.Lock()

        def fault(spec: CommandSpec, payload: dict) -> dict:
            nonlocal failed
            seat = payload["seat_id"]
            with lock:
                calls.append(seat)
                should_fail = seat == "seat-g" and not failed
                if should_fail:
                    failed = True
            if should_fail:
                raise RuntimeError("fault injection")
            return self.builder(spec, payload)

        runtime = TrialRuntime(self.trial, FunctionRunner(fault))
        with self.assertRaisesRegex(RuntimeError, "fault injection"):
            runtime.build_dossiers(self.config, self.plan)
        state = runtime.load_state()
        self.assertEqual(set(state["dossiers"]), {"seat-m", "seat-d"})
        state = runtime.build_dossiers(self.config, self.plan)
        self.assertEqual(state["status"], "dossiers_frozen")
        self.assertEqual(calls.count("seat-m"), 1)
        self.assertEqual(calls.count("seat-d"), 1)
        self.assertEqual(calls.count("seat-g"), 2)

    def test_builder_rejects_output_escape(self) -> None:
        def escape(_: CommandSpec, payload: dict) -> dict:
            return {"seat_id": payload["seat_id"], "dossier_path": str(self.paths[0])}

        runtime = TrialRuntime(self.trial, FunctionRunner(escape))
        with self.assertRaisesRegex(ContractError, "escapes assigned"):
            runtime.build_dossiers(self.config, self.plan)

    def test_builder_config_must_bind_exact_trial_seat_ids(self) -> None:
        config = json.loads(self.config.read_text())
        config["seat_builders"]["seat-x"] = config["seat_builders"].pop("seat-g")
        atomic_write_json(self.config, config)
        runtime = TrialRuntime(self.trial, FunctionRunner(self.builder))
        with self.assertRaisesRegex(ContractError, "three trial seat IDs"):
            runtime.build_dossiers(self.config, self.plan)
        self.assertIsNone(runtime.load_state()["builder_config_sha256"])

    def test_register_rejects_any_source_symlink(self) -> None:
        source = self.fixture / "seat-m"
        (source / "innocent-link").symlink_to(source / "profile.json")
        runtime = TrialRuntime(self.trial)
        with self.assertRaisesRegex(ContractError, "contains a symlink"):
            runtime.register_dossier("seat-m", source / "dossier.json")

    def test_register_adopts_valid_copy_after_interrupted_state_write(self) -> None:
        runtime = TrialRuntime(self.trial)
        runtime._bind_assignment_plan(runtime.load_state(), self.plan)
        runtime.register_dossier("seat-m", self.paths[0])
        state = json.loads((self.trial / "trial.json").read_text())
        state["dossiers"] = {}
        state["status"] = "awaiting_dossiers"
        atomic_write_json(self.trial / "trial.json", state)
        resumed = runtime.register_dossier("seat-m", self.paths[0])
        self.assertIn("seat-m", resumed["dossiers"])


if __name__ == "__main__":
    unittest.main()
