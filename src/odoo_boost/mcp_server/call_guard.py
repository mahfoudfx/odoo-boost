"""Small per-server guard against accidental identical MCP call loops."""

from __future__ import annotations

import json
from threading import Lock
from typing import Any

from mcp.server.mcpserver.exceptions import ToolError


class ConsecutiveCallGuard:
    """Reject only consecutive identical calls after a configurable limit.

    Any different tool or argument resets the counter. This catches mechanical
    loops without imposing a process-lifetime request budget on legitimate work.
    """

    def __init__(self, limit: int) -> None:
        self.limit = limit
        self._last_key = ""
        self._count = 0
        self._lock = Lock()

    @staticmethod
    def _key(tool_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> str:
        try:
            payload = json.dumps([args, kwargs], sort_keys=True, default=str, separators=(",", ":"))
        except (TypeError, ValueError):
            payload = repr((args, sorted(kwargs.items())))
        return f"{tool_name}:{payload}"

    def check(self, tool_name: str, args: tuple[Any, ...], kwargs: dict[str, Any]) -> None:
        """Record a call or raise when the identical-call limit is exceeded."""
        if self.limit == 0:
            return
        key = self._key(tool_name, args, kwargs)
        with self._lock:
            if key == self._last_key:
                self._count += 1
            else:
                self._last_key = key
                self._count = 1
            if self._count > self.limit:
                raise ToolError(
                    f"Repeated identical call blocked after {self.limit} attempts: {tool_name}. "
                    "Reuse the previous result, change the arguments, or stop and reassess."
                )
