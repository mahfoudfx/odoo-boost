"""MCPServer definition – registers Odoo tools, resources, and prompts."""

from __future__ import annotations

import logging
from typing import Any

from mcp.server import MCPServer
from mcp.server.auth.settings import AuthSettings
from pydantic import AnyHttpUrl

from odoo_boost.__version__ import __version__
from odoo_boost.config.schema import OdooBoostConfig
from odoo_boost.connection.factory import create_connection
from odoo_boost.guidelines.composer import compose_guidelines, compose_guidelines_index
from odoo_boost.logging_config import configure_logging
from odoo_boost.mcp_launcher import build_http_url
from odoo_boost.mcp_server.auth import StaticTokenVerifier
from odoo_boost.mcp_server.context import ServerContext, set_context
from odoo_boost.mcp_server.registry import LIVE_TOOLS, LOCAL_TOOLS, is_enabled, resilient_live_tool
from odoo_boost.mcp_server.tools.database_schema import database_schema
from odoo_boost.skills.loader import generate_skills_routing

logger = logging.getLogger(__name__)


def create_mcp_server(config: OdooBoostConfig) -> Any:
    """Build an MCP v2 server wired to a live Odoo connection and local workspace tools."""
    configure_logging()

    # Establish connection
    conn = create_connection(config.connection)
    try:
        conn.authenticate()
    except Exception as exc:
        logger.warning(
            "Could not pre-authenticate with Odoo at %s (%s).",
            config.connection.url,
            exc,
        )
        logger.warning("MCP server running in resilient mode. Live tools will connect on demand.")

    set_context(ServerContext(connection=conn, config=config))

    token_verifier = None
    auth_settings = None
    if config.mcp_token:
        endpoint = AnyHttpUrl(build_http_url(config))
        token_verifier = StaticTokenVerifier(config.mcp_token)
        # The SDK requires auth settings alongside a token verifier. Static
        # tokens do not use the OAuth issuer, so it mirrors the resource URL.
        # Audience validation is disabled because the verifier already compares
        # the token exactly; this also future-proofs the 3.0 default change.
        auth_settings = AuthSettings(
            issuer_url=endpoint,
            resource_server_url=endpoint,
            validate_token_resource=False,
        )

    mcp = MCPServer(
        "odoo-boost",
        version=__version__,
        auth=auth_settings,
        token_verifier=token_verifier,
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
        """OCA standards and development guidelines (full text)."""
        return compose_guidelines(version=config.odoo_version)

    @mcp.resource("odoo://guidelines/oca/compact")
    def resource_oca_guidelines_index() -> str:
        """Compact index of the OCA guidelines (titles and headings only)."""
        return compose_guidelines_index(version=config.odoo_version)

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
    # Tools Registration (see mcp_server/registry.py for the tool inventory)
    # -------------------------------------------------------------------------
    lean = config.lean_tools
    for tool in LIVE_TOOLS:
        if is_enabled(tool, lean=lean):
            mcp.tool()(resilient_live_tool(tool))
    for local_tool in LOCAL_TOOLS:
        if is_enabled(local_tool, lean=lean):
            mcp.tool()(local_tool)

    return mcp
