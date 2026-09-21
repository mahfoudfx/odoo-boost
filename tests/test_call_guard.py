"""MCP loop guard allows progress while stopping identical mechanical retries."""

from __future__ import annotations

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from odoo_boost.mcp_server.call_guard import ConsecutiveCallGuard


def test_blocks_third_consecutive_identical_call():
    guard = ConsecutiveCallGuard(2)
    guard.check("search", (), {"model": "res.partner"})
    guard.check("search", (), {"model": "res.partner"})
    with pytest.raises(ToolError, match="Repeated identical call blocked"):
        guard.check("search", (), {"model": "res.partner"})


def test_different_call_resets_counter():
    guard = ConsecutiveCallGuard(1)
    guard.check("search", (), {"model": "res.partner"})
    guard.check("search", (), {"model": "sale.order"})
    guard.check("search", (), {"model": "res.partner"})


def test_zero_disables_guard():
    guard = ConsecutiveCallGuard(0)
    for _ in range(10):
        guard.check("search", (), {})
