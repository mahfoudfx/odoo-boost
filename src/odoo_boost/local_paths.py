"""Project path resolution and local-file access rules shared by CLI and MCP."""

from __future__ import annotations

from pathlib import Path

from odoo_boost.config.schema import OdooBoostConfig


def resolve_path(raw: str | Path, base: Path) -> Path:
    path = Path(raw).expanduser()
    return (path if path.is_absolute() else base / path).resolve()


def venv_python(root: Path) -> Path:
    return root / ("Scripts/python.exe" if (root / "Scripts").is_dir() else "bin/python")


def local_roots(config: OdooBoostConfig) -> tuple[Path, ...]:
    """Explicit roots use the working directory; empty means unrestricted access."""
    if config.allowed_roots:
        return tuple(resolve_path(raw, Path.cwd()) for raw in config.allowed_roots)
    return () if config.allow_external_local_paths else (config.project_root,)


def path_allowed(path: Path, config: OdooBoostConfig) -> bool:
    roots = local_roots(config)
    return not roots or any(path.is_relative_to(root) for root in roots)
