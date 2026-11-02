"""Batch generation preserves agent output and avoids rewriting unchanged files."""

from __future__ import annotations

import os

from odoo_boost.agents import AGENTS, install_agents


def test_batch_generation_matches_individual_agents(sample_config, tmp_path):
    config = sample_config.model_copy(update={"agents": list(AGENTS)})
    for agent_class in AGENTS.values():
        agent_class(config, tmp_path).install()
    expected = {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()}

    created = install_agents(config, tmp_path)

    assert len(created) == len(set(created))
    assert {path: path.read_bytes() for path in tmp_path.rglob("*") if path.is_file()} == expected


def test_repeated_batch_update_preserves_timestamps_and_local_edits(sample_config, tmp_path):
    config = sample_config.model_copy(update={"agents": ["antigravity", "codex", "antigravity"]})
    installed = install_agents(config, tmp_path)
    local = tmp_path / ".agents" / "skills" / "creating-models" / "SKILL.md"
    local.write_text("Project-specific model guidance")
    for path in installed:
        os.utime(path, ns=(1_000_000_000, 1_000_000_000))

    created = install_agents(config, tmp_path)

    assert local not in created
    assert local.read_text() == "Project-specific model guidance"
    assert all(path.stat().st_mtime_ns == 1_000_000_000 for path in installed)
