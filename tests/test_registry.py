"""Tests for the MCP tool registry."""

from __future__ import annotations

from pathlib import Path

from mcp.server.mcpserver.exceptions import ToolError

from odoo_boost.mcp_server.registry import (
    ALL_TOOLS,
    LEAN_TOOL_NAMES,
    LIVE_TOOLS,
    LOCAL_TOOLS,
    is_enabled,
    resilient_live_tool,
)


class TestToolInventory:
    def test_tool_count(self):
        assert len(ALL_TOOLS) == 22

    def test_no_duplicates(self):
        names = [tool.__name__ for tool in ALL_TOOLS]
        assert len(names) == len(set(names))

    def test_live_and_local_are_disjoint(self):
        live = {tool.__name__ for tool in LIVE_TOOLS}
        local = {tool.__name__ for tool in LOCAL_TOOLS}
        assert live.isdisjoint(local)

    def test_every_tool_has_docstring(self):
        for tool in ALL_TOOLS:
            assert tool.__doc__ and tool.__doc__.strip(), f"{tool.__name__} lacks a docstring"

    def test_docs_reference_every_tool(self):
        docs = (Path(__file__).resolve().parents[1] / "docs" / "mcp-tools.md").read_text(
            encoding="utf-8"
        )
        for tool in ALL_TOOLS:
            assert tool.__name__ in docs, f"{tool.__name__} missing from docs/mcp-tools.md"


class TestLeanProfile:
    def test_lean_names_are_known_tools(self):
        assert {tool.__name__ for tool in ALL_TOOLS} >= LEAN_TOOL_NAMES

    def test_is_enabled(self):
        by_name = {tool.__name__: tool for tool in ALL_TOOLS}
        assert is_enabled(by_name["database_query"], lean=True)
        assert is_enabled(by_name["inspect_local_addon"], lean=True)
        assert not is_enabled(by_name["list_views"], lean=True)
        assert is_enabled(by_name["list_views"], lean=False)


class TestResilientLiveTool:
    def test_passes_through_success(self):
        @resilient_live_tool
        def ok() -> str:
            return "ok"

        assert ok() == "ok"

    def test_converts_connection_error(self):
        @resilient_live_tool
        def boom() -> str:
            raise ConnectionError("Cannot reach Odoo")

        try:
            boom()
        except ToolError as exc:
            assert "Cannot reach Odoo" in str(exc)
        else:  # pragma: no cover - defensive
            raise AssertionError("ToolError was not raised")

    def test_does_not_swallow_other_errors(self):
        @resilient_live_tool
        def boom() -> str:
            raise ValueError("nope")

        try:
            boom()
        except ValueError:
            pass
        else:  # pragma: no cover - defensive
            raise AssertionError("ValueError was swallowed")

    def test_preserves_name_and_doc(self):
        @resilient_live_tool
        def my_tool() -> str:
            """My doc."""
            return "x"

        assert my_tool.__name__ == "my_tool"
        assert my_tool.__doc__ == "My doc."
