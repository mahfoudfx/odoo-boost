"""Access introspection follows the connected server's security schema."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

import pytest

from odoo_boost.connection.base import OdooConnection
from odoo_boost.mcp_server.tools.list_access_rights import list_access_rights


@pytest.fixture()
def unified_connection(server_context):
    conn = MagicMock(spec=OdooConnection)
    conn.get_version.return_value = {"server_serie": "20.0", "server_version": "20.0"}
    permission = {
        "name": "Editors",
        "model_id": [5, "example.document"],
        "group_id": [8, "Editors"],
        "operation": "cru",
        "domain": "[('owner_id', '=', user.id)]",
    }
    restriction = {
        "name": "Enabled companies",
        "model_id": [5, "example.document"],
        "group_id": False,
        "operation": "rud",
        "domain": "[('company_id', 'in', company_ids)]",
    }

    def is_permission(model, domain):
        # Reproduce the removed-model failure, rather than returning empty results.
        assert model == "ir.access", f"Odoo 20 has no legacy access model: {model}"
        assert ("group_id", "!=", False) in domain or ("group_id", "=", False) in domain
        return ("group_id", "!=", False) in domain

    def search_read(model, **kwargs):
        record = permission if is_permission(model, kwargs["domain"]) else restriction
        assert set(kwargs["fields"]) <= {"name", "model_id", "group_id", "operation", "domain"}
        return [dict(record)]

    conn.search_count.side_effect = lambda model, domain: 12 if is_permission(model, domain) else 3
    conn.search_read.side_effect = search_read
    server_context.connection = conn
    # Intentionally retain the stale config version (18): the live server wins.
    return conn, permission, restriction


def test_odoo20_uses_unified_permissions_and_restrictions(unified_connection):
    conn, _, _ = unified_connection
    data = json.loads(list_access_rights("example.document", limit=2, offset=4))
    assert data["security_model"] == "ir.access"
    assert data["access_rights_total"] == 12
    assert data["record_rules_total"] == 3
    assert data["access_rights_returned"] == data["record_rules_returned"] == 1
    permission = data["access_rights"][0]
    restriction = data["record_rules"][0]
    assert permission["kind"] == "permission"
    assert permission["group"] == "Editors"
    assert permission["domain"] == "[('owner_id', '=', user.id)]"
    assert permission["create"] and permission["read"] and permission["write"]
    assert permission["unlink"] is False
    assert restriction["kind"] == "restriction" and restriction["global"] is True
    assert restriction["read"] and restriction["write"] and restriction["unlink"]
    assert restriction["create"] is False
    for call in conn.search_count.call_args_list:
        assert ("model_id.model", "=", "example.document") in call.args[1]
    for call in conn.search_read.call_args_list:
        assert ("model_id.model", "=", "example.document") in call.kwargs["domain"]
        assert call.kwargs["limit"] == 2 and call.kwargs["offset"] == 4


@pytest.mark.parametrize(
    "operation",
    ["c", "r", "u", "d", "cr", "cu", "cd", "ru", "rd", "ud", "cru", "crd", "cud", "rud", "crud"],
)
def test_odoo20_operation_selection(unified_connection, operation):
    _, permission, restriction = unified_connection
    permission["operation"] = restriction["operation"] = operation
    data = json.loads(list_access_rights())
    for entry in [*data["access_rights"], *data["record_rules"]]:
        assert entry["operation"] == operation
        assert (entry["create"], entry["read"], entry["write"], entry["unlink"]) == (
            "c" in operation,
            "r" in operation,
            "u" in operation,
            "d" in operation,
        )


@pytest.mark.parametrize(
    "kwargs, truncated",
    [({}, True), ({"response_format": "full"}, False), ({"model_name": "example.document"}, False)],
)
def test_odoo20_domain_compaction(unified_connection, kwargs, truncated):
    _, permission, restriction = unified_connection
    permission["domain"] = restriction["domain"] = "x" * 300
    data = json.loads(list_access_rights(**kwargs))
    for entry in [*data["access_rights"], *data["record_rules"]]:
        assert ("truncated" in entry["domain"]) is truncated
        if not truncated:
            assert entry["domain"] == "x" * 300


def test_odoo20_empty_page_keeps_totals(unified_connection):
    conn, _, _ = unified_connection
    conn.search_read.side_effect = None
    conn.search_read.return_value = []
    data = json.loads(list_access_rights(offset=100))
    assert data["access_rights"] == data["record_rules"] == []
    assert data["access_rights_returned"] == data["record_rules_returned"] == 0
    assert data["access_rights_total"] == 12 and data["record_rules_total"] == 3


def test_odoo20_unset_domain_stays_unrestricted(unified_connection):
    _, permission, restriction = unified_connection
    permission["domain"] = restriction["domain"] = False
    data = json.loads(list_access_rights())
    assert data["access_rights"][0]["domain"] == ""
    assert data["record_rules"][0]["domain"] == ""
    assert data["record_rules"][0]["group"] == ""


@pytest.mark.parametrize("series", ["15.0", "17.0", "18.0", "19.0"])
def test_older_servers_keep_legacy_response(server_context, monkeypatch, series):
    conn = server_context.connection
    monkeypatch.setattr(conn, "get_version", lambda: {"server_serie": series})
    server_context.config.odoo_version = "20.0"
    count = MagicMock(wraps=conn.search_count)
    read = MagicMock(wraps=conn.search_read)
    monkeypatch.setattr(conn, "search_count", count)
    monkeypatch.setattr(conn, "search_read", read)
    data = json.loads(list_access_rights())
    assert {call.args[0] for call in read.call_args_list} == {"ir.model.access", "ir.rule"}
    assert {call.args[0] for call in count.call_args_list} == {"ir.model.access", "ir.rule"}
    assert data["access_rights"] and data["record_rules"]
    assert "kind" not in data["access_rights"][0]


def test_unified_rpc_failure_does_not_fall_back(unified_connection):
    conn, _, _ = unified_connection
    conn.search_count.side_effect = PermissionError("Metadata access denied")
    with pytest.raises(PermissionError, match="Metadata access denied"):
        list_access_rights()
    assert conn.search_count.call_args.args[0] == "ir.access"
    conn.search_read.assert_not_called()


@pytest.mark.parametrize("version", [{}, {"server_serie": "21.0"}, {"server_serie": "20.1"}])
def test_unknown_schema_does_not_guess_legacy_models(unified_connection, version):
    conn, _, _ = unified_connection
    conn.get_version.return_value = version
    with pytest.raises(ValueError, match="Cannot select access metadata schema"):
        list_access_rights()
    conn.search_count.assert_not_called()
    conn.search_read.assert_not_called()


def test_version_lookup_failure_does_not_use_stale_config(unified_connection):
    conn, _, _ = unified_connection
    conn.get_version.side_effect = ConnectionError("Version endpoint unavailable")
    with pytest.raises(ConnectionError, match="Version endpoint unavailable"):
        list_access_rights()
    conn.search_count.assert_not_called()
    conn.search_read.assert_not_called()
