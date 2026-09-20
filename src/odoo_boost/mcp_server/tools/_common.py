"""Shared helpers for MCP tool implementations.

Centralises response serialization, token-efficient compaction, JSON argument
parsing, secret redaction, and the global response-size safety net so every
tool returns a consistent shape.
"""

from __future__ import annotations

import json
import os
import re
from typing import Any

from odoo_boost.config.schema import OdooBoostConfig

DEFAULT_MAX_RESPONSE_CHARS = 40000

# Config keys that commonly hold secrets. Used to redact get_config output.
_SECRET_KEY_RE = re.compile(
    r"(password|passwd|secret|token|api[_-]?key|private[_-]?key|smtp_pass|auth)",
    re.IGNORECASE,
)


def active_config() -> OdooBoostConfig | None:
    """Return the active server config, or None outside an MCP server (CLI)."""
    try:
        from odoo_boost.mcp_server.context import get_context

        return get_context().config
    except RuntimeError:
        return None


def resolve_full(response_format: str | None) -> bool:
    """Resolve the compact/full decision with per-call > config > default precedence."""
    if response_format:
        return response_format.strip().lower() == "full"
    config = active_config()
    if config is not None:
        return not config.compact_responses
    return False


def max_response_chars() -> int:
    """Return the configured response budget (0 = unlimited)."""
    config = active_config()
    if config is not None:
        return config.max_response_chars
    raw = os.environ.get("ODOO_BOOST_MAX_RESPONSE_CHARS")
    if not raw:
        return DEFAULT_MAX_RESPONSE_CHARS
    try:
        return int(raw)
    except ValueError:
        return DEFAULT_MAX_RESPONSE_CHARS


def json_response(payload: Any, *, bypass_budget: bool = False) -> str:
    """Serialize a tool payload, enforcing the global response budget."""
    text = json.dumps(payload, indent=2, default=str)
    if bypass_budget:
        return text

    limit = max_response_chars()
    if limit > 0 and len(text) > limit:
        envelope = {
            "truncated": True,
            "full_length": len(text),
            "message": "Narrow filters or increase max_response_chars to see more.",
            "preview": "",
        }
        serialized = json.dumps(envelope)
        if len(serialized) > limit:
            # A tiny configured budget cannot fit the normal envelope.
            for fallback in ('{"truncated":true}', "{}", "0"):
                if len(fallback) <= limit:
                    return fallback
            return ""
        low, high = 0, len(text)
        while low < high:
            middle = (low + high + 1) // 2
            envelope["preview"] = text[:middle]
            if len(json.dumps(envelope)) <= limit:
                low = middle
            else:
                high = middle - 1
        envelope["preview"] = text[:low]
        return json.dumps(envelope)
    return text


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
                clean[key] = compact_text(value, max_string)
            else:
                clean[key] = value
        compacted.append(clean)
    return compacted


def compact_text(value: str | None, max_chars: int) -> str:
    """Truncate a string with an explicit, machine-readable marker."""
    if not value:
        return ""
    if max_chars <= 0 or len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}… [truncated, {len(value)} chars total]"


def is_secret_key(key: str) -> bool:
    """Return True when a config key likely holds a secret."""
    return bool(_SECRET_KEY_RE.search(key or ""))


def redact(value: str, *, reveal: bool) -> tuple[str, bool]:
    """Return ``(value, redacted)`` redacting the value unless *reveal* is True."""
    if reveal or not value:
        return value, False
    return "***redacted***", True
