"""Zed integration using project instructions, skills, and MCP settings."""

from odoo_boost.agents.base import Agent
from odoo_boost.agents.spec import AGENT_SPECS


class ZedAgent(Agent):
    spec = AGENT_SPECS["zed"]
