"""Windsurf agent – generates .windsurfrules + .windsurf/mcp.json."""

from __future__ import annotations

import json
from pathlib import Path

from odoo_boost.agents.base import Agent


class WindsurfAgent(Agent):
    id = "windsurf"
    display_name = "Windsurf"

    @property
    def guidelines_path(self) -> Path:
        return self.project_path / ".windsurfrules"

    @property
    def mcp_config_path(self) -> Path:
        return self.project_path / ".windsurf" / "mcp.json"

    @property
    def skills_dir(self) -> Path:
        return self.project_path / ".windsurf" / "skills"

    def _mcp_config_content(self) -> str:
        cmd = self._mcp_command()
        return (
            json.dumps(
                {
                    "mcpServers": {
                        "odoo-boost": {
                            "command": cmd[0],
                            "args": cmd[1:],
                        }
                    }
                },
                indent=2,
            )
            + "\n"
        )
