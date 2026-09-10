"""Junie agent – generates .junie/guidelines.md + .junie/mcp/mcp.json."""

from __future__ import annotations

from odoo_boost.agents.base import Agent
from odoo_boost.agents.spec import AGENT_SPECS


class JunieAgent(Agent):
    spec = AGENT_SPECS["junie"]
