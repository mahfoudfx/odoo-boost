"""MCP tool: inspect_local_addon – scan uncommitted/uninstalled addon code on disk."""

from __future__ import annotations

import json
from pathlib import Path

from odoo_boost.ast_scanner.analyzer import scan_addon


def inspect_local_addon(addon_path: str) -> str:
    """Analyze a local Odoo addon directory on disk without requiring database installation.

    Extracts declared models, fields, methods, views, actions, and manifest metadata.

    Args:
        addon_path: Absolute or relative path to the local addon directory.
    """
    path = Path(addon_path)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()

    if not path.exists():
        return json.dumps({"error": f"Path '{addon_path}' does not exist."}, indent=2)

    scanned = scan_addon(path)
    return json.dumps(scanned, indent=2, default=str)
