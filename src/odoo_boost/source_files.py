"""Deterministic source discovery that prunes generated and hidden directories."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

_GENERATED = frozenset({"__pycache__", "build", "dist"})


def _excluded(name: str) -> bool:
    return name.startswith(".") or name in _GENERATED


def source_allowed(source: Path, root: Path) -> bool:
    """Allow internal file symlinks while excluding links outside the scan root."""
    return not any(_excluded(part) for part in source.relative_to(root).parts) and (
        not source.is_symlink() or source.resolve().is_relative_to(root)
    )


def iter_source_files(root: Path, suffixes: set[str]) -> Iterator[Path]:
    """Walk once without entering excluded directories or directory symlinks."""
    for directory, folders, files in os.walk(root):
        folders[:] = sorted(name for name in folders if not _excluded(name))
        for name in sorted(files):
            source = Path(directory) / name
            if source.suffix in suffixes and source_allowed(source, root):
                yield source
