"""Behavioral regressions for source discovery, diagnostics and execution boundaries."""

from __future__ import annotations

import json
import subprocess
from unittest.mock import patch

import pytest

from odoo_boost.config import OdooBoostConfig, OdooConnection, load_config
from odoo_boost.mcp_server.metrics import ToolMetrics
from odoo_boost.source_trace import source_index
from odoo_boost.static_checks import check_static
from odoo_boost.test_runner import run_tests
from odoo_boost.validation import diagnose, validation_plan


@pytest.fixture
def addon(tmp_path):
    (tmp_path / "__manifest__.py").write_text("{'name': 'Demo', 'data': ['missing.xml']}")
    (tmp_path / "models.py").write_text("""from odoo import models, fields, http
class Demo(models.Model):
    _name = 'demo.record'
    _inherit = ['mail.thread']
    _inherits = {'res.partner': 'partner_id'}
    name = fields.Char()
    def action(self):
        self.sudo()
        self.env.cr.execute(f"SELECT {self.name}")
class Controller(http.Controller):
    @http.route('/demo', auth='public', csrf=False)
    def demo(self): pass
    @http.route()
    def inherited(self): pass
""")
    (tmp_path / "views.xml").write_text(
        """<odoo><record id="demo_view" model="ir.ui.view"><field name="model">demo.record</field><field name="inherit_id" ref="base.parent"/></record></odoo>"""
    )
    return tmp_path


def test_source_relationships_and_overrides(addon):
    index = source_index(addon)
    assert index["complete"]
    assert index["models"][0]["inherits"] == {"res.partner": "partner_id"}
    assert index["models"][0]["inherit"] == ["mail.thread"]
    assert index["routes"][0]["routes"] == "/demo"
    assert index["routes"][1]["inherits_route"]
    assert index["views"][0]["inherit_id"] == "base.parent"


def test_static_errors_and_review_candidates(addon):
    report = check_static(addon, "18.0")
    codes = {i["code"]: i for i in report["issues"]}
    assert codes["OBMAN001"]["certainty"] == "definite"
    assert codes["OBACL001"]["certainty"] == "review_required"
    assert codes["OBSEC002"]["certainty"] == "review_required"
    assert "OBSEC001" in codes and "OBSEC003" in codes
    (addon / "ir.model.access.csv").write_text(
        "id,name,model_id:id,perm_read\naccess_demo,Demo,model_demo_record,1\n"
    )
    assert "OBACL001" not in {i["code"] for i in check_static(addon)["issues"]}


def test_xml_syntax_and_scope(addon, tmp_path):
    (addon / "bad.xml").write_text("<odoo>")
    assert any(i["code"] == "OBPARSE001" for i in check_static(addon)["issues"])
    report = check_static(addon / "models.py")
    assert not any(i["code"] == "OBACL001" for i in report["issues"])


def test_unified_partial_is_not_clean_pass(addon):
    with patch(
        "odoo_boost.validation.run_lint",
        return_value={"engine": "pylint-odoo", "error": "unavailable"},
    ):
        result = diagnose(addon / "views.xml")
    assert result["status"] == "partial"
    assert result["engines"]["lint"]["status"] == "unavailable"
    assert result["engines"]["odoo_ls"]["status"] == "not_run"


def test_changed_plan_includes_untracked_and_staged(tmp_path):
    def git(*args):
        return subprocess.run(["git", "-C", str(tmp_path), *args], check=True, capture_output=True)

    git("init")
    git(
        "-c",
        "user.email=test@example.com",
        "-c",
        "user.name=Test",
        "commit",
        "--allow-empty",
        "-m",
        "init",
    )
    (tmp_path / "models.py").write_text("pass")
    git("add", "models.py")
    (tmp_path / "view.xml").write_text("<odoo/>")
    plan = validation_plan(tmp_path)
    assert plan["files"] == ["models.py", "view.xml"]
    assert "focused-odoo-tests" in plan["recommended_checks"]
    with pytest.raises(ValueError):
        validation_plan(tmp_path, "--help")


