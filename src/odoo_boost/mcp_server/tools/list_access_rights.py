"""MCP tool: list_access_rights – ir.model.access + ir.rule."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import json_response


def list_access_rights(
    model_name: str = "",
    limit: int = 100,
) -> str:
    """List access rights (ir.model.access) and record rules (ir.rule) for a model.

    Args:
        model_name: Filter by model technical name (e.g. 'res.partner').
        limit: Maximum number of entries to return per type (default 100).
    """
    conn = get_connection()

    # --- ACL (ir.model.access) ---
    acl_domain: list = []
    if model_name:
        acl_domain.append(("model_id.model", "=", model_name))

    acls = conn.search_read(
        "ir.model.access",
        domain=acl_domain,
        fields=[
            "name",
            "model_id",
            "group_id",
            "perm_read",
            "perm_write",
            "perm_create",
            "perm_unlink",
        ],
        limit=limit,
        order="model_id, name",
    )

    # --- Record rules (ir.rule) ---
    rule_domain: list = []
    if model_name:
        rule_domain.append(("model_id.model", "=", model_name))

    rules = conn.search_read(
        "ir.rule",
        domain=rule_domain,
        fields=[
            "name",
            "model_id",
            "groups",
            "domain_force",
            "perm_read",
            "perm_write",
            "perm_create",
            "perm_unlink",
            "global",
        ],
        limit=limit,
        order="model_id, name",
    )

    result = {
        "model_filter": model_name or "(all)",
        "access_rights": [
            {
                "name": a["name"],
                "model": a.get("model_id", [False, ""])[1]
                if isinstance(a.get("model_id"), list)
                else str(a.get("model_id", "")),
                "group": a.get("group_id", [False, ""])[1]
                if isinstance(a.get("group_id"), list)
                else str(a.get("group_id", "")),
                "read": a.get("perm_read", False),
                "write": a.get("perm_write", False),
                "create": a.get("perm_create", False),
                "unlink": a.get("perm_unlink", False),
            }
            for a in acls
        ],
        "record_rules": [
            {
                "name": r["name"],
                "model": r.get("model_id", [False, ""])[1]
                if isinstance(r.get("model_id"), list)
                else str(r.get("model_id", "")),
                "domain": r.get("domain_force", ""),
                "global": r.get("global", False),
                "read": r.get("perm_read", False),
                "write": r.get("perm_write", False),
                "create": r.get("perm_create", False),
                "unlink": r.get("perm_unlink", False),
            }
            for r in rules
        ],
    }
    return json_response(result)
