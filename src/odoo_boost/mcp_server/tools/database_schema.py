"""MCP tool: database_schema – model fields via ir.model / ir.model.fields."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import error_response, json_response, resolve_full


def database_schema(
    model_name: str,
    field_name: str = "",
    ttype: str = "",
    limit: int = 0,
    offset: int = 0,
    include_help: bool | None = None,
    response_format: str | None = None,
) -> str:
    """Get the field definitions (schema) of an Odoo model.

    Compact mode returns the fields needed to write code (name, type, relation,
    flags). Labels, help texts, and index info are only included with
    ``response_format="full"`` (or ``include_help=true``).

    Args:
        model_name: Technical model name, e.g. 'res.partner'.
        field_name: Optional substring filter on the field name.
        ttype: Optional exact field type filter (e.g. 'many2one').
        limit: Maximum fields to return (0 = all, default).
        offset: Number of fields to skip (default 0).
        include_help: Include label/help/indexed metadata (defaults to full mode).
        response_format: 'compact' (default) or 'full'.
    """
    full = resolve_full(response_format)
    if include_help is None:
        include_help = full

    conn = get_connection()

    models = conn.search_read(
        "ir.model",
        [("model", "=", model_name)],
        fields=["id", "name", "model", "info"],
        limit=1,
    )
    if not models:
        return error_response(f"Model '{model_name}' not found.")

    ir_model = models[0]

    domain: list = [("model_id", "=", ir_model["id"])]
    if field_name:
        domain.append(("name", "ilike", field_name))
    if ttype:
        domain.append(("ttype", "=", ttype))

    total = conn.search_count("ir.model.fields", domain)
    fields = conn.search_read(
        "ir.model.fields",
        domain=domain,
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
        ],
        limit=limit or None,
        offset=offset,
        order="name",
    )

    rendered = []
    for f in fields:
        entry = {
            "name": f["name"],
            "type": f["ttype"],
            "relation": f.get("relation", False) or None,
            "required": f.get("required", False),
            "readonly": f.get("readonly", False),
            "stored": f.get("store", True),
        }
        if include_help:
            entry["label"] = f.get("field_description", "")
            entry["indexed"] = f.get("index", False)
            entry["help"] = f.get("help", False) or None
        rendered.append(entry)

    result = {
        "model": ir_model["model"],
        "name": ir_model["name"],
        "info": ir_model.get("info", ""),
        "field_count": total,
        "returned": len(rendered),
        "offset": offset,
        "limit": limit,
        "included_help": include_help,
        "response_format": "full" if full else "compact",
        "fields": rendered,
    }
    return json_response(result)
