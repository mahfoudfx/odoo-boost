"""Tests for all 15 MCP tools using MockOdooConnection."""

from __future__ import annotations

import json

import pytest

from odoo_boost.mcp_server.tools.aggregate_records import aggregate_records
from odoo_boost.mcp_server.tools.application_info import application_info
from odoo_boost.mcp_server.tools.check_odoo_ls import check_odoo_ls
from odoo_boost.mcp_server.tools.database_query import database_query
from odoo_boost.mcp_server.tools.database_schema import database_schema
from odoo_boost.mcp_server.tools.execute_method import execute_method
from odoo_boost.mcp_server.tools.get_config import get_config
from odoo_boost.mcp_server.tools.get_model_inheritance import get_model_inheritance
from odoo_boost.mcp_server.tools.get_module_info import get_module_info
from odoo_boost.mcp_server.tools.inspect_local_addon import inspect_local_addon
from odoo_boost.mcp_server.tools.lint_odoo_code import lint_odoo_code
from odoo_boost.mcp_server.tools.list_access_rights import list_access_rights
from odoo_boost.mcp_server.tools.list_menus import list_menus
from odoo_boost.mcp_server.tools.list_models import list_models
from odoo_boost.mcp_server.tools.list_routes import list_routes
from odoo_boost.mcp_server.tools.list_views import list_views
from odoo_boost.mcp_server.tools.list_workflows import list_workflows
from odoo_boost.mcp_server.tools.read_log_entries import read_log_entries
from odoo_boost.mcp_server.tools.resolve_local_xml_id import resolve_local_xml_id
from odoo_boost.mcp_server.tools.resolve_xml_id import resolve_xml_id
from odoo_boost.mcp_server.tools.search_docs import search_docs
from odoo_boost.mcp_server.tools.search_records import search_records

pytestmark = pytest.mark.usefixtures("server_context")


# ---------------------------------------------------------------------------
# application_info
# ---------------------------------------------------------------------------


class TestApplicationInfo:
    def test_returns_json(self):
        result = json.loads(application_info())
        assert "server_version" in result
        assert result["server_version"] == "18.0"

    def test_installed_modules(self):
        result = json.loads(application_info(include_modules=True))
        assert result["installed_modules_count"] == 2  # base + sale (installed)
        names = [m["name"] for m in result["installed_modules"]]
        assert "base" in names
        assert "sale" in names

    def test_compact_omits_module_list(self):
        result = json.loads(application_info())
        assert result["installed_modules_count"] == 2
        assert "installed_modules" not in result


# ---------------------------------------------------------------------------
# database_schema
# ---------------------------------------------------------------------------


class TestDatabaseSchema:
    def test_known_model(self):
        result = json.loads(database_schema("res.partner"))
        assert result["model"] == "res.partner"
        assert result["field_count"] == 3

    def test_unknown_model(self):
        result = json.loads(database_schema("nonexistent.model"))
        assert "error" in result

    def test_fields_have_type(self):
        result = json.loads(database_schema("res.partner"))
        types = {f["name"]: f["type"] for f in result["fields"]}
        assert types["name"] == "char"
        assert types["company_id"] == "many2one"


# ---------------------------------------------------------------------------
# database_query
# ---------------------------------------------------------------------------


class TestDatabaseQuery:
    def test_basic_query(self):
        result = json.loads(database_query("res.partner"))
        assert result["model"] == "res.partner"
        assert result["total_count"] == 2
        assert result["returned_count"] == 2

    def test_domain_filter(self):
        result = json.loads(database_query("res.partner", domain='[["is_company", "=", true]]'))
        assert result["total_count"] == 1

    def test_fields_filter(self):
        result = json.loads(database_query("res.partner", fields='["name"]'))
        for rec in result["records"]:
            assert "name" in rec

    def test_limit(self):
        result = json.loads(database_query("res.partner", limit=1))
        assert result["returned_count"] == 1


# ---------------------------------------------------------------------------
# list_models
# ---------------------------------------------------------------------------


class TestListModels:
    def test_returns_models(self):
        result = json.loads(list_models())
        assert result["total"] == 2

    def test_filter_by_name(self):
        result = json.loads(list_models(filter_name="partner"))
        assert result["total"] == 1
        assert result["models"][0]["model"] == "res.partner"

    def test_field_count(self):
        result = json.loads(list_models())
        partner = [m for m in result["models"] if m["model"] == "res.partner"][0]
        assert partner["field_count"] == 3


# ---------------------------------------------------------------------------
# list_views
# ---------------------------------------------------------------------------


