"""MCP tool: resolve_local_xml_id – look up an XML ID in local source files on disk."""

from __future__ import annotations

import json
from pathlib import Path

from odoo_boost.ast_scanner.analyzer import find_local_xml_id


def resolve_local_xml_id(addon_path: str, xml_id: str) -> str:
    """Find the exact file and definition for an XML ID in a local addon directory on disk.

    Args:
        addon_path: Path to the local addon directory.
        xml_id: XML ID to locate (e.g. 'view_partner_form' or 'my_module.view_partner_form').
    """
    path = Path(addon_path)
    if not path.is_absolute():
        path = (Path.cwd() / path).resolve()

    if not path.exists():
        return json.dumps({"error": f"Path '{addon_path}' does not exist."}, indent=2)

    found = find_local_xml_id(path, xml_id)
    if not found:
        return json.dumps(
            {
                "found": False,
                "xml_id": xml_id,
                "message": f"XML ID '{xml_id}' not found in local files under '{addon_path}'.",
            },
            indent=2,
        )

    return json.dumps({"found": True, "xml_id": xml_id, "definition": found}, indent=2)
