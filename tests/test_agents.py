"""Tests for odoo_boost.agents (base + all concrete agents)."""

from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10
    import tomli as tomllib

from odoo_boost.agents import AGENTS, ALL_AGENT_IDS, Agent
from odoo_boost.agents.antigravity import AntigravityAgent
from odoo_boost.agents.claude_code import ClaudeCodeAgent
from odoo_boost.agents.cline import ClineAgent
from odoo_boost.agents.codex import CodexAgent
from odoo_boost.agents.copilot import CopilotAgent
from odoo_boost.agents.cursor import CursorAgent
from odoo_boost.agents.hermes import HermesAgent
from odoo_boost.agents.junie import JunieAgent
from odoo_boost.agents.opencode import OpenCodeAgent
from odoo_boost.agents.pi import PiAgent
from odoo_boost.agents.spec import AGENT_SPECS
from odoo_boost.agents.windsurf import WindsurfAgent
from odoo_boost.agents.zed import ZedAgent
from odoo_boost.config.schema import OdooBoostConfig

# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------


class TestAgentRegistry:
    def test_twelve_agents(self):
        assert len(AGENTS) == 12

    def test_all_ids(self):
        assert list(AGENTS.keys()) == ALL_AGENT_IDS

    def test_known_ids(self):
        expected_ids = [
            "antigravity",
            "claude_code",
            "cursor",
            "opencode",
            "pi",
            "hermes",
            "windsurf",
            "cline",
            "codex",
            "copilot",
            "junie",
            "zed",
        ]
        for agent_id in expected_ids:
            assert agent_id in AGENTS

    def test_registry_matches_specs(self):
        assert set(AGENTS) == set(AGENT_SPECS)

    def test_class_attrs_derived_from_spec(self):
        for agent_id, cls in AGENTS.items():
            assert cls.id == agent_id
            assert cls.display_name == AGENT_SPECS[agent_id].display_name

    def test_missing_spec_raises(self, sample_config, tmp_path):
        class BrokenAgent(Agent):
            pass

        with pytest.raises(TypeError):
            BrokenAgent(config=sample_config, project_path=tmp_path)


# ---------------------------------------------------------------------------
# Parametrized: every agent must satisfy these contracts
# ---------------------------------------------------------------------------


AGENT_CLASSES = [
    AntigravityAgent,
    ClaudeCodeAgent,
    CursorAgent,
    OpenCodeAgent,
    PiAgent,
    HermesAgent,
    WindsurfAgent,
    ClineAgent,
    CodexAgent,
    CopilotAgent,
    JunieAgent,
    ZedAgent,
]


@pytest.fixture(params=AGENT_CLASSES, ids=[a.id for a in AGENT_CLASSES])
def agent(request, sample_config: OdooBoostConfig, tmp_path: Path) -> Agent:
    cls = request.param
    return cls(config=sample_config, project_path=tmp_path)