class TestListViews:
    def test_all_views(self):
        result = json.loads(list_views())
        assert result["total"] == 2

    def test_filter_by_model(self):
        result = json.loads(list_views(model_name="res.partner"))
        assert result["total"] == 2

    def test_filter_by_type(self):
        result = json.loads(list_views(view_type="form"))
        assert result["total"] == 1
        assert result["views"][0]["type"] == "form"


# ---------------------------------------------------------------------------
# list_menus
# ---------------------------------------------------------------------------


class TestListMenus:
    def test_root_menus(self):
        result = json.loads(list_menus(parent_id=0))
        assert result["total"] == 1
        assert result["menus"][0]["name"] == "Sales"

    def test_all_menus(self):
        result = json.loads(list_menus(parent_id=-1))
        assert result["total"] == 2


# ---------------------------------------------------------------------------
# list_routes
# ---------------------------------------------------------------------------


class TestListRoutes:
    def test_returns_result(self):
        # No website.page / website.rewrite seeded, so routes should be empty
        # (the tool catches exceptions silently)
        result = json.loads(list_routes())
        assert "total" in result
        assert "routes" in result
        assert "scope" in result

    def test_rewrite_filter_uses_existing_fields(self, monkeypatch):
        from unittest.mock import MagicMock

        conn = MagicMock()
        conn.search_read.return_value = []
        monkeypatch.setattr("odoo_boost.mcp_server.tools.list_routes.get_connection", lambda: conn)
        list_routes(filter_url="shop")
        rewrite_call = conn.search_read.call_args_list[1]
        assert rewrite_call.kwargs["domain"] == [
            "|",
            ("url_from", "ilike", "shop"),
            ("url_to", "ilike", "shop"),
        ]

    def test_unavailable_source_reported(self, monkeypatch):
        from unittest.mock import MagicMock
        from xmlrpc.client import Fault

        conn = MagicMock()
        conn.search_read.side_effect = [Fault(1, "AccessError: forbidden"), []]
        monkeypatch.setattr("odoo_boost.mcp_server.tools.list_routes.get_connection", lambda: conn)
        result = json.loads(list_routes())
        assert result["complete"] is False
        assert result["unavailable"]["website.page"] == "access denied"

    def test_connection_failure_is_not_reported_as_empty(self, monkeypatch):
        from unittest.mock import MagicMock

        conn = MagicMock()
        conn.search_read.side_effect = ConnectionError("Odoo offline")
        monkeypatch.setattr("odoo_boost.mcp_server.tools.list_routes.get_connection", lambda: conn)
        with pytest.raises(ConnectionError, match="Odoo offline"):
            list_routes()


# ---------------------------------------------------------------------------
# list_access_rights
# ---------------------------------------------------------------------------


class TestListAccessRights:
    def test_returns_acls_and_rules(self):
        result = json.loads(list_access_rights())
        assert "access_rights" in result
        assert "record_rules" in result

    def test_has_entries(self):
        result = json.loads(list_access_rights())
        assert len(result["access_rights"]) >= 1
        assert len(result["record_rules"]) >= 1


# ---------------------------------------------------------------------------
# get_config
# ---------------------------------------------------------------------------


class TestGetConfig:
    def test_all_params(self):
        result = json.loads(get_config())
        assert result["total"] == 2

    def test_filter_by_key(self):
        result = json.loads(get_config(key="web.base"))
        assert result["total"] == 1
        assert result["parameters"][0]["key"] == "web.base.url"


# ---------------------------------------------------------------------------
# get_module_info
# ---------------------------------------------------------------------------


class TestGetModuleInfo:
    def test_known_module(self):
        result = json.loads(get_module_info("base"))
        assert result["name"] == "base"
        assert result["state"] == "installed"

    def test_unknown_module(self):
        result = json.loads(get_module_info("nonexistent_mod"))
        assert "error" in result


# ---------------------------------------------------------------------------
# search_records
# ---------------------------------------------------------------------------


class TestSearchRecords:
    def test_basic_search(self):
        result = json.loads(search_records("res.partner"))
        assert result["model"] == "res.partner"
        assert result["total_count"] == 2

    def test_with_domain(self):
        result = json.loads(search_records("res.partner", domain='[["is_company", "=", true]]'))
        assert result["total_count"] == 1


# ---------------------------------------------------------------------------
# execute_method
# ---------------------------------------------------------------------------


class TestExecuteMethod:
    def test_execute(self):
        result = json.loads(execute_method("res.partner", "name_search"))
        assert result["model"] == "res.partner"
        assert result["method"] == "name_search"
        assert "result" in result

    @pytest.mark.parametrize(
        ("args", "kwargs"),
        [('"not an array"', "{}"), ("[]", '"not an object"')],
    )
    def test_rejects_invalid_argument_shapes(self, args, kwargs):
        result = json.loads(execute_method("res.partner", "name_search", args=args, kwargs=kwargs))
        assert "error" in result


