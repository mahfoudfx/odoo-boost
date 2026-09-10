"""Tests for compact-by-default tool responses and the response budget."""

from __future__ import annotations

import json

from odoo_boost.mcp_server.tools._common import (
    compact_text,
    is_secret_key,
    redact,
    resolve_full,
)
from odoo_boost.mcp_server.tools.application_info import application_info
from odoo_boost.mcp_server.tools.database_schema import database_schema
from odoo_boost.mcp_server.tools.execute_method import execute_method
from odoo_boost.mcp_server.tools.get_config import get_config
from odoo_boost.mcp_server.tools.inspect_local_addon import inspect_local_addon
from odoo_boost.mcp_server.tools.list_access_rights import list_access_rights
from odoo_boost.mcp_server.tools.list_views import list_views
from odoo_boost.mcp_server.tools.read_log_entries import read_log_entries
from odoo_boost.mcp_server.tools.search_records import search_records


class TestResolveFull:
    def test_per_call_wins(self, server_context):
        assert resolve_full("full") is True
        assert resolve_full("compact") is False
        assert resolve_full(None) is False

    def test_config_flip_defaults_to_full(self, server_context):
        server_context.config.compact_responses = False
        assert resolve_full(None) is True
        assert resolve_full("compact") is False


class TestResponseBudget:
    def test_oversized_payload_is_wrapped(self, server_context):
        server_context.config.max_response_chars = 200
        data = json.loads(search_records("res.partner"))
        assert data["truncated"] is True
        assert data["full_length"] > 200
        assert "preview" in data

    def test_zero_disables_budget(self, server_context):
        server_context.config.max_response_chars = 0
        data = json.loads(search_records("res.partner"))
        assert "truncated" not in data
        assert "records" in data

    def test_full_execute_method_bypasses_budget(self, server_context):
        server_context.config.max_response_chars = 50
        data = json.loads(execute_method("res.partner", "name_search", response_format="full"))
        assert "result" in data
        assert data.get("truncated") is not True


class TestCompactTextAndSecrets:
    def test_compact_text_marker(self):
        assert compact_text("short", 10) == "short"
        truncated = compact_text("a" * 30, 10)
        assert truncated.startswith("a" * 10)
        assert "30 chars total" in truncated

    def test_secret_detection(self):
        assert is_secret_key("smtp.password")
        assert is_secret_key("database.secret")
        assert is_secret_key("api_key")
        assert not is_secret_key("web.base.url")

    def test_redact(self):
        assert redact("value", reveal=False) == ("***redacted***", True)
        assert redact("value", reveal=True) == ("value", False)


class TestListViews:
    def test_compact_omits_arch(self, server_context):
        data = json.loads(list_views())
        assert data["included_arch"] is False
        assert "arch" not in data["views"][0]
        assert "arch_length" in data["views"][0]
        assert data["returned"] == 2

    def test_full_includes_arch(self, server_context):
        data = json.loads(list_views(response_format="full"))
        assert data["included_arch"] is True
        assert "arch" in data["views"][0]

    def test_single_view_by_id(self, server_context):
        data = json.loads(list_views(view_id=1, include_arch=True))
        assert data["returned"] == 1
        assert data["views"][0]["id"] == 1


class TestDatabaseSchema:
    def test_compact_omits_help(self, server_context):
        data = json.loads(database_schema("res.partner"))
        assert data["response_format"] == "compact"
        assert "help" not in data["fields"][0]
        assert "label" not in data["fields"][0]

    def test_full_includes_help(self, server_context):
        data = json.loads(database_schema("res.partner", response_format="full"))
        assert "help" in data["fields"][0]
        assert "label" in data["fields"][0]

    def test_field_name_filter(self, server_context):
        data = json.loads(database_schema("res.partner", field_name="email"))
        assert data["field_count"] == 1
        assert data["fields"][0]["name"] == "email"


class TestGetConfig:
    def _seed(self, server_context, value: str) -> None:
        server_context.connection.seed(
            "ir.config_parameter",
            [{"id": 1, "key": "smtp.password", "value": value}],
        )

    def test_secret_redacted(self, server_context):
        self._seed(server_context, "topsecret")
        data = json.loads(get_config(key="smtp.password", match="exact"))
        assert data["parameters"][0]["value"] == "***redacted***"
        assert data["parameters"][0]["redacted"] is True

    def test_secret_revealed(self, server_context):
        self._seed(server_context, "topsecret")
        data = json.loads(get_config(key="smtp.password", match="exact", reveal_secrets=True))
        assert data["parameters"][0]["value"] == "topsecret"

    def test_long_value_truncated(self, server_context):
        self._seed(server_context, "x" * 500)
        data = json.loads(get_config(key="smtp.password", match="exact", reveal_secrets=True))
        assert data["parameters"][0]["value_length"] == 500
        assert "truncated" in data["parameters"][0]["value"]

    def test_full_value_not_truncated(self, server_context):
        self._seed(server_context, "x" * 500)
        data = json.loads(
            get_config(
                key="smtp.password",
                match="exact",
                reveal_secrets=True,
                response_format="full",
            )
        )
        assert data["parameters"][0]["value"] == "x" * 500


