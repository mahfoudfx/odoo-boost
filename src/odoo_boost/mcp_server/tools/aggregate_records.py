"""MCP tool: aggregate_records – ORM read_group aggregation for token-efficient metrics."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import (
    error_response,
    json_response,
    parse_json_arg,
)


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

    try:
        parsed_domain = parse_json_arg(domain, default=[])
        parsed_fields = parse_json_arg(fields, default=[])
        parsed_groupby = parse_json_arg(groupby, default=[])
    except ValueError as exc:
        return error_response(str(exc), model=model)

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
        return error_response(str(exc), model=model)

    result = {
        "model": model,
        "groupby": parsed_groupby,
        "returned_groups": len(groups),
        "offset": offset,
        "limit": limit,
        "groups": groups,
    }
    return json_response(result)
