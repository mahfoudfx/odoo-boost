"""Cline agent – generates .clinerules + .cline/mcp_settings.json."""

from __future__ import annotations

from odoo_boost.agents.base import Agent
from odoo_boost.agents.spec import AGENT_SPECS


class ClineAgent(Agent):
    spec = AGENT_SPECS["cline"]
