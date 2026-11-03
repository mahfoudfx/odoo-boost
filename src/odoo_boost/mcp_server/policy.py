"""Opt-in tool guardrails: readonly mode and filesystem confinement.

These checks are defense-in-depth against accidental destructive calls from an
agent. They are *not* a sandbox: access control is still enforced by Odoo
itself for ORM operations, and by the OS user for file access.
"""

from __future__ import annotations

from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError

from odoo_boost.local_paths import path_allowed, resolve_path
from odoo_boost.mcp_server.context import active_config

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


def enforce_method(method: str) -> None:
    """Allow only known read methods through arbitrary execution in readonly mode."""
    config = active_config()
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
    path = resolve_path(raw_path, Path.cwd())
    config = active_config()
    if config is not None and not path_allowed(path, config):
        allowed = ", ".join(config.allowed_roots or [config.project_path])
        raise ToolError(f"Path '{raw_path}' is outside the allowed roots: {allowed}.")
    return path
