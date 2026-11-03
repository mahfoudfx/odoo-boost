"""Bounded in-memory telemetry without credentials or record payloads."""

from __future__ import annotations

from threading import Lock
from typing import Any


class ToolMetrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._tools: dict[str, dict[str, Any]] = {}
        self._last: str | None = None

    def record(self, name: str, elapsed: float, size: int, failed: bool) -> None:
        with self._lock:
            entry = self._tools.setdefault(
                name,
                dict(calls=0, failures=0, seconds=0.0, response_chars=0, consecutive_same_tool=0),
            )
            entry["calls"] += 1
            entry["failures"] += int(failed)
            entry["seconds"] += elapsed
            entry["response_chars"] += size
            entry["consecutive_same_tool"] += int(self._last == name)
            self._last = name

    def snapshot(self) -> dict[str, Any]:
        with self._lock:
            return {
                "tools": {k: dict(v) for k, v in self._tools.items()},
                "scope": "This MCP server process only; chars are not tokens; same-tool calls are not necessarily duplicate requests.",
            }
