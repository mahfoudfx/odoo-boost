"""Detect and clean up orphaned files from removed agents."""

from __future__ import annotations

from pathlib import Path

from odoo_boost.agents import AGENTS
from odoo_boost.agents.files import (
    assert_safe_path,
    remove_generated_skills,
    update_guidelines,
    update_mcp_config,
)
from odoo_boost.agents.spec import AGENT_SPECS
from odoo_boost.config.schema import OdooBoostConfig


def find_orphaned_agent_files(config: OdooBoostConfig, project_path: Path) -> dict[str, list[Path]]:
    """Identify files on disk that belong to agents not in config.agents.

    Shared paths (e.g. AGENTS.md used by multiple agents) are preserved
    if any currently active agent still requires them.
    """
    active_agents = [
        AGENTS[aid](config=config, project_path=project_path)
        for aid in config.agents
        if aid in AGENTS
    ]

    active_guidelines = {a.guidelines_path for a in active_agents if config.generate_ai_files}
    active_mcp = set()
    if config.generate_mcp:
        for a in active_agents:
            active_mcp.add(a.mcp_config_path)
            active_mcp.add(a.windows_mcp_config_path)
    active_skills = {a.skills_dir for a in active_agents if config.generate_ai_files}

    orphans: dict[str, list[Path]] = {}

    for agent_id, agent_cls in AGENTS.items():
        if agent_id in config.agents:
            continue

        agent = agent_cls(config=config, project_path=project_path)
        agent_orphans: list[Path] = []

        if agent.guidelines_path.is_file() and agent.guidelines_path not in active_guidelines:
            agent_orphans.append(agent.guidelines_path)

        if agent.mcp_config_path.is_file() and agent.mcp_config_path not in active_mcp:
            agent_orphans.append(agent.mcp_config_path)

        if (
            agent.windows_mcp_config_path.is_file()
            and agent.windows_mcp_config_path not in active_mcp
        ):
            agent_orphans.append(agent.windows_mcp_config_path)

        if agent.skills_dir.is_dir() and agent.skills_dir not in active_skills:
            agent_orphans.append(agent.skills_dir)

        if agent_orphans:
            orphans[agent_id] = agent_orphans

    return orphans


def clean_orphaned_agent_files(orphans: dict[str, list[Path]], project_path: Path) -> list[Path]:
    """Delete orphaned files and remove any empty parent directories."""
    removed: list[Path] = []
    parents_to_check: list[Path] = []

    for agent_id, path_list in orphans.items():
        spec = AGENT_SPECS[agent_id]
        mcp_path = project_path.joinpath(*spec.mcp_config_path)
        windows_path = mcp_path.with_name(f"{mcp_path.stem}.windows{mcp_path.suffix}")
        guideline_path = project_path.joinpath(*spec.guidelines_path)
        for path in path_list:
            if path.is_symlink():
                continue
            assert_safe_path(path, project_path)
            if path in (mcp_path, windows_path) and path.is_file():
                if update_mcp_config(path, "", spec.mcp_format, remove=True):
                    removed.append(path)
                    parents_to_check.append(path.parent)
            elif path == guideline_path and path.is_file():
                if update_guidelines(path, "", remove=True):
                    removed.append(path)
                    parents_to_check.append(path.parent)
            elif path.is_dir():
                removed.extend(remove_generated_skills(path))
                parents_to_check.append(path.parent)

    for candidate in parents_to_check:
        curr = candidate
        while curr != project_path and curr.is_relative_to(project_path) and curr != curr.parent:
            try:
                if curr.is_dir() and not any(curr.iterdir()):
                    curr.rmdir()
                    curr = curr.parent
                else:
                    break
            except OSError:
                break

    return removed
