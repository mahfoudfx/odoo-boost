"""Opt-in tool guardrails: readonly mode and filesystem confinement.

These checks are defense-in-depth against accidental destructive calls from an
agent. They are *not* a sandbox: access control is still enforced by Odoo
itself for ORM operations, and by the OS user for file access.
"""

from __future__ import annotations

from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError

from odoo_boost.config.schema import OdooBoostConfig
from odoo_boost.mcp_server.context import get_context

# Common ORM introspection methods allowed through execute_method in readonly mode.
# Public addon methods can mutate state regardless of their name, so a blacklist
# cannot provide a meaningful readonly boundary.
READONLY_METHODS: frozenset[str] = frozenset(
    {
        "search",
        "read",
        "search_read",
        "search_count",
        "read_group",
        "fields_get",
        "default_get",
        "name_search",
        "name_get",
        "get_view",
        "get_views",
        "fields_view_get",
        "check_access_rights",
        "check_access_rule",
    }
)


def _current_config() -> OdooBoostConfig | None:
    """Return the active config, or None outside an MCP server (e.g. CLI lint)."""
    try:
        return get_context().config
    except RuntimeError:
        return None


def enforce_method(method: str) -> None:
    """Allow only known read methods through arbitrary execution in readonly mode."""
    config = _current_config()
    if config is None or not config.readonly:
        return
    name = method.strip()
    if name not in READONLY_METHODS:
        raise ToolError(
            f"Method '{method}' is not on the readonly allowlist. "
            "Set 'readonly' to false in odoo-boost.json to allow it."
        )


def enforce_path(raw_path: str) -> Path:
    """Resolve *raw_path* and ensure it lives under one of ``allowed_roots``.

    Explicit ``allowed_roots`` take precedence. Otherwise the configured project
    path is the boundary unless external local paths were deliberately enabled.
    """
    path = Path(raw_path).expanduser()
    path = path.resolve() if path.is_absolute() else (Path.cwd() / path).resolve()

    config = _current_config()
    roots = config.allowed_roots if config else []
    if config and not roots and not config.allow_external_local_paths:
        roots = [config.project_path]
    if not roots:
        return path

    for root in roots:
        root_path = Path(root).expanduser().resolve()
        if path == root_path or root_path in path.parents:
            return path

    allowed = ", ".join(roots)
    raise ToolError(f"Path '{raw_path}' is outside the allowed roots: {allowed}.")
