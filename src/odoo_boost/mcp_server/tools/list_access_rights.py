"""MCP tool: list_access_rights – ir.model.access + ir.rule."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import compact_text, json_response, resolve_full


def _m2o_name(value: object) -> str:
    if isinstance(value, list) and len(value) > 1:
        return str(value[1])
    return str(value or "")


def list_access_rights(
    model_name: str = "",
    limit: int = 50,
    offset: int = 0,
    response_format: str | None = None,
) -> str:
    """List access rights (ir.model.access) and record rules (ir.rule) for a model.

    Compact mode truncates record-rule domains when no model filter is given
    (they can be long); a model-specific query keeps them complete.

    Args:
        model_name: Filter by model technical name (e.g. 'res.partner').
        limit: Maximum number of entries to return per type (default 50).
        offset: Number of entries to skip per type (default 0).
        response_format: 'compact' (default) or 'full'.
    """
    full = resolve_full(response_format)
    conn = get_connection()

    # --- ACL (ir.model.access) ---
    acl_domain: list = []
    if model_name:
        acl_domain.append(("model_id.model", "=", model_name))

    acl_total = conn.search_count("ir.model.access", acl_domain)
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
        offset=offset,
        order="model_id, name",
    )

    # --- Record rules (ir.rule) ---
    rule_domain: list = []
    if model_name:
        rule_domain.append(("model_id.model", "=", model_name))

    rule_total = conn.search_count("ir.rule", rule_domain)
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
        offset=offset,
        order="model_id, name",
    )

    # Domains are most useful in full when scoped to a single model; truncate
    # them for broad, unfiltered listings.
    truncate_domain = not full and not model_name

    result = {
        "model_filter": model_name or "(all)",
        "response_format": "full" if full else "compact",
        "offset": offset,
        "limit": limit,
        "access_rights_total": acl_total,
        "access_rights_returned": len(acls),
        "record_rules_total": rule_total,
        "record_rules_returned": len(rules),
        "access_rights": [
            {
                "name": a["name"],
                "model": _m2o_name(a.get("model_id")),
                "group": _m2o_name(a.get("group_id")),
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
                "model": _m2o_name(r.get("model_id")),
                "domain": compact_text(r.get("domain_force", ""), 120)
                if truncate_domain
                else r.get("domain_force", ""),
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
