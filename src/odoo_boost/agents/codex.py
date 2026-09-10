"""Codex agent – generates AGENTS.md + .codex/config.toml."""

from __future__ import annotations

from odoo_boost.agents.base import Agent
from odoo_boost.agents.spec import AGENT_SPECS


class CodexAgent(Agent):
    spec = AGENT_SPECS["codex"]
