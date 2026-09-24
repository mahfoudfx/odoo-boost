"""Pydantic models for odoo-boost.json configuration."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class OdooConnection(BaseModel):
    """Odoo server connection settings."""

    url: str = Field(description="Odoo server URL, e.g. http://localhost:8069")
    database: str = Field(description="Database name")
    username: str = Field(default="admin", description="Login username")
    password: str = Field(default="admin", description="Login password or API key")
    protocol: Literal["xmlrpc"] = Field(default="xmlrpc", description="Connection protocol")


class OdooBoostConfig(BaseModel):
    """Root configuration model for odoo-boost.json."""

    connection: OdooConnection
    odoo_version: str | None = Field(
        default=None, description="Detected Odoo version (e.g. '18.0', '19.0', '20.0')"
    )
    agents: list[str] = Field(
        default_factory=list,
        description="Enabled agent identifiers (e.g. ['claude_code', 'cursor'])",
    )
    project_path: str = Field(default=".", description="Path to the Odoo project root")
    venv_path: str | None = Field(
        default=None, description="Project Python VENV root used for Odoo and Python checks."
    )
    odoo_conf_path: str | None = Field(
        default=None, description="Path to the Odoo configuration used by the project."
    )
    odoo_launch_cwd: str | None = Field(
        default=None,
        description="Working directory of the Odoo launch command for relative addon paths.",
    )
    addons_path_override: list[str] | None = Field(
        default=None,
        description="Effective --addons-path from the launch command, if it overrides odoo.conf.",
    )
    odoo_source_path: str | None = Field(
        default=None, description="Odoo framework source checkout, separate from custom addons."
    )
    odoo_docs_path: str | None = Field(
        default=None,
        description="Optional indexed local Odoo documentation cache for this version.",
    )
    generate_mcp: bool = Field(default=True, description="Generate MCP config files for agents")
    generate_ai_files: bool = Field(
        default=True, description="Generate AI guideline and skill files for agents"
    )
    mcp_transport: Literal["stdio", "http"] = Field(
        default="stdio",
        description=(
            "MCP transport. 'stdio' spawns a local process (default); 'http' emits "
            "URL-based configs that connect to a separately started server."
        ),
    )
    mcp_target: Literal["auto", "native", "wsl"] = Field(
        default="auto",
        description=(
            "How the stdio server process is launched. 'native' uses the running "
            "interpreter, 'wsl' wraps it in wsl.exe for Windows IDEs, 'auto' writes "
            "the native config plus a '*.windows' companion for WSL workflows."
        ),
    )
    wsl_distro: str | None = Field(
        default=None,
        description="WSL distribution name used by the 'wsl' target (e.g. 'Ubuntu')",
    )
    mcp_host: str = Field(
        default="127.0.0.1",
        description="Host the HTTP MCP server binds to when mcp_transport is 'http'",
    )
    mcp_port: int = Field(
        default=8765,
        description="Port the HTTP MCP server binds to when mcp_transport is 'http'",
    )
    mcp_http_url: str | None = Field(
        default=None,
        description=(
            "Optional client-facing Streamable HTTP endpoint override, useful when a "
            "Windows client reaches WSL through a hostname/IP different from the bind host."
        ),
    )
    mcp_command: list[str] | None = Field(
        default=None,
        description=(
            "Advanced: full command override for the stdio MCP server "
            "(e.g. ['docker', 'run', ...]). When set, it is used verbatim."
        ),
    )
    mcp_token: str | None = Field(
        default=None,
        repr=False,
        description=(
            "Bearer token required by the HTTP MCP transport. Non-loopback "
            "binds are refused unless a token is configured."
        ),
    )
    readonly: bool = Field(
        default=False,
        description=(
            "When True, execute_method refuses mutating methods. Defense-in-depth, not a sandbox."
        ),
    )
    allowed_roots: list[str] = Field(
        default_factory=list,
        description=(
            "Restrict file-based tools (inspect_local_addon, lint_odoo_code) to these "
            "roots. Empty uses project_path unless allow_external_local_paths is enabled."
        ),
    )
    allow_external_local_paths: bool = Field(
        default=False,
        description=(
            "Allow local file tools outside project_path when allowed_roots is empty. "
            "Enable only for deliberate shared-source inspection."
        ),
    )
    odoo_ls_path: str | None = Field(
        default=None,
        description="Optional path to the official odoo_ls_server executable.",
    )
    compact_responses: bool = Field(
        default=True,
        description=(
            "Return token-efficient tool responses by default. Every heavy tool still "
            "accepts response_format='full' per call."
        ),
    )
    max_response_chars: int = Field(
        default=40000,
        ge=0,
        description=(
            "Safety cap for a single tool response (0 disables). Oversized payloads are "
            "replaced by a truncated envelope instead of blowing up the agent context."
        ),
    )
    redact_config_secrets: bool = Field(
        default=True,
        description="Redact secret-looking ir.config_parameter values in get_config.",
    )
    cache_local_scans: bool = Field(
        default=True,
        description=("Cache local addon scans until a Python/XML file timestamp or size changes."),
    )
    max_consecutive_identical_calls: int = Field(
        default=2,
        ge=0,
        description=(
            "Block an MCP tool after this many consecutive calls with identical arguments "
            "(0 disables loop detection)."
        ),
    )
    max_repeated_calls_per_window: int = Field(
        default=2,
        ge=0,
        description=(
            "Block an identical MCP request after this many occurrences in the recent-call "
            "window, even when other calls occur between them (0 disables)."
        ),
    )
    repeated_call_window_size: int = Field(
        default=12,
        ge=0,
        description="Number of recent MCP calls used by repeated-call loop detection.",
    )
