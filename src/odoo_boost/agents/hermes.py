"""Hermes agent – generates AGENTS.md + .hermes/config.yaml."""

from __future__ import annotations

from odoo_boost.agents.base import Agent
from odoo_boost.agents.spec import AGENT_SPECS


class HermesAgent(Agent):
    spec = AGENT_SPECS["hermes"]