class TestAgentContracts:
    def test_has_id(self, agent: Agent):
        assert isinstance(agent.id, str)
        assert len(agent.id) > 0

    def test_has_display_name(self, agent: Agent):
        assert isinstance(agent.display_name, str)
        assert len(agent.display_name) > 0

    def test_guidelines_path_is_absolute(self, agent: Agent):
        assert agent.guidelines_path.is_absolute()

    def test_mcp_config_path_is_absolute(self, agent: Agent):
        assert agent.mcp_config_path.is_absolute()

    def test_skills_dir_is_absolute(self, agent: Agent):
        assert agent.skills_dir.is_absolute()

    def test_install_creates_files(self, agent: Agent):
        paths = agent.install()
        assert len(paths) > 0
        for p in paths:
            assert p.exists(), f"{p} was not created"

    def test_guidelines_written(self, agent: Agent):
        agent.install()
        assert agent.guidelines_path.exists()
        content = agent.guidelines_path.read_text(encoding="utf-8")
        assert "Odoo" in content
        reference_dir = agent.skills_dir / "guidelines"
        assert (reference_dir / "security.md").exists()
        assert (reference_dir / "versions" / "v18.md").exists()
        assert f"{agent.spec.skills_dir[-1]}/guidelines/security.md" in content

    def test_mcp_config_written(self, agent: Agent):
        agent.install()
        assert agent.mcp_config_path.exists()
        content = agent.mcp_config_path.read_text(encoding="utf-8")
        assert "odoo-boost" in content

    def test_skills_dir_populated(self, agent: Agent):
        agent.install()
        assert agent.skills_dir.is_dir()
        skill_files = list(agent.skills_dir.rglob("SKILL.md"))
        assert len(skill_files) >= 8

    def test_uninstall_removes_files(self, agent: Agent):
        agent.install()
        agent.uninstall()
        assert not agent.guidelines_path.exists()
        assert not agent.mcp_config_path.exists()
        assert not agent.skills_dir.exists()

    def test_custom_skills_survive_uninstall(self, agent: Agent):
        agent.install()
        custom = agent.skills_dir / "my_skill" / "SKILL.md"
        custom.parent.mkdir(parents=True, exist_ok=True)
        custom.write_text("custom", encoding="utf-8")
        packaged = agent.skills_dir / "creating_models" / "SKILL.md"
        packaged.write_text("edited", encoding="utf-8")
        agent.uninstall()
        assert custom.read_text(encoding="utf-8") == "custom"
        assert packaged.read_text(encoding="utf-8") == "edited"

    def test_shared_mcp_config_preserves_other_entries(self, agent: Agent):
        path = agent.mcp_config_path
        path.parent.mkdir(parents=True, exist_ok=True)
        if agent.spec.mcp_format == "codex":
            path.write_text('[mcp_servers.other]\ncommand = "other"\n', encoding="utf-8")
        elif agent.spec.mcp_format == "hermes":
            path.write_text("mcp_servers:\n  other:\n    command: other\n", encoding="utf-8")
        else:
            key = {"vscode": "servers", "opencode": "mcp"}.get(agent.spec.mcp_format, "mcpServers")
            path.write_text(
                json.dumps({key: {"other": {"command": "other"}}, "custom": True}), encoding="utf-8"
            )
        agent.install()
        agent.uninstall()
        content = path.read_text(encoding="utf-8")
        assert "other" in content
        assert "odoo-boost" not in content

    def test_invalid_mcp_config_is_not_overwritten(self, agent: Agent):
        path = agent.mcp_config_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("invalid [", encoding="utf-8")
        with pytest.raises(ValueError):
            agent.write_mcp_config()
        assert path.read_text(encoding="utf-8") == "invalid ["

    def test_codex_toml_escapes_control_characters(self, sample_config, tmp_path):
        cfg = sample_config.model_copy(
            update={"mcp_command": ["server", "line\nbreak", "tab\tvalue"]}
        )
        agent = CodexAgent(config=cfg, project_path=tmp_path)
        agent.write_mcp_config()
        parsed = tomllib.loads(agent.mcp_config_path.read_text(encoding="utf-8"))
        assert parsed["mcp_servers"]["odoo-boost"]["args"] == ["line\nbreak", "tab\tvalue"]

    def test_existing_guidelines_are_preserved(self, agent: Agent):
        path = agent.guidelines_path
        path.parent.mkdir(parents=True, exist_ok=True)
        original = "# Team instructions\nKeep the company style.\n"
        path.write_text(original, encoding="utf-8")
        agent.install()
        installed = path.read_text(encoding="utf-8")
        assert original.strip() in installed
        assert "<!-- odoo-boost:start" in installed
        agent.uninstall()
        assert original.strip() in path.read_text(encoding="utf-8")
        assert "<!-- odoo-boost:start" not in path.read_text(encoding="utf-8")

    def test_edited_generated_guidelines_survive_uninstall(self, agent: Agent):
        agent.install()
        path = agent.guidelines_path
        content = path.read_text(encoding="utf-8")
        path.write_text(
            content.replace(
                "# Odoo Boost: adaptive development workflow", "# Team-edited Guidelines"
            ),
            encoding="utf-8",
        )
        agent.uninstall()
        assert "Team-edited Guidelines" in path.read_text(encoding="utf-8")

    def test_edited_nested_skill_reference_survives_uninstall(self, agent: Agent):
        agent.install()
        path = agent.skills_dir / "pattern_library" / "references" / "INDEX.md"
        path.write_text(path.read_text(encoding="utf-8") + "\nTeam note.\n", encoding="utf-8")

        agent.uninstall()

        assert path.is_file()
        assert "Team note." in path.read_text(encoding="utf-8")
        assert not (agent.skills_dir / "pattern_library" / "SKILL.md").exists()

    def test_legacy_generated_guidelines_upgrade_without_duplication(self, agent: Agent):
        path = agent.guidelines_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(agent._legacy_guidelines_content(), encoding="utf-8")
        agent.install()
        assert path.read_text(encoding="utf-8").count("<!-- odoo-boost:start") == 1
        agent.uninstall()
        assert not path.exists()

    def test_symlinked_output_is_rejected(self, agent: Agent, tmp_path: Path):
        external = tmp_path.parent / f"outside-{agent.id}.txt"
        external.write_text("safe", encoding="utf-8")
        path = agent.guidelines_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.symlink_to(external)
        with pytest.raises(ValueError, match="symlink"):
            agent.install()
        assert external.read_text(encoding="utf-8") == "safe"

    def test_cursor_frontmatter_remains_first(self, sample_config, tmp_path):
        agent = CursorAgent(config=sample_config, project_path=tmp_path)
        path = agent.guidelines_path
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("---\ndescription: Team rule\n---\n\nKeep this rule.\n", encoding="utf-8")
        agent.install()
        content = path.read_text(encoding="utf-8")
        assert content.startswith("---\ndescription: Team rule\n---\n")
        assert content.count("<!-- odoo-boost:start") == 1
        agent.uninstall()
        assert "Keep this rule." in path.read_text(encoding="utf-8")

    def test_mcp_command(self, agent: Agent):
        cmd = agent._mcp_command()
        assert cmd[0] == sys.executable
        assert cmd[1:4] == ["-m", "odoo_boost", "mcp"]
        assert cmd[4] == "-c"
        assert cmd[5].endswith("odoo-boost.json")

    def test_windows_command_uses_wsl_launcher(self, agent: Agent):
        cmd = agent._mcp_command(windows=True)
        assert cmd[0] == "wsl.exe"
        assert "--cd" in cmd
        assert sys.executable in cmd
        assert cmd[-1].endswith("odoo-boost.json")

    def test_auto_emits_windows_companion(self, agent: Agent):
        agent.install()
        assert agent.mcp_config_path.exists()
        assert agent.windows_mcp_config_path.exists()
        assert agent.windows_mcp_config_path.name.endswith(
            ".windows" + agent.mcp_config_path.suffix
        )

    def test_native_target_skips_windows_companion(self, sample_config, tmp_path):
        cfg = sample_config.model_copy(update={"mcp_target": "native"})
        a = ClaudeCodeAgent(config=cfg, project_path=tmp_path)
        a.install()
        assert a.mcp_config_path.exists()
        assert not a.windows_mcp_config_path.exists()

    def test_http_transport_emits_url(self, sample_config, tmp_path):
        cfg = sample_config.model_copy(update={"mcp_transport": "http", "mcp_port": 9000})
        a = AntigravityAgent(config=cfg, project_path=tmp_path)
        a.install()
        data = json.loads(a.mcp_config_path.read_text())
        assert data["mcpServers"]["odoo-boost"]["serverUrl"] == "http://127.0.0.1:9000/mcp"
        assert not a.windows_mcp_config_path.exists()

    def test_custom_command_override(self, sample_config, tmp_path):
        cfg = sample_config.model_copy(
            update={"mcp_command": ["docker", "run", "odoo-boost", "mcp"]}
        )
        a = AntigravityAgent(config=cfg, project_path=tmp_path)
        cmd = a._mcp_command()
        assert cmd == ["docker", "run", "odoo-boost", "mcp"]
        a.install()
        assert not a.windows_mcp_config_path.exists()


