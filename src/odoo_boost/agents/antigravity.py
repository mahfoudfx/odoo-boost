"""Antigravity agent – generates AGENTS.md + .agents/mcp_config.json."""

from __future__ import annotations

from odoo_boost.agents.base import Agent
from odoo_boost.agents.spec import AGENT_SPECS


class AntigravityAgent(Agent):
    spec = AGENT_SPECS["antigravity"]
