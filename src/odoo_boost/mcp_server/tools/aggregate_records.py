"""MCP tool: aggregate_records – ORM read_group aggregation for token-efficient metrics."""

from __future__ import annotations

from typing import Any

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import (
    error_response,
    json_response,
    parse_json_arg,
    resolve_full,
)


def _drop_empty_groups(groups: Any) -> tuple[list, int]:
    """Drop groups whose values are all falsy (zero/None measures)."""
    if not isinstance(groups, list):
        return groups, 0
    kept = [
        group
        for group in groups
        if not isinstance(group, dict) or any(bool(value) for value in group.values())
    ]
    return kept, len(groups) - len(kept)


def aggregate_records(
    model: str,
    domain: str = "[]",
    fields: str = "[]",
    groupby: str = "[]",
    limit: int = 80,
    offset: int = 0,
    orderby: str = "",
    response_format: str | None = None,
) -> str:
    """Execute an ORM read_group on an Odoo model for aggregated grouping and metrics.

    Compact mode drops groups whose measures are all zero/empty; use
    ``response_format="full"`` to keep every returned group.

    Args:
        model: Technical model name, e.g. 'sale.order'.
        domain: Odoo domain filter as JSON string, e.g. '[["state", "=", "sale"]]'.
        fields: JSON list of field names to aggregate, e.g. '["amount_total:sum"]'.
        groupby: JSON list of field names to group by, e.g. '["partner_id", "date_order:month"]'.
        limit: Maximum number of groups to return (default 80).
        offset: Number of groups to skip (default 0).
        orderby: Sort order for groups, e.g. 'amount_total desc'.
        response_format: 'compact' (default) or 'full'.
    """
    full = resolve_full(response_format)
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

    dropped = 0
    if not full:
        groups, dropped = _drop_empty_groups(groups)

    result = {
        "model": model,
        "groupby": parsed_groupby,
        "returned_groups": len(groups) if isinstance(groups, list) else groups,
        "dropped_empty_groups": dropped,
        "offset": offset,
        "limit": limit,
        "response_format": "full" if full else "compact",
        "groups": groups,
    }
    return json_response(result)
