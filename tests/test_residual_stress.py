from __future__ import annotations

import copy
import unittest
from pathlib import Path

from magi.evaluation import evaluate_arm, evaluate_experiment, load_fixture, validate_fixture
from magi.errors import ContractError


FIXTURE = Path(__file__).parent / "fixtures" / "king-loong-residual-stress.json"


class ResidualStressTest(unittest.TestCase):
    def setUp(self) -> None:
        self.fixture = load_fixture(FIXTURE)

    def test_fixture_is_closed_and_zero_token(self) -> None:
        validated = validate_fixture(copy.deepcopy(self.fixture))
        self.assertEqual(validated["case_id"], "king-loong-synthetic-ablation-v1")
        stress_calls = [
            arm["nominal_model_calls"]
            for arm in validated["arms"]
            if arm["arm_type"] == "stress"
        ]
        self.assertTrue(stress_calls)
        self.assertEqual(set(stress_calls), {0})

    def test_same_family_profiles_are_echoes_not_independent_families(self) -> None:
        metrics = evaluate_arm(self.fixture, "same-family-profile-echo")
        self.assertEqual(metrics["supported_claim_ids"], ["C-QUANTITIES"])
        self.assertEqual(metrics["independent_supported_claim_ids"], ["C-QUANTITIES"])
        self.assertEqual(metrics["same_family_echoes"][0]["observation_count"], 3)
        self.assertEqual(metrics["same_family_echoes"][0]["independent_family_count"], 1)

    def test_cross_review_novel_findings_are_supported_and_linked(self) -> None:
        metrics = evaluate_arm(self.fixture, "cross-review-novel")
        self.assertEqual(metrics["precision"], 1.0)
        self.assertEqual(set(metrics["supported_claim_ids"]), {"C-RAW-GAP", "C-NO-WITNESS"})
        self.assertEqual(
            metrics["linked_challenge_refs"], ["finding://deepseek-cross-review/d1"]
        )
        self.assertFalse(metrics["fail_closed"])

    def test_false_difference_is_detected_by_equivalence_key(self) -> None:
        metrics = evaluate_arm(self.fixture, "same-family-profile-echo")
        self.assertEqual(len(metrics["false_differences"]), 1)
        self.assertEqual(metrics["false_difference_ratio"], 1.0)
        self.assertEqual(metrics["substantive_differences"], [])

    def test_baseline_reports_high_risk_omission_and_severity_drift(self) -> None:
        metrics = evaluate_arm(self.fixture, "baseline-incomplete")
        self.assertEqual(set(metrics["omitted_high_risk_claim_ids"]), {"C-RAW-GAP", "C-NO-WITNESS"})
        self.assertEqual(metrics["severity_drifts"][0]["claim_id"], "C-RESERVATION")
        self.assertEqual(metrics["severity_drifts"][0]["expected"], "HIGH")
        self.assertEqual(metrics["severity_drifts"][0]["observed"], "LOW")

    def test_explicit_severity_fault_is_not_hidden_by_citation_support(self) -> None:
        metrics = evaluate_arm(self.fixture, "severity-drift")
        self.assertEqual(metrics["precision"], 1.0)
        self.assertEqual(len(metrics["severity_drifts"]), 1)
        self.assertEqual(metrics["severity_drifts"][0]["expected"], "P0")

    def test_unsupported_citation_fails_closed(self) -> None:
        metrics = evaluate_arm(self.fixture, "unsupported-citation")
        self.assertTrue(metrics["fail_closed"])
        self.assertEqual(metrics["precision"], 0.0)
        self.assertEqual(
            metrics["unsupported_findings"][0]["unknown_evidence_refs"],
            ["snapshot://invented/calculation.xlsx"],
        )

    def test_author_consistency_does_not_count_as_independent_support(self) -> None:
        metrics = evaluate_arm(self.fixture, "author-consistency-only")
        self.assertEqual(metrics["supported_claim_ids"], ["C-RAW-GAP"])
        self.assertEqual(metrics["author_consistency_claim_ids"], ["C-RAW-GAP"])
        self.assertEqual(metrics["independent_supported_claim_ids"], [])
        experiment = evaluate_experiment(self.fixture)
        self.assertFalse(experiment["author_consistency_is_independent"])

    def test_experiment_continues_after_weak_baseline_then_stops_at_acceptance(self) -> None:
        experiment = evaluate_experiment(self.fixture)
        self.assertEqual(experiment["steps"][0]["decision"], "CONTINUE")
        self.assertIn("material recall below threshold", experiment["steps"][0]["reasons"])
        self.assertEqual(experiment["steps"][1]["decision"], "STOP_ACCEPTANCE_MET")
        self.assertEqual(
            set(experiment["steps"][1]["novel_material_independent_claim_ids"]),
            {"C-RAW-GAP", "C-NO-WITNESS"},
        )
        self.assertEqual(experiment["nominal_model_calls_before_stop"], 46)
        self.assertEqual(
            set(experiment["independent_supported_claim_ids"]),
            {claim["claim_id"] for claim in self.fixture["oracle_claims"]},
        )

    def test_profiles_stop_when_they_add_no_material_novelty(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        fixture["experiment_order"] = ["baseline-incomplete", "same-family-profile-echo"]
        experiment = evaluate_experiment(fixture)
        self.assertEqual(experiment["steps"][1]["decision"], "STOP_NO_PROFILE_INCREMENT")
        self.assertEqual(experiment["steps"][1]["novel_material_independent_claim_ids"], [])

    def test_sufficient_baseline_stops_before_any_later_arm(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        baseline = next(arm for arm in fixture["arms"] if arm["arm_id"] == "baseline-incomplete")
        baseline["outputs"][0]["findings"][1]["severity"] = "HIGH"
        baseline["outputs"][0]["findings"].extend(
            [
                {
                    "finding_id": "b6",
                    "claim_id": "C-RAW-GAP",
                    "severity": "P0",
                    "relation": "assertion",
                    "target_ref": None,
                    "evidence_refs": [
                        "snapshot://documents/letter-of-protest.pdf",
                        "snapshot://receipts/media-coverage.json",
                    ],
                    "text": "Primary records and version history remain missing.",
                },
                {
                    "finding_id": "b7",
                    "claim_id": "C-NO-WITNESS",
                    "severity": "HIGH",
                    "relation": "assertion",
                    "target_ref": None,
                    "evidence_refs": ["snapshot://documents/chat-records.pdf"],
                    "text": "No company representative witnessed the disputed survey.",
                },
            ]
        )
        experiment = evaluate_experiment(fixture)
        self.assertEqual(len(experiment["steps"]), 1)
        self.assertEqual(experiment["final_decision"], "STOP_BASELINE_SUFFICIENT")
        self.assertEqual(experiment["nominal_model_calls_before_stop"], 12)

    def test_cross_review_stops_when_it_only_repeats_baseline(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        cross = next(arm for arm in fixture["arms"] if arm["arm_id"] == "cross-review-novel")
        cross["outputs"][0]["findings"] = [
            {
                "finding_id": "repeat",
                "claim_id": "C-NOT-LOSS",
                "severity": "HIGH",
                "relation": "challenge",
                "target_ref": "finding://baseline-incomplete/b3",
                "evidence_refs": [
                    "snapshot://documents/ccic-final-report.pdf",
                    "snapshot://documents/vessel-calculation.pdf",
                ],
                "text": "The cross-review repeats the baseline measurement-dispute finding.",
            }
        ]
        fixture["experiment_order"] = ["baseline-incomplete", "cross-review-novel"]
        experiment = evaluate_experiment(fixture)
        self.assertEqual(experiment["steps"][1]["decision"], "STOP_NO_CROSS_REVIEW_INCREMENT")

    def test_unknown_linked_challenge_target_is_contract_error(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        cross = next(arm for arm in fixture["arms"] if arm["arm_id"] == "cross-review-novel")
        cross["outputs"][0]["findings"][0]["target_ref"] = "finding://missing/target"
        with self.assertRaisesRegex(ContractError, "unknown finding"):
            validate_fixture(fixture)

    def test_linked_challenge_cannot_point_forward(self) -> None:
        fixture = copy.deepcopy(self.fixture)
        baseline = next(arm for arm in fixture["arms"] if arm["arm_id"] == "baseline-incomplete")
        baseline["outputs"][0]["findings"][0]["relation"] = "challenge"
        baseline["outputs"][0]["findings"][0]["target_ref"] = "finding://deepseek-cross-review/d2"
        with self.assertRaisesRegex(ContractError, "earlier arm"):
            validate_fixture(fixture)


if __name__ == "__main__":
    unittest.main()
