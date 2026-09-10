"""Claude Code agent – generates CLAUDE.md + .mcp.json."""

from __future__ import annotations

from odoo_boost.agents.base import Agent
from odoo_boost.agents.spec import AGENT_SPECS


class ClaudeCodeAgent(Agent):
    spec = AGENT_SPECS["claude_code"]
