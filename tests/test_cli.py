"""Tests for odoo_boost.cli via typer.testing.CliRunner."""

from __future__ import annotations

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
        assert "18.0" in result.output


class TestUpdateCommand:
    def test_update_no_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["update"])
        assert result.exit_code == 1


class TestMcpCommand:
    def test_mcp_no_config(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = runner.invoke(app, ["mcp"])
        assert result.exit_code == 1


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
