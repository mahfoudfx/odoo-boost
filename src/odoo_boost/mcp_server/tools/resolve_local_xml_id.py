"""MCP tool: resolve_local_xml_id – look up an XML ID in local source files on disk."""

from __future__ import annotations

from odoo_boost.ast_scanner.analyzer import find_local_xml_id
from odoo_boost.mcp_server.policy import enforce_path
from odoo_boost.mcp_server.tools._common import error_response, json_response


def resolve_local_xml_id(addon_path: str, xml_id: str) -> str:
    """Find the exact file and definition for an XML ID in a local addon directory on disk.

    Args:
        addon_path: Path to the local addon directory.
        xml_id: XML ID to locate (e.g. 'view_partner_form' or 'my_module.view_partner_form').
    """
    path = enforce_path(addon_path)

    if not path.exists():
        return error_response(f"Path '{addon_path}' does not exist.")

    found = find_local_xml_id(path, xml_id)
    if not found:
        return json_response(
            {
                "found": False,
                "xml_id": xml_id,
                "message": f"XML ID '{xml_id}' not found in local files under '{addon_path}'.",
            }
        )

    return json_response({"found": True, "xml_id": xml_id, "definition": found})
