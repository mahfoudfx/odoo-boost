"""MCP tool: list_views – ir.ui.view with arch XML, filter by model/type."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import json_response


def list_views(
    model_name: str = "",
    view_type: str = "",
    limit: int = 50,
) -> str:
    """List Odoo views (ir.ui.view), optionally filtered by model or type.

    Args:
        model_name: Filter by model technical name (e.g. 'res.partner').
        view_type: Filter by view type (e.g. 'form', 'tree', 'kanban', 'search').
        limit: Maximum number of views to return (default 50).
    """
    conn = get_connection()

    domain: list = []
    if model_name:
        domain.append(("model", "=", model_name))
    if view_type:
        domain.append(("type", "=", view_type))

    views = conn.search_read(
        "ir.ui.view",
        domain=domain,
        fields=["name", "model", "type", "arch", "inherit_id", "priority", "active"],
        limit=limit,
        order="model, priority",
    )

    result = {
        "total": len(views),
        "views": [
            {
                "id": v["id"],
                "name": v["name"],
                "model": v["model"],
                "type": v["type"],
                "priority": v.get("priority", 16),
                "inherit_id": v.get("inherit_id", False) or None,
                "active": v.get("active", True),
                "arch": v.get("arch", ""),
            }
            for v in views
        ],
    }
    return json_response(result)
