"""Declarative specifications for the supported AI coding agents.

Keeping the per-agent paths and output format in one dataclass means adding a
new agent is a single registry entry plus a thin wrapper class.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

# How the MCP config file is serialized for a given agent.
McpFormat = Literal["mcpServers", "vscode", "opencode", "codex", "hermes"]


@dataclass(frozen=True)
class AgentSpec:
    """Static description of an agent integration."""

    id: str
    display_name: str
    guidelines_path: tuple[str, ...]
    mcp_config_path: tuple[str, ...]
    skills_dir: tuple[str, ...]
    mcp_format: McpFormat = "mcpServers"
    cursor_rules: bool = False


AGENT_SPECS: dict[str, AgentSpec] = {
    "antigravity": AgentSpec(
        id="antigravity",
        display_name="Antigravity (App & CLI)",
        guidelines_path=("AGENTS.md",),
        mcp_config_path=(".agents", "mcp_config.json"),
        skills_dir=(".agents", "skills"),
    ),
    "claude_code": AgentSpec(
        id="claude_code",
        display_name="Claude Code",
        guidelines_path=("CLAUDE.md",),
        mcp_config_path=(".mcp.json",),
        skills_dir=(".ai", "skills"),
    ),
    "cursor": AgentSpec(
        id="cursor",
        display_name="Cursor",
        guidelines_path=(".cursor", "rules", "odoo-boost.mdc"),
        mcp_config_path=(".cursor", "mcp.json"),
        skills_dir=(".cursor", "skills"),
        cursor_rules=True,
    ),
    "opencode": AgentSpec(
        id="opencode",
        display_name="OpenCode",
        guidelines_path=("AGENTS.md",),
        mcp_config_path=("opencode.json",),
        skills_dir=(".agents", "skills"),
        mcp_format="opencode",
    ),
    "pi": AgentSpec(
        id="pi",
        display_name="Pi Coding Agent",
        guidelines_path=("AGENTS.md",),
        mcp_config_path=(".pi", "mcp.json"),
        skills_dir=(".pi", "skills"),
    ),
    "hermes": AgentSpec(
        id="hermes",
        display_name="Hermes Agent",
        guidelines_path=("AGENTS.md",),
        mcp_config_path=(".hermes", "config.yaml"),
        skills_dir=(".hermes", "skills"),
        mcp_format="hermes",
    ),
    "windsurf": AgentSpec(
        id="windsurf",
        display_name="Windsurf",
        guidelines_path=(".windsurfrules",),
        mcp_config_path=(".windsurf", "mcp.json"),
        skills_dir=(".windsurf", "skills"),
    ),
    "cline": AgentSpec(
        id="cline",
        display_name="Cline / Roo Code",
        guidelines_path=(".clinerules",),
        mcp_config_path=(".cline", "mcp_settings.json"),
        skills_dir=(".agents", "skills"),
    ),
    "codex": AgentSpec(
        id="codex",
        display_name="OpenAI Codex",
        guidelines_path=("AGENTS.md",),
        mcp_config_path=(".codex", "config.toml"),
        skills_dir=(".agents", "skills"),
        mcp_format="codex",
    ),
    "copilot": AgentSpec(
        id="copilot",
        display_name="GitHub Copilot",
        guidelines_path=(".github", "copilot-instructions.md"),
        mcp_config_path=(".vscode", "mcp.json"),
        skills_dir=(".github", "skills"),
        mcp_format="vscode",
    ),
    "junie": AgentSpec(
        id="junie",
        display_name="Junie",
        guidelines_path=(".junie", "guidelines.md"),
        mcp_config_path=(".junie", "mcp", "mcp.json"),
        skills_dir=(".junie", "skills"),
    ),
}
