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


def test_blocks_repeated_call_even_when_calls_are_interleaved():
    guard = ConsecutiveCallGuard(2, repeat_limit=2, window_size=6)
    guard.check("search", (), {"model": "res.partner"})
    guard.check("schema", (), {"model": "res.partner"})
    guard.check("search", (), {"model": "res.partner"})
    guard.check("schema", (), {"model": "sale.order"})
    with pytest.raises(ToolError, match="alternating tools does not reset"):
        guard.check("search", (), {"model": "res.partner"})


def test_repeated_call_expires_from_rolling_window():
    guard = ConsecutiveCallGuard(2, repeat_limit=1, window_size=2)
    guard.check("search", (), {"model": "res.partner"})
    guard.check("schema", (), {"model": "res.partner"})
    guard.check("schema", (), {"model": "sale.order"})
    guard.check("search", (), {"model": "res.partner"})