def test_profiles_select_without_leaking_credentials(tmp_path, monkeypatch):
    data = {
        "connection": {"url": "http://local", "database": "local"},
        "profiles": {
            "production": {"url": "http://prod", "database": "prod", "password": "secret"}
        },
    }
    path = tmp_path / "odoo-boost.json"
    path.write_text(json.dumps(data))
    monkeypatch.setenv("ODOO_BOOST_PROFILE", "production")
    config = load_config(path)
    assert config.connection.database == "prod" and config.readonly
    monkeypatch.setenv("ODOO_BOOST_PROFILE", "typo")
    with pytest.raises(ValueError, match="Unknown"):
        load_config(path)


def test_test_runner_refuses_live_database(addon):
    config = OdooBoostConfig(
        connection=OdooConnection(url="http://local", database="live"), test_database="live"
    )
    with patch("subprocess.run") as run:
        result = run_tests(config, addon, "/demo", "live")
    assert result["status"] == "unavailable"
    run.assert_not_called()


def test_test_runner_no_tests_is_partial(addon):
    config = OdooBoostConfig(
        connection=OdooConnection(url="http://local", database="live"),
        test_database="tests",
        test_odoo_conf_path="/tmp/test.conf",
        venv_path="/tmp/venv",
        odoo_source_path="/tmp/odoo",
    )
    with patch("subprocess.run", return_value=subprocess.CompletedProcess([], 0, "", "")) as run:
        result = run_tests(config, addon, "/demo", "tests")
    assert result["status"] == "partial"
    assert "--stop-after-init" in run.call_args.args[0]


def test_metrics_store_no_arguments():
    metrics = ToolMetrics()
    metrics.record("search_records", 0.1, 50, False)
    metrics.record("search_records", 0.2, 0, True)
    entry = metrics.snapshot()["tools"]["search_records"]
    assert entry["calls"] == 2 and entry["failures"] == 1 and entry["response_chars"] == 50


def test_trace_follows_ancestors_without_including_prototype_children(addon):
    from odoo_boost.mcp_server.tools.development import trace_odoo_source

    (addon / "parents.py").write_text("""class Mail:
    _name = 'mail.thread'
    _inherit = 'base.thread'
class Child:
    _name = 'demo.child'
    _inherit = 'demo.record'
""")
    result = json.loads(trace_odoo_source(str(addon), "demo.record"))
    names = {m["name"] for m in result["models"]}
    assert "mail.thread" in names and "demo.child" not in names
    assert "base.thread" in result["unresolved_models"]


def test_mcp_budget_and_metrics(monkeypatch, sample_config, mock_connection):
    from mcp.server.mcpserver.exceptions import ToolError

    from odoo_boost.mcp_server.server import create_mcp_server

    class Server:
        def __init__(self, *args, **kwargs):
            self.handlers = {}

        def resource(self, *args, **kwargs):
            return lambda fn: fn

        def prompt(self, *args, **kwargs):
            return lambda fn: fn

        def tool(self):
            def register(fn):
                self.handlers[fn.__name__] = fn
                return fn

            return register

    monkeypatch.setattr("odoo_boost.mcp_server.server.MCPServer", Server)
    monkeypatch.setattr("odoo_boost.mcp_server.server.create_connection", lambda _: mock_connection)
    sample_config.max_tool_calls = 1
    server = create_mcp_server(sample_config)
    server.handlers["application_info"]()
    with pytest.raises(ToolError, match="budget exhausted"):
        server.handlers["list_models"]()
    metrics = json.loads(server.handlers["tool_metrics"]())
    assert metrics["tools"]["application_info"]["calls"] == 1
    assert metrics["tools"]["list_models"]["failures"] == 1
    assert "local_scan_caches" in metrics


def test_runtime_comparison(addon, server_context, mock_connection):
    from odoo_boost.mcp_server.tools.development import compare_local_runtime

    with (
        patch.object(mock_connection, "execute", return_value={"name": {}, "id": {}}),
        patch.object(mock_connection, "search_read", side_effect=[[], []]),
    ):
        result = json.loads(compare_local_runtime(str(addon), "demo.record"))
    assert result["local_fields_missing_at_runtime"] == []
    assert result["runtime_fields_not_declared_here"] == ["id"]
    assert result["local_xml_ids_missing_at_runtime"] == ["demo_view"]
