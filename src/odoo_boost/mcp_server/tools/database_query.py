"""MCP tool: database_query – ORM search_read (safe, goes through access rights)."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import (
    compact_records,
    json_response,
    parse_json_arg,
)


def database_query(
    model: str,
    domain: str = "[]",
    fields: str = "[]",
    limit: int = 80,
    offset: int = 0,
    order: str = "",
    compact: bool = False,
) -> str:
    """Execute an ORM search_read on any Odoo model (safe, respects access rights).

    Args:
        model: Technical model name, e.g. 'res.partner'.
        domain: Odoo domain filter as JSON string, e.g. '[["is_company","=",true]]'.
        fields: JSON list of field names to return, e.g. '["name","email"]'. Empty for all.
        limit: Maximum number of records to return (default 80).
        offset: Number of records to skip (default 0).
        order: Sort order, e.g. 'name asc, id desc'.
        compact: When True, strips null/empty fields and truncates bulky strings to save tokens.
    """
    conn = get_connection()

    try:
        parsed_domain = parse_json_arg(domain, default=[])
        parsed_fields = parse_json_arg(fields, default=[])
    except ValueError as exc:
        return json_response({"error": str(exc), "model": model})

    records = conn.search_read(
        model,
        domain=parsed_domain,
        fields=parsed_fields or None,
        limit=limit,
        offset=offset,
        order=order or None,
    )

    if compact:
        records = compact_records(records)

    total = conn.search_count(model, domain=parsed_domain)

    result = {
        "model": model,
        "total_count": total,
        "returned_count": len(records),
        "offset": offset,
        "limit": limit,
        "records": records,
    }
    return json_response(result)
