"""Cursor agent – generates .cursor/rules/odoo-boost.mdc + .cursor/mcp.json."""

from __future__ import annotations

from odoo_boost.agents.base import Agent
from odoo_boost.agents.spec import AGENT_SPECS


class CursorAgent(Agent):
    spec = AGENT_SPECS["cursor"]
