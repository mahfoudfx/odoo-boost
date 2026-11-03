"""Serialized configuration contracts across every agent and transport."""

from __future__ import annotations

import json
import sys

import pytest
import yaml

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

from odoo_boost.agents import AGENTS


@pytest.mark.parametrize("platform", ["native", "windows", "http", "auto"])
@pytest.mark.parametrize("agent_id", sorted(AGENTS))
def test_platform_generation(agent_id, platform, sample_config, tmp_path):
    config = sample_config.model_copy(
        update={
            "generate_ai_files": False,
            "mcp_token": "tok123",
            "mcp_transport": "http" if platform == "http" else "stdio",
            "mcp_target": "wsl"
            if platform == "windows"
            else platform
            if platform == "auto"
            else "native",
            "wsl_distro": "Ubuntu",
        }
    )
    agent = AGENTS[agent_id](config=config, project_path=tmp_path)
    created = agent.install()
    expected_paths = [agent.mcp_config_path]
    if platform == "auto":
        expected_paths.append(agent.windows_mcp_config_path)
    assert created == expected_paths
    assert agent.windows_mcp_config_path.exists() is (platform == "auto")

    for path in expected_paths:
        content = path.read_text(encoding="utf-8")
        if agent_id == "codex":
            data, root = tomllib.loads(content), "mcp_servers"
        elif agent_id == "hermes":
            data, root = yaml.safe_load(content), "mcp_servers"
        else:
            data = json.loads(content)
            root = {"copilot": "servers", "opencode": "mcp", "zed": "context_servers"}.get(
                agent_id, "mcpServers"
            )
        assert set(data) == {root}
        assert set(data[root]) == {"odoo-boost"}
        server = data[root]["odoo-boost"]
        if platform == "http":
            url_key = "serverUrl" if agent_id == "antigravity" else "url"
            header_key = "http_headers" if agent_id == "codex" else "headers"
            expected = {
                url_key: "http://127.0.0.1:8765/mcp",
                header_key: {"Authorization": "Bearer tok123"},
            }
            if agent_id == "opencode":
                expected.update(type="remote", enabled=True)
            elif agent_id not in {"antigravity", "codex", "hermes", "zed"}:
                expected["type"] = "http"
        else:
            command = [
                sys.executable,
                "-m",
                "odoo_boost",
                "mcp",
                "-c",
                str(tmp_path / "odoo-boost.json"),
            ]
            if platform == "windows" or path == agent.windows_mcp_config_path:
                command = ["wsl.exe", "-d", "Ubuntu", "--cd", str(tmp_path), "--", *command]
            expected = (
                {"type": "local", "command": command}
                if agent_id == "opencode"
                else {"command": command[0], "args": command[1:]}
            )
        assert server == expected
