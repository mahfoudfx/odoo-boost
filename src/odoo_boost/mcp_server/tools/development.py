"""Focused development workflows exposed through MCP."""

from __future__ import annotations

import importlib.util
from pathlib import Path

from odoo_boost.mcp_server.context import active_config, get_connection, get_context
from odoo_boost.mcp_server.policy import enforce_path
from odoo_boost.mcp_server.tools._common import json_response
from odoo_boost.source_trace import source_index
from odoo_boost.validation import diagnose, validation_plan


def trace_odoo_source(path: str, model: str = "", method: str = "") -> str:
    """Find model inheritance/delegation, methods and view parents in local source. No runtime MRO guarantee."""
    index = source_index(enforce_path(path))
    if model:
        # Follow parent declarations transitively without claiming an effective MRO.
        wanted = {model}
        selected: list[dict] = []
        while True:
            before = len(wanted)
            selected = []
            for item in index["models"]:
                parents = item.get("inherit") or []
                if isinstance(parents, str):
                    parents = [parents]
                delegated = item.get("inherits") or {}
                name = item.get("name")
                # In-place extensions belong to their inherited model; prototype
                # children do not become ancestors merely by inheriting it.
                own = {name} if name else set(parents)
                if own & wanted:
                    selected.append(item)
                    wanted.update(parents)
                    wanted.update(delegated)
            if len(wanted) == before:
                break
        index["models"] = selected
        index["views"] = [v for v in index["views"] if v["model"] in wanted]
        declared = {m["name"] for m in selected if m["name"]}
        index["unresolved_models"] = sorted(wanted - declared)
    if method:
        index["models"] = [
            m for m in index["models"] if any(n["name"] == method for n in m["methods"])
        ]
    index.pop("routes")
    return json_response(index)


def list_controller_routes(path: str, filter_url: str = "") -> str:
    """Discover Python @route declarations and route overrides in local controller source."""
    index = source_index(enforce_path(path))
    return json_response(
        {
            "routes": [r for r in index["routes"] if filter_url in str(r["routes"])],
            "errors": index["errors"],
            "complete": index["complete"],
            "limitation": index["limitation"],
        }
    )


def diagnose_odoo_code(path: str, include_odoo_ls: bool = False) -> str:
    """Combine static, pylint and optional Odoo LS checks, with explicit coverage and deduplicated findings."""
    target = enforce_path(path)
    if target.is_dir():
        for source in target.rglob("*"):
            if source.is_file() and source.suffix in {".py", ".xml", ".csv"}:
                enforce_path(str(source))
    config = active_config()
    return json_response(diagnose(target, config.odoo_version if config else None, include_odoo_ls))


def plan_changed_checks(path: str = ".", base: str = "HEAD") -> str:
    """Recommend focused checks from git changes, including staged and untracked files; does not execute checks."""
    return json_response(validation_plan(enforce_path(path), base))


def compare_local_runtime(addon_path: str, model: str) -> str:
    """Compare locally declared field names with runtime fields; inherited runtime extras are informational."""
    from odoo_boost.ast_scanner.analyzer import model_matches, scan_addon

    scanned = scan_addon(enforce_path(addon_path))
    definitions = [m for m in scanned.get("models", []) if model_matches(m, model)]
    if not definitions:
        return json_response(
            {"status": "unavailable", "message": "No local model declaration matched."}
        )
    local = {name for m in definitions for name in m.get("fields", {})}
    conn = get_connection()
    runtime = set(conn.execute(model, "fields_get"))
    addon_name = Path(addon_path).resolve().name
    xml_names = {
        r.get("id")
        for group in ("records", "templates", "menuitems")
        for r in scanned.get(group, [])
        if r.get("id")
    }
    xml_names = {
        name.split(".", 1)[1] if name.startswith(addon_name + ".") else name
        for name in xml_names
        if "." not in name or name.startswith(addon_name + ".")
    }
    present: set[str] = set()
    names = sorted(xml_names)
    for offset in range(0, len(names), 100):
        batch = conn.search_read(
            "ir.model.data",
            domain=[("module", "=", addon_name), ("name", "in", names[offset : offset + 100])],
            fields=["name"],
            limit=100,
        )
        present.update(row["name"] for row in batch)
    modules = conn.search_read(
        "ir.module.module",
        domain=[("name", "=", addon_name)],
        fields=["name", "state", "installed_version"],
        limit=1,
    )
    return json_response(
        {
            "model": model,
            "local_fields_missing_at_runtime": sorted(local - runtime),
            "runtime_fields_not_declared_here": sorted(runtime - local),
            "local_xml_ids_missing_at_runtime": sorted(xml_names - present),
            "local_manifest_version": (scanned.get("manifest") or {}).get("version"),
            "runtime_module": modules[0] if modules else None,
            "scope": "field_names_xml_ids_module_metadata",
            "limitation": "Extra runtime fields usually come from core/dependencies. Does not compare field semantics or effective XML view architecture; source version strings do not prove deployment freshness.",
        }
    )


def tool_readiness() -> str:
    """Report registered tools and prerequisites without executing business methods or claiming live permissions."""
    from odoo_boost.mcp_server.registry import LIVE_TOOLS, LOCAL_TOOLS
    from odoo_boost.odoo_ls import find_odoo_ls, is_usable

    config = active_config()
    binary = find_odoo_ls(config.odoo_ls_path if config else None)
    return json_response(
        {
            "live": [
                {
                    "name": t.__name__,
                    "status": "not_probed",
                    "requires": "Odoo connection and per-model permissions",
                }
                for t in LIVE_TOOLS
            ],
            "local": [t.__name__ for t in LOCAL_TOOLS],
            "pylint_odoo_installed": importlib.util.find_spec("pylint_odoo") is not None,
            "odoo_ls_usable": bool(binary and is_usable(binary)),
            "profile": config.active_profile if config else None,
            "readonly": config.readonly if config else None,
            "note": "Registered does not mean runtime-verified. Use check --mcp for a protocol probe; targeted live calls verify their own permissions.",
        }
    )


def tool_metrics() -> str:
    """Return per-server MCP call counts, failures, latency and response characters; no arguments or record data."""
    from odoo_boost.ast_scanner.analyzer import (
        _parse_python_file_cached,
        _parse_xml_file_cached,
        _scan_addon_cached,
    )

    return json_response(
        {
            **get_context().metrics.snapshot(),
            "local_scan_caches": {
                "addon": _scan_addon_cached.cache_info()._asdict(),
                "python": _parse_python_file_cached.cache_info()._asdict(),
                "xml": _parse_xml_file_cached.cache_info()._asdict(),
            },
            "cache_scope": "Process-wide; shared between server instances in this process.",
        }
    )


def run_odoo_tests(addon_path: str, test_tags: str, database: str) -> str:
    """Run focused Odoo tests only on an explicitly configured disposable test database, never the live database."""
    from odoo_boost.test_runner import run_tests

    config = active_config()
    if config is None:
        return json_response({"status": "unavailable", "error": "Project configuration required."})
    return json_response(run_tests(config, enforce_path(addon_path), test_tags, database))
