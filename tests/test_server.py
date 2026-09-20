"""Tests for the MCP server construction (version, auth wiring, context)."""

from __future__ import annotations

from unittest.mock import MagicMock

import pytest
from mcp.server.mcpserver.exceptions import ToolError

import odoo_boost.mcp_server.server as server_mod
from odoo_boost.__version__ import __version__
from odoo_boost.mcp_server.context import get_context, reset_context


class _FakeMCPServer:
    """Minimal stand-in capturing constructor args and no-op decorators."""

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs
        self.registered = []
        self.resources = {}

    def resource(self, *args, **kwargs):
        def decorator(fn):
            self.resources[args[0]] = fn
            return fn

        return decorator

    def prompt(self, *args, **kwargs):
        return lambda fn: fn

    def tool(self, *args, **kwargs):
        def decorator(fn):
            self.registered.append(fn)
            return fn

        return decorator


def _run_create(monkeypatch, sample_config, **config_updates):
    captured: dict = {}

    def _factory(*args, **kwargs):
        server = _FakeMCPServer(*args, **kwargs)
        captured["server"] = server
        return server

    monkeypatch.setattr(server_mod, "MCPServer", _factory)
    conn = MagicMock()
    conn.authenticate.return_value = 2
    monkeypatch.setattr(server_mod, "create_connection", lambda cfg: conn)

    cfg = sample_config.model_copy(update=config_updates)
    server_mod.create_mcp_server(cfg)
    reset_context()
    return captured["server"]


class TestCreateMcpServer:
    def test_handlers_keep_their_own_server_context(self, monkeypatch, sample_config):
        monkeypatch.setattr(server_mod, "MCPServer", _FakeMCPServer)
        first_conn, second_conn = MagicMock(), MagicMock()
        first_conn.search_read.return_value = [{"id": 1}]
        second_conn.search_read.return_value = [{"id": 2}]
        connections = iter((first_conn, second_conn))
        monkeypatch.setattr(server_mod, "create_connection", lambda cfg: next(connections))

        first = server_mod.create_mcp_server(sample_config.model_copy(update={"readonly": True}))
        second = server_mod.create_mcp_server(sample_config.model_copy(update={"readonly": False}))
        first_tools = {fn.__name__: fn for fn in first.registered}
        second_tools = {fn.__name__: fn for fn in second.registered}

        assert '"id": 1' in first_tools["search_records"]("res.partner")
        assert '"id": 2' in second_tools["search_records"]("res.partner")
        assert get_context().connection is second_conn
        with pytest.raises(ToolError, match="readonly allowlist"):
            first_tools["execute_method"]("res.partner", "unlink")
        assert second_tools["execute_method"]("res.partner", "unlink")
        assert get_context().connection is second_conn

        monkeypatch.setattr(
            server_mod, "database_schema", lambda model: str(get_context().connection is first_conn)
        )
        assert first.resources["odoo://schema/{model_name}"]("res.partner") == "True"
        assert get_context().connection is second_conn
        reset_context()

    def test_sets_version(self, monkeypatch, sample_config):
        server = _run_create(monkeypatch, sample_config)
        assert server.kwargs["version"] == __version__

    def test_no_token_verifier_without_token(self, monkeypatch, sample_config):
        server = _run_create(monkeypatch, sample_config)
        assert server.kwargs["token_verifier"] is None
        assert server.kwargs["auth"] is None

    def test_token_verifier_when_token_set(self, monkeypatch, sample_config):
        server = _run_create(monkeypatch, sample_config, mcp_token="tok")
        verifier = server.kwargs["token_verifier"]
        assert verifier is not None
        assert server.kwargs["auth"] is not None

        import asyncio

        assert asyncio.run(verifier.verify_token("tok")) is not None
        assert asyncio.run(verifier.verify_token("nope")) is None

    def test_full_profile_registers_all_tools(self, monkeypatch, sample_config):
        server = _run_create(monkeypatch, sample_config, lean_tools=False)
        assert len(server.registered) == 22

    def test_default_registers_all_tools(self, monkeypatch, sample_config):
        server = _run_create(monkeypatch, sample_config)
        assert len(server.registered) == 22

    def test_lean_tools_registers_subset(self, monkeypatch, sample_config):
        server = _run_create(monkeypatch, sample_config, lean_tools=True)
        names = {fn.__name__ for fn in server.registered}
        assert len(names) == 8
        assert "database_query" in names
        assert "list_views" not in names
