"""OCI image digest observation and fail-closed reconcile tests."""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from magi.errors import ContractError
from magi.oci import (
    digest_from_inspect_payload,
    normalize_image_digest,
    read_source_lock,
    reconcile_declared_and_observed,
)


class OciTests(unittest.TestCase):
    def test_normalize_and_repo_digest(self) -> None:
        self.assertEqual(normalize_image_digest("A" * 64), "sha256:" + "a" * 64)
        self.assertEqual(
            normalize_image_digest("sha256:" + "b" * 64), "sha256:" + "b" * 64
        )
        payload = {
            "RepoDigests": ["magi-seat@sha256:" + "c" * 64],
            "Id": "sha256:" + "d" * 64,
        }
        self.assertEqual(digest_from_inspect_payload(payload), "sha256:" + "c" * 64)

    def test_mismatch_fails_closed(self) -> None:
        with self.assertRaisesRegex(ContractError, "does not match declared"):
            reconcile_declared_and_observed(
                declared_digest="sha256:" + "1" * 64,
                observed_digest="sha256:" + "2" * 64,
            )

    def test_missing_observation_fails_unless_allowed(self) -> None:
        with self.assertRaisesRegex(ContractError, "observation is required"):
            reconcile_declared_and_observed(
                declared_digest="sha256:" + "1" * 64,
                observed_digest=None,
            )
        value = reconcile_declared_and_observed(
            declared_digest="sha256:" + "1" * 64,
            observed_digest=None,
            allow_missing_observation=True,
        )
        self.assertEqual(value, "sha256:" + "1" * 64)

    def test_source_lock_requires_full_commits(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source-lock.env"
            path.write_text("HERMES_COMMIT=abc\nQUINTE_COMMIT=def\n", encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "full commit"):
                read_source_lock(path)
            path.write_text(
                "HERMES_COMMIT=" + "a" * 40 + "\nQUINTE_COMMIT=" + "b" * 40 + "\n",
                encoding="utf-8",
            )
            values = read_source_lock(path)
            self.assertEqual(len(values["HERMES_COMMIT"]), 40)


if __name__ == "__main__":
    unittest.main()
