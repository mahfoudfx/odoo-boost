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
        assert len(compacted[0]["body"]) == 50
        assert compacted[0]["body"].endswith("...")

    def test_non_list_passthrough(self):
        assert compact_records("nope") == "nope"

    def test_non_dict_entries_preserved(self):
        assert compact_records([1, 2]) == [1, 2]
