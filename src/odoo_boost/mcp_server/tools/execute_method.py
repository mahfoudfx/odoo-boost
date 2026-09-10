"""MCP tool: execute_method – call any method on a model (like Tinker)."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.policy import enforce_method
from odoo_boost.mcp_server.tools._common import json_response, parse_json_arg, resolve_full


def execute_method(
    model: str,
    method: str,
    args: str = "[]",
    kwargs: str = "{}",
    response_format: str | None = None,
) -> str:
    """Execute an arbitrary ORM method on an Odoo model.

    This is similar to Laravel's Tinker – it lets you call any public method
    on any model. Use with care. Compact mode enforces the global response
    budget; ``response_format="full"`` returns the uncapped result.

    Args:
        model: Technical model name, e.g. 'res.partner'.
        method: Method name, e.g. 'name_search', 'default_get', 'fields_get'.
        args: Positional arguments as JSON list, e.g. '[[1, 2, 3]]' for record IDs.
        kwargs: Keyword arguments as JSON object, e.g. '{"fields": ["name"]}'.
        response_format: 'compact' (default) or 'full' (uncapped).
    """
    enforce_method(method)

    conn = get_connection()

    try:
        parsed_args = parse_json_arg(args, default=[])
        parsed_kwargs = parse_json_arg(kwargs, default={})
    except ValueError as exc:
        return json_response({"error": str(exc), "model": model, "method": method})

    result = conn.execute(model, method, *parsed_args, **parsed_kwargs)

    return json_response(
        {"model": model, "method": method, "result": result},
        bypass_budget=resolve_full(response_format),
    )
