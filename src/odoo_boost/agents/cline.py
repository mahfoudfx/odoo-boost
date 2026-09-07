"""Cline agent – generates .clinerules + .cline/mcp_settings.json."""

from __future__ import annotations

import json
from pathlib import Path

from odoo_boost.agents.base import Agent


class ClineAgent(Agent):
    id = "cline"
    display_name = "Cline / Roo Code"

    @property
    def guidelines_path(self) -> Path:
        return self.project_path / ".clinerules"

    @property
    def mcp_config_path(self) -> Path:
        return self.project_path / ".cline" / "mcp_settings.json"

    @property
    def skills_dir(self) -> Path:
        return self.project_path / ".agents" / "skills"

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
