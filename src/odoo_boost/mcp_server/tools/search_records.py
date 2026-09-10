"""MCP tool: search_records – search_read on any model with domain/fields/pagination."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import compact_records, json_response, parse_json_arg


def search_records(
    model: str,
    domain: str = "[]",
    fields: str = "[]",
    limit: int = 20,
    offset: int = 0,
    order: str = "",
    compact: bool = False,
) -> str:
    """Search and read records from any Odoo model with domain filtering and pagination.

    Values are returned verbatim by default to preserve data fidelity. Set
    ``compact=true`` to drop empty values and truncate long strings when
    skimming. Always pass ``fields`` to keep responses small.

    Args:
        model: Technical model name, e.g. 'res.partner'.
        domain: Odoo domain filter as JSON string, e.g. '[["is_company","=",true]]'.
        fields: JSON list of field names, e.g. '["name","email"]'. Empty for default fields.
        limit: Maximum records to return (default 20).
        offset: Number of records to skip (default 0).
        order: Sort order, e.g. 'name asc, id desc'.
        compact: Strip empty values and truncate long strings (default false).
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

    total = conn.search_count(model, domain=parsed_domain)

    if compact:
        records = compact_records(records)

    result = {
        "model": model,
        "total_count": total,
        "returned_count": len(records),
        "offset": offset,
        "limit": limit,
        "records": records,
    }
    return json_response(result)
