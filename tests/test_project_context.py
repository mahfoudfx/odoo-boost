"""Project paths must be useful without broad scans or misleading access claims."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from odoo_boost.cli.install import _detect_project_venv
from odoo_boost.config.schema import OdooBoostConfig, OdooConnection
from odoo_boost.mcp_server.context import ServerContext, bound_context
from odoo_boost.mcp_server.tools.search_docs import search_docs
from odoo_boost.project_context import project_context


def _config(tmp_path, **updates):
    return OdooBoostConfig(
        connection=OdooConnection(url="http://localhost:8069", database="test"),
        project_path=str(tmp_path),
        **updates,
    )


def test_project_context_reports_venv_and_external_access_separately(tmp_path):
    project = tmp_path / "custom"
    project.mkdir()
    venv = project / ".venv"
    (venv / "bin").mkdir(parents=True)
    (venv / "pyvenv.cfg").write_text("home = /usr/bin\n")
    (venv / "bin" / "python").write_text("")
    core = tmp_path / "odoo"
    core.mkdir()
    conf = project / "odoo.conf"
    conf.write_text(f"[options]\naddons_path = {project}, {core}, relative/addons\n")

    result = project_context(
        _config(
            project,
            venv_path=".venv",
            odoo_conf_path="odoo.conf",
            odoo_source_path=str(core),
            odoo_version="18.0",
        )
    )

    assert result["venv"]["valid"] is True
    assert result["venv"]["python"] == str(venv / "bin" / "python")
    assert result["addons_path_source"] == "odoo.conf"
    assert result["addons_path"][0]["mcp_file_access"] == "allowed"
    assert result["addons_path"][1]["mcp_file_access"] == "outside_allowed_roots"
    assert result["addons_path"][2] == {
        "raw_path": "relative/addons",
        "status": "relative_to_unknown_launch_cwd",
    }
    assert result["odoo_source"]["path"] == str(core)


def test_launch_override_wins_and_external_root_can_be_allowed(tmp_path):
    project = tmp_path / "custom"
    project.mkdir()
    core = tmp_path / "odoo"
    core.mkdir()
    (project / "odoo.conf").write_text("[options]\naddons_path = /wrong\n")
    result = project_context(
        _config(
            project,
            odoo_conf_path="odoo.conf",
            addons_path_override=[str(core)],
            allowed_roots=[str(project), str(core)],
        )
    )
    assert result["addons_path_source"] == "launch_override"
    assert result["addons_path"] == [
        {"path": str(core), "exists": True, "mcp_file_access": "allowed"}
    ]


def test_relative_addons_use_explicit_launch_directory(tmp_path):
    project = tmp_path / "custom"
    project.mkdir()
    launch = tmp_path / "server"
    addons = launch / "addons"
    addons.mkdir(parents=True)
    result = project_context(
        _config(project, odoo_launch_cwd=str(launch), addons_path_override=["addons"])
    )
    assert result["addons_path"] == [
        {
            "raw_path": "addons",
            "path": str(addons),
            "exists": True,
            "mcp_file_access": "outside_allowed_roots",
        }
    ]


def test_missing_conf_is_compact_and_does_not_leak_other_options(tmp_path):
    conf = tmp_path / "odoo.conf"
    conf.write_text("[options]\nadmin_passwd = secret\naddons_path = /addons\n")
    result = project_context(_config(tmp_path, odoo_conf_path=str(conf)))
    assert result["addons_path"][0]["path"] == "/addons"
    assert "secret" not in str(result)


def test_search_docs_uses_configured_local_checkout_when_page_exists(tmp_path):
    page = tmp_path / "docs" / "content" / "developer" / "reference" / "backend" / "orm.rst"
    page.parent.mkdir(parents=True)
    page.write_text("ORM reference\n")
    config = _config(tmp_path, odoo_version="18.0", odoo_docs_path="docs")
    with bound_context(ServerContext(connection=MagicMock(), config=config)):
        result = json.loads(search_docs("orm"))
    assert result["results"][0]["local_source"] == str(page)


def test_installer_prefers_active_project_venv_over_its_own_python(tmp_path, monkeypatch):
    project = tmp_path / "custom"
    project.mkdir()
    venv = tmp_path / "odoo-venv"
    venv.mkdir()
    (venv / "pyvenv.cfg").write_text("home = /usr/bin\n")
    monkeypatch.setenv("VIRTUAL_ENV", str(venv))
    assert _detect_project_venv(project) == str(venv)
    monkeypatch.delenv("VIRTUAL_ENV")
    assert _detect_project_venv(project) is None
