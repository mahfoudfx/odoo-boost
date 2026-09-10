"""Parametric generation checks across every agent and platform."""

from __future__ import annotations

import pytest

from odoo_boost.agents import AGENTS
from odoo_boost.agents.base import Agent

AGENT_IDS = sorted(AGENTS)
PLATFORMS = ("native", "windows", "http")
ENDPOINT = "http://127.0.0.1:8765/mcp"


def _make_config(sample_config, platform: str):
    updates: dict = {"generate_ai_files": False, "mcp_token": "tok123"}
    if platform == "native":
        updates.update(mcp_transport="stdio", mcp_target="native")
    elif platform == "windows":
        updates.update(mcp_transport="stdio", mcp_target="wsl", wsl_distro="Ubuntu")
    else:
        updates.update(mcp_transport="http")
    return sample_config.model_copy(update=updates)


@pytest.mark.parametrize("platform", PLATFORMS)
@pytest.mark.parametrize("agent_id", AGENT_IDS)
def test_platform_generation(agent_id: str, platform: str, sample_config, tmp_path):
    agent: Agent = AGENTS[agent_id](
        config=_make_config(sample_config, platform), project_path=tmp_path
    )

    created = agent.install()
    assert agent.mcp_config_path in created
    content = agent.mcp_config_path.read_text(encoding="utf-8")
    assert content.strip(), f"{agent_id}/{platform}: empty config"

    if platform == "windows":
        assert "wsl.exe" in content, f"{agent_id}: missing wsl.exe launcher"
    elif platform == "http":
        assert ENDPOINT in content, f"{agent_id}: missing endpoint URL"
        assert "tok123" in content, f"{agent_id}: token not embedded for HTTP"
    else:
        assert "wsl.exe" not in content, f"{agent_id}: unexpected wsl.exe in native config"