# ---------------------------------------------------------------------------
# Agent-specific format tests
# ---------------------------------------------------------------------------


class TestAntigravityAgent:
    def test_paths(self, sample_config, tmp_path):
        a = AntigravityAgent(config=sample_config, project_path=tmp_path)
        assert a.guidelines_path.name == "AGENTS.md"
        assert a.mcp_config_path == tmp_path / ".agents" / "mcp_config.json"
        assert a.skills_dir == tmp_path / ".agents" / "skills"

    def test_mcp_config_json(self, sample_config, tmp_path):
        a = AntigravityAgent(config=sample_config, project_path=tmp_path)
        a.install()
        data = json.loads(a.mcp_config_path.read_text())
        assert "mcpServers" in data
        assert "odoo-boost" in data["mcpServers"]


class TestOpenCodeAgent:
    def test_mcp_format(self, sample_config, tmp_path):
        a = OpenCodeAgent(config=sample_config, project_path=tmp_path)
        a.install()
        data = json.loads(a.mcp_config_path.read_text())
        assert "mcp" in data
        assert data["mcp"]["odoo-boost"]["type"] == "local"


class TestHermesAgent:
    def test_mcp_yaml_format(self, sample_config, tmp_path):
        a = HermesAgent(config=sample_config, project_path=tmp_path)
        a.install()
        data = yaml.safe_load(a.mcp_config_path.read_text())
        assert "mcp_servers" in data
        assert "odoo-boost" in data["mcp_servers"]


