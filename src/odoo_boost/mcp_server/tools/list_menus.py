"""MCP tool: list_menus – ir.ui.menu hierarchy."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import json_response


def list_menus(
    parent_id: int = 0,
    limit: int = 50,
    offset: int = 0,
) -> str:
    """List Odoo menu items (ir.ui.menu).

    Args:
        parent_id: Filter by parent menu ID. 0 = root menus only. -1 = all menus.
        limit: Maximum number of menus to return (default 50).
        offset: Number of menus to skip (default 0).
    """
    conn = get_connection()

    domain: list = []
    if parent_id == 0:
        domain.append(("parent_id", "=", False))
    elif parent_id > 0:
        domain.append(("parent_id", "=", parent_id))
    # parent_id == -1 means no filter (all menus)

    total = conn.search_count("ir.ui.menu", domain)
    menus = conn.search_read(
        "ir.ui.menu",
        domain=domain,
        fields=["name", "parent_id", "action", "sequence", "child_id", "complete_name"],
        limit=limit,
        offset=offset,
        order="sequence, id",
    )

    result = {
        "total": total,
        "returned": len(menus),
        "offset": offset,
        "limit": limit,
        "menus": [
            {
                "id": m["id"],
                "name": m["name"],
                "complete_name": m.get("complete_name", ""),
                "parent_id": m.get("parent_id", False) or None,
                "action": str(m.get("action", "")) if m.get("action") else None,
                "sequence": m.get("sequence", 10),
                "child_count": len(m.get("child_id", [])),
            }
            for m in menus
        ],
    }
    return json_response(result)
