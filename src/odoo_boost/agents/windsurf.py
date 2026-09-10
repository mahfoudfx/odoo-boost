"""Windsurf agent – generates .windsurfrules + .windsurf/mcp.json."""

from __future__ import annotations

from odoo_boost.agents.base import Agent
from odoo_boost.agents.spec import AGENT_SPECS


class WindsurfAgent(Agent):
    spec = AGENT_SPECS["windsurf"]
