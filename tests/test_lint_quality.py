"""Linter failures must not become successful validation claims."""

from __future__ import annotations

import importlib
import json
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from odoo_boost.cli.app import app

lint_module = importlib.import_module("odoo_boost.mcp_server.tools.lint_odoo_code")


@pytest.mark.parametrize("stdout", ["", "not json", "{}", "[1]"])
def test_invalid_linter_output_fails(monkeypatch, tmp_path, stdout):
    monkeypatch.setattr(
        lint_module.subprocess,
        "run",
        lambda *a, **kw: SimpleNamespace(stdout=stdout, stderr="failed", returncode=32),
    )
    result = lint_module._run_pylint_odoo(tmp_path)
    assert result["success"] is False
    assert "error" in result


def test_full_linter_output_and_target_version(monkeypatch, tmp_path, server_context):
    calls = []
    server_context.config.odoo_version = "16.0"
    diagnostics = [{"type": "warning", "message": str(i)} for i in range(40)]

    def run(cmd, **kwargs):
        calls.append(cmd)
        return SimpleNamespace(stdout=json.dumps(diagnostics), stderr="", returncode=4)

    monkeypatch.setattr(lint_module.subprocess, "run", run)
    result = lint_module._run_pylint_odoo(tmp_path)
    assert "--valid-odoo-versions=16.0" in calls[0]
    assert len(lint_module._compact_lint_result(result, full=True)["warnings"]) == 40
    assert len(lint_module._compact_lint_result(result, full=False)["warnings"]) == 30
    assert result["total_issues"] == 40


def test_cli_fails_on_fallback_errors(monkeypatch):
    monkeypatch.setattr(
        "odoo_boost.cli.lint_cmd.lint_odoo_code",
        lambda *a, **kw: json.dumps(
            {
                "success": False,
                "engine": "ast-fallback",
                "total_issues": 1,
                "issues": [{"type": "error", "message": "Syntax error"}],
            }
        ),
    )
    result = CliRunner().invoke(app, ["lint", "."])
    assert result.exit_code == 1
