"""MCP tool: database_query – ORM search_read (safe, goes through access rights)."""

from __future__ import annotations

import json

from odoo_boost.mcp_server.context import get_connection


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

    parsed_domain = json.loads(domain) if domain else []
    parsed_fields = json.loads(fields) if fields else []

    records = conn.search_read(
        model,
        domain=parsed_domain,
        fields=parsed_fields or None,
        limit=limit,
        offset=offset,
        order=order or None,
    )

    if compact and isinstance(records, list):
        cleaned_records = []
        for rec in records:
            clean_rec = {}
            for k, v in rec.items():
                if v is None or v is False or v == "":
                    continue
                if isinstance(v, str) and len(v) > 100:
                    clean_rec[k] = f"{v[:97]}..."
                else:
                    clean_rec[k] = v
            cleaned_records.append(clean_rec)
        records = cleaned_records

    total = conn.search_count(model, domain=parsed_domain)

    result = {
        "model": model,
        "total_count": total,
        "returned_count": len(records),
        "offset": offset,
        "limit": limit,
        "records": records,
    }
    return json.dumps(result, indent=2, default=str)
