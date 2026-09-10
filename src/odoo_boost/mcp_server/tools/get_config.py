"""MCP tool: get_config – ir.config_parameter values."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import (
    active_config,
    compact_text,
    is_secret_key,
    json_response,
    redact,
    resolve_full,
)


def get_config(
    key: str = "",
    limit: int = 20,
    offset: int = 0,
    match: str = "ilike",
    reveal_secrets: bool | None = None,
    value_max_chars: int | None = None,
    response_format: str | None = None,
) -> str:
    """Get Odoo system configuration parameters (ir.config_parameter).

    Compact mode truncates long values and redacts secret-looking keys.
    ``response_format="full"`` removes the truncation; secrets still require
    ``reveal_secrets=true`` (or disabling ``redact_config_secrets``).

    Args:
        key: Key filter. Empty returns all.
        limit: Maximum parameters to return (default 20).
        offset: Number of parameters to skip (default 0).
        match: 'ilike' (substring, default) or 'exact'.
        reveal_secrets: Return secret values unredacted (default false).
        value_max_chars: Truncate values to this length (0 = no truncation).
        response_format: 'compact' (default) or 'full'.
    """
    full = resolve_full(response_format)

    config = active_config()
    if reveal_secrets is None:
        reveal_secrets = not (config.redact_config_secrets if config else True)
    if value_max_chars is None:
        value_max_chars = 0 if full else 200

    conn = get_connection()

    domain: list = []
    if key:
        domain.append(("key", "=" if match == "exact" else "ilike", key))

    total = conn.search_count("ir.config_parameter", domain)
    params = conn.search_read(
        "ir.config_parameter",
        domain=domain,
        fields=["key", "value"],
        limit=limit,
        offset=offset,
        order="key",
    )

    rendered = []
    for p in params:
        raw_value = p.get("value", "") or ""
        reveal_value = reveal_secrets or not is_secret_key(p["key"])
        value, was_redacted = redact(raw_value, reveal=reveal_value)
        if not was_redacted:
            value = compact_text(value, value_max_chars)
        rendered.append(
            {
                "key": p["key"],
                "value": value,
                "value_length": len(raw_value),
                "redacted": was_redacted,
            }
        )

    result = {
        "total": total,
        "returned": len(rendered),
        "offset": offset,
        "limit": limit,
        "response_format": "full" if full else "compact",
        "parameters": rendered,
    }
    return json_response(result)
