"""Compact, read-only view of configured custom-addon development paths."""

from __future__ import annotations

import configparser
from pathlib import Path
from typing import Any

from odoo_boost.config.schema import OdooBoostConfig


def _resolve(raw: str, project: Path) -> Path:
    path = Path(raw).expanduser()
    return (path if path.is_absolute() else project / path).resolve()


def _access(path: Path, config: OdooBoostConfig, project: Path) -> str:
    if config.allow_external_local_paths and not config.allowed_roots:
        return "allowed"
    roots = config.allowed_roots or [str(project)]
    for raw in roots:
        # Match enforce_path: relative allowed_roots use the server working directory.
        root = Path(raw).expanduser().resolve()
        if path == root or path.is_relative_to(root):
            return "allowed"
    return "outside_allowed_roots"


def _location(raw: str | None, config: OdooBoostConfig, project: Path) -> dict[str, Any] | None:
    if not raw:
        return None
    path = _resolve(raw, project)
    return {
        "path": str(path),
        "exists": path.exists(),
        "mcp_file_access": _access(path, config, project),
    }


def _config_addons(conf: Path) -> tuple[list[str], str | None]:
    parser = configparser.RawConfigParser(strict=False)
    try:
        with conf.open(encoding="utf-8") as stream:
            parser.read_file(stream)
        value = parser.get("options", "addons_path", fallback="")
    except (OSError, configparser.Error, UnicodeError) as exc:
        return [], f"Could not read addons_path: {type(exc).__name__}"
    return [part.strip() for part in value.split(",") if part.strip()], None


def project_context(config: OdooBoostConfig) -> dict[str, Any]:
    """Resolve only explicit paths and the addons_path in an explicit odoo.conf.

    Relative config fields use project_path. Relative addons_path entries use
    the explicitly configured Odoo launch directory or remain unresolved.
    """
    project = Path(config.project_path).expanduser().resolve()
    conf = _location(config.odoo_conf_path, config, project)
    launch_cwd = _location(config.odoo_launch_cwd, config, project)
    source = "not_configured"
    raw_addons: list[str] = []
    warning: str | None = None
    if config.addons_path_override is not None:
        source, raw_addons = "launch_override", config.addons_path_override
    elif conf is not None:
        source = "odoo.conf"
        raw_addons, warning = _config_addons(Path(conf["path"]))

    addons: list[dict[str, Any]] = []
    for raw in raw_addons:
        path = Path(raw).expanduser()
        if path.is_absolute():
            resolved = path.resolve()
            addons.append(
                {
                    "path": str(resolved),
                    "exists": resolved.is_dir(),
                    "mcp_file_access": _access(resolved, config, project),
                }
            )
        else:
            if launch_cwd is None:
                addons.append({"raw_path": raw, "status": "relative_to_unknown_launch_cwd"})
                continue
            resolved = (Path(launch_cwd["path"]) / path).resolve()
            addons.append(
                {
                    "raw_path": raw,
                    "path": str(resolved),
                    "exists": resolved.is_dir(),
                    "mcp_file_access": _access(resolved, config, project),
                }
            )

    venv = _location(config.venv_path, config, project)
    if venv is not None:
        root = Path(venv["path"])
        python = root / ("Scripts/python.exe" if (root / "Scripts").is_dir() else "bin/python")
        venv = {
            "path": str(root),
            "valid": (root / "pyvenv.cfg").is_file() and python.is_file(),
            "python": str(python),
        }

    result: dict[str, Any] = {
        "project_path": str(project),
        "odoo_version": config.odoo_version,
        "venv": venv,
        "odoo_conf": conf,
        "odoo_launch_cwd": launch_cwd,
        "addons_path_source": source,
        "addons_path": addons,
        "odoo_source": _location(config.odoo_source_path, config, project),
        "odoo_docs": _location(config.odoo_docs_path, config, project),
    }
    if warning:
        result["warning"] = warning
    return result
