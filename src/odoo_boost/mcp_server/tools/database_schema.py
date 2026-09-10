"""MCP tool: database_schema – model fields via ir.model / ir.model.fields."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import error_response, json_response


def database_schema(model_name: str) -> str:
    """Get the field definitions (schema) of an Odoo model.

    Args:
        model_name: Technical model name, e.g. 'res.partner'.
    """
    conn = get_connection()

    # Look up the ir.model record
    models = conn.search_read(
        "ir.model",
        [("model", "=", model_name)],
        fields=["id", "name", "model", "info"],
        limit=1,
    )
    if not models:
        return error_response(f"Model '{model_name}' not found.")

    ir_model = models[0]

    # Fetch all fields for this model
    fields = conn.search_read(
        "ir.model.fields",
        [("model_id", "=", ir_model["id"])],
        fields=[
            "name",
            "field_description",
            "ttype",
            "relation",
            "required",
            "readonly",
            "store",
            "index",
            "help",
            "selection_ids",
        ],
        order="name",
    )

    result = {
        "model": ir_model["model"],
        "name": ir_model["name"],
        "info": ir_model.get("info", ""),
        "field_count": len(fields),
        "fields": [
            {
                "name": f["name"],
                "label": f.get("field_description", ""),
                "type": f["ttype"],
                "relation": f.get("relation", False) or None,
                "required": f.get("required", False),
                "readonly": f.get("readonly", False),
                "stored": f.get("store", True),
                "indexed": f.get("index", False),
                "help": f.get("help", False) or None,
            }
            for f in fields
        ],
    }
    return json_response(result)
