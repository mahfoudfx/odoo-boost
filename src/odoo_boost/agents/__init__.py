"""Agent registry – all supported AI coding agents."""

from __future__ import annotations

from odoo_boost.agents.antigravity import AntigravityAgent
from odoo_boost.agents.base import Agent
from odoo_boost.agents.claude_code import ClaudeCodeAgent
from odoo_boost.agents.cline import ClineAgent
from odoo_boost.agents.codex import CodexAgent
from odoo_boost.agents.copilot import CopilotAgent
from odoo_boost.agents.cursor import CursorAgent
from odoo_boost.agents.hermes import HermesAgent
from odoo_boost.agents.junie import JunieAgent
from odoo_boost.agents.opencode import OpenCodeAgent
from odoo_boost.agents.pi import PiAgent
from odoo_boost.agents.windsurf import WindsurfAgent

AGENTS: dict[str, type[Agent]] = {
    "antigravity": AntigravityAgent,
    "claude_code": ClaudeCodeAgent,
    "cursor": CursorAgent,
    "opencode": OpenCodeAgent,
    "pi": PiAgent,
    "hermes": HermesAgent,
    "windsurf": WindsurfAgent,
    "cline": ClineAgent,
    "codex": CodexAgent,
    "copilot": CopilotAgent,
    "junie": JunieAgent,
}

ALL_AGENT_IDS = list(AGENTS.keys())

__all__ = [
    "Agent",
    "AGENTS",
    "ALL_AGENT_IDS",
    "AntigravityAgent",
    "ClaudeCodeAgent",
    "CursorAgent",
    "OpenCodeAgent",
    "PiAgent",
    "HermesAgent",
    "WindsurfAgent",
    "ClineAgent",
    "CodexAgent",
    "CopilotAgent",
    "JunieAgent",
]
