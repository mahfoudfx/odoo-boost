"""MCP tool: get_module_info – detailed module info, dependencies, models."""

from __future__ import annotations

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import error_response, json_response


def get_module_info(module_name: str) -> str:
    """Get detailed information about an Odoo module including dependencies and models.

    Args:
        module_name: Technical module name, e.g. 'sale' or 'account'.
    """
    conn = get_connection()

    # Module record
    modules = conn.search_read(
        "ir.module.module",
        [("name", "=", module_name)],
        fields=[
            "name",
            "shortdesc",
            "summary",
            "description",
            "author",
            "website",
            "installed_version",
            "state",
            "category_id",
            "license",
            "application",
        ],
        limit=1,
    )
    if not modules:
        return error_response(f"Module '{module_name}' not found.")

    mod = modules[0]

    # Dependencies
    deps = conn.search_read(
        "ir.module.module.dependency",
        [("module_id.name", "=", module_name)],
        fields=["name", "auto_install_required"],
    )

    # Models provided by this module.
    # The `modules` field on ir.model is not stored in Odoo 19+, so we
    # look up ir.model.data for model registrations from this module.
    model_data = conn.search_read(
        "ir.model.data",
        [("module", "=", module_name), ("model", "=", "ir.model")],
        fields=["res_id"],
    )
    model_ids = [d["res_id"] for d in model_data]
    if model_ids:
        models = conn.search_read(
            "ir.model",
            [("id", "in", model_ids)],
            fields=["model", "name"],
            order="model",
        )
    else:
        models = []

    result = {
        "name": mod["name"],
        "title": mod.get("shortdesc", ""),
        "summary": mod.get("summary", ""),
        "author": mod.get("author", ""),
        "website": mod.get("website", ""),
        "version": mod.get("installed_version", ""),
        "state": mod.get("state", ""),
        "category": mod.get("category_id", [False, ""])[1]
        if isinstance(mod.get("category_id"), list)
        else str(mod.get("category_id", "")),
        "license": mod.get("license", ""),
        "application": mod.get("application", False),
        "dependencies": [
            {"name": d["name"], "auto_install_required": d.get("auto_install_required", False)}
            for d in deps
        ],
        "models": [{"model": m["model"], "name": m["name"]} for m in models],
    }
    return json_response(result)
