"""MCP tool: read_log_entries – ir.logging entries (if log_db configured)."""

from __future__ import annotations

import logging

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import error_response, json_response

logger = logging.getLogger(__name__)


def read_log_entries(
    level: str = "",
    func: str = "",
    limit: int = 50,
) -> str:
    """Read Odoo log entries from ir.logging (requires log_db to be configured).

    Args:
        level: Filter by log level (e.g. 'WARNING', 'ERROR', 'CRITICAL').
        func: Filter by function name substring.
        limit: Maximum entries to return (default 50).
    """
    conn = get_connection()

    domain: list = []
    if level:
        domain.append(("level", "=", level.upper()))
    if func:
        domain.append(("func", "ilike", func))

    try:
        logs = conn.search_read(
            "ir.logging",
            domain=domain,
            fields=["create_date", "name", "level", "dbname", "func", "path", "line", "message"],
            limit=limit,
            order="create_date desc",
        )
    except Exception as exc:
        logger.debug("Cannot read ir.logging: %s", exc)
        return error_response(
            f"Cannot read ir.logging: {exc}. Ensure log_db is configured in odoo.conf."
        )

    result = {
        "total": len(logs),
        "entries": [
            {
                "timestamp": entry.get("create_date", ""),
                "level": entry.get("level", ""),
                "name": entry.get("name", ""),
                "function": entry.get("func", ""),
                "path": entry.get("path", ""),
                "line": entry.get("line", ""),
                "message": entry.get("message", ""),
            }
            for entry in logs
        ],
    }
    return json_response(result)
