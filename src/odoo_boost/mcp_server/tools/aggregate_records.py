"""MCP tool: aggregate_records – ORM read_group aggregation for token-efficient metrics."""

from __future__ import annotations

import json

from odoo_boost.mcp_server.context import get_connection


def aggregate_records(
    model: str,
    domain: str = "[]",
    fields: str = "[]",
    groupby: str = "[]",
    limit: int = 80,
    offset: int = 0,
    orderby: str = "",
) -> str:
    """Execute an ORM read_group on an Odoo model for aggregated grouping and metrics.

    Args:
        model: Technical model name, e.g. 'sale.order'.
        domain: Odoo domain filter as JSON string, e.g. '[["state", "=", "sale"]]'.
        fields: JSON list of field names to aggregate, e.g. '["amount_total:sum"]'.
        groupby: JSON list of field names to group by, e.g. '["partner_id", "date_order:month"]'.
        limit: Maximum number of groups to return (default 80).
        offset: Number of groups to skip (default 0).
        orderby: Sort order for groups, e.g. 'amount_total desc'.
    """
    conn = get_connection()

    parsed_domain = json.loads(domain) if domain else []
    parsed_fields = json.loads(fields) if fields else []
    parsed_groupby = json.loads(groupby) if groupby else []

    try:
        groups = conn.execute(
            model,
            "read_group",
            parsed_domain,
            parsed_fields,
            parsed_groupby,
            offset,
            limit,
            orderby or False,
        )
    except Exception as exc:
        return json.dumps({"error": str(exc), "model": model}, indent=2)

    result = {
        "model": model,
        "groupby": parsed_groupby,
        "returned_groups": len(groups),
        "offset": offset,
        "limit": limit,
        "groups": groups,
    }
    return json.dumps(result, indent=2, default=str)
