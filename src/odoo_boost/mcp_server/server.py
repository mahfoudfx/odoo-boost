"""MCPServer definition – registers Odoo tools, resources, and prompts."""

from __future__ import annotations

import functools
import logging
from collections.abc import Callable
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
from odoo_boost.mcp_server.call_guard import ConsecutiveCallGuard
from odoo_boost.mcp_server.context import ServerContext, bound_context, set_context
from odoo_boost.mcp_server.registry import LIVE_TOOLS, LOCAL_TOOLS, resilient_live_tool
from odoo_boost.mcp_server.tools._common import json_response
from odoo_boost.mcp_server.tools.database_schema import database_schema
from odoo_boost.project_context import project_context
from odoo_boost.skills.loader import generate_skills_routing

logger = logging.getLogger(__name__)


def _bind_handler(
    fn: Callable[..., Any], context: ServerContext, guard: ConsecutiveCallGuard
) -> Callable[..., Any]:
    """Keep a registered handler attached to its originating server instance."""

    @functools.wraps(fn)
    def wrapped(*args: Any, **kwargs: Any) -> Any:
        guard.check(fn.__name__, args, kwargs)
        with bound_context(context):
            return fn(*args, **kwargs)

    return wrapped


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

    context = ServerContext(connection=conn, config=config)
    set_context(context)

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
            "inspect local code on disk, and validate code against OCA standards. "
            "Use live tools only when the task depends on current Odoo state. "
            "Reuse prior results and never repeat an identical successful call. "
            "Start with compact, filtered requests and deepen only for a concrete uncertainty. "
            "If a live call reports an access denial, do not retry it or investigate "
            "permissions unless the user asked for that."
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

    @mcp.resource("odoo://project/context")
    def resource_project_context() -> str:
        """Configured VENV, Odoo source, addon roots, and documentation paths."""
        with bound_context(context):
            return json_response(project_context(config))

    @mcp.resource("odoo://schema/{model_name}")
    def resource_model_schema(model_name: str) -> str:
        """Dynamic schema resource for a given Odoo model."""
        with bound_context(context):
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
    def prompt_upgrade_addon(path: str, target_version: str = "") -> str:
        """Prompt to analyze migration and upgrade steps for an Odoo addon."""
        version = target_version or config.odoo_version
        return (
            f"Please analyze the Odoo addon at '{path}' for migration to Odoo {version or '(target not configured)'}. "
            "Check version-specific view syntax, ORM and frontend API changes against "
            "documentation for the target version before recommending changes."
        )

    # -------------------------------------------------------------------------
    # Tools Registration (see mcp_server/registry.py for the tool inventory)
    # -------------------------------------------------------------------------
    call_guard = ConsecutiveCallGuard(
        config.max_consecutive_identical_calls,
        config.max_repeated_calls_per_window,
        config.repeated_call_window_size,
    )
    for tool in LIVE_TOOLS:
        mcp.tool()(_bind_handler(resilient_live_tool(tool), context, call_guard))
    for local_tool in LOCAL_TOOLS:
        mcp.tool()(_bind_handler(local_tool, context, call_guard))

    return mcp
