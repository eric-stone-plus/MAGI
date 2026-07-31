#!/usr/bin/env python3
"""Compose an immutable MAGI seat profile from private Hermes rules."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shlex
import shutil
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any

try:
    import yaml
except ImportError as exc:  # pragma: no cover - exercised by launcher diagnostics
    raise SystemExit(
        "profile composition requires PyYAML; run this helper with the Hermes "
        "technical-profile Python or install the pinned PyYAML dependency"
    ) from exc


REQUIRED_BASE_FILES = ("SOUL.md",)
FORBIDDEN_NAMES = {
    ".env",
    ".hermes_history",
    ".skills_prompt_snapshot.json",
    "active_profile",
    "auth.json",
    "auth.lock",
    "config.yaml",
    "gateway_state.json",
    "profile.json",
    "provider_models_cache.json",
    "models_dev_cache.json",
    "ollama_cloud_models_cache.json",
    "processes.json",
    "sessions.db",
    "shell-hooks-allowlist.json",
    "state.db",
    "state.db-shm",
    "state.db-wal",
    "verification_evidence.db",
}
FORBIDDEN_SUFFIXES = (".db", ".db-shm", ".db-wal", ".env", ".lock", ".log")
SECRET_FILE_NAMES = {".env", "auth.json"}
SECRET_PERMISSION_MASK = stat.S_IRWXG | stat.S_IRWXO
FORBIDDEN_PARTS = {
    ".git",
    ".pytest_cache",
    "archive",
    "audio_cache",
    "cache",
    "checkpoints",
    "cron",
    "debates",
    "image_cache",
    "local-archive",
    "logs",
    "pairing",
    "pastes",
    "quinte-briefs",
    "sandboxes",
    "sessions",
    "state",
    "state-snapshots",
}
SAFE_MEMORY_NAMES = {"MEMORY.md", "POSTMORTEM.md", "USER.md"}
RUNTIME_PROFILE_HOME = "/runtime/hermes-home/profiles/magi-seat"
SECRET_KEY_TOKENS = ("api_key", "password", "secret", "session_key", "access_token", "record_key")
REQUIRED_SOUL_MARKERS = {
    "output format": ("## 输出格式",),
    "authorization/write rules": ("## 授权与写入", "## 授权门"),
}

SEAT_APPENDIX = """# MAGI Independent Seat Appendix

