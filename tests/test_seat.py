from __future__ import annotations

import json
import tempfile
import unittest
from dataclasses import replace
from pathlib import Path

from magi.errors import ContractError
from magi.io import atomic_write_json, digest_file
from magi.seat import load_seat_dossier, validate_trial_seats
from tests.helpers import make_fixture


class SeatLoaderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.paths = make_fixture(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_three_distinct_family_products_load(self) -> None:
        seats = [load_seat_dossier(path) for path in self.paths]
        validate_trial_seats(seats)
        self.assertEqual({seat.family for seat in seats}, {"mimo", "deepseek", "openai"})

    def test_rejects_tampered_result_digest(self) -> None:
        result = self.paths[0].parent / "quinte-run" / "result.json"
        result.write_text(result.read_text() + " ", encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "result digest"):
            load_seat_dossier(self.paths[0])

    def test_rejects_intra_run_family_mix(self) -> None:
        dossier_path = self.paths[0]
        run = dossier_path.parent / "quinte-run"
        result_path = run / "result.json"
        result = json.loads(result_path.read_text())
        result["route_bindings"][0]["family"] = "other"
        atomic_write_json(result_path, result)
        manifest_path = run / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["route_bindings"][0]["family"] = "other"
        manifest["result_sha256"] = digest_file(result_path)
        atomic_write_json(manifest_path, manifest)
        dossier = json.loads(dossier_path.read_text())
        dossier["quinte_manifest_sha256"] = digest_file(manifest_path)
        dossier["quinte_result_sha256"] = digest_file(result_path)
        atomic_write_json(dossier_path, dossier)
        with self.assertRaisesRegex(ContractError, "does not match seat binding"):
            load_seat_dossier(dossier_path)

    def test_rejects_manual_primary_arbiter_policy(self) -> None:
        dossier_path = self.paths[0]
        policy_path = dossier_path.parent / "quinte-run" / "input" / "policy.json"
        policy = json.loads(policy_path.read_text())
        policy["auto_primary_arbiter"] = False
        atomic_write_json(policy_path, policy)
        self._rebind_policy_digest(dossier_path)
        with self.assertRaisesRegex(ContractError, "auto_primary_arbiter=true"):
            load_seat_dossier(dossier_path)

    def test_rejects_policy_route_drift(self) -> None:
        dossier_path = self.paths[0]
        policy_path = dossier_path.parent / "quinte-run" / "input" / "policy.json"
        policy = json.loads(policy_path.read_text())
        policy["roster"][0]["perspective"] = "changed after run"
        atomic_write_json(policy_path, policy)
        self._rebind_policy_digest(dossier_path)
        with self.assertRaisesRegex(ContractError, "policy route bindings do not match"):
            load_seat_dossier(dossier_path)

    def test_rejects_unconsumed_primary_arbiter_challenge(self) -> None:
        dossier_path = self.paths[0]
        run = dossier_path.parent / "quinte-run"
        manifest_path = run / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        manifest["primary_arbiter_challenge"]["consumed"] = False
        atomic_write_json(manifest_path, manifest)
        dossier = json.loads(dossier_path.read_text())
        dossier["quinte_manifest_sha256"] = digest_file(manifest_path)
        atomic_write_json(dossier_path, dossier)
        with self.assertRaisesRegex(ContractError, "challenge must be consumed"):
            load_seat_dossier(dossier_path)

    @staticmethod
    def _rebind_policy_digest(dossier_path: Path) -> None:
        from magi.io import digest_bytes, quinte_json_bytes

        run = dossier_path.parent / "quinte-run"
        manifest_path = run / "manifest.json"
        manifest = json.loads(manifest_path.read_text())
        policy = json.loads((run / "input" / "policy.json").read_text())
        manifest["policy_sha256"] = digest_bytes(quinte_json_bytes(policy))
        atomic_write_json(manifest_path, manifest)
        dossier = json.loads(dossier_path.read_text())
        dossier["quinte_manifest_sha256"] = digest_file(manifest_path)
        atomic_write_json(dossier_path, dossier)

    def test_rejects_reused_run(self) -> None:
        seats = [load_seat_dossier(path) for path in self.paths]
        reused = replace(seats[0], dossier={**seats[0].dossier, "seat_id": "other-seat"})
        with self.assertRaisesRegex(ContractError, "distinct run IDs"):
            validate_trial_seats([seats[0], reused, seats[2]])

    def test_anonymous_view_redacts_route_and_family(self) -> None:
        view = load_seat_dossier(self.paths[0]).anonymous_view("Expert-1")
        encoded = json.dumps(view)
        self.assertNotIn("mimo", encoded)
        self.assertNotIn("seat-m", encoded)
        self.assertNotIn("route_bindings", encoded)
        self.assertNotIn("run_id", encoded)

    def test_anonymous_view_redacts_case_variants_without_substring_damage(self) -> None:
        seat = load_seat_dossier(self.paths[0])
        seat.result["summary"] = "MIMO and mimo are identities; mimosa is unrelated."
        view = seat.anonymous_view("Expert-1")
        self.assertEqual(
            view["quinte_result"]["summary"],
            "Expert-1 and Expert-1 are identities; mimosa is unrelated.",
        )

    def test_rejects_out_of_order_route_bindings(self) -> None:
        dossier_path = self.paths[0]
        run = dossier_path.parent / "quinte-run"
        result_path = run / "result.json"
        manifest_path = run / "manifest.json"
        result = json.loads(result_path.read_text())
        manifest = json.loads(manifest_path.read_text())
        result["route_bindings"][0], result["route_bindings"][1] = (
            result["route_bindings"][1],
            result["route_bindings"][0],
        )
        manifest["route_bindings"] = result["route_bindings"]
        atomic_write_json(result_path, result)
        manifest["result_sha256"] = digest_file(result_path)
        atomic_write_json(manifest_path, manifest)
        dossier = json.loads(dossier_path.read_text())
        dossier["quinte_manifest_sha256"] = digest_file(manifest_path)
        dossier["quinte_result_sha256"] = digest_file(result_path)
        atomic_write_json(dossier_path, dossier)
        with self.assertRaisesRegex(ContractError, "fixed seven-route order"):
            load_seat_dossier(dossier_path)

    def test_rejects_duplicate_route_ids(self) -> None:
        dossier_path = self.paths[0]
        run = dossier_path.parent / "quinte-run"
        result_path = run / "result.json"
        manifest_path = run / "manifest.json"
        result = json.loads(result_path.read_text())
        manifest = json.loads(manifest_path.read_text())
        result["route_bindings"][1]["route_id"] = result["route_bindings"][0]["route_id"]
        manifest["route_bindings"] = result["route_bindings"]
        atomic_write_json(result_path, result)
        manifest["result_sha256"] = digest_file(result_path)
        atomic_write_json(manifest_path, manifest)
        dossier = json.loads(dossier_path.read_text())
        dossier["quinte_manifest_sha256"] = digest_file(manifest_path)
        dossier["quinte_result_sha256"] = digest_file(result_path)
        atomic_write_json(dossier_path, dossier)
        with self.assertRaisesRegex(ContractError, "distinct route IDs"):
            load_seat_dossier(dossier_path)

    def test_rejects_invalid_residual_disposition(self) -> None:
        dossier_path = self.paths[0]
        run = dossier_path.parent / "quinte-run"
        result_path = run / "result.json"
        manifest_path = run / "manifest.json"
        result = json.loads(result_path.read_text())
        result["residuals"][0]["disposition"] = "maybe"
        atomic_write_json(result_path, result)
        manifest = json.loads(manifest_path.read_text())
        manifest["result_sha256"] = digest_file(result_path)
        atomic_write_json(manifest_path, manifest)
        dossier = json.loads(dossier_path.read_text())
        dossier["quinte_manifest_sha256"] = digest_file(manifest_path)
        dossier["quinte_result_sha256"] = digest_file(result_path)
        atomic_write_json(dossier_path, dossier)
        with self.assertRaisesRegex(ContractError, "disposition is invalid"):
            load_seat_dossier(dossier_path)

    def test_rejects_invalid_residual_closure_state(self) -> None:
        dossier_path = self.paths[0]
        run = dossier_path.parent / "quinte-run"
        result_path = run / "result.json"
        manifest_path = run / "manifest.json"
        result = json.loads(result_path.read_text())
        result["residuals"][0]["closure_state"] = "pretend_closed"
        atomic_write_json(result_path, result)
        manifest = json.loads(manifest_path.read_text())
        manifest["result_sha256"] = digest_file(result_path)
        atomic_write_json(manifest_path, manifest)
        dossier = json.loads(dossier_path.read_text())
        dossier["quinte_manifest_sha256"] = digest_file(manifest_path)
        dossier["quinte_result_sha256"] = digest_file(result_path)
        atomic_write_json(dossier_path, dossier)
        with self.assertRaisesRegex(ContractError, "closure_state is invalid"):
            load_seat_dossier(dossier_path)

    def test_rejects_inner_manifest_route_drift(self) -> None:
        dossier_path = self.paths[0]
        run = dossier_path.parent / "quinte-run"
        result_path = run / "result.json"
        manifest_path = run / "manifest.json"
        result = json.loads(result_path.read_text())
        result["trial_manifest"]["perspectives"][0]["route_id"] = "foreign-route"
        atomic_write_json(result_path, result)
        manifest = json.loads(manifest_path.read_text())
        manifest["result_sha256"] = digest_file(result_path)
        atomic_write_json(manifest_path, manifest)
        dossier = json.loads(dossier_path.read_text())
        dossier["quinte_manifest_sha256"] = digest_file(manifest_path)
        dossier["quinte_result_sha256"] = digest_file(result_path)
        atomic_write_json(dossier_path, dossier)
        with self.assertRaisesRegex(ContractError, "perspective route does not match"):
            load_seat_dossier(dossier_path)


if __name__ == "__main__":
    unittest.main()
