from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from magi.errors import AgentError, ContractError
from magi.model_agent import (
    _json_object,
    _json_object_from_events,
    _validate_output,
    invoke,
    parser,
)


class ModelAgentTests(unittest.TestCase):
    def test_production_backend_allowlist_is_native_only(self) -> None:
        backend = next(action for action in parser()._actions if action.dest == "backend")
        self.assertEqual(tuple(backend.choices), ("mimo", "reasonix", "codex"))

    def test_strict_json_parser_allows_one_plain_object(self) -> None:
        self.assertEqual(_json_object('{"ok":true}', "test"), {"ok": True})

    def test_strict_json_parser_rejects_prose(self) -> None:
        with self.assertRaises(AgentError):
            _json_object('result: {"ok":true}', "test")

    def test_reasonix_envelope_is_unwrapped(self) -> None:
        with patch("magi.model_agent._run") as run:
            run.return_value.stdout = json.dumps(
                {"is_error": False, "result": '{"value":"ok"}'}
            )
            result = invoke(
                backend="reasonix",
                executable="reasonix",
                model="deepseek-v4-pro",
                prompt="prompt",
                schema_path=Path("schema.json"),
                timeout=10,
                cwd=None,
                provider=None,
                base_url=None,
                env_key=None,
            )
        self.assertEqual(result, {"value": "ok"})

    def test_mimo_json_events_are_strictly_parsed(self) -> None:
        with patch.dict(
            "os.environ",
            {
                "MAGI_TEST_MIMO_KEY": "secret",
                "MAGI_UNRELATED_SECRET": "must-not-propagate",
            },
        ), patch(
            "magi.model_agent._run"
        ) as run:
            run.return_value.stdout = "\n".join(
                [
                    json.dumps({"type": "start"}),
                    json.dumps({"type": "text", "part": {"text": '{"value":"ok"}'}}),
                    json.dumps({"type": "step_finish", "part": {"reason": "stop"}}),
                ]
            )
            result = invoke(
                backend="mimo",
                executable=None,
                model="mimo-v2.5-pro",
                prompt="prompt",
                schema_path=Path("schema.json"),
                timeout=10,
                cwd=None,
                provider="xiaomi",
                base_url="https://example.invalid/v1",
                env_key="MAGI_TEST_MIMO_KEY",
            )
        self.assertEqual(result, {"value": "ok"})
        command = run.call_args.args[0]
        self.assertEqual(command[:2], ["mimo", "run"])
        self.assertIn("--pure", command)
        self.assertIn("--format", command)
        self.assertIn("magi", command)
        environment = run.call_args.kwargs["environment"]
        self.assertNotIn("MAGI_UNRELATED_SECRET", environment)
        self.assertNotIn("secret", environment["MIMOCODE_CONFIG_CONTENT"])
        self.assertIn("secret", environment["MIMOCODE_AUTH_CONTENT"])

    def test_mimo_stream_rejects_non_jsonl(self) -> None:
        with self.assertRaisesRegex(AgentError, "invalid JSONL"):
            _json_object_from_events("prose", "MiMo result")

    def test_codex_requires_explicit_scoped_credential_name(self) -> None:
        with self.assertRaisesRegex(AgentError, "credential environment"):
            invoke(
                backend="codex",
                executable="codex",
                model="gpt-5.6-sol",
                prompt="prompt",
                schema_path=Path("schema.json"),
                timeout=10,
                cwd=None,
                provider="relay",
                base_url="https://example.invalid/v1",
                env_key="MAGI_TEST_MISSING_KEY",
            )

    def test_reasonix_rejects_provider_override(self) -> None:
        with self.assertRaisesRegex(ContractError, "does not accept provider"):
            invoke(
                backend="reasonix",
                executable="reasonix",
                model="deepseek-v4-pro",
                prompt="prompt",
                schema_path=Path("schema.json"),
                timeout=10,
                cwd=None,
                provider="relay",
                base_url=None,
                env_key=None,
            )

    def test_mimo_requires_scoped_credential_name(self) -> None:
        with self.assertRaisesRegex(AgentError, "credential environment"):
            invoke(
                backend="mimo",
                executable="mimo",
                model="mimo-v2.5-pro",
                prompt="prompt",
                schema_path=Path("schema.json"),
                timeout=10,
                cwd=None,
                provider="xiaomi",
                base_url="https://example.invalid/v1",
                env_key="MAGI_TEST_MISSING_MIMO_KEY",
            )

    def test_cross_review_output_must_preserve_profile_binding_and_methodology(self) -> None:
        binding = {
            "profile_id": "formalist",
            "profile_sha256": "sha256:" + "1" * 64,
            "profile_source_sha256": "sha256:" + "2" * 64,
            "thesis_sha256": "sha256:" + "3" * 64,
        }
        payload = {
            "task": "magi_cross_review",
            "reviewer_alias": "Expert-1",
            "subject_alias": "Expert-2",
            "reviewer_profile_binding": binding,
            "reviewer_methodology": {
                "methods": ["trace invariants"],
                "failure_checks": ["seek counterexample"],
            },
        }
        output = {
            "review_version": "1.1",
            "reviewer_alias": "Expert-1",
            "subject_alias": "Expert-2",
            "reviewer_profile_binding": binding,
            "methodology_trace": [
                {
                    "kind": "method",
                    "method": "trace invariants",
                    "application": "Traced the subject's claimed invariant.",
                },
                {
                    "kind": "failure_check",
                    "method": "seek counterexample",
                    "application": "Constructed a boundary counterexample.",
                },
            ],
            "summary": "Profiled review complete.",
            "findings": [],
            "dissent": [],
        }
        _validate_output(payload, output)
        output["reviewer_profile_binding"] = {**binding, "profile_sha256": "sha256:" + "0" * 64}
        with self.assertRaisesRegex(ContractError, "profile binding does not match"):
            _validate_output(payload, output)


if __name__ == "__main__":
    unittest.main()
