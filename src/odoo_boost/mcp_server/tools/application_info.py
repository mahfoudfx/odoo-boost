"""MCP tool: application_info – Odoo version, installed modules, database info."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import json_response, resolve_full


def application_info(
    include_modules: bool | None = None,
    module_filter: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str | None = None,
) -> str:
    """Get Odoo application info: server version, installed modules, database details.

    Compact mode returns the version and installed-module count without listing
    modules (and without querying them). Use ``response_format="full"`` or
    ``include_modules=true`` for the module list.

    Args:
        include_modules: Include the installed module list (defaults to full mode).
        module_filter: Optional substring filter on module names.
        limit: Maximum modules to return (default 50).
        offset: Number of modules to skip (default 0).
        response_format: 'compact' (default) or 'full'.
    """
    full = resolve_full(response_format)
    if include_modules is None:
        include_modules = full

    conn = get_connection()

    version_info = conn.get_version()
    result = {
        "server_version": version_info.get("server_version", "unknown"),
        "server_serie": version_info.get("server_serie", "unknown"),
        "protocol_version": version_info.get("protocol_version", 1),
        "response_format": "full" if full else "compact",
    }

    if not include_modules:
        result["installed_modules_count"] = conn.search_count(
            "ir.module.module", [("state", "=", "installed")]
        )
        return json_response(result)

    domain: list = [("state", "=", "installed")]
    if module_filter:
        domain.append(("name", "ilike", module_filter))

    total = conn.search_count("ir.module.module", domain)
    modules = conn.search_read(
        "ir.module.module",
        domain,
        fields=["name", "shortdesc", "installed_version"],
        limit=limit,
        offset=offset,
        order="name",
    )

    result.update(
        {
            "installed_modules_count": total,
            "returned": len(modules),
            "offset": offset,
            "limit": limit,
            "installed_modules": [
                {
                    "name": m["name"],
                    "description": m.get("shortdesc", ""),
                    "version": m.get("installed_version", ""),
                }
                for m in modules
            ],
        }
    )
    return json_response(result)