class TestWindsurfAgent:
    def test_guidelines_at_windsurfrules(self, sample_config, tmp_path):
        a = WindsurfAgent(config=sample_config, project_path=tmp_path)
        assert a.guidelines_path.name == ".windsurfrules"
        assert a.mcp_config_path == tmp_path / ".windsurf" / "mcp.json"


class TestClineAgent:
    def test_guidelines_at_clinerules(self, sample_config, tmp_path):
        a = ClineAgent(config=sample_config, project_path=tmp_path)
        assert a.guidelines_path.name == ".clinerules"
        assert a.mcp_config_path == tmp_path / ".cline" / "mcp_settings.json"


class TestClaudeCodeAgent:
    def test_guidelines_at_claude_md(self, sample_config, tmp_path):
        a = ClaudeCodeAgent(config=sample_config, project_path=tmp_path)
        assert a.guidelines_path.name == "CLAUDE.md"

    def test_mcp_config_json(self, sample_config, tmp_path):
        a = ClaudeCodeAgent(config=sample_config, project_path=tmp_path)
        a.install()
        data = json.loads(a.mcp_config_path.read_text())
        assert "mcpServers" in data
        assert "odoo-boost" in data["mcpServers"]


class TestCursorAgent:
    def test_guidelines_has_frontmatter(self, sample_config, tmp_path):
        a = CursorAgent(config=sample_config, project_path=tmp_path)
        a.install()
        content = a.guidelines_path.read_text()
        assert content.startswith("---\n")
        assert "alwaysApply: true" in content


class TestCopilotAgent:
    def test_mcp_uses_servers_key(self, sample_config, tmp_path):
        a = CopilotAgent(config=sample_config, project_path=tmp_path)
        a.install()
        data = json.loads(a.mcp_config_path.read_text())
        assert "servers" in data


class TestCodexAgent:
    def test_mcp_config_is_toml(self, sample_config, tmp_path):
        a = CodexAgent(config=sample_config, project_path=tmp_path)
        a.install()
        content = a.mcp_config_path.read_text()
        assert "[mcp_servers.odoo-boost]" in content
        assert a.mcp_config_path.suffix == ".toml"


class TestJunieAgent:
    def test_paths_under_junie_dir(self, sample_config, tmp_path):
        a = JunieAgent(config=sample_config, project_path=tmp_path)
        assert ".junie" in str(a.guidelines_path)
        assert ".junie" in str(a.mcp_config_path)
        assert ".junie" in str(a.skills_dir)


class TestZedAgent:
    def test_native_project_configuration(self, sample_config, tmp_path):
        a = ZedAgent(config=sample_config, project_path=tmp_path)
        a.install()

        data = json.loads(a.mcp_config_path.read_text())
        server = data["context_servers"]["odoo-boost"]
        assert server["command"] == sys.executable
        assert a.mcp_config_path == tmp_path / ".zed" / "settings.json"
        assert a.guidelines_path == tmp_path / "AGENTS.md"
        assert a.skills_dir == tmp_path / ".agents" / "skills"

    def test_http_configuration_and_existing_settings_are_preserved(self, sample_config, tmp_path):
        path = tmp_path / ".zed" / "settings.json"
        path.parent.mkdir(parents=True)
        path.write_text(
            json.dumps({"theme": "One Dark", "context_servers": {"other": {"url": "x"}}})
        )
        cfg = sample_config.model_copy(update={"mcp_transport": "http", "mcp_token": "tok123"})
        ZedAgent(config=cfg, project_path=tmp_path).install()

        data = json.loads(path.read_text())
        assert data["theme"] == "One Dark"
        assert data["context_servers"]["other"] == {"url": "x"}
        assert data["context_servers"]["odoo-boost"] == {
            "url": "http://127.0.0.1:8765/mcp",
            "headers": {"Authorization": "Bearer tok123"},
        }


# ---------------------------------------------------------------------------
# HTTP transport config variants
# ---------------------------------------------------------------------------


