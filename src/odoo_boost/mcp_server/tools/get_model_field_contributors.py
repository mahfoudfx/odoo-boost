"""MCP tool: get_model_field_contributors – field contributors."""

from __future__ import annotations

from typing import Any

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import json_response, resolve_full


def get_model_field_contributors(model: str, response_format: str | None = None) -> str:
    """Inspect field counts and modules contributing fields to a model.

    This metadata does not
    expose Python _inherit chains or _inherits delegation; inspect addon source
    for those relationships.

    Compact mode returns a sample of custom fields; ``response_format="full"``
    returns up to the first 50.

    Args:
        model: Technical model name, e.g. 'res.partner'.
        response_format: 'compact' (default) or 'full'.
    """
    full = resolve_full(response_format)
    conn = get_connection()

    # Look up model in ir.model
    models = conn.search_read(
        "ir.model",
        domain=[("model", "=", model)],
        fields=["id", "name", "model", "info", "state"],
        limit=1,
    )

    if not models:
        return json_response(
            {"found": False, "model": model, "message": f"Model '{model}' not found in ir.model."}
        )

    model_data = models[0]

    # Read every field before computing counts and contributing modules.
    field_data: list[dict[str, Any]] = []
    while True:
        batch = conn.search_read(
            "ir.model.fields",
            domain=[("model", "=", model)],
            fields=["name", "modules", "state"],
            limit=200,
            offset=len(field_data),
            order="id",
        )
        field_data.extend(batch)
        if len(batch) < 200:
            break

    contributing_modules: set[str] = set()
    custom_fields: list[str] = []

    for f in field_data:
        mods = [m.strip() for m in (f.get("modules") or "").split(",") if m.strip()]
        contributing_modules.update(mods)
        if f.get("state") == "manual" or f["name"].startswith("x_"):
            custom_fields.append(f["name"])

    result: dict[str, Any] = {
        "found": True,
        "model": model,
        "name": model_data.get("name"),
        "state": model_data.get("state"),
        "scope": "field_contributors",
        "hierarchy_available": False,
        "hierarchy_note": (
            "Field metadata does not expose _inherit chains or _inherits delegation. "
            "Inspect the model definitions in addon source for those relationships."
        ),
        "total_fields": len(field_data),
        "custom_fields_count": len(custom_fields),
        "custom_fields": custom_fields[:50] if full else custom_fields[:20],
        "custom_fields_truncated": len(custom_fields) > (50 if full else 20),
        "contributing_modules": sorted(contributing_modules),
        "response_format": "full" if full else "compact",
    }

    return json_response(result)