# ---------------------------------------------------------------------------
# read_log_entries
# ---------------------------------------------------------------------------


class TestReadLogEntries:
    def test_no_logs(self):
        # ir.logging not seeded, so should return empty or error
        result = json.loads(read_log_entries())
        # Could be {"total": 0, "entries": []} or {"error": ...}
        assert "total" in result or "error" in result


# ---------------------------------------------------------------------------
# search_docs
# ---------------------------------------------------------------------------


class TestSearchDocs:
    def test_list_all_topics(self):
        result = json.loads(search_docs())
        assert "available_topics" in result
        assert len(result["available_topics"]) > 10

    def test_search_orm(self):
        result = json.loads(search_docs(topic="orm"))
        assert "results" in result
        assert any("orm" in r["topic"].lower() for r in result["results"])

    def test_search_with_version(self):
        result = json.loads(search_docs(topic="views", version="17.0"))
        assert "results" in result
        assert any("/17.0/" in r["url"] for r in result["results"])

    def test_patch_version_normalized(self):
        result = json.loads(search_docs(topic="views", version="18.0.1"))
        assert any("/18.0/" in r["url"] for r in result["results"])

    def test_two_digit_major_version(self):
        result = json.loads(search_docs(topic="views", version="10.0"))
        assert result["supported"] is False
        assert result["results"] == []

    def test_invalid_version_does_not_guess(self):
        result = json.loads(search_docs(topic="views", version="latest"))
        assert result["supported"] is False
        assert result["results"] == []
        assert "warning" in result

    def test_no_match(self):
        result = json.loads(search_docs(topic="xyznonexistent"))
        assert "message" in result
        assert "available_topics" in result


# ---------------------------------------------------------------------------
# list_workflows
# ---------------------------------------------------------------------------


class TestListWorkflows:
    def test_returns_both_types(self):
        result = json.loads(list_workflows())
        assert "automated_actions" in result
        assert "server_actions" in result

    def test_filter_by_model(self):
        result = json.loads(list_workflows(model_name="res.partner"))
        if result["automated_actions"]:
            assert result["automated_actions"][0]["model"] == "res.partner"


# ---------------------------------------------------------------------------
# aggregate_records
# ---------------------------------------------------------------------------


class TestAggregateRecords:
    def test_aggregate_records_returns_groups(self):
        result = json.loads(aggregate_records("sale.order", groupby='["partner_id"]'))
        assert "model" in result
        assert result["model"] == "sale.order"
        assert "groups" in result
        assert len(result["groups"]) > 0


# ---------------------------------------------------------------------------
# resolve_xml_id
# ---------------------------------------------------------------------------


class TestResolveXmlId:
    def test_resolve_existing_xml_id(self):
        result = json.loads(resolve_xml_id("base.partner_admin"))
        assert result["found"] is True
        assert result["module"] == "base"
        assert result["model"] == "res.partner"

    def test_resolve_nonexistent_xml_id(self):
        result = json.loads(resolve_xml_id("nonexistent.id"))
        assert result["found"] is False


# ---------------------------------------------------------------------------
# get_model_inheritance
# ---------------------------------------------------------------------------


class TestGetModelInheritance:
    def test_get_model_inheritance_existing(self):
        result = json.loads(get_model_inheritance("res.partner"))
        assert result["found"] is True
        assert result["model"] == "res.partner"
        assert "contributing_modules" in result

    def test_get_model_inheritance_nonexistent(self):
        result = json.loads(get_model_inheritance("nonexistent.model"))
        assert result["found"] is False


# ---------------------------------------------------------------------------
# inspect_local_addon & resolve_local_xml_id
# ---------------------------------------------------------------------------


class TestLocalAddonTools:
    def test_inspect_local_addon(self, tmp_path):
        (tmp_path / "__manifest__.py").write_text('{"name": "Local Addon", "version": "1.0"}')
        (tmp_path / "models.py").write_text(
            'from odoo import models, fields\nclass Local(models.Model):\n    _name = "local.test"\n'
        )
        result = json.loads(inspect_local_addon(str(tmp_path)))
        assert result["addon_name"] == tmp_path.name
        assert len(result["models"]) == 1
        assert result["models"][0]["_name"] == "local.test"

    def test_resolve_local_xml_id(self, tmp_path):
        (tmp_path / "views.xml").write_text(
            '<odoo><record id="view_test" model="ir.ui.view"></record></odoo>'
        )
        result = json.loads(resolve_local_xml_id(str(tmp_path), "view_test"))
        assert result["found"] is True
        assert result["definition"]["id"] == "view_test"


