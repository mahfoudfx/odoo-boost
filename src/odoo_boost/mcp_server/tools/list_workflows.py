"""MCP tool: list_workflows – base.automation + ir.actions.server."""

from __future__ import annotations

import logging

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import json_response

logger = logging.getLogger(__name__)


def list_workflows(
    model_name: str = "",
    limit: int = 50,
) -> str:
    """List automated actions (base.automation) and server actions (ir.actions.server).

    Args:
        model_name: Filter by model technical name (e.g. 'sale.order').
        limit: Maximum entries per type (default 50).
    """
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
            order="model_name, sequence, name",
        )
        for a in actions:
            server_actions.append(
                {
                    "id": a["id"],
                    "name": a["name"],
                    "model": a.get("model_name", ""),
                    "type": a.get("state", ""),
                    "code_preview": (a.get("code") or "")[:200],
                    "sequence": a.get("sequence", 5),
                }
            )
    except Exception as exc:
        logger.debug("ir.actions.server unavailable: %s", exc)

    result = {
        "model_filter": model_name or "(all)",
        "automated_actions": automations,
        "server_actions": server_actions,
    }
    return json_response(result)
