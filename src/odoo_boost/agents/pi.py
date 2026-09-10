"""Pi coding agent – generates AGENTS.md + .pi/mcp.json."""

from __future__ import annotations

from odoo_boost.agents.base import Agent
from odoo_boost.agents.spec import AGENT_SPECS


class PiAgent(Agent):
    spec = AGENT_SPECS["pi"]
