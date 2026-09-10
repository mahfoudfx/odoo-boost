"""MCP tool: read_log_entries – ir.logging entries (if log_db configured)."""

from __future__ import annotations

import logging

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import (
    compact_text,
    error_response,
    json_response,
    resolve_full,
)

logger = logging.getLogger(__name__)


def read_log_entries(
    level: str = "",
    func: str = "",
    limit: int = 20,
    offset: int = 0,
    entry_id: int = 0,
    response_format: str | None = None,
) -> str:
    """Read Odoo log entries from ir.logging (requires log_db to be configured).

    Compact mode truncates long messages; ``response_format="full"`` returns
    them verbatim. Use ``entry_id`` to fetch one specific entry.

    Args:
        level: Filter by log level (e.g. 'WARNING', 'ERROR', 'CRITICAL').
        func: Filter by function name substring.
        limit: Maximum entries to return (default 20).
        offset: Number of entries to skip (default 0).
        entry_id: Fetch a single log entry by ID.
        response_format: 'compact' (default) or 'full'.
    """
    full = resolve_full(response_format)
    message_max = 0 if full else 500

    conn = get_connection()

    domain: list = []
    if level:
        domain.append(("level", "=", level.upper()))
    if func:
        domain.append(("func", "ilike", func))
    if entry_id:
        domain.append(("id", "=", entry_id))

    try:
        logs = conn.search_read(
            "ir.logging",
            domain=domain,
            fields=["create_date", "name", "level", "dbname", "func", "path", "line", "message"],
            limit=limit,
            offset=offset,
            order="create_date desc",
        )
    except Exception as exc:
        logger.debug("Cannot read ir.logging: %s", exc)
        return error_response(
            f"Cannot read ir.logging: {exc}. Ensure log_db is configured in odoo.conf."
        )

    entries = []
    for entry in logs:
        message = entry.get("message", "") or ""
        entries.append(
            {
                "timestamp": entry.get("create_date", ""),
                "level": entry.get("level", ""),
                "name": entry.get("name", ""),
                "function": entry.get("func", ""),
                "path": entry.get("path", ""),
                "line": entry.get("line", ""),
                "message": compact_text(message, message_max),
                "message_length": len(message),
            }
        )

    result = {
        "total": len(entries),
        "offset": offset,
        "limit": limit,
        "response_format": "full" if full else "compact",
        "entries": entries,
    }
    return json_response(result)
