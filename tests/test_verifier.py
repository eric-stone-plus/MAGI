from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from magi.errors import ContractError
from magi.seat import load_seat_dossier
from magi.verifier import (
    build_residual_reduction_receipt,
    build_highball_trace,
    review_source_ref,
    seat_source_ref,
    verify_final,
)
from tests.helpers import finding, make_fixture


class VerifierTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        paths = make_fixture(Path(self.temporary.name))
        seats = [load_seat_dossier(path) for path in paths]
        self.seats = {f"Expert-{index}": seat for index, seat in enumerate(seats, 1)}

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def verdict(self) -> dict:
        findings = [
            finding(
                f"FINAL-{index}",
                seat_source_ref(alias, seat.result["residuals"][0]["id"]),
            )
            for index, (alias, seat) in enumerate(self.seats.items(), 1)
        ]
        return {
            "verdict_version": "1.0",
            "decision": "BLOCK",
            "summary": "Open high risks block release.",
            "recommendation": "Close every high risk.",
            "findings": findings,
            "dissent": [],
        }

    def review(self, reviewer: str, subject: str, identifier: str, dissent=None) -> dict:
        seat = self.seats[reviewer]
        profile = seat.reviewer_profile()
        return {
            "review_version": "1.1",
            "reviewer_alias": reviewer,
            "subject_alias": subject,
            "reviewer_profile_binding": seat.reviewer_profile_binding(),
            "methodology_trace": [
                {
                    "kind": "method",
                    "method": profile["methods"][0],
                    "application": "Applied the declared method to the dossier.",
                },
                {
                    "kind": "failure_check",
                    "method": profile["failure_checks"][0],
                    "application": "Applied the declared failure check.",
                },
            ],
            "summary": "Review found a risk.",
            "findings": [finding(identifier, review_source_ref(reviewer, subject, identifier))],
            "dissent": dissent or [],
        }

    def test_accepts_complete_block_and_builds_trace(self) -> None:
        verdict = verify_final(self.verdict(), self.seats, [])
        trace = build_highball_trace(verdict, self.seats, [], action_boundary="protected_write")
        self.assertEqual(trace["trace_version"], "1.1")
        self.assertEqual(trace["highball_decision"], "block")
        self.assertEqual(trace["trial_manifest"]["base_model_relation"], "heterogeneous_models")

    def test_residual_reduction_receipt_separates_novel_and_linked_review_work(self) -> None:
        novel = self.review("Expert-1", "Expert-2", "novel-risk")
        linked = self.review("Expert-2", "Expert-1", "false-positive")
        seat_ref = seat_source_ref(
            "Expert-1", self.seats["Expert-1"].result["residuals"][0]["id"]
        )
        linked["findings"][0]["source_refs"].append(seat_ref)
        linked["findings"][0]["disposition"] = "falsified"
        verdict = self.verdict()
        verdict["findings"].append(
            finding("FINAL-NOVEL", review_source_ref("Expert-1", "Expert-2", "novel-risk"))
        )
        verdict["findings"][0]["source_refs"].append(
            review_source_ref("Expert-2", "Expert-1", "false-positive")
        )
        verdict["findings"][0]["disposition"] = "falsified"
        receipt = build_residual_reduction_receipt(
            verdict, self.seats, [novel, linked]
        )
        self.assertEqual(receipt["counts"]["cross_review_novel_findings"], 1)
        self.assertEqual(receipt["counts"]["cross_review_linked_findings"], 1)
        self.assertEqual(receipt["challenged_seat_source_refs"], [seat_ref])
        self.assertIn("error rate", " ".join(receipt["limitations"]))

    def test_rejects_omitted_high_risk(self) -> None:
        verdict = self.verdict()
        verdict["findings"].pop()
        with self.assertRaisesRegex(ContractError, "omitted"):
            verify_final(verdict, self.seats, [])

    def test_rejects_invented_source_ref(self) -> None:
        verdict = self.verdict()
        verdict["findings"][0]["source_refs"] = ["seat:fake:residual:fake"]
        with self.assertRaisesRegex(ContractError, "invalid source refs"):
            verify_final(verdict, self.seats, [])

    def test_rejects_pass_with_open_high_risk(self) -> None:
        verdict = self.verdict()
        verdict["decision"] = "PASS"
        with self.assertRaisesRegex(ContractError, "PASS conflicts"):
            verify_final(verdict, self.seats, [])

    def test_rejects_unsupported_closed_finding(self) -> None:
        verdict = self.verdict()
        verdict["findings"][0]["closure_state"] = "closed"
        with self.assertRaisesRegex(ContractError, "without closure evidence"):
            verify_final(verdict, self.seats, [])

    def test_rejects_invalid_evidence_ref(self) -> None:
        verdict = self.verdict()
        verdict["findings"][0]["evidence_refs"] = ["snapshot://invented"]
        with self.assertRaisesRegex(ContractError, "invalid evidence refs"):
            verify_final(verdict, self.seats, [])

    def test_rejects_high_risk_downgrade(self) -> None:
        verdict = self.verdict()
        verdict["findings"][0]["severity"] = "LOW"
        with self.assertRaisesRegex(ContractError, "preserve the highest"):
            verify_final(verdict, self.seats, [])

    def test_rejects_high_risk_severity_inflation(self) -> None:
        verdict = self.verdict()
        verdict["findings"][0]["severity"] = "P0"
        with self.assertRaisesRegex(ContractError, "preserve the highest"):
            verify_final(verdict, self.seats, [])

    def test_rejects_evidence_unrelated_to_cited_source(self) -> None:
        verdict = self.verdict()
        first_alias, first_seat = next(iter(self.seats.items()))
        second_alias, second_seat = list(self.seats.items())[1]
        first_seat.result["residuals"][0]["evidence_refs"] = ["snapshot://first"]
        second_seat.result["residuals"][0]["evidence_refs"] = ["snapshot://second"]
        verdict["findings"][0]["source_refs"] = [
            seat_source_ref(first_alias, first_seat.result["residuals"][0]["id"])
        ]
        verdict["findings"][0]["evidence_refs"] = [
            f"seat:{second_alias}:evidence:snapshot://second"
        ]
        with self.assertRaisesRegex(ContractError, "unrelated to its sources"):
            verify_final(verdict, self.seats, [])

    def test_rejects_omitted_cross_review_dissent(self) -> None:
        reviewer, subject = "Expert-1", "Expert-2"
        identifier = "review-risk"
        review = self.review(
            reviewer,
            subject,
            identifier,
            ["The deployment assumption remains contested."],
        )
        verdict = self.verdict()
        verdict["findings"].append(
            finding(
                "FINAL-REVIEW",
                review_source_ref(reviewer, subject, identifier),
            )
        )
        with self.assertRaisesRegex(ContractError, "preserve exactly"):
            verify_final(verdict, self.seats, [review])

    def test_accepts_cross_review_dissent_only_with_escalation(self) -> None:
        reviewer, subject = "Expert-1", "Expert-2"
        identifier = "review-risk"
        dissent = "The deployment assumption remains contested."
        review = self.review(reviewer, subject, identifier, [dissent])
        verdict = self.verdict()
        verdict["findings"].append(
            finding(
                "FINAL-REVIEW",
                review_source_ref(reviewer, subject, identifier),
            )
        )
        verdict["decision"] = "ESCALATE"
        verdict["dissent"] = [dissent]
        verify_final(verdict, self.seats, [review])

    def test_requires_seat_result_dissent(self) -> None:
        alias, seat = next(iter(self.seats.items()))
        seat.result["dissent"] = ["MIMO identity remains disputed by the seat."]
        verdict = self.verdict()
        with self.assertRaisesRegex(ContractError, "preserve exactly"):
            verify_final(verdict, self.seats, [])
        verdict["decision"] = "ESCALATE"
        verdict["dissent"] = [f"{alias} identity remains disputed by the seat."]
        verify_final(verdict, self.seats, [])

    def test_accepts_blocked_high_risk_with_inherited_block_record(self) -> None:
        verdict = self.verdict()
        alias, seat = next(iter(self.seats.items()))
        source = seat.result["residuals"][0]
        source["closure_state"] = "blocked"
        source["closure_evidence"] = ["snapshot://block-record"]
        verdict["findings"][0]["closure_state"] = "blocked"
        verdict["findings"][0]["closure_evidence"] = [
            f"seat:{alias}:evidence:snapshot://block-record"
        ]
        verify_final(verdict, self.seats, [])

    def test_rejects_invented_final_closure_evidence(self) -> None:
        verdict = self.verdict()
        verdict["findings"][0]["closure_state"] = "blocked"
        verdict["findings"][0]["closure_evidence"] = ["block:invented"]
        with self.assertRaisesRegex(ContractError, "invents closure evidence"):
            verify_final(verdict, self.seats, [])

    def test_rejects_blocked_source_rewritten_as_closed(self) -> None:
        verdict = self.verdict()
        alias, seat = next(iter(self.seats.items()))
        source = seat.result["residuals"][0]
        source["closure_state"] = "blocked"
        source["closure_evidence"] = ["snapshot://block-record"]
        verdict["findings"][0]["closure_state"] = "closed"
        verdict["findings"][0]["disposition"] = "verified"
        verdict["findings"][0]["closure_evidence"] = [
            f"seat:{alias}:evidence:snapshot://block-record"
        ]
        with self.assertRaisesRegex(ContractError, "suppresses a blocked source"):
            verify_final(verdict, self.seats, [])


if __name__ == "__main__":
    unittest.main()
