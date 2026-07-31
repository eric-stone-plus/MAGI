from __future__ import annotations

import os
import sys
import unittest

from magi.errors import AgentError, ContractError
from magi.runner import CommandRunner, CommandSpec


class RunnerTests(unittest.TestCase):
    def test_json_round_trip_without_shell(self) -> None:
        spec = CommandSpec(
            (
                sys.executable,
                "-c",
                "import json,sys; print(json.dumps({'seen': json.load(sys.stdin)['value']}))",
            ),
            10,
            (),
        )
        self.assertEqual(CommandRunner().run(spec, {"value": "ok"}), {"seen": "ok"})

    def test_rejects_non_json_output(self) -> None:
        spec = CommandSpec((sys.executable, "-c", "print('noise')"), 10, ())
        with self.assertRaises(AgentError):
            CommandRunner().run(spec, {})

    def test_command_spec_is_closed(self) -> None:
        with self.assertRaises(ContractError):
            CommandSpec.from_value(
                {"argv": ["agent"], "timeout_seconds": 1, "pass_env": [], "shell": True},
                "agent",
            )

    def test_execution_identity_is_closed_and_secret_free(self) -> None:
        spec = CommandSpec.from_value(
            {
                "argv": ["agent"],
                "timeout_seconds": 10,
                "pass_env": ["OPENAI_API_KEY"],
                "execution": {
                    "family": "openai",
                    "provider": "openai-api",
                    "text_model": "gpt-5.6-sol",
                    "multimodal_model": "gpt-5.6-sol",
                    "mode": "container",
                    "service": "final-adjudicator",
                    "image_digest": "sha256:" + "a" * 64,
                },
            },
            "agent",
        )
        self.assertTrue(spec.identity_sha256().startswith("sha256:"))
        self.assertNotIn("secret", str(spec.identity()).lower())

    def test_execution_rejects_unbound_image(self) -> None:
        with self.assertRaisesRegex(ContractError, "image_digest"):
            CommandSpec.from_value(
                {
                    "argv": ["agent"],
                    "timeout_seconds": 10,
                    "pass_env": [],
                    "execution": {
                        "family": "openai",
                        "provider": "openai-api",
                        "text_model": "gpt-5.6-sol",
                        "multimodal_model": "gpt-5.6-sol",
                        "mode": "container",
                        "service": "agent",
                        "image_digest": "latest",
                    },
                },
                "agent",
            )

    def test_container_execution_injects_required_image_digest_pin(self) -> None:
        pin = "sha256:" + "c" * 64
        spec = CommandSpec.from_value(
            {
                "argv": ["scripts/host/magi-seat.sh", "final-agent"],
                "timeout_seconds": 30,
                "pass_env": ["MAGI_FINAL_CONFIG", "MAGI_FINAL_SECRET_FILE", "MAGI_REQUIRED_IMAGE_DIGEST"],
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
        # Even when the parent process lacks MAGI_REQUIRED_IMAGE_DIGEST, the runner
        # must inject the frozen pin so final-agent cannot skip image reconcile.
        old = os.environ.pop("MAGI_REQUIRED_IMAGE_DIGEST", None)
        try:
            env = CommandRunner().environment_for(spec)
            self.assertEqual(env["MAGI_REQUIRED_IMAGE_DIGEST"], pin)
        finally:
            if old is not None:
                os.environ["MAGI_REQUIRED_IMAGE_DIGEST"] = old

    def test_container_execution_without_digest_fails_closed(self) -> None:
        # Bypass from_value digest checks by constructing CommandSpec directly.
        spec = CommandSpec(
            argv=("final-agent",),
            timeout_seconds=10,
            pass_env=(),
            execution={
                "family": "openai",
                "provider": "openai-api",
                "text_model": "x",
                "multimodal_model": "x",
                "mode": "container",
                "service": "final-adjudicator",
                "image_digest": "not-a-digest",
            },
        )
        with self.assertRaisesRegex(ContractError, "MAGI_REQUIRED_IMAGE_DIGEST"):
            CommandRunner().environment_for(spec)


if __name__ == "__main__":
    unittest.main()
