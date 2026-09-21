"""Count matching records without reading payloads or making a second RPC call."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import error_response, json_response, parse_json_arg


def count_records(model: str, domain: str = "[]") -> str:
    """Count accessible records with an ORM domain; use when only existence or size matters.

    This makes one read-only `search_count` call. Use `search_records` when record
    values are needed. Odoo access rights and record rules still apply.

    Args:
        model: Technical model name, e.g. 'sale.order'.
        domain: JSON Odoo domain list, e.g. '[["state", "=", "sale"]]'.
    """
    try:
        parsed_domain = parse_json_arg(domain, default=[])
    except ValueError as exc:
        return error_response(str(exc), model=model)
    if not isinstance(parsed_domain, list):
        return error_response("Domain must be a JSON list.", model=model)
    return json_response(
        {"model": model, "count": get_connection().search_count(model, parsed_domain)}
    )
