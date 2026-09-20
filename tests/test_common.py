"""Tests for odoo_boost.mcp_server.tools._common."""

from __future__ import annotations

import json

import pytest

from odoo_boost.mcp_server.tools._common import (
    compact_records,
    error_response,
    json_response,
    parse_json_arg,
)


class TestJsonResponse:
    def test_serializes_with_default_str(self):
        payload = {"id": 1, "when": object()}
        assert "id" in json.loads(json_response(payload))

    def test_indented(self):
        assert "\n" in json_response({"a": 1})

    def test_escaped_preview_stays_within_budget(self, monkeypatch):
        monkeypatch.setattr("odoo_boost.mcp_server.tools._common.max_response_chars", lambda: 190)
        text = json_response({"body": '\\"' * 1000})
        assert len(text) <= 190
        assert json.loads(text)["truncated"] is True

    def test_tiny_budget_stays_bounded(self, monkeypatch):
        monkeypatch.setattr("odoo_boost.mcp_server.tools._common.max_response_chars", lambda: 20)
        assert len(json_response({"body": "x" * 100})) <= 20


class TestErrorResponse:
    def test_shape(self):
        data = json.loads(error_response("boom", model="res.partner"))
        assert data == {"error": "boom", "model": "res.partner"}


class TestParseJsonArg:
    def test_empty_returns_default(self):
        assert parse_json_arg("", default=[]) == []
        assert parse_json_arg(None, default={"a": 1}) == {"a": 1}

    def test_parses_valid_json(self):
        assert parse_json_arg('[["a", "=", 1]]', default=[]) == [["a", "=", 1]]

    def test_invalid_json_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid JSON argument"):
            parse_json_arg("[broken", default=[])


class TestCompactRecords:
    def test_drops_empty_values(self):
        records = [{"id": 1, "name": "x", "empty": "", "none": None, "flag": False}]
        assert compact_records(records) == [{"id": 1, "name": "x"}]

    def test_truncates_long_strings(self):
        records = [{"body": "a" * 200}]
        compacted = compact_records(records, max_string=50)
        assert compacted[0]["body"].startswith("a" * 50)
        assert "truncated" in compacted[0]["body"]
        assert "200 chars total" in compacted[0]["body"]

    def test_non_list_passthrough(self):
        assert compact_records("nope") == "nope"

    def test_non_dict_entries_preserved(self):
        assert compact_records([1, 2]) == [1, 2]
