from __future__ import annotations

import copy
import unittest

from magi.assignment import bind_assignment_plan, validate_assignment_plan
from magi.errors import ContractError


def plan_fixture() -> dict:
    checks = ["citation entailment", "contradiction scan", "high-risk closure"]
    seats = []
    for seat, family, profile, focus in (
        ("seat-m", "mimo", "formalist", "multimodal evidence reconstruction"),
        ("seat-d", "deepseek", "adversarial", "failure-chain challenge"),
        ("seat-g", "openai", "empirical", "author-consistency and conclusion audit"),
    ):
        seats.append(
            {
                "seat_id": seat,
                "family": family,
                "provider": family,
                "text_model": f"{family}-model",
                "multimodal_model": f"{family}-vision",
                "profile_id": profile,
                "profile_source_sha256": "sha256:" + {
                    "seat-m": "1", "seat-d": "2", "seat-g": "3"
                }[seat] * 64,
                "container_service": seat,
                "image_digest": "sha256:" + {
                    "mimo": "4", "deepseek": "5", "openai": "6"
                }[family] * 64,
                "primary_focus": [focus],
                "mandatory_global_checks": list(checks),
                "evidence_refs": [],
                "carrier_capabilities": {
                    "carrier_id": family,
                    "snapshot_media_classes": ["document"],
                    "multimodal_media_types": [],
                    "allow_sampled_video": False,
                },
                "cost_rationale": "Use only where this family adds a distinct check.",
                "independence_class": "distinct_family_and_profile",
                "limitations": [],
            }
        )
    review_checks = ["challenge unsupported claims", "preserve material dissent"]
    reviews = [
        {
            "reviewer_seat_id": reviewer,
            "subject_seat_id": subject,
            "review_kind": "artifact_review",
            "required_checks": review_checks,
            "evidence_refs": [],
            "limitations": ["Original evidence is not exposed in artifact-review mode."],
        }
        for reviewer in ("seat-d", "seat-g", "seat-m")
        for subject in ("seat-d", "seat-g", "seat-m")
        if reviewer != subject
    ]
    return {
        "assignment_plan_version": "1.0",
        "trial_id": "trial-1",
        "objective": "Reduce decision-relevant residual uncertainty.",
        "global_checks": checks,
        "seats": seats,
        "cross_review_obligations": reviews,
        "finale_condition": {
            "allowed_outcomes": ["BLOCK", "ESCALATE", "PASS"],
            "material_residual_states": ["bounded_escalation", "closed", "falsified"],
            "required_receipts": ["evidence coverage", "residual reduction"],
            "stop_rule": "Stop when expected information gain is below the declared threshold.",
        },
        "limitations": ["One trial does not estimate a true error rate."],
    }


class AssignmentPlanTests(unittest.TestCase):
    def test_binds_three_frozen_identities_and_six_reviews(self) -> None:
        plan = bind_assignment_plan(plan_fixture())
        validate_assignment_plan(plan)
        self.assertEqual(len(plan["seats"]), 3)
        self.assertEqual(len(plan["cross_review_obligations"]), 6)

    def test_every_seat_must_keep_complete_global_checks(self) -> None:
        plan = plan_fixture()
        plan["seats"][0]["mandatory_global_checks"].pop()
        with self.assertRaisesRegex(ContractError, "complete global check set"):
            bind_assignment_plan(plan)

    def test_family_profile_and_container_disguises_fail_closed(self) -> None:
        for field in ("family", "profile_source_sha256", "container_service"):
            plan = copy.deepcopy(plan_fixture())
            plan["seats"][1][field] = plan["seats"][0][field]
            with self.assertRaisesRegex(ContractError, "three distinct"):
                bind_assignment_plan(plan)

    def test_artifact_review_cannot_claim_original_evidence(self) -> None:
        plan = plan_fixture()
        plan["cross_review_obligations"][0]["evidence_refs"] = ["snapshot://proof"]
        with self.assertRaisesRegex(ContractError, "must not claim"):
            bind_assignment_plan(plan)

    def test_author_consistency_is_explicit_not_independent(self) -> None:
        plan = plan_fixture()
        review = plan["cross_review_obligations"][0]
        review["review_kind"] = "author_consistency_review"
        review["limitations"] = [
            "The reviewer authored the reference report and is not an independent confirmation."
        ]
        bound = bind_assignment_plan(plan)
        self.assertEqual(
            bound["cross_review_obligations"][0]["review_kind"],
            "author_consistency_review",
        )

    def test_binding_tamper_is_rejected(self) -> None:
        plan = bind_assignment_plan(plan_fixture())
        plan["objective"] = "changed"
        with self.assertRaisesRegex(ContractError, "binding digest"):
            validate_assignment_plan(plan)


if __name__ == "__main__":
    unittest.main()
