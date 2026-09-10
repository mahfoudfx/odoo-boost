"""MCP tool: inspect_local_addon – scan uncommitted/uninstalled addon code on disk."""

from __future__ import annotations

from odoo_boost.ast_scanner.analyzer import scan_addon
from odoo_boost.mcp_server.policy import enforce_path
from odoo_boost.mcp_server.tools._common import error_response, json_response


def inspect_local_addon(addon_path: str) -> str:
    """Analyze a local Odoo addon directory on disk without requiring database installation.

    Extracts declared models, fields, methods, views, actions, and manifest metadata.

    Args:
        addon_path: Absolute or relative path to the local addon directory.
    """
    path = enforce_path(addon_path)

    if not path.exists():
        return error_response(f"Path '{addon_path}' does not exist.")

    scanned = scan_addon(path)
    return json_response(scanned)
