"""End-to-end tests for HTTP bearer-token auth on the MCP ASGI app.

The app is exercised in-process with ``httpx.ASGITransport``. The session
manager requires the HTTP lifespan (which ASGITransport does not run), so a
*successful* auth attempt is detected by the request reaching the session
manager instead of returning 401/403.
"""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import httpx

from odoo_boost.mcp_server import server as server_mod
from odoo_boost.mcp_server.context import reset_context

INITIALIZE = {
    "jsonrpc": "2.0",
    "id": 1,
    "method": "initialize",
    "params": {
        "protocolVersion": "2025-06-18",
        "capabilities": {},
        "clientInfo": {"name": "test", "version": "1"},
    },
}
BASE_HEADERS = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}


def _build_app(monkeypatch, sample_config, token: str = "tok123"):
    conn = MagicMock()
    conn.authenticate.return_value = 2
    monkeypatch.setattr(server_mod, "create_connection", lambda cfg: conn)

    cfg = sample_config.model_copy(
        update={
            "mcp_transport": "http",
            "mcp_token": token,
            "mcp_host": "127.0.0.1",
            "mcp_port": 8799,
            "generate_ai_files": False,
        }
    )
    server = server_mod.create_mcp_server(cfg)
    reset_context()
    return server.streamable_http_app(host="127.0.0.1")


async def _post(app, headers: dict[str, str]) -> int | str:
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://127.0.0.1:8799") as client:
        try:
            response = await client.post("/mcp", json=INITIALIZE, headers=headers)
        except RuntimeError as exc:
            # Auth passed and the request reached the session manager.
            assert "Task group is not initialized" in str(exc)
            return "auth-passed"
    return response.status_code


class TestHttpBearerAuth:
    def test_missing_token_is_rejected(self, monkeypatch, sample_config):
        app = _build_app(monkeypatch, sample_config)
        assert asyncio.run(_post(app, BASE_HEADERS)) == 401

    def test_wrong_token_is_rejected(self, monkeypatch, sample_config):
        app = _build_app(monkeypatch, sample_config)
        headers = {**BASE_HEADERS, "Authorization": "Bearer wrong"}
        assert asyncio.run(_post(app, headers)) == 401

    def test_valid_token_passes_auth(self, monkeypatch, sample_config):
        app = _build_app(monkeypatch, sample_config)
        headers = {**BASE_HEADERS, "Authorization": "Bearer tok123"}
        assert asyncio.run(_post(app, headers)) == "auth-passed"
