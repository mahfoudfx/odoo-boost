"""MCP tool: database_query – ORM search_read (safe, goes through access rights)."""

from __future__ import annotations

from odoo_boost.mcp_server.tools.search_records import search_records


def database_query(
    model: str,
    domain: str = "[]",
    fields: str = "[]",
    limit: int = 80,
    offset: int = 0,
    order: str = "",
    compact: bool = False,
) -> str:
    """Compatibility alias for search_records with a larger default limit.

    Use search_records for new calls; both tools perform the same ORM search_read.

    Args:
        model: Technical model name, e.g. 'res.partner'.
        domain: Odoo domain filter as JSON string, e.g. '[["is_company","=",true]]'.
        fields: JSON list of field names to return, e.g. '["name","email"]'. Empty for all.
        limit: Maximum number of records to return (default 80).
        offset: Number of records to skip (default 0).
        order: Sort order, e.g. 'name asc, id desc'.
        compact: When True, strips null/empty fields and truncates bulky strings to save tokens.
    """
    return search_records(
        model=model,
        domain=domain,
        fields=fields,
        limit=limit,
        offset=offset,
        order=order,
        compact=compact,
    )
