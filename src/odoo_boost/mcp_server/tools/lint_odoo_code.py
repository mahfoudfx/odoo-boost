"""MCP tool: lint_odoo_code – run OCA quality checks (pylint-odoo) or AST diagnostics."""

from __future__ import annotations

from typing import Any

from odoo_boost.diagnostics import run_lint
from odoo_boost.mcp_server.policy import enforce_path
from odoo_boost.mcp_server.tools._common import (
    active_config,
    compact_text,
    error_response,
    json_response,
    resolve_full,
)

_MESSAGE_KEYS = ("messages", "errors", "warnings", "conventions", "issues")


def _compact_lint_result(result: dict[str, Any], *, full: bool) -> dict[str, Any]:
    """Truncate bulky linter output unless full fidelity was requested."""
    if full:
        return result

    if isinstance(result.get("raw_output"), str):
        raw = result["raw_output"]
        result["raw_output"] = compact_text(raw, 4000)
        result["raw_output_length"] = len(raw)

    for key in _MESSAGE_KEYS:
        items = result.get(key)
        if not isinstance(items, list):
            continue
        result[key] = items[:30]
        for item in result[key]:
            if isinstance(item, dict) and isinstance(item.get("message"), str):
                item["message"] = compact_text(item["message"], 500)
    return result


def lint_odoo_code(path: str, response_format: str | None = None) -> str:
    """Validate Odoo Python and XML files against OCA coding standards and deprecated APIs.

    Args:
        path: Path to file or addon directory to lint.
        response_format: 'compact' (default) truncates bulk output, 'full' keeps it.
    """
    full = resolve_full(response_format)
    target = enforce_path(path)

    if not target.exists():
        return error_response(f"Path '{path}' does not exist.")

    # Validate descendants as well: a permitted directory can contain symlinked files.
    if target.is_dir():
        for source in target.rglob("*"):
            if source.is_file() and source.suffix in {".py", ".xml"}:
                enforce_path(str(source))

    config = active_config()
    res = run_lint(target, version=config.odoo_version if config else None)
    res = _compact_lint_result(res, full=full)
    res["response_format"] = "full" if full else "compact"

    return json_response(res)
