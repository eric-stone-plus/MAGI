#!/usr/bin/env python3
"""Deterministically hash an immutable Hermes profile tree."""

from __future__ import annotations

import hashlib
import os
import sys
from pathlib import Path


def validate_tree(root: Path) -> list[Path]:
    if not root.is_dir():
        raise ValueError(f"profile is not a directory: {root}")
    files: list[Path] = []
    for path in root.rglob("*"):
        relative = path.relative_to(root)
        if path.is_symlink():
            raise ValueError(f"profile symlink is forbidden: {relative}")
        if path.is_file():
            if path.name == ".env" or path.name.endswith(".env"):
                raise ValueError(f"secret-bearing profile file is forbidden: {relative}")
            files.append(path)
    if not files:
        raise ValueError(f"profile contains no files: {root}")
    return files


def digest_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(validate_tree(root)):
        relative = path.relative_to(root).as_posix().encode()
        data = path.read_bytes()
        digest.update(len(relative).to_bytes(8, "big"))
        digest.update(relative)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return "sha256:" + digest.hexdigest()


if __name__ == "__main__":
    try:
        print(digest_tree(Path(sys.argv[1]).resolve()))
    except (IndexError, OSError, ValueError) as exc:
        print(f"profile digest error: {exc}", file=sys.stderr)
        raise SystemExit(2)
