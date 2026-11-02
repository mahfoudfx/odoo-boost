"""Linter failures must not become successful validation claims."""

from __future__ import annotations

import json
import sys
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from odoo_boost import diagnostics
from odoo_boost.cli.app import app


@pytest.mark.parametrize(("cursor", "expected"), [("cr", 1), ("self.env.cr", 1), ("db", 0)])
def test_optional_linter_fallback_prunes_generated_files(monkeypatch, tmp_path, cursor, expected):
    monkeypatch.setitem(sys.modules, "pylint_odoo", None)
    (tmp_path / "model.py").write_text(f"def save(self):\n    {cursor}.commit()\n")
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "generated.py").write_text("not valid python!")

    result = diagnostics.run_lint(tmp_path, version="18.0")

    assert result["engine"] == "ast-fallback"
    assert result["total_issues"] == expected
    assert result["success"] is (expected == 0)
    assert all(issue["code"] == "E8102" for issue in result["issues"])


@pytest.mark.parametrize("stdout", ["", "not json", "{}", "[1]"])
def test_invalid_linter_output_fails(monkeypatch, tmp_path, stdout):
    monkeypatch.setitem(sys.modules, "pylint_odoo", SimpleNamespace())
    monkeypatch.setattr(
        diagnostics.subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(stdout=stdout, stderr="failed", returncode=32),
    )
    result = diagnostics.run_lint(tmp_path)
    assert result["success"] is False
    assert "error" in result


def test_linter_preserves_all_diagnostics_and_passes_target_version(monkeypatch, tmp_path):
    monkeypatch.setitem(sys.modules, "pylint_odoo", SimpleNamespace())
    calls = []
    messages = [{"type": "warning", "message": str(i)} for i in range(40)]

    def run(cmd, **kwargs):
        calls.append(cmd)
        return SimpleNamespace(stdout=json.dumps(messages), stderr="", returncode=4)

    monkeypatch.setattr(diagnostics.subprocess, "run", run)
    result = diagnostics.run_lint(tmp_path, version="16.0")
    assert "--valid-odoo-versions=16.0" in calls[0]
    assert result["warnings"] == messages
    assert result["total_issues"] == 40


def test_cli_fails_on_fallback_errors(monkeypatch):
    monkeypatch.setattr(
        "odoo_boost.cli.lint_cmd.run_lint",
        lambda *a, **kw: {
            "success": False,
            "engine": "ast-fallback",
            "total_issues": 1,
            "issues": [{"type": "error", "message": "Syntax error"}],
        },
    )
    result = CliRunner().invoke(app, ["lint", "."])
    assert result.exit_code == 1


def test_cli_shows_all_diagnostics_independently_of_mcp_budget(monkeypatch):
    monkeypatch.setenv("ODOO_BOOST_MAX_RESPONSE_CHARS", "20")
    messages = [{"type": "warning", "message": f"warning {i}"} for i in range(34)]
    messages.append({"type": "warning", "message": "last-warning"})
    monkeypatch.setattr(
        "odoo_boost.cli.lint_cmd.run_lint",
        lambda *a, **kw: {
            "success": True,
            "engine": "pylint-odoo",
            "total_issues": len(messages),
            "warnings": messages,
        },
    )
    result = CliRunner().invoke(app, ["lint", "."])
    assert result.exit_code == 0
    assert "last-warning" in result.output
    strict = CliRunner().invoke(app, ["lint", ".", "--strict"])
    assert strict.exit_code == 1
