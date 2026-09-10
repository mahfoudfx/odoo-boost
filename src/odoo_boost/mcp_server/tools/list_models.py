"""MCP tool: list_models – all models with field counts, filter by name/module."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import json_response


def list_models(
    filter_name: str = "",
    filter_module: str = "",
    limit: int = 200,
) -> str:
    """List available Odoo models with field counts.

    Args:
        filter_name: Optional substring filter on model technical name.
        filter_module: Optional module name filter (models belonging to a module).
        limit: Maximum number of models to return (default 200).
    """
    conn = get_connection()

    domain: list = []
    if filter_name:
        domain.append(("model", "ilike", filter_name))

    # If filtering by module, look up model IDs via ir.model.data first
    if filter_module:
        model_data = conn.search_read(
            "ir.model.data",
            [("module", "=", filter_module), ("model", "=", "ir.model")],
            fields=["res_id"],
        )
        model_ids = [d["res_id"] for d in model_data]
        if not model_ids:
            return json_response({"total": 0, "models": []})
        domain.append(("id", "in", model_ids))

    models = conn.search_read(
        "ir.model",
        domain=domain,
        fields=["model", "name", "info", "field_id"],
        limit=limit,
        order="model",
    )

    result = {
        "total": len(models),
        "models": [
            {
                "model": m["model"],
                "name": m["name"],
                "field_count": len(m.get("field_id", [])),
            }
            for m in models
        ],
    }
    return json_response(result)
