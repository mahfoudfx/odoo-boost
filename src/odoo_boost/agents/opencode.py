"""OpenCode agent – generates AGENTS.md + opencode.json."""

from __future__ import annotations

import json
from pathlib import Path

from odoo_boost.agents.base import Agent


class OpenCodeAgent(Agent):
    id = "opencode"
    display_name = "OpenCode"

    @property
    def guidelines_path(self) -> Path:
        return self.project_path / "AGENTS.md"

    @property
    def mcp_config_path(self) -> Path:
        return self.project_path / "opencode.json"

    @property
    def skills_dir(self) -> Path:
        return self.project_path / ".agents" / "skills"

    def _mcp_config_content(self) -> str:
        cmd = self._mcp_command()
        return (
            json.dumps(
                {
                    "mcp": {
                        "odoo-boost": {
                            "type": "local",
                            "command": cmd,
                        }
                    }
                },
                indent=2,
            )
            + "\n"
        )
