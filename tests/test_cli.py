"""Tests for odoo_boost.cli via typer.testing.CliRunner."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from typer.testing import CliRunner

from odoo_boost.__version__ import __version__
from odoo_boost.cli.app import app

runner = CliRunner()


class TestVersionFlag:
    def test_version(self):
        result = runner.invoke(app, ["--version"])
        assert result.exit_code == 0
        assert __version__ in result.output

    def test_short_version(self):
        result = runner.invoke(app, ["-v"])
        assert result.exit_code == 0
        assert __version__ in result.output


class TestNoArgs:
    def test_shows_help(self):
        result = runner.invoke(app, [])
        # no_args_is_help=True causes Typer to exit with code 0 or 2 depending on version
        assert result.exit_code in (0, 2)
        assert "Usage" in result.output or "odoo-boost" in result.output


class TestCheckCommand:
    def test_check_no_config_no_flags(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["check"])
        assert result.exit_code == 1

    def test_check_with_config(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(sample_config.model_dump_json(indent=2))

        mock_conn = MagicMock()
        mock_conn.get_version.return_value = {"server_version": "18.0"}
        mock_conn.authenticate.return_value = 2
        mock_conn.search_count.return_value = 10

        with patch("odoo_boost.cli.check.create_connection", return_value=mock_conn):
            result = runner.invoke(app, ["check", "--config", str(cfg_path)])

        assert result.exit_code == 0
        assert "Odoo Boost" in result.output
        assert __version__ in result.output
        assert "Target Odoo" in result.output
        assert "Configuration" in result.output
        assert "18.0" in result.output

    def test_check_shows_local_setup_when_server_is_unreachable(
        self, tmp_path, sample_config, monkeypatch
    ):
        monkeypatch.chdir(tmp_path)
        venv = tmp_path / "venv"
        (venv / "bin").mkdir(parents=True)
        (venv / "pyvenv.cfg").write_text("home = /usr/bin\n")
        (venv / "bin/python").touch()
        docs = tmp_path / "docs"
        docs.mkdir()
        (docs / "index.sqlite3").touch()
        (docs / ".odoo-boost-docs.json").write_text("{}")
        cfg = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "venv_path": "venv",
                "odoo_docs_path": "docs",
            }
        )
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(cfg.model_dump_json(indent=2))
        mock_conn = MagicMock()
        mock_conn.get_version.side_effect = ConnectionError("offline")

        with patch("odoo_boost.cli.check.create_connection", return_value=mock_conn):
            result = runner.invoke(app, ["check", "--config", str(cfg_path)])

        assert result.exit_code == 1
        assert __version__ in result.output
        assert "Project VENV" in result.output
        assert "different interpreter" in result.output
        assert "Offline docs" in result.output
        assert "indexed" in result.output
        assert "Failed to reach server" in result.output

    def test_check_with_mcp_probe(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(sample_config.model_dump_json(indent=2))

        mock_conn = MagicMock()
        mock_conn.get_version.return_value = {"server_version": "18.0"}
        mock_conn.authenticate.return_value = 2
        mock_conn.search_count.return_value = 10

        with (
            patch("odoo_boost.cli.check.create_connection", return_value=mock_conn),
            patch(
                "odoo_boost.cli.check._probe_stdio",
                return_value=(True, "MCP server responded to initialize"),
            ) as probe,
        ):
            result = runner.invoke(app, ["check", "--config", str(cfg_path), "--mcp"])

        assert result.exit_code == 0
        assert "MCP server responded" in result.output
        probe.assert_called_once()

    def test_check_mcp_without_config_warns(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        mock_conn = MagicMock()
        mock_conn.get_version.return_value = {"server_version": "18.0"}
        mock_conn.authenticate.return_value = 2
        mock_conn.search_count.return_value = 10

        with patch("odoo_boost.cli.check.create_connection", return_value=mock_conn):
            result = runner.invoke(
                app,
                ["check", "--url", "http://localhost:8069", "--database", "db", "--mcp"],
            )

        assert result.exit_code == 0
        assert __version__ in result.output
        assert "CLI flags" in result.output
        assert "requires an odoo-boost.json" in result.output


class TestUpdateCommand:
    def test_update_no_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["update"])
        assert result.exit_code == 1

    def test_update_regenerates_files(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "agents": ["antigravity"],
                "mcp_target": "native",
            }
        )
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(cfg.model_dump_json(indent=2))

        result = runner.invoke(app, ["update", "--config", str(cfg_path)])

        assert result.exit_code == 0
        assert (tmp_path / "AGENTS.md").exists()
        assert (tmp_path / ".agents" / "mcp_config.json").exists()
        skill_files = list((tmp_path / ".agents" / "skills").rglob("SKILL.md"))
        assert len(skill_files) == 25

    def test_update_is_idempotent(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "agents": ["antigravity"],
                "mcp_target": "native",
            }
        )
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(cfg.model_dump_json(indent=2))

        assert runner.invoke(app, ["update", "--config", str(cfg_path)]).exit_code == 0
        content_first = (tmp_path / ".agents" / "mcp_config.json").read_text()
        assert runner.invoke(app, ["update", "--config", str(cfg_path)]).exit_code == 0
        assert (tmp_path / ".agents" / "mcp_config.json").read_text() == content_first

    def test_update_cleans_orphaned_agents(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # 1. Install with antigravity and claude_code
        cfg = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "agents": ["antigravity", "claude_code"],
                "mcp_target": "native",
            }
        )
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(cfg.model_dump_json(indent=2))
        res = runner.invoke(app, ["update", "--config", str(cfg_path)])
        assert res.exit_code == 0
        assert (tmp_path / "AGENTS.md").exists()
        assert (tmp_path / "CLAUDE.md").exists()
        assert (tmp_path / ".mcp.json").exists()

        # 2. Update config to only have antigravity
        cfg_updated = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "agents": ["antigravity"],
                "mcp_target": "native",
            }
        )
        cfg_path.write_text(cfg_updated.model_dump_json(indent=2))

        # 3. Run update -y (should clean claude_code files)
        res_update = runner.invoke(app, ["update", "--config", str(cfg_path), "-y"])
        assert res_update.exit_code == 0
        assert (tmp_path / "AGENTS.md").exists()
        assert not (tmp_path / "CLAUDE.md").exists()
        assert not (tmp_path / ".mcp.json").exists()

    def test_claude_only_update_keeps_shared_guide(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = sample_config.model_copy(
            update={"project_path": str(tmp_path), "agents": ["claude_code"]}
        )
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(cfg.model_dump_json(indent=2))

        assert runner.invoke(app, ["update", "--config", str(cfg_path), "-y"]).exit_code == 0
        shared = tmp_path / "AGENTS.md"
        content = shared.read_text()
        assert "@AGENTS.md" in (tmp_path / "CLAUDE.md").read_text()
        assert runner.invoke(app, ["update", "--config", str(cfg_path), "-y"]).exit_code == 0
        assert shared.read_text() == content

    def test_update_keep_orphans_flag(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "agents": ["antigravity", "claude_code"],
                "mcp_target": "native",
            }
        )
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(cfg.model_dump_json(indent=2))
        runner.invoke(app, ["update", "--config", str(cfg_path)])

        # Remove claude_code but pass --keep-orphans
        cfg_updated = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "agents": ["antigravity"],
                "mcp_target": "native",
            }
        )
        cfg_path.write_text(cfg_updated.model_dump_json(indent=2))
        res_update = runner.invoke(app, ["update", "--config", str(cfg_path), "--keep-orphans"])
        assert res_update.exit_code == 0
        assert (tmp_path / "CLAUDE.md").exists()
        assert (tmp_path / ".mcp.json").exists()

    def test_update_preserves_shared_files(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # antigravity and codex both use AGENTS.md and .agents/skills
        cfg = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "agents": ["antigravity", "codex"],
                "mcp_target": "native",
            }
        )
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(cfg.model_dump_json(indent=2))
        runner.invoke(app, ["update", "--config", str(cfg_path)])
        assert (tmp_path / ".codex" / "config.toml").exists()
        assert (tmp_path / "AGENTS.md").exists()

        # Remove codex
        cfg_updated = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "agents": ["antigravity"],
                "mcp_target": "native",
            }
        )
        cfg_path.write_text(cfg_updated.model_dump_json(indent=2))
        runner.invoke(app, ["update", "--config", str(cfg_path), "-y"])

        # Codex config should be removed, but AGENTS.md and skills must be kept!
        assert not (tmp_path / ".codex" / "config.toml").exists()
        assert (tmp_path / "AGENTS.md").exists()
        assert (tmp_path / ".agents" / "skills").is_dir()


class TestInstallWizard:
    def test_gitignore_opt_in_and_uninstall_removes_only_managed_entry(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / ".gitignore").write_text("__pycache__/\n")
        mock_conn = MagicMock()
        mock_conn.get_version.return_value = {"server_version": "18.0", "server_serie": "18.0"}
        mock_conn.authenticate.return_value = 2

        with patch("odoo_boost.cli.install.create_connection", return_value=mock_conn):
            result = runner.invoke(
                app,
                ["install", "--skip-dev-tools", "--skip-docs", "--gitignore"],
                input="\ndb\n\n\n1\nn\nn\n",
            )
        assert result.exit_code == 0, result.output
        assert "/odoo-boost.json" in (tmp_path / ".gitignore").read_text()

        result = runner.invoke(app, ["uninstall", "-y", "--gitignore"])
        assert result.exit_code == 0, result.output
        assert (tmp_path / ".gitignore").read_text() == "__pycache__/\n"

    def test_minimal_install(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)

        mock_conn = MagicMock()
        mock_conn.get_version.return_value = {
            "server_version": "18.0",
            "server_serie": "18.0",
        }
        mock_conn.authenticate.return_value = 2

        # url, database, username, password, agent #1, generated files, dev tools
        user_input = "\ndb\n\n\n1\nn\nn\nn\nn\n"
        with patch("odoo_boost.cli.install.create_connection", return_value=mock_conn):
            result = runner.invoke(app, ["install", "--skip-docs"], input=user_input)

        assert result.exit_code == 0, result.output
        assert (tmp_path / "odoo-boost.json").exists()
        assert not (tmp_path / "AGENTS.md").exists()

    def test_install_defaults_to_development_tools(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mock_conn = MagicMock()
        mock_conn.get_version.return_value = {"server_version": "18.0", "server_serie": "18.0"}
        mock_conn.authenticate.return_value = 2

        with (
            patch("odoo_boost.cli.install.create_connection", return_value=mock_conn),
            patch("odoo_boost.cli.install._install_development_tools") as install_tools,
        ):
            result = runner.invoke(
                app, ["install", "--skip-docs"], input="\ndb\n\n\n1\nn\nn\n\nn\n"
            )

        assert result.exit_code == 0, result.output
        install_tools.assert_called_once()

    def test_install_skip_dev_tools_flag(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        mock_conn = MagicMock()
        mock_conn.get_version.return_value = {"server_version": "18.0", "server_serie": "18.0"}
        mock_conn.authenticate.return_value = 2

        with (
            patch("odoo_boost.cli.install.create_connection", return_value=mock_conn),
            patch("odoo_boost.cli.install._install_development_tools") as install_tools,
        ):
            result = runner.invoke(
                app, ["install", "--skip-dev-tools", "--skip-docs"], input="\ndb\n\n\n1\nn\nn\nn\n"
            )

        assert result.exit_code == 0, result.output
        install_tools.assert_not_called()


class TestMcpCommand:
    def test_mcp_no_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["mcp"])
        assert result.exit_code == 1

    def test_mcp_http_refuses_remote_bind_without_token(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(sample_config.model_dump_json(indent=2))
        result = runner.invoke(
            app,
            ["mcp", "--config", str(cfg_path), "--transport", "http", "--host", "0.0.0.0"],
        )
        assert result.exit_code == 1

    def test_mcp_rejects_unknown_transport(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(sample_config.model_dump_json(indent=2))
        result = runner.invoke(
            app, ["mcp", "--config", str(cfg_path), "--transport", "carrier-pigeon"]
        )
        assert result.exit_code == 1


class TestCheckMcpHttp:
    def test_check_mcp_http_passes_token(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = sample_config.model_copy(
            update={"mcp_transport": "http", "mcp_token": "tok", "generate_ai_files": False}
        )
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(cfg.model_dump_json(indent=2))

        mock_conn = MagicMock()
        mock_conn.get_version.return_value = {"server_version": "18.0"}
        mock_conn.authenticate.return_value = 2
        mock_conn.search_count.return_value = 10

        with (
            patch("odoo_boost.cli.check.create_connection", return_value=mock_conn),
            patch(
                "odoo_boost.cli.check._probe_http",
                return_value=(True, "reachable"),
            ) as probe,
        ):
            result = runner.invoke(app, ["check", "--config", str(cfg_path), "--mcp"])

        assert result.exit_code == 0
        probe.assert_called_once()
        assert probe.call_args.kwargs.get("token") == "tok"


class TestHttpProbe:
    def test_performs_initialize_with_authentication(self):
        from odoo_boost.cli.check import _probe_http

        response = MagicMock(
            status_code=200,
            headers={"content-type": "application/json"},
        )
        response.json.return_value = {"jsonrpc": "2.0", "id": 1, "result": {}}
        with patch("httpx.post", return_value=response) as post:
            ok, detail = _probe_http("http://localhost:8765/mcp", token="secret")

        assert ok is True
        assert "initialize" in detail
        request = post.call_args
        assert request.kwargs["json"]["method"] == "initialize"
        assert request.kwargs["headers"]["Authorization"] == "Bearer secret"

    def test_rejects_non_mcp_endpoint(self):
        from odoo_boost.cli.check import _probe_http

        response = MagicMock(status_code=404, headers={}, text="not found")
        with patch("httpx.post", return_value=response):
            ok, detail = _probe_http("http://localhost:8765/")

        assert ok is False
        assert "HTTP 404" in detail

    def test_reports_rejected_token(self):
        from odoo_boost.cli.check import _probe_http

        response = MagicMock(status_code=401, headers={}, text="unauthorized")
        with patch("httpx.post", return_value=response):
            ok, detail = _probe_http("http://localhost:8765/mcp", token="bad")

        assert ok is False
        assert "rejected" in detail


class TestMcpConfigCommand:
    def _write_config(self, tmp_path, sample_config):
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(sample_config.model_dump_json(indent=2))
        return cfg_path

    def test_native_writes_primary_only(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg_path = self._write_config(tmp_path, sample_config)
        result = runner.invoke(
            app,
            [
                "mcp-config",
                "--config",
                str(cfg_path),
                "--platform",
                "native",
                "--agents",
                "antigravity",
            ],
        )
        assert result.exit_code == 0
        agents_dir = tmp_path / ".agents"
        assert (agents_dir / "mcp_config.json").exists()
        assert not (agents_dir / "mcp_config.windows.json").exists()

    def test_windows_emits_wsl_launcher(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg_path = self._write_config(tmp_path, sample_config)
        result = runner.invoke(
            app,
            [
                "mcp-config",
                "--config",
                str(cfg_path),
                "--platform",
                "windows",
                "--agents",
                "antigravity",
            ],
        )
        assert result.exit_code == 0
        data = json.loads((tmp_path / ".agents" / "mcp_config.json").read_text())
        assert data["mcpServers"]["odoo-boost"]["command"] == "wsl.exe"

    def test_http_emits_url(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg_path = self._write_config(tmp_path, sample_config)
        result = runner.invoke(
            app,
            [
                "mcp-config",
                "--config",
                str(cfg_path),
                "--platform",
                "http",
                "--agents",
                "antigravity",
            ],
        )
        assert result.exit_code == 0
        data = json.loads((tmp_path / ".agents" / "mcp_config.json").read_text())
        server = data["mcpServers"]["odoo-boost"]
        assert server["serverUrl"] == "http://127.0.0.1:8765/mcp"
        assert "url" not in server

    def test_unknown_platform_rejected(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg_path = self._write_config(tmp_path, sample_config)
        result = runner.invoke(
            app, ["mcp-config", "--config", str(cfg_path), "--platform", "amiga"]
        )
        assert result.exit_code == 1


class TestManagedGitignore:
    def test_preserves_other_entries_and_only_removes_owned_entries(self, tmp_path):
        from odoo_boost.cli.gitignore import managed_entries, update_gitignore

        gitignore = tmp_path / ".gitignore"
        gitignore.write_text("__pycache__/\n/AGENTS.md\n")
        update_gitignore(tmp_path, add={"/odoo-boost.json", "/.mcp.json"})
        first = gitignore.read_text()
        update_gitignore(tmp_path, add={"/odoo-boost.json"})
        assert gitignore.read_text() == first
        assert managed_entries(tmp_path) == {"/odoo-boost.json", "/.mcp.json"}

        update_gitignore(tmp_path, remove={"/odoo-boost.json"})
        assert gitignore.read_text().startswith("__pycache__/\n/AGENTS.md\n")
        assert managed_entries(tmp_path) == {"/.mcp.json"}

    def test_creates_file_only_when_adding_entries(self, tmp_path):
        from odoo_boost.cli.gitignore import update_gitignore

        update_gitignore(tmp_path, remove={"/odoo-boost.json"})
        assert not (tmp_path / ".gitignore").exists()
        update_gitignore(tmp_path, add={"/odoo-boost.json"})
        assert "/odoo-boost.json" in (tmp_path / ".gitignore").read_text()


class TestLintCommand:
    def test_lint_help(self):
        result = runner.invoke(app, ["lint", "--help"])
        assert result.exit_code == 0
        assert "Run OCA coding standard checks" in result.output

    def test_lint_clean_file(self):
        result = runner.invoke(app, ["lint", "src/odoo_boost/__init__.py"])
        assert result.exit_code == 0
        assert "No issues found" in result.output

    def test_lint_issues_file(self, tmp_path):
        bad_file = tmp_path / "bad.py"
        bad_file.write_text(
            "from odoo import models\n\nclass BadModel(models.Model):\n    def test(self):\n        self.env.cr.commit()\n"
        )
        result = runner.invoke(app, ["lint", str(bad_file)])
        assert result.exit_code == 1
        assert "Linter Results" in result.output or "issues found" in result.output


class TestUninstallCommand:
    def test_uninstall_no_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["uninstall"])
        assert result.exit_code == 1
        assert "No odoo-boost.json found" in result.output

    def test_uninstall_abort_when_keeping_files(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "agents": ["antigravity"],
                "mcp_target": "native",
            }
        )
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(cfg.model_dump_json(indent=2))
        runner.invoke(app, ["update", "--config", str(cfg_path)])
        assert (tmp_path / "AGENTS.md").exists()

        # Input 'y' to "Do you want to keep generated agent files?"
        result = runner.invoke(app, ["uninstall", "--config", str(cfg_path)], input="y\n")
        assert result.exit_code == 0
        assert "Aborted uninstall. Keeping all files." in result.output
        assert (tmp_path / "AGENTS.md").exists()
        assert cfg_path.exists()

    def test_uninstall_default_enter_deletes_all(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "agents": ["antigravity"],
                "mcp_target": "native",
            }
        )
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(cfg.model_dump_json(indent=2))
        runner.invoke(app, ["update", "--config", str(cfg_path)])
        assert (tmp_path / "AGENTS.md").exists()

        # Two enters = default 'N' (don't keep agent files) and default 'N' (don't keep config)
        result = runner.invoke(app, ["uninstall", "--config", str(cfg_path)], input="\n\n")
        assert result.exit_code == 0
        assert "Uninstall complete!" in result.output
        assert not (tmp_path / "AGENTS.md").exists()
        assert not (tmp_path / ".agents").exists()
        assert not cfg_path.exists()

    def test_uninstall_yes_flag(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "agents": ["antigravity", "claude_code"],
                "mcp_target": "native",
            }
        )
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(cfg.model_dump_json(indent=2))
        runner.invoke(app, ["update", "--config", str(cfg_path)])
        assert (tmp_path / "AGENTS.md").exists()
        assert (tmp_path / "CLAUDE.md").exists()

        result = runner.invoke(app, ["uninstall", "--config", str(cfg_path), "-y"])
        assert result.exit_code == 0
        assert not (tmp_path / "AGENTS.md").exists()
        assert not (tmp_path / "CLAUDE.md").exists()
        assert not (tmp_path / ".mcp.json").exists()
        assert not (tmp_path / ".agents").exists()
        assert not cfg_path.exists()

    def test_uninstall_keep_config_flag(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = sample_config.model_copy(
            update={
                "project_path": str(tmp_path),
                "agents": ["antigravity"],
                "mcp_target": "native",
            }
        )
        cfg_path = tmp_path / "odoo-boost.json"
        cfg_path.write_text(cfg.model_dump_json(indent=2))
        runner.invoke(app, ["update", "--config", str(cfg_path)])
        assert (tmp_path / "AGENTS.md").exists()

        result = runner.invoke(app, ["uninstall", "--config", str(cfg_path), "-y", "--keep-config"])
        assert result.exit_code == 0
        assert not (tmp_path / "AGENTS.md").exists()
        assert cfg_path.exists()
