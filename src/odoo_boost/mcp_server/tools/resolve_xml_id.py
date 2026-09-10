"""MCP tool: resolve_xml_id – look up external ID (ir.model.data) in the live database."""

from __future__ import annotations

import logging

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import json_response

logger = logging.getLogger(__name__)


def resolve_xml_id(xml_id: str) -> str:
    """Resolve an external XML ID (e.g. 'base.partner_admin') to its model and database ID.

    Args:
        xml_id: Fully qualified XML ID, e.g. 'base.group_user' or 'sale.action_orders'.
    """
    conn = get_connection()

    if "." in xml_id:
        module, name = xml_id.split(".", 1)
        domain = [("module", "=", module), ("name", "=", name)]
    else:
        domain = [("name", "=", xml_id)]

    records = conn.search_read(
        "ir.model.data",
        domain=domain,
        fields=["module", "name", "model", "res_id", "noupdate"],
        limit=10,
    )

    if not records:
        return json_response(
            {
                "found": False,
                "xml_id": xml_id,
                "message": f"External ID '{xml_id}' not found in ir.model.data.",
            }
        )

    item = records[0]
    result = {
        "found": True,
        "xml_id": f"{item['module']}.{item['name']}",
        "module": item["module"],
        "name": item["name"],
        "model": item["model"],
        "res_id": item["res_id"],
        "noupdate": item.get("noupdate", False),
    }

    # If the target record exists, try to get its display name
    if item.get("model") and item.get("res_id"):
        try:
            target_data = conn.search_read(
                item["model"],
                domain=[("id", "=", item["res_id"])],
                fields=["display_name"]
                if conn.search_count(
                    "ir.model.fields",
                    [("model", "=", item["model"]), ("name", "=", "display_name")],
                )
                else ["name"],
                limit=1,
            )
            if target_data:
                result["target_record"] = target_data[0]
        except Exception as exc:
            logger.debug("Could not resolve display name for %s: %s", item.get("model"), exc)

    return json_response(result)
