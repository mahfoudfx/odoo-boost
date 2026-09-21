"""Count-only investigation avoids record reads and exposes ORM errors safely."""

from __future__ import annotations

import json

from odoo_boost.mcp_server.tools.count_records import count_records


def test_count_records_uses_one_rpc(server_context, monkeypatch):
    calls = []
    connection = server_context.connection
    monkeypatch.setattr(
        connection, "search_count", lambda model, domain: calls.append((model, domain)) or 7
    )
    monkeypatch.setattr(
        connection,
        "search_read",
        lambda *args, **kwargs: (_ for _ in ()).throw(AssertionError("unexpected record read")),
    )
    result = json.loads(count_records("sale.order", '[["state", "=", "sale"]]'))
    assert result == {"model": "sale.order", "count": 7}
    assert calls == [("sale.order", [["state", "=", "sale"]])]


def test_bad_domain_does_not_call_odoo(server_context, monkeypatch):
    monkeypatch.setattr(
        server_context.connection,
        "search_count",
        lambda *args: (_ for _ in ()).throw(AssertionError("unexpected RPC")),
    )
    for domain in ('{ "state": "sale" }', "not-json"):
        result = json.loads(count_records("sale.order", domain))
        assert "error" in result
