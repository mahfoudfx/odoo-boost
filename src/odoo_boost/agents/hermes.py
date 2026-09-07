"""Hermes agent – generates AGENTS.md + .hermes/config.yaml."""

from __future__ import annotations

from pathlib import Path

import yaml

from odoo_boost.agents.base import Agent


class HermesAgent(Agent):
    id = "hermes"
    display_name = "Hermes Agent"

    @property
    def guidelines_path(self) -> Path:
        return self.project_path / "AGENTS.md"

    @property
    def mcp_config_path(self) -> Path:
        return self.project_path / ".hermes" / "config.yaml"

    @property
    def skills_dir(self) -> Path:
        return self.project_path / ".hermes" / "skills"

    def _mcp_config_content(self) -> str:
        cmd = self._mcp_command()
        data = {
            "mcp_servers": {
                "odoo-boost": {
                    "command": cmd[0],
                    "args": cmd[1:],
                }
            }
        }
        return yaml.dump(data, default_flow_style=False, sort_keys=False)
