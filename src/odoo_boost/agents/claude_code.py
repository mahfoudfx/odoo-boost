"""Claude Code agent – generates CLAUDE.md + .mcp.json."""

from __future__ import annotations

from pathlib import Path

from odoo_boost.agents.base import Agent
from odoo_boost.agents.files import assert_safe_path, update_guidelines
from odoo_boost.agents.spec import AGENT_SPECS
from odoo_boost.guidelines.composer import compose_agent_guidelines


class ClaudeCodeAgent(Agent):
    spec = AGENT_SPECS["claude_code"]

    def _write_guidelines(self) -> Path:
        """Keep shared instructions in AGENTS.md and import them for Claude."""
        shared = self.project_path / "AGENTS.md"
        assert_safe_path(shared, self.project_path)
        reference_dir = Path(*self.spec.skills_dir).as_posix() + "/guidelines"
        update_guidelines(
            shared,
            compose_agent_guidelines(self.config.odoo_version, reference_dir),
        )
        update_guidelines(
            self.guidelines_path,
            "@AGENTS.md\n",
            legacy=self._legacy_guidelines_content(),
        )
        return self.guidelines_path

    def uninstall(self) -> list[Path]:
        removed = super().uninstall()
        shared_users = {
            agent_id
            for agent_id in self.config.agents
            if agent_id != "claude_code"
            and agent_id in AGENT_SPECS
            and AGENT_SPECS[agent_id].guidelines_path == ("AGENTS.md",)
        }
        if not shared_users:
            shared = self.project_path / "AGENTS.md"
            assert_safe_path(shared, self.project_path)
            if update_guidelines(shared, "", remove=True):
                removed.append(shared)
        return removed
