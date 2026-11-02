"""Load and save odoo-boost.json configuration."""

from __future__ import annotations

import contextlib
import json
import os
from pathlib import Path

from odoo_boost.config.schema import OdooBoostConfig

CONFIG_FILENAME = "odoo-boost.json"


def find_config_path(start: Path | None = None) -> Path | None:
    """Walk up from *start* looking for odoo-boost.json. Returns None if not found."""
    current = (start or Path.cwd()).resolve()
    while True:
        candidate = current / CONFIG_FILENAME
        if candidate.is_file():
            return candidate
        parent = current.parent
        if parent == current:
            return None
        current = parent


def load_config(path: Path | None = None) -> OdooBoostConfig:
    """Load config and anchor relative project paths to its containing directory."""
    if path is None:
        path = find_config_path()
    if path is None:
        raise FileNotFoundError(f"No {CONFIG_FILENAME} found. Run 'odoo-boost install' first.")
    data = json.loads(path.read_text(encoding="utf-8"))
    config = OdooBoostConfig.model_validate(data)
    config._config_path = path.absolute()
    project = Path(config.project_path).expanduser()
    if not project.is_absolute():
        project = path.absolute().parent / project
    config.project_path = str(project.resolve())
    return config


def save_config(config: OdooBoostConfig, path: Path | None = None) -> Path:
    """Persist config to *path* (defaults to ./odoo-boost.json).

    The file contains credentials and an optional bearer token, so it is
    restricted to the owner on POSIX systems where possible.
    """
    if path is None:
        path = Path.cwd() / CONFIG_FILENAME
    path.write_text(
        config.model_dump_json(indent=2) + "\n",
        encoding="utf-8",
    )
    if os.name == "posix":
        with contextlib.suppress(OSError):  # best effort on exotic filesystems
            os.chmod(path, 0o600)
    config._config_path = path.absolute()
    return path
