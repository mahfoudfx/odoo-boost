"""MCP tool: list_views – ir.ui.view metadata, with arch opt-in."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import json_response, resolve_full


def list_views(
    model_name: str = "",
    view_type: str = "",
    limit: int = 20,
    offset: int = 0,
    view_id: int = 0,
    include_arch: bool | None = None,
    response_format: str | None = None,
) -> str:
    """List Odoo views (ir.ui.view), optionally filtered by model or type.

    By default the bulky ``arch`` XML is omitted; a compact ``arch_length`` is
    returned instead. Pass ``response_format="full"`` (or ``include_arch=true``)
    to include the XML, ideally together with ``view_id`` for a single view.

    Args:
        model_name: Filter by model technical name (e.g. 'res.partner').
        view_type: Filter by view type (e.g. 'form', 'tree', 'kanban').
        limit: Maximum number of views to return (default 20).
        offset: Number of views to skip (default 0).
        view_id: Fetch exactly one view by database ID.
        include_arch: Include the ``arch`` XML. Defaults to true for
            ``response_format="full"`` and false otherwise.
        response_format: 'compact' (default) or 'full'.
    """
    full = resolve_full(response_format)
    if include_arch is None:
        include_arch = full

    conn = get_connection()

    domain: list = []
    if model_name:
        domain.append(("model", "=", model_name))
    if view_type:
        domain.append(("type", "=", view_type))
    if view_id:
        domain.append(("id", "=", view_id))

    fields = ["name", "model", "type", "priority", "inherit_id", "active"]
    if include_arch:
        fields.append("arch")

    total = conn.search_count("ir.ui.view", domain)
    views = conn.search_read(
        "ir.ui.view",
        domain=domain,
        fields=fields,
        limit=limit,
        offset=offset,
        order="model, priority",
    )

    rendered = []
    for v in views:
        entry = {
            "id": v["id"],
            "name": v["name"],
            "model": v["model"],
            "type": v["type"],
            "priority": v.get("priority", 16),
            "inherit_id": v.get("inherit_id", False) or None,
            "active": v.get("active", True),
        }
        if include_arch:
            arch = v.get("arch", "") or ""
            entry["arch"] = arch
            entry["arch_length"] = len(arch)
        else:
            arch = v.get("arch", "") or ""
            entry["arch_length"] = len(arch)
            entry["has_arch"] = bool(arch)
        rendered.append(entry)

    result = {
        "total": total,
        "returned": len(rendered),
        "offset": offset,
        "limit": limit,
        "included_arch": include_arch,
        "response_format": "full" if full else "compact",
        "views": rendered,
    }
    return json_response(result)