# ---------------------------------------------------------------------------
# lint_odoo_code & check_odoo_ls
# ---------------------------------------------------------------------------


class TestLintAndLsTools:
    @pytest.mark.parametrize(
        ("version", "warns"),
        [("16.0", False), ("17.0", True), ("20.0", True), ("21.0", False)],
    )
    def test_name_get_warning_is_version_specific(
        self, tmp_path, monkeypatch, sample_config, version, warns
    ):
        import importlib

        lint_module = importlib.import_module("odoo_boost.mcp_server.tools.lint_odoo_code")
        source = tmp_path / "model.py"
        source.write_text("class Model:\n    def name_get(self):\n        return []\n")
        monkeypatch.setattr(
            lint_module,
            "active_config",
            lambda: sample_config.model_copy(update={"odoo_version": version}),
        )
        result = lint_module._run_fallback_ast_lint(source)
        assert any(issue.get("code") == "E8146" for issue in result["issues"]) is warns

    def test_lint_odoo_code(self, tmp_path):
        bad_file = tmp_path / "bad.py"
        bad_file.write_text(
            "from odoo import models\nclass Bad(models.Model):\n    def test(self):\n        self.env.cr.commit()\n"
        )
        result = json.loads(lint_odoo_code(str(bad_file)))
        assert "engine" in result
        assert result["total_issues"] > 0

    def test_check_odoo_ls(self):
        result = json.loads(check_odoo_ls())
        assert "installed" in result


# ---------------------------------------------------------------------------
# database_query compact mode
# ---------------------------------------------------------------------------


class TestDatabaseQueryCompact:
    def test_compact_mode(self):
        raw = json.loads(database_query("res.partner", compact=False))
        compact = json.loads(database_query("res.partner", compact=True))
        assert raw["returned_count"] == compact["returned_count"]
        # Compact records should omit None or empty values
        if compact["records"]:
            for _k, v in compact["records"][0].items():
                assert v is not None and v is not False and v != ""


# ---------------------------------------------------------------------------
# MCP v2 Server, Resources, and Prompts
# ---------------------------------------------------------------------------


class TestMcpServerV2:
    @pytest.mark.anyio
    async def test_server_resources_and_prompts(self, monkeypatch, mock_connection, sample_config):
        from odoo_boost.mcp_server.server import create_mcp_server

        monkeypatch.setattr(
            "odoo_boost.mcp_server.server.create_connection", lambda cfg: mock_connection
        )
        server = create_mcp_server(sample_config)

        # Verify resources
        resources = await server.list_resources()
        uris = [str(r.uri) for r in resources]
        assert "odoo://guidelines/oca" in uris
        assert "odoo://skills/catalog" in uris

        templates = await server.list_resource_templates()
        template_uris = [t.uri_template for t in templates]
        assert "odoo://schema/{model_name}" in template_uris

        # Verify prompts
        prompts = await server.list_prompts()
        prompt_names = [p.name for p in prompts]
        assert "review_odoo_addon" in prompt_names
        assert "upgrade_odoo_addon" in prompt_names

        # Verify tools count
        tools = await server.list_tools()
        assert len(tools) == 23

    @pytest.mark.anyio
    async def test_server_resilient_when_odoo_offline(
        self, monkeypatch, mock_connection, sample_config
    ):
        from unittest.mock import MagicMock

        from odoo_boost.mcp_server.server import create_mcp_server

        mock_connection.authenticate = MagicMock(
            side_effect=ConnectionError("Cannot connect to Odoo (502 Bad Gateway)")
        )
        monkeypatch.setattr(
            "odoo_boost.mcp_server.server.create_connection", lambda cfg: mock_connection
        )
        # Server must start successfully without crashing
        server = create_mcp_server(sample_config)
        tools = await server.list_tools()
        assert len(tools) == 23

    @pytest.mark.anyio
    async def test_live_tool_error_when_offline(self, monkeypatch, mock_connection, sample_config):
        from unittest.mock import MagicMock

        from mcp.server.mcpserver.exceptions import ToolError

        from odoo_boost.mcp_server.server import create_mcp_server

        mock_connection.authenticate = MagicMock(
            side_effect=ConnectionError("Cannot connect to Odoo (502 Bad Gateway)")
        )
        mock_connection.search_read = MagicMock(
            side_effect=ConnectionError("Cannot connect to Odoo (502 Bad Gateway)")
        )
        monkeypatch.setattr(
            "odoo_boost.mcp_server.server.create_connection", lambda cfg: mock_connection
        )
        server = create_mcp_server(sample_config)
        with pytest.raises(ToolError, match="502 Bad Gateway"):
            await server.call_tool("search_records", {"model": "res.partner"})
