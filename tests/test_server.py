"""Tests for the MCP server construction (version, auth wiring, context)."""

from __future__ import annotations

from unittest.mock import MagicMock

import odoo_boost.mcp_server.server as server_mod
from odoo_boost.__version__ import __version__
from odoo_boost.mcp_server.context import reset_context


class _FakeMCPServer:
    """Minimal stand-in capturing constructor args and no-op decorators."""

    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs

    def resource(self, *args, **kwargs):
        return lambda fn: fn

    def prompt(self, *args, **kwargs):
        return lambda fn: fn

    def tool(self, *args, **kwargs):
        return lambda fn: fn


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