- Work only from the original brief, this immutable technical profile, and evidence explicitly supplied to this seat.
- Do not inspect, infer, request, or imitate another seat's thesis, provider identity, model family, runtime state, or artifacts.
- Treat this profile as read-only. Do not create or modify memories, skills, rules, schedules, curator state, or self-improvement state.
- Keep claims traceable to supplied evidence, state uncertainty and scope boundaries, and never present convergence as proof.
- Profile diversity and model-family independence are separate facts. Never infer one from the other.
- Do not perform external actions. Produce only the requested closed JSON artifact.
"""
SEAT_DISABLED_TOOLSETS = [
    "clarify",
    "code_execution",
    "context_engine",
    "file",
    "image_gen",
    "kanban",
    "memory",
    "session_search",
    "skills",
    "terminal",
    "todo",
    "vision",
    "web",
]


class CompositionError(ValueError):
    pass


def _read_text(path: Path, label: str) -> str:
    try:
        value = path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as exc:
        raise CompositionError(f"cannot read {label}: {path}: {exc}") from exc
    if not value.strip():
        raise CompositionError(f"{label} is empty: {path}")
    return value


def _safe_files(root: Path, *, composed: bool = False) -> list[Path]:
    if not root.is_dir():
        raise CompositionError(f"technical base is not a directory: {root}")
    for required in REQUIRED_BASE_FILES:
        if not (root / required).is_file():
            raise CompositionError(f"technical base is missing {required}")
    files: list[Path] = []
    for directory, names, filenames in os.walk(root, followlinks=False):
        directory_path = Path(directory)
        relative_dir = directory_path.relative_to(root)
        names[:] = sorted(name for name in names if name not in FORBIDDEN_PARTS)
        for name in names:
            candidate = directory_path / name
            if candidate.is_symlink():
                raise CompositionError(f"profile symlink is forbidden: {candidate.relative_to(root)}")
        for name in sorted(filenames):
            candidate = directory_path / name
            relative = candidate.relative_to(root)
            if candidate.is_symlink():
                raise CompositionError(f"profile symlink is forbidden: {relative}")
            permitted_composed = composed and name in {"config.yaml", "profile.json", "COMPOSITION.json"}
            if (name in FORBIDDEN_NAMES or name.endswith(FORBIDDEN_SUFFIXES)) and not permitted_composed:
                if name in SECRET_FILE_NAMES or name.endswith(".env"):
                    raise CompositionError(f"runtime/secret profile file is forbidden: {relative}")
                continue
            if any(part in FORBIDDEN_PARTS for part in relative.parts):
                raise CompositionError(f"runtime profile path is forbidden: {relative}")
            if relative.parts and relative.parts[0] == "memories":
                if len(relative.parts) != 2 or name not in SAFE_MEMORY_NAMES or candidate.suffix != ".md":
                    raise CompositionError(f"runtime/unknown memory file is forbidden: {relative}")
            if not candidate.is_file():
                raise CompositionError(f"non-regular profile entry is forbidden: {relative}")
            if candidate.stat().st_size > 2 * 1024 * 1024:
                raise CompositionError(f"profile file exceeds 2 MiB immutable-rule limit: {relative}")
            files.append(candidate)
    return files


def _load_config(path: Path) -> dict[str, Any]:
    text = _read_text(path, "technical config")
    try:
        value = yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise CompositionError(f"technical config is invalid YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise CompositionError("technical config must contain a YAML mapping")
    return value


def _validate_agents_text(value: str) -> None:
    lower = value.lower()
    categories = {
        "repository rules": ("github repositories", "repository"),
        "workspace layout": ("workspace", "layout"),
        "zero-write lockdown": ("zero-write", "self-write", "自写封印", "lockdown"),
    }
    missing = [label for label, alternatives in categories.items() if not any(token in lower for token in alternatives)]
    if missing:
        raise CompositionError("technical AGENTS.md is missing required categories: " + ", ".join(missing))


def _validate_soul_text(value: str, label: str) -> None:
    missing = [
        name for name, alternatives in REQUIRED_SOUL_MARKERS.items()
        if not any(marker in value for marker in alternatives)
    ]
    if missing:
        raise CompositionError(f"{label} is missing required categories: " + ", ".join(missing))


def _rewrite_config_paths(value: Any, roots: tuple[Path, ...]) -> Any:
    if isinstance(value, dict):
        return {key: _rewrite_config_paths(item, roots) for key, item in value.items()}
    if isinstance(value, list):
        return [_rewrite_config_paths(item, roots) for item in value]
    if isinstance(value, str):
        rendered = value
        for root in sorted(roots, key=lambda item: len(str(item)), reverse=True):
            candidates = {str(root), os.path.abspath(root), os.path.realpath(root)}
            if str(root).startswith("/private/"):
                candidates.add(str(root)[len("/private"):])
            for candidate in sorted(candidates, key=len, reverse=True):
                rendered = rendered.replace(candidate, RUNTIME_PROFILE_HOME)
        return rendered
    return value


def _strip_config_secrets(value: Any, path: tuple[str, ...] = ()) -> Any:
    if isinstance(value, dict):
        rendered: dict[str, Any] = {}
        for key, item in value.items():
            key_text = str(key).lower()
            if any(token in key_text for token in SECRET_KEY_TOKENS):
                rendered[key] = "" if isinstance(item, str) else _strip_config_secrets(item, path + (str(key),))
            else:
                rendered[key] = _strip_config_secrets(item, path + (str(key),))
        return rendered
    if isinstance(value, list):
        return [_strip_config_secrets(item, path) for item in value]
    return value


def _normalize_python_hooks(value: dict[str, Any]) -> dict[str, Any]:
    """Run bare Python hooks through the interpreter on noexec profiles."""
    hooks = value.get("hooks")
    if not isinstance(hooks, dict):
        return value
    for event, entries in hooks.items():
        if not isinstance(entries, list):
            continue
        for index, entry in enumerate(entries):
            if not isinstance(entry, dict):
                continue
            command = entry.get("command")
            if not isinstance(command, str) or not command.strip():
                continue
            try:
                argv = shlex.split(command)
            except ValueError as exc:
                raise CompositionError(
                    f"hooks.{event}[{index}].command is not valid shell-word syntax: {exc}"
                ) from exc
            if argv and argv[0].lower().endswith((".py", ".pyw")):
                entry["command"] = shlex.join(["python3", *argv])
    return value


def _patch_config(value: dict[str, Any], source_roots: tuple[Path, ...]) -> dict[str, Any]:
    value = _strip_config_secrets(_rewrite_config_paths(value, source_roots))
    value = dict(value)
    value = _normalize_python_hooks(value)
    # Hermes merges modern and legacy fallback keys. A seat must never cross
    # its provider boundary after authentication or transport failure.
    value["fallback_providers"] = []
    value.pop("fallback_model", None)
    value["self_improvement"] = {**_mapping(value.get("self_improvement")), "enabled": False}
    value["memory"] = {
        **_mapping(value.get("memory")),
        "memory_enabled": False,
        "user_profile_enabled": False,
        "write_approval": True,
    }
    value["skills"] = {
        **_mapping(value.get("skills")),
        "creation_nudge_interval": 0,
        "write_approval": True,
    }
    value["curator"] = {**_mapping(value.get("curator")), "enabled": False}
    value["agent"] = {
        **_mapping(value.get("agent")),
        "disabled_toolsets": SEAT_DISABLED_TOOLSETS.copy(),
    }
    platform = _mapping(value.get("platform_toolsets"))
    platform["cli"] = ["no_mcp"]
    value["platform_toolsets"] = platform
    value["mcp_servers"] = {}
    return value


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _python_hooks_are_interpreter_bound(config: dict[str, Any]) -> bool:
    hooks = config.get("hooks")
    if not isinstance(hooks, dict):
        return True
    for entries in hooks.values():
        if not isinstance(entries, list):
            continue
        for entry in entries:
            if not isinstance(entry, dict) or not isinstance(entry.get("command"), str):
                continue
            try:
                argv = shlex.split(entry["command"])
            except ValueError:
                return False
            if argv and argv[0].lower().endswith((".py", ".pyw")):
                return False
    return True


def _verify_lockdown(config: dict[str, Any]) -> None:
    checks = (
        (config.get("self_improvement", {}).get("enabled") is False, "self_improvement.enabled=false"),
        (config.get("memory", {}).get("memory_enabled") is False, "memory.memory_enabled=false"),
        (config.get("memory", {}).get("user_profile_enabled") is False, "memory.user_profile_enabled=false"),
        (config.get("memory", {}).get("write_approval") is True, "memory.write_approval=true"),
        (config.get("skills", {}).get("write_approval") is True, "skills.write_approval=true"),
        (config.get("curator", {}).get("enabled") is False, "curator.enabled=false"),
        (config.get("fallback_providers") == [], "fallback_providers is empty"),
        ("fallback_model" not in config, "legacy fallback_model is absent"),
        (_python_hooks_are_interpreter_bound(config), "Python hooks are interpreter-bound"),
        (config.get("platform_toolsets", {}).get("cli") == ["no_mcp"], "platform_toolsets.cli is no_mcp only"),
        (
            set(config.get("agent", {}).get("disabled_toolsets", [])) >= set(SEAT_DISABLED_TOOLSETS),
            "agent.disabled_toolsets closes every production toolset",
        ),
        (config.get("mcp_servers") == {}, "mcp_servers is empty"),
    )
    missing = [label for ok, label in checks if not ok]
    if missing:
        raise CompositionError("zero-write config invariant failed: " + ", ".join(missing))


def _tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(path for path in root.rglob("*") if path.is_file()):
        relative = path.relative_to(root).as_posix().encode()
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big")); digest.update(relative)
        digest.update(len(data).to_bytes(8, "big")); digest.update(data)
    return "sha256:" + digest.hexdigest()


def _source_digest(files: list[Path], root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(files):
        relative = path.relative_to(root).as_posix().encode()
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big")); digest.update(relative)
        digest.update(len(data).to_bytes(8, "big")); digest.update(data)
    return "sha256:" + digest.hexdigest()


def _content_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(path for path in root.rglob("*") if path.is_file() and path.name != "COMPOSITION.json"):
        relative = path.relative_to(root).as_posix().encode()
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big")); digest.update(relative)
        digest.update(len(data).to_bytes(8, "big")); digest.update(data)
    return "sha256:" + digest.hexdigest()


def _write_text(path: Path, value: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.chmod(0o600)
    path.write_text(value, encoding="utf-8")
    path.chmod(0o600)


def _copy_mode(source: Path, target: Path) -> int:
    if source.stat().st_mode & 0o111 and source.suffix in {".py", ".sh"}:
        return 0o500
    return 0o400


def _rewrite_private_paths(text: str, source_root: Path, destination_root: str) -> str:
    rendered = text
    candidates = {str(source_root), os.path.abspath(source_root), os.path.realpath(source_root)}
    if str(source_root).startswith("/private/"):
        candidates.add(str(source_root)[len("/private"):])
    for source in sorted(candidates, key=len, reverse=True):
        rendered = rendered.replace(source, destination_root)
    return rendered


def compose(base: Path, agents: Path, config_path: Path, overlay: Path, destination: Path, seat: str) -> str:
    base = base.resolve(); agents = agents.resolve(); config_path = config_path.resolve(); overlay = overlay.resolve()
    source_files = _safe_files(base)
    if config_path.stat().st_mode & SECRET_PERMISSION_MASK:
        raise CompositionError(f"technical config must not grant group/other permissions: {config_path}")
    base_sha = _source_digest(source_files, base)
    agents_text = _read_text(agents, "technical AGENTS.md")
    overlay_soul = _read_text(overlay / "SOUL.md", "seat overlay SOUL.md")
    overlay_profile = overlay / "profile.json"
    if not overlay_profile.is_file():
        raise CompositionError("seat overlay is missing profile.json")
    try:
        profile = json.loads(_read_text(overlay_profile, "seat overlay profile.json"))
    except json.JSONDecodeError as exc:
        raise CompositionError(f"seat overlay profile.json is invalid: {exc}") from exc
    if not isinstance(profile, dict) or not profile.get("profile_id"):
        raise CompositionError("seat overlay profile.json must identify profile_id")
    overlay_sha = _source_digest(
        sorted(path for path in overlay.rglob("*") if path.is_file()), overlay
    )
    soul_text = _read_text(base / "SOUL.md", "technical SOUL.md")
    _validate_soul_text(soul_text, "technical SOUL.md")
    _validate_agents_text(agents_text)
    config_roots = (base, config_path.parent)
    config = _patch_config(_load_config(config_path), config_roots)
    _verify_lockdown(config)

    destination = destination.resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    stage = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent))
    try:
        for source in source_files:
            relative = source.relative_to(base)
            target = stage / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            data = source.read_bytes()
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError:
                target.write_bytes(data)
            else:
                _write_text(target, _rewrite_private_paths(text, base, "/runtime/hermes-home/profiles/magi-seat"))
            target.chmod(_copy_mode(source, target))
        _write_text(stage / "SOUL.md", soul_text.rstrip() + "\n\n" + overlay_soul.rstrip() + "\n")
        _write_text(stage / "AGENTS.md", agents_text.rstrip() + "\n\n" + SEAT_APPENDIX)
        _write_text(stage / "config.yaml", yaml.safe_dump(config, allow_unicode=True, sort_keys=False))
        _write_text(stage / "profile.json", json.dumps(profile, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        digest = _content_digest(stage)
        _write_text(stage / "COMPOSITION.json", json.dumps({
            "base_sha256": base_sha,
            "composition_version": "1.0",
            "overlay_sha256": overlay_sha,
            "profile_id": profile["profile_id"],
            "seat_id": seat,
            "composed_content_sha256": digest,
        }, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
        if destination.exists():
            try:
                existing_digest = validate_composed(destination, seat)
                stage_digest = _tree_digest(stage)
            except (CompositionError, OSError) as exc:
                raise CompositionError(
                    f"composed destination exists but is not reusable: {destination}: {exc}"
                ) from exc
            if existing_digest != stage_digest:
                raise CompositionError(
                    f"composed destination exists with different source content: {destination}"
                )
            shutil.rmtree(stage)
            return existing_digest
        os.replace(stage, destination)
        for path in (path for path in destination.rglob("*") if path.is_file()):
            if path.name in {"SOUL.md", "AGENTS.md", "config.yaml", "profile.json", "COMPOSITION.json"}:
                path.chmod(0o400)
        for directory in sorted((path for path in destination.rglob("*") if path.is_dir()), reverse=True):
            directory.chmod(0o500)
        destination.chmod(0o500)
        return _tree_digest(destination)
    except Exception:
        shutil.rmtree(stage, ignore_errors=True)
        raise


def validate_composed(root: Path, seat: str | None = None) -> str:
    root = root.resolve()
    if not root.is_dir():
        raise CompositionError(f"composed profile is not a directory: {root}")
    for required in ("SOUL.md", "AGENTS.md", "config.yaml", "profile.json", "COMPOSITION.json"):
        if not (root / required).is_file():
            raise CompositionError(f"composed profile is missing {required}")
    _safe_files(root, composed=True)
    try:
        receipt = json.loads(_read_text(root / "COMPOSITION.json", "composition receipt"))
        profile = json.loads(_read_text(root / "profile.json", "profile metadata"))
    except json.JSONDecodeError as exc:
        raise CompositionError(f"composed profile JSON is invalid: {exc}") from exc
    required = {"base_sha256", "composition_version", "overlay_sha256", "profile_id", "seat_id", "composed_content_sha256"}
    if not isinstance(receipt, dict) or set(receipt) != required or receipt.get("composition_version") != "1.0":
        raise CompositionError("composition receipt has a closed-field/version mismatch")
    if seat is not None and receipt.get("seat_id") != seat:
        raise CompositionError("composition receipt seat_id mismatch")
    if not isinstance(profile, dict) or profile.get("profile_id") != receipt.get("profile_id"):
        raise CompositionError("profile metadata does not match the composition receipt")
    if receipt["composed_content_sha256"] != _content_digest(root):
        raise CompositionError("composed profile content digest mismatch")
    soul = _read_text(root / "SOUL.md", "composed SOUL.md")
    agents = _read_text(root / "AGENTS.md", "composed AGENTS.md")
    _validate_soul_text(soul, "composed SOUL.md")
    _validate_agents_text(agents)
    if "MAGI Independent Seat Appendix" not in agents:
        raise CompositionError("composed AGENTS.md is missing the independent-seat appendix")
    _verify_lockdown(_load_config(root / "config.yaml"))
    return _tree_digest(root)


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    sub = result.add_subparsers(dest="command", required=True)
    create = sub.add_parser("compose")
    create.add_argument("--technical-base", required=True)
    create.add_argument("--technical-agents", required=True)
    create.add_argument("--technical-config", required=True)
    create.add_argument("--overlay", required=True)
    create.add_argument("--destination", required=True)
    create.add_argument("--seat", required=True, choices=("seat-m", "seat-d", "seat-g"))
    validate = sub.add_parser("validate")
    validate.add_argument("path")
    validate.add_argument("--seat", choices=("seat-m", "seat-d", "seat-g"))
    return result


def main() -> int:
    try:
        args = parser().parse_args()
        if args.command == "compose":
            print(compose(
                Path(args.technical_base), Path(args.technical_agents), Path(args.technical_config),
                Path(args.overlay), Path(args.destination), args.seat,
            ))
        else:
            print(validate_composed(Path(args.path), args.seat))
        return 0
    except (CompositionError, OSError) as exc:
        print(f"profile composition error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
