"""Single source of truth for the MCP tools exposed by the server.

Live tools talk to the running Odoo instance and are wrapped so connection
failures surface as clear ``ToolError`` messages. Local tools only read the
local filesystem or spawn a local linter; they do not need a database.
"""

from __future__ import annotations

import functools
import xmlrpc.client
from collections.abc import Callable
from typing import Any

from mcp.server.mcpserver.exceptions import ToolError

# Live XML-RPC tools
from odoo_boost.mcp_server.tools.aggregate_records import aggregate_records
from odoo_boost.mcp_server.tools.application_info import application_info

# Local AST, verification, and diagnostics tools
from odoo_boost.mcp_server.tools.check_odoo_ls import check_odoo_ls
from odoo_boost.mcp_server.tools.count_records import count_records
from odoo_boost.mcp_server.tools.database_query import database_query
from odoo_boost.mcp_server.tools.database_schema import database_schema
from odoo_boost.mcp_server.tools.execute_method import execute_method
from odoo_boost.mcp_server.tools.get_config import get_config
from odoo_boost.mcp_server.tools.get_model_inheritance import get_model_inheritance
from odoo_boost.mcp_server.tools.get_module_info import get_module_info
from odoo_boost.mcp_server.tools.inspect_local_addon import inspect_local_addon
from odoo_boost.mcp_server.tools.lint_odoo_code import lint_odoo_code
from odoo_boost.mcp_server.tools.list_access_rights import list_access_rights
from odoo_boost.mcp_server.tools.list_menus import list_menus
from odoo_boost.mcp_server.tools.list_models import list_models
from odoo_boost.mcp_server.tools.list_routes import list_routes
from odoo_boost.mcp_server.tools.list_views import list_views
from odoo_boost.mcp_server.tools.list_workflows import list_workflows
from odoo_boost.mcp_server.tools.read_log_entries import read_log_entries
from odoo_boost.mcp_server.tools.resolve_local_xml_id import resolve_local_xml_id
from odoo_boost.mcp_server.tools.resolve_xml_id import resolve_xml_id
from odoo_boost.mcp_server.tools.search_docs import search_docs
from odoo_boost.mcp_server.tools.search_records import search_records

ToolFn = Callable[..., Any]


def resilient_live_tool(fn: ToolFn) -> ToolFn:
    """Translate connection failures into user-friendly ``ToolError`` messages."""

    @functools.wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        try:
            return fn(*args, **kwargs)
        except ConnectionError as exc:
            raise ToolError(str(exc)) from exc
        except xmlrpc.client.Fault as exc:
            # Odoo XML-RPC faults include a Python traceback. Keep the useful
            # access denial while avoiding a large traceback in the agent context.
            marker = "odoo.exceptions.AccessError:"
            if marker not in exc.faultString:
                raise
            message = exc.faultString.rsplit(marker, 1)[1].strip()
            raise ToolError(f"Odoo access denied: {message[:500]}") from exc

    return wrapper


LIVE_TOOLS: tuple[ToolFn, ...] = (
    application_info,
    database_schema,
    database_query,
    count_records,
    list_models,
    list_views,
    list_menus,
    list_routes,
    list_access_rights,
    get_config,
    get_module_info,
    search_records,
    execute_method,
    read_log_entries,
    list_workflows,
    aggregate_records,
    resolve_xml_id,
    get_model_inheritance,
)

LOCAL_TOOLS: tuple[ToolFn, ...] = (
    inspect_local_addon,
    resolve_local_xml_id,
    lint_odoo_code,
    check_odoo_ls,
    search_docs,
)

ALL_TOOLS: tuple[ToolFn, ...] = LIVE_TOOLS + LOCAL_TOOLS

# Commonly used subset registered when ``lean_tools`` is enabled to reduce the
# tool-schema overhead paid on every model turn.
LEAN_TOOL_NAMES: frozenset[str] = frozenset(
    {
        "application_info",
        "database_query",
        "database_schema",
        "search_records",
        "list_models",
        "inspect_local_addon",
        "lint_odoo_code",
        "search_docs",
    }
)


def is_enabled(tool: ToolFn, *, lean: bool) -> bool:
    """Return True when a tool should be registered for the given profile."""
    return not lean or tool.__name__ in LEAN_TOOL_NAMES
