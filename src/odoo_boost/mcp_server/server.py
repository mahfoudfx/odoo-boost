"""MCPServer definition – registers Odoo tools, resources, and prompts."""

from __future__ import annotations

from typing import Any

from mcp.server import MCPServer

from odoo_boost.config.schema import OdooBoostConfig
from odoo_boost.connection.factory import create_connection
from odoo_boost.guidelines.composer import compose_guidelines
from odoo_boost.mcp_server.context import ServerContext, set_context

# Live XML-RPC tools
from odoo_boost.mcp_server.tools.aggregate_records import aggregate_records
from odoo_boost.mcp_server.tools.application_info import application_info
from odoo_boost.mcp_server.tools.check_odoo_ls import check_odoo_ls
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
from odoo_boost.skills.loader import generate_skills_routing


def create_mcp_server(config: OdooBoostConfig) -> Any:
    """Build an MCP v2 server wired to a live Odoo connection and local workspace tools."""

    # Establish connection
    conn = create_connection(config.connection)
    conn.authenticate()

    set_context(ServerContext(connection=conn, config=config))

    mcp = MCPServer(
        "odoo-boost",
        instructions=(
            "Odoo Boost MCP server – provides deep introspection into running Odoo "
            "instances, local uncommitted custom addons, AST scanning, and OCA quality linting. "
            "Use these tools to explore models, views, records, configuration, access rights, "
            "inspect local code on disk, and validate code against OCA standards."
        ),
    )

    # -------------------------------------------------------------------------
    # Native MCP Resources
    # -------------------------------------------------------------------------
    @mcp.resource("odoo://guidelines/oca")
    def resource_oca_guidelines() -> str:
        """OCA standards and development guidelines."""
        return compose_guidelines(version=config.odoo_version)

    @mcp.resource("odoo://skills/catalog")
    def resource_skills_catalog() -> str:
        """Progressive skills catalog and routing table."""
        return generate_skills_routing()

    @mcp.resource("odoo://schema/{model_name}")
    def resource_model_schema(model_name: str) -> str:
        """Dynamic schema resource for a given Odoo model."""
        return database_schema(model_name)

    # -------------------------------------------------------------------------
    # Native MCP Prompts
    # -------------------------------------------------------------------------
    @mcp.prompt("review_odoo_addon")
    def prompt_review_addon(path: str) -> str:
        """Prompt to perform a comprehensive OCA code review on a local addon."""
        return (
            f"Please review the Odoo addon at '{path}'. "
            "Check it against OCA standards, verify security/ir.model.access.csv, "
            "audit for direct SQL injection risks, check compute method dependencies, "
            "and ensure multi-company security rules are properly respected."
        )

    @mcp.prompt("upgrade_odoo_addon")
    def prompt_upgrade_addon(path: str, target_version: str = "18.0") -> str:
        """Prompt to analyze migration and upgrade steps for an Odoo addon."""
        return (
            f"Please analyze the Odoo addon at '{path}' for migration to Odoo {target_version}. "
            "Identify deprecated view tags (e.g. <tree> vs <list>), obsolete attrs attributes, "
            "outdated relational Command tuples, and any breaking Python/ORM changes."
        )

    # -------------------------------------------------------------------------
    # Tools Registration (22 tools)
    # -------------------------------------------------------------------------
    # Live database tools
    mcp.tool()(application_info)
    mcp.tool()(database_schema)
    mcp.tool()(database_query)
    mcp.tool()(list_models)
    mcp.tool()(list_views)
    mcp.tool()(list_menus)
    mcp.tool()(list_routes)
    mcp.tool()(list_access_rights)
    mcp.tool()(get_config)
    mcp.tool()(get_module_info)
    mcp.tool()(search_records)
    mcp.tool()(execute_method)
    mcp.tool()(read_log_entries)
    mcp.tool()(search_docs)
    mcp.tool()(list_workflows)
    mcp.tool()(aggregate_records)
    mcp.tool()(resolve_xml_id)
    mcp.tool()(get_model_inheritance)

    # Local AST, verification, and diagnostics tools
    mcp.tool()(inspect_local_addon)
    mcp.tool()(resolve_local_xml_id)
    mcp.tool()(lint_odoo_code)
    mcp.tool()(check_odoo_ls)

    return mcp
