"""MCP tool: list_workflows – base.automation + ir.actions.server."""

from __future__ import annotations

import logging

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import compact_text, json_response, resolve_full

logger = logging.getLogger(__name__)


def list_workflows(
    model_name: str = "",
    limit: int = 25,
    offset: int = 0,
    response_format: str | None = None,
) -> str:
    """List automated actions (base.automation) and server actions (ir.actions.server).

    Compact mode returns a truncated code preview; ``response_format="full"``
    returns the complete server-action code.

    Args:
        model_name: Filter by model technical name (e.g. 'sale.order').
        limit: Maximum entries per type (default 25).
        offset: Number of entries to skip per type (default 0).
        response_format: 'compact' (default) or 'full'.
    """
    full = resolve_full(response_format)
    conn = get_connection()

    automations: list[dict] = []
    server_actions: list[dict] = []

    # 1. base.automation (automated actions)
    try:
        auto_domain: list = []
        if model_name:
            auto_domain.append(("model_name", "=", model_name))

        autos = conn.search_read(
            "base.automation",
            domain=auto_domain,
            fields=["name", "model_name", "trigger", "active", "action_server_ids"],
            limit=limit,
            offset=offset,
            order="model_name, name",
        )
        for a in autos:
            automations.append(
                {
                    "id": a["id"],
                    "name": a["name"],
                    "model": a.get("model_name", ""),
                    "trigger": a.get("trigger", ""),
                    "active": a.get("active", True),
                    "server_action_count": len(a.get("action_server_ids", [])),
                }
            )
    except Exception as exc:  # base_automation module may not be installed
        logger.debug("base.automation unavailable: %s", exc)

    # 2. ir.actions.server
    sa_domain: list = []
    if model_name:
        sa_domain.append(("model_name", "=", model_name))

    try:
        actions = conn.search_read(
            "ir.actions.server",
            domain=sa_domain,
            fields=["name", "model_name", "state", "code", "sequence"],
            limit=limit,
            offset=offset,
            order="model_name, sequence, name",
        )
        for a in actions:
            code = a.get("code") or ""
            entry = {
                "id": a["id"],
                "name": a["name"],
                "model": a.get("model_name", ""),
                "type": a.get("state", ""),
                "sequence": a.get("sequence", 5),
            }
            if full:
                entry["code"] = code
            else:
                entry["code_preview"] = compact_text(code, 120)
                entry["code_length"] = len(code)
            server_actions.append(entry)
    except Exception as exc:
        logger.debug("ir.actions.server unavailable: %s", exc)

    result = {
        "model_filter": model_name or "(all)",
        "offset": offset,
        "limit": limit,
        "response_format": "full" if full else "compact",
        "automated_actions": automations,
        "server_actions": server_actions,
    }
    return json_response(result)
