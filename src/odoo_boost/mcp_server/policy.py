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

# Methods that mutate state. ``readonly`` blocks these (and any private method).
MUTATING_METHODS: frozenset[str] = frozenset(
    {
        "create",
        "write",
        "unlink",
        "copy",
        "toggle_active",
        "action_confirm",
        "action_cancel",
        "action_done",
        "button_confirm",
        "button_validate",
        "commit",
        "rollback",
        "flush",
        "_sql",
    }
)


def _current_config() -> OdooBoostConfig | None:
    """Return the active config, or None outside an MCP server (e.g. CLI lint)."""
    try:
        return get_context().config
    except RuntimeError:
        return None


def enforce_method(method: str) -> None:
    """Reject mutating ORM methods when readonly mode is enabled."""
    config = _current_config()
    if config is None or not config.readonly:
        return
    name = method.strip()
    if name.startswith("_") or name in MUTATING_METHODS:
        raise ToolError(
            f"Method '{method}' is blocked because readonly mode is enabled. "
            "Set 'readonly' to false in odoo-boost.json to allow it."
        )


def enforce_path(raw_path: str) -> Path:
    """Resolve *raw_path* and ensure it lives under one of ``allowed_roots``.

    When ``allowed_roots`` is empty (default) no confinement is applied.
    """
    path = Path(raw_path).expanduser()
    path = path.resolve() if path.is_absolute() else (Path.cwd() / path).resolve()

    config = _current_config()
    roots = config.allowed_roots if config else []
    if not roots:
        return path

    for root in roots:
        root_path = Path(root).expanduser().resolve()
        if path == root_path or root_path in path.parents:
            return path

    allowed = ", ".join(roots)
    raise ToolError(f"Path '{raw_path}' is outside the allowed roots: {allowed}.")
