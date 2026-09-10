"""MCP tool: inspect_local_addon – scan local addon code on disk."""

from __future__ import annotations

from odoo_boost.ast_scanner.analyzer import find_local_xml_id, scan_addon
from odoo_boost.mcp_server.policy import enforce_path
from odoo_boost.mcp_server.tools._common import error_response, json_response, resolve_full


def _model_summary(model: dict) -> dict:
    """Return a compact description of a scanned model without field details."""
    return {
        "_name": model.get("_name"),
        "_inherit": model.get("_inherit"),
        "class_name": model.get("class_name"),
        "file": model.get("file"),
        "line": model.get("line"),
        "field_count": len(model.get("fields", {})),
        "method_count": len(model.get("methods", [])),
    }


def inspect_local_addon(
    addon_path: str,
    model: str = "",
    xml_id: str = "",
    response_format: str | None = None,
) -> str:
    """Analyze a local Odoo addon directory on disk without requiring database installation.

    Compact mode returns a summary (manifest, counts, and per-model field/method
    counts) instead of the entire scan. Use ``response_format="full"`` for every
    field, method, view, and record. Use ``model=`` or ``xml_id=`` to fetch a
    single definition directly.

    Args:
        addon_path: Absolute or relative path to the local addon directory.
        model: Optional technical model name to return in full detail.
        xml_id: Optional XML ID to locate in the addon's XML files.
        response_format: 'compact' (default) or 'full'.
    """
    full = resolve_full(response_format)

    path = enforce_path(addon_path)
    if not path.exists():
        return error_response(f"Path '{addon_path}' does not exist.")

    if xml_id:
        found = find_local_xml_id(path, xml_id)
        if not found:
            return json_response(
                {
                    "found": False,
                    "xml_id": xml_id,
                    "message": f"XML ID '{xml_id}' not found under '{addon_path}'.",
                }
            )
        return json_response({"found": True, "xml_id": xml_id, "definition": found})

    scanned = scan_addon(path)

    if model:
        matches = [
            m
            for m in scanned.get("models", [])
            if m.get("_name") == model or m.get("_inherit") == model
        ]
        return json_response({"model": model, "found": bool(matches), "definitions": matches})

    if full:
        return json_response({**scanned, "response_format": "full"})

    result = {
        "addon_name": scanned.get("addon_name"),
        "path": scanned.get("path"),
        "response_format": "compact",
        "manifest": scanned.get("manifest"),
        "python_files_count": scanned.get("python_files_count", 0),
        "xml_files_count": scanned.get("xml_files_count", 0),
        "counts": {
            "models": len(scanned.get("models", [])),
            "records": len(scanned.get("records", [])),
            "templates": len(scanned.get("templates", [])),
            "menuitems": len(scanned.get("menuitems", [])),
        },
        "models": [_model_summary(m) for m in scanned.get("models", [])],
    }
    return json_response(result)
