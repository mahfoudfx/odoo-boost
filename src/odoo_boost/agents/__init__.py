"""Agent registry – all supported AI coding agents."""

from __future__ import annotations

import logging
from collections.abc import Iterable, Iterator
from pathlib import Path

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
from odoo_boost.agents.zed import ZedAgent
from odoo_boost.config.schema import OdooBoostConfig

logger = logging.getLogger(__name__)

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
    "zed": ZedAgent,
}

ALL_AGENT_IDS = list(AGENTS.keys())


def iter_agents(
    config: OdooBoostConfig, project_path: Path, agent_ids: Iterable[str] | None = None
) -> Iterator[Agent]:
    """Instantiate selected agents in order, ignoring duplicate and unknown IDs."""
    for agent_id in dict.fromkeys(config.agents if agent_ids is None else agent_ids):
        agent_cls = AGENTS.get(agent_id)
        if agent_cls is None:
            logger.warning("Unknown agent '%s', skipping.", agent_id)
        else:
            yield agent_cls(config=config, project_path=project_path)


def install_agents(config: OdooBoostConfig, project_path: Path) -> list[Path]:
    """Generate agent files, installing each shared skills directory once."""
    created: list[Path] = []
    installed_skills: set[Path] = set()
    for agent in iter_agents(config, project_path):
        created.extend(agent.install(include_skills=agent.skills_dir not in installed_skills))
        installed_skills.add(agent.skills_dir)
    return list(dict.fromkeys(created))


__all__ = [
    "Agent",
    "AGENTS",
    "ALL_AGENT_IDS",
    "iter_agents",
    "install_agents",
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
    "ZedAgent",
]