class TestHttpConfigVariants:
    def test_json_agents_without_token_have_no_headers(self, sample_config, tmp_path):
        cfg = sample_config.model_copy(update={"mcp_transport": "http"})
        a = AntigravityAgent(config=cfg, project_path=tmp_path)
        a.install()
        data = json.loads(a.mcp_config_path.read_text())
        server = data["mcpServers"]["odoo-boost"]
        assert "headers" not in server
        assert server["serverUrl"] == "http://127.0.0.1:8765/mcp"
        assert "url" not in server
        assert "type" not in server

    def test_json_agents_embed_bearer_token(self, sample_config, tmp_path):
        cfg = sample_config.model_copy(update={"mcp_transport": "http", "mcp_token": "tok123"})
        a = AntigravityAgent(config=cfg, project_path=tmp_path)
        a.install()
        data = json.loads(a.mcp_config_path.read_text())
        assert data["mcpServers"]["odoo-boost"]["headers"] == {"Authorization": "Bearer tok123"}

    def test_copilot_http_uses_type_and_headers(self, sample_config, tmp_path):
        cfg = sample_config.model_copy(update={"mcp_transport": "http", "mcp_token": "tok123"})
        a = CopilotAgent(config=cfg, project_path=tmp_path)
        a.install()
        server = json.loads(a.mcp_config_path.read_text())["servers"]["odoo-boost"]
        assert server["type"] == "http"
        assert server["headers"]["Authorization"] == "Bearer tok123"

    def test_opencode_http_remote_with_headers(self, sample_config, tmp_path):
        cfg = sample_config.model_copy(update={"mcp_transport": "http", "mcp_token": "tok123"})
        a = OpenCodeAgent(config=cfg, project_path=tmp_path)
        a.install()
        server = json.loads(a.mcp_config_path.read_text())["mcp"]["odoo-boost"]
        assert server["type"] == "remote"
        assert server["enabled"] is True
        assert server["headers"]["Authorization"] == "Bearer tok123"

    def test_codex_http_uses_http_headers(self, sample_config, tmp_path):
        cfg = sample_config.model_copy(update={"mcp_transport": "http", "mcp_token": "tok123"})
        a = CodexAgent(config=cfg, project_path=tmp_path)
        a.install()
        content = a.mcp_config_path.read_text()
        assert 'url = "http://127.0.0.1:8765/mcp"' in content
        assert 'http_headers = { Authorization = "Bearer tok123" }' in content

    def test_hermes_http_token_in_yaml(self, sample_config, tmp_path):
        cfg = sample_config.model_copy(update={"mcp_transport": "http", "mcp_token": "tok123"})
        a = HermesAgent(config=cfg, project_path=tmp_path)
        a.install()
        server = yaml.safe_load(a.mcp_config_path.read_text())["mcp_servers"]["odoo-boost"]
        assert server["headers"]["Authorization"] == "Bearer tok123"


# ---------------------------------------------------------------------------
# Conditional generation based on config flags
# ---------------------------------------------------------------------------


class TestConditionalGeneration:
    @pytest.fixture()
    def _config_factory(self, sample_config):
        def _make(generate_mcp: bool = True, generate_ai_files: bool = True) -> OdooBoostConfig:
            return OdooBoostConfig(
                connection=sample_config.connection,
                odoo_version=sample_config.odoo_version,
                agents=sample_config.agents,
                project_path=sample_config.project_path,
                generate_mcp=generate_mcp,
                generate_ai_files=generate_ai_files,
            )

        return _make

    def test_no_mcp_when_disabled(self, _config_factory, tmp_path):
        cfg = _config_factory(generate_mcp=False, generate_ai_files=True)
        a = ClaudeCodeAgent(config=cfg, project_path=tmp_path)
        paths = a.install()
        assert a.guidelines_path.exists()
        assert a.skills_dir.is_dir()
        assert not a.mcp_config_path.exists()
        assert a.mcp_config_path not in paths

    def test_no_ai_files_when_disabled(self, _config_factory, tmp_path):
        cfg = _config_factory(generate_mcp=True, generate_ai_files=False)
        a = ClaudeCodeAgent(config=cfg, project_path=tmp_path)
        paths = a.install()
        assert a.mcp_config_path.exists()
        assert not a.guidelines_path.exists()
        assert not a.skills_dir.exists()
        assert a.guidelines_path not in paths

    def test_both_disabled(self, _config_factory, tmp_path):
        cfg = _config_factory(generate_mcp=False, generate_ai_files=False)
        a = ClaudeCodeAgent(config=cfg, project_path=tmp_path)
        paths = a.install()
        assert paths == []
        assert not a.guidelines_path.exists()
        assert not a.mcp_config_path.exists()
        assert not a.skills_dir.exists()


@pytest.mark.parametrize(
    "table",
    [
        '[mcp_servers."odoo-boost"]\ncommand = "old"\n',
        '[mcp_servers.odoo-boost]\ncommand = "old"\n[mcp_servers.odoo-boost.env]\nKEY = "value"\n',
    ],
)
def test_nonstandard_toml_is_preserved_on_regeneration(tmp_path, table):
    from odoo_boost.agents.files import update_mcp_config

    path = tmp_path / "config.toml"
    path.write_text(table)
    with pytest.raises(ValueError):
        update_mcp_config(path, '[mcp_servers.odoo-boost]\ncommand = "new"\n', "codex")
    assert path.read_text() == table
