"""Shared helpers for MCP tool implementations.

Centralises response serialization, JSON argument parsing, and record
compaction so every tool returns a consistent shape.
"""

from __future__ import annotations

import json
from typing import Any


def json_response(payload: Any) -> str:
    """Serialize a tool payload with stable formatting."""
    return json.dumps(payload, indent=2, default=str)


def error_response(message: str, **extra: Any) -> str:
    """Serialize a standard error payload."""
    return json_response({"error": message, **extra})


def parse_json_arg(value: str | None, *, default: Any = None) -> Any:
    """Parse a JSON string tool argument, returning *default* when empty.

    Raises:
        ValueError: when the value is not valid JSON (including a short excerpt
            of the offending input to help the caller fix their request).
    """
    if value is None or value == "":
        return default
    try:
        return json.loads(value)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON argument: {exc.msg} at position {exc.pos}") from exc


def compact_records(records: Any, *, max_string: int = 100) -> Any:
    """Drop empty values and truncate long strings to reduce token usage."""
    if not isinstance(records, list):
        return records

    compacted: list[dict[str, Any]] = []
    for record in records:
        if not isinstance(record, dict):
            compacted.append(record)
            continue
        clean: dict[str, Any] = {}
        for key, value in record.items():
            if value is None or value is False or value == "":
                continue
            if isinstance(value, str) and len(value) > max_string:
                clean[key] = f"{value[: max_string - 3]}..."
            else:
                clean[key] = value
        compacted.append(clean)
    return compacted