class TestReadLogEntries:
    def _seed(self, server_context) -> None:
        server_context.connection.seed(
            "ir.logging",
            [
                {
                    "id": 1,
                    "create_date": "2026-01-01 00:00:00",
                    "name": "odoo.addons.x",
                    "level": "ERROR",
                    "dbname": "db",
                    "func": "f",
                    "path": "/x.py",
                    "line": "1",
                    "message": "m" * 2000,
                }
            ],
        )

    def test_compact_truncates_message(self, server_context):
        self._seed(server_context)
        data = json.loads(read_log_entries())
        assert data["entries"][0]["message_length"] == 2000
        assert "truncated" in data["entries"][0]["message"]

    def test_full_message(self, server_context):
        self._seed(server_context)
        data = json.loads(read_log_entries(response_format="full"))
        assert data["entries"][0]["message"] == "m" * 2000


class TestAccessRights:
    def test_unfiltered_domain_truncated(self, server_context):
        server_context.connection.seed(
            "ir.rule",
            [
                {
                    "id": 1,
                    "name": "rule",
                    "model_id": [1, "res.partner"],
                    "groups": [],
                    "domain_force": "x" * 300,
                    "perm_read": True,
                    "perm_write": True,
                    "perm_create": True,
                    "perm_unlink": True,
                    "global": True,
                }
            ],
        )
        data = json.loads(list_access_rights())
        assert "truncated" in data["record_rules"][0]["domain"]

    def test_full_keeps_domain(self, server_context):
        server_context.connection.seed(
            "ir.rule",
            [
                {
                    "id": 1,
                    "name": "rule",
                    "model_id": [1, "res.partner"],
                    "groups": [],
                    "domain_force": "x" * 300,
                    "perm_read": True,
                    "perm_write": True,
                    "perm_create": True,
                    "perm_unlink": True,
                    "global": True,
                }
            ],
        )
        data = json.loads(list_access_rights(response_format="full"))
        assert data["record_rules"][0]["domain"] == "x" * 300


class TestSearchRecordsCompact:
    def test_compact_matches_full_count(self, server_context):
        raw = json.loads(search_records("res.partner"))
        compact = json.loads(search_records("res.partner", compact=True))
        assert raw["returned_count"] == compact["returned_count"]


class TestInspectLocalAddon:
    def _make_addon(self, tmp_path):
        (tmp_path / "__manifest__.py").write_text('{"name": "Local", "version": "1.0"}')
        (tmp_path / "models.py").write_text(
            "from odoo import models, fields\n"
            "class Local(models.Model):\n"
            '    _name = "local.test"\n'
            "    name = fields.Char()\n"
        )
        (tmp_path / "views.xml").write_text(
            '<odoo><record id="view_test" model="ir.ui.view"></record></odoo>'
        )
        return tmp_path

    def test_compact_summary(self, server_context, tmp_path):
        path = self._make_addon(tmp_path)
        data = json.loads(inspect_local_addon(str(path)))
        assert data["response_format"] == "compact"
        assert data["counts"]["models"] == 1
        assert data["models"][0]["field_count"] == 1
        assert "records" not in data

    def test_full_scan(self, server_context, tmp_path):
        path = self._make_addon(tmp_path)
        data = json.loads(inspect_local_addon(str(path), response_format="full"))
        assert data["response_format"] == "full"
        assert "records" in data

    def test_model_filter(self, server_context, tmp_path):
        path = self._make_addon(tmp_path)
        data = json.loads(inspect_local_addon(str(path), model="local.test"))
        assert data["found"] is True
        assert data["definitions"][0]["_name"] == "local.test"

    def test_xml_id_lookup(self, server_context, tmp_path):
        path = self._make_addon(tmp_path)
        data = json.loads(inspect_local_addon(str(path), xml_id="view_test"))
        assert data["found"] is True
        assert data["definition"]["id"] == "view_test"


class TestApplicationInfoCompact:
    def test_default_has_no_module_list(self, server_context):
        data = json.loads(application_info())
        assert data["installed_modules_count"] == 2
        assert "installed_modules" not in data
