"""MCP tool: application_info – Odoo version, installed modules, database info."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import json_response


def application_info() -> str:
    """Get Odoo application info: server version, installed modules, database details."""
    conn = get_connection()

    version_info = conn.get_version()
    server_version = version_info.get("server_version", "unknown")
    server_serie = version_info.get("server_serie", "unknown")

    # Installed modules
    modules = conn.search_read(
        "ir.module.module",
        [("state", "=", "installed")],
        fields=["name", "shortdesc", "installed_version"],
        order="name",
    )

    result = {
        "server_version": server_version,
        "server_serie": server_serie,
        "protocol_version": version_info.get("protocol_version", 1),
        "installed_modules_count": len(modules),
        "installed_modules": [
            {
                "name": m["name"],
                "description": m.get("shortdesc", ""),
                "version": m.get("installed_version", ""),
            }
            for m in modules
        ],
    }
    return json_response(result)
