"""No-shell JSON command runner used for every model boundary."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Callable

from .errors import AgentError, ContractError  # ContractError used by environment_for


@dataclass(frozen=True)
class CommandSpec:
    argv: tuple[str, ...]
    timeout_seconds: int
    pass_env: tuple[str, ...]
    reviewer_profile_mode: str = "native_model_with_bound_methodology"
    profile_source: str | None = None
    execution: dict[str, str] | None = None

    @classmethod
    def from_value(cls, value: Any, label: str) -> "CommandSpec":
        if not isinstance(value, dict):
            raise ContractError(f"{label} must be an object")
        allowed = {
            "argv",
            "timeout_seconds",
            "pass_env",
            "reviewer_profile_mode",
            "profile_source",
            "execution",
        }
        required = {"argv", "timeout_seconds", "pass_env"}
        _closed(value, allowed, required, label)
        argv = value.get("argv")
        timeout = value.get("timeout_seconds")
        pass_env = value.get("pass_env")
        if not isinstance(argv, list) or not argv or not all(_text(item) for item in argv):
            raise ContractError(f"{label}.argv must be a non-empty string array")
        if not isinstance(timeout, int) or isinstance(timeout, bool) or timeout < 1 or timeout > 7200:
            raise ContractError(f"{label}.timeout_seconds must be an integer from 1 to 7200")
        if not isinstance(pass_env, list) or not all(_text(item) for item in pass_env):
            raise ContractError(f"{label}.pass_env must be a string array")
        if len(set(pass_env)) != len(pass_env):
            raise ContractError(f"{label}.pass_env contains duplicates")
        reviewer_profile_mode = value.get(
            "reviewer_profile_mode", "native_model_with_bound_methodology"
        )
        if reviewer_profile_mode not in {
            "native_model_with_bound_methodology",
            "hermes_profile",
        }:
            raise ContractError(f"{label}.reviewer_profile_mode is invalid")
        profile_source = value.get("profile_source")
        if profile_source is not None and not _text(profile_source):
            raise ContractError(f"{label}.profile_source must be a non-empty path")
        if reviewer_profile_mode == "hermes_profile" and profile_source is None:
            raise ContractError(f"{label}.profile_source is required for Hermes profile review")
        if reviewer_profile_mode != "hermes_profile" and profile_source is not None:
            raise ContractError(f"{label}.profile_source is only valid for Hermes profile review")
        execution = value.get("execution")
        if execution is not None:
            if not isinstance(execution, dict):
                raise ContractError(f"{label}.execution must be an object")
            execution_fields = {
                "family",
                "provider",
                "text_model",
                "multimodal_model",
                "mode",
                "service",
                "image_digest",
            }
            _closed(execution, execution_fields, execution_fields, f"{label}.execution")
            if not all(_text(execution.get(field)) for field in execution_fields):
                raise ContractError(f"{label}.execution fields must be non-empty strings")
            image_digest = execution["image_digest"]
            if not image_digest.startswith("sha256:") or len(image_digest) != 71:
                raise ContractError(f"{label}.execution.image_digest must be a sha256 digest")
        return cls(
            tuple(argv),
            timeout,
            tuple(pass_env),
            reviewer_profile_mode,
            profile_source,
            dict(execution) if execution is not None else None,
        )

    def identity(self) -> dict[str, object]:
        """Return the secret-free, stable command identity used by receipts."""
        return {
            "argv": list(self.argv),
            "timeout_seconds": self.timeout_seconds,
            "pass_env": list(self.pass_env),
            "reviewer_profile_mode": self.reviewer_profile_mode,
            "profile_source": self.profile_source,
            "execution": self.execution,
        }

    def identity_sha256(self) -> str:
        encoded = json.dumps(
            self.identity(), ensure_ascii=False, sort_keys=True, separators=(",", ":")
        ).encode("utf-8")
        return "sha256:" + hashlib.sha256(encoded).hexdigest()


class CommandRunner:
    """Invoke an agent with one JSON object on stdin and one on stdout."""

    def environment_for(self, spec: CommandSpec) -> dict[str, str]:
        """Build the minimal subprocess environment for one command.

        Container executions always inject MAGI_REQUIRED_IMAGE_DIGEST from the
        frozen execution.image_digest pin so host launchers cannot skip image
        reconcile by leaving the env unset.
        """

        base_names = ("PATH", "HOME", "USERPROFILE", "SYSTEMROOT", "TMP", "TEMP", "LANG")
        names = set(base_names) | set(spec.pass_env)
        environment = {name: os.environ[name] for name in names if name in os.environ}
        if spec.execution is not None:
            pin = spec.execution.get("image_digest")
            if isinstance(pin, str) and pin.startswith("sha256:") and len(pin) == 71:
                environment["MAGI_REQUIRED_IMAGE_DIGEST"] = pin
            if spec.execution.get("mode") == "container":
                required = environment.get("MAGI_REQUIRED_IMAGE_DIGEST")
                if not isinstance(required, str) or not required.startswith("sha256:"):
                    raise ContractError(
                        "container execution requires MAGI_REQUIRED_IMAGE_DIGEST "
                        "from frozen execution.image_digest"
                    )
        return environment

    def run(self, spec: CommandSpec, payload: dict[str, Any]) -> dict[str, Any]:
        environment = self.environment_for(spec)
        try:
            completed = subprocess.run(
                spec.argv,
                input=json.dumps(payload, ensure_ascii=False),
                text=True,
                capture_output=True,
                timeout=spec.timeout_seconds,
                check=False,
                shell=False,
                env=environment,
            )
        except (OSError, subprocess.TimeoutExpired) as exc:
            raise AgentError(f"agent command failed to start or timed out: {exc}") from exc
        if completed.returncode != 0:
            detail = completed.stderr.strip()[-2000:]
            raise AgentError(f"agent command exited {completed.returncode}: {detail}")
        output = completed.stdout.strip()
        try:
            value = json.loads(output)
        except json.JSONDecodeError as exc:
            raise AgentError("agent stdout must contain exactly one JSON object") from exc
        if not isinstance(value, dict):
            raise AgentError("agent stdout must be a JSON object")
        return value


class FunctionRunner(CommandRunner):
    """Test runner that preserves the same JSON object boundary."""

    def __init__(self, function: Callable[[CommandSpec, dict[str, Any]], dict[str, Any]]) -> None:
        self.function = function

    def run(self, spec: CommandSpec, payload: dict[str, Any]) -> dict[str, Any]:
        value = self.function(spec, json.loads(json.dumps(payload)))
        if not isinstance(value, dict):
            raise AgentError("test agent returned a non-object")
        return value


def _text(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def _closed(value: dict[str, Any], allowed: set[str], required: set[str], label: str) -> None:
    unknown = sorted(set(value) - allowed)
    missing = sorted(required - set(value))
    if unknown:
        raise ContractError(f"{label} has unknown fields: {', '.join(unknown)}")
    if missing:
        raise ContractError(f"{label} is missing fields: {', '.join(missing)}")
