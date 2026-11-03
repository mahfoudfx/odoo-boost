"""Checksum ownership for generated skill and reference files."""

from __future__ import annotations

import hashlib
import json
import logging
from pathlib import Path

logger = logging.getLogger(__name__)
MANIFEST = ".odoo-boost-files.json"


def _digest(content: str) -> str:
    return hashlib.sha256(content.encode("utf-8")).hexdigest()


def _ownership(root: Path) -> dict[str, str]:
    path = root / MANIFEST
    if not path.exists():
        return {}
    if path.is_symlink():
        raise ValueError(f"Ownership manifest uses a symlink: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or any(
        not isinstance(key, str) or not isinstance(value, str) for key, value in data.items()
    ):
        raise ValueError(f"Invalid ownership manifest: {path}")
    return data


def _safe_file(root: Path, relative: str) -> Path:
    path = root / relative
    if Path(relative).is_absolute() or ".." in Path(relative).parts:
        raise ValueError(f"Invalid generated file path: {relative}")
    for candidate in (path, *path.parents):
        if candidate.is_symlink():
            raise ValueError(f"Generated file uses a symlink: {candidate}")
        if candidate == root:
            break
    return path


def write_owned_files(root: Path, files: dict[str, str]) -> list[Path]:
    """Update unchanged owned files, adopting identical legacy files safely."""
    root = root.absolute()
    owned = _ownership(root)
    written = []
    for relative, content in files.items():
        path = _safe_file(root, relative)
        digest = _digest(content)
        if path.exists():
            current = path.read_text(encoding="utf-8")
            if current == content:
                owned[relative] = digest
                written.append(path)
                continue
            if _digest(current) != owned.get(relative):
                logger.warning("Preserving custom or edited generated file: %s", path)
                continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        owned[relative] = digest
        written.append(path)
    if owned:
        manifest = _safe_file(root, MANIFEST)
        content = json.dumps(owned, indent=2) + "\n"
        if not manifest.exists() or manifest.read_text(encoding="utf-8") != content:
            manifest.write_text(content, encoding="utf-8")
        written.append(manifest)
    return written


def remove_owned_files(root: Path) -> list[Path]:
    """Remove unchanged owned files, including files from older package versions."""
    root = root.absolute()
    if root.is_symlink():
        return []
    removed = []
    for relative, digest in _ownership(root).items():
        try:
            path = _safe_file(root, relative)
        except ValueError:
            logger.warning("Preserving unsafe generated file path: %s", root / relative)
            continue
        if path.is_file() and _digest(path.read_text(encoding="utf-8")) == digest:
            path.unlink()
            removed.append(path)
    manifest = root / MANIFEST
    if manifest.is_file():
        manifest.unlink()
        removed.append(manifest)
    return removed


def remove_empty_parents(candidates: list[Path], root: Path) -> None:
    """Remove empty ancestor directories, stopping at the project root."""
    for current in candidates:
        while current != root and current.is_relative_to(root) and current != current.parent:
            try:
                current.rmdir()
            except OSError:
                break
            current = current.parent
