"""Canonical JSON, digests, and atomic artifact I/O."""

from __future__ import annotations

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import Any

from .errors import ContractError


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def quinte_json_bytes(value: Any) -> bytes:
    """Match serde_json's compact, struct-field-order encoding."""
    return json.dumps(value, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def digest_bytes(value: bytes) -> str:
    return f"sha256:{hashlib.sha256(value).hexdigest()}"


def digest_value(value: Any) -> str:
    return digest_bytes(canonical_json_bytes(value))


def digest_file(path: Path) -> str:
    try:
        return digest_bytes(path.read_bytes())
    except OSError as exc:
        raise ContractError(f"cannot read artifact {path}: {exc}") from exc


def digest_tree(root: Path, relative_paths: list[Path]) -> str:
    """Bind a selected runtime tree with path and byte framing."""
    hasher = hashlib.sha256()
    for relative in sorted(relative_paths, key=lambda item: item.as_posix()):
        path = root / relative
        try:
            raw = path.read_bytes()
        except OSError as exc:
            raise ContractError(f"cannot read runtime artifact {path}: {exc}") from exc
        name = relative.as_posix().encode("utf-8")
        hasher.update(len(name).to_bytes(8, "big"))
        hasher.update(name)
        hasher.update(len(raw).to_bytes(8, "big"))
        hasher.update(raw)
    return f"sha256:{hasher.hexdigest()}"


def runtime_digest(repository_root: Path | None = None) -> str:
    root = repository_root or Path(__file__).resolve().parents[1]
    paths: list[Path] = []
    for directory in (root / "magi", root / "schemas"):
        paths.extend(
            path.relative_to(root)
            for path in directory.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        )
    for name in ("magi", "magi-agent"):
        path = root / "bin" / name
        if path.is_file():
            paths.append(path.relative_to(root))
    return digest_tree(root, paths)


def read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON artifact {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"JSON artifact must be an object: {path}")
    return value


def atomic_write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
