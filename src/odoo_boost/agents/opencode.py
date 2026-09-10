"""OpenCode agent – generates AGENTS.md + opencode.json."""

from __future__ import annotations

from odoo_boost.agents.base import Agent
from odoo_boost.agents.spec import AGENT_SPECS


class OpenCodeAgent(Agent):
    spec = AGENT_SPECS["opencode"]
