"""Per-server guards against accidental MCP call loops."""

from __future__ import annotations

import json
from collections import Counter, deque
from threading import Lock
from typing import Any

from mcp.server.mcpserver.exceptions import ToolError


class ConsecutiveCallGuard:
    """Reject only consecutive identical calls after a configurable limit.

    Any different tool or argument resets the counter. This catches mechanical
    loops without imposing a process-lifetime request budget on legitimate work.
    """

    def __init__(self, limit: int, repeat_limit: int = 0, window_size: int = 0) -> None:
        self.limit = limit
        self.repeat_limit = repeat_limit
        self.window_size = window_size
        self._last_key = ""
        self._count = 0
        self._recent: deque[str] = deque(maxlen=window_size or None)
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
        if self.limit == 0 and (self.repeat_limit == 0 or self.window_size == 0):
            return
        key = self._key(tool_name, args, kwargs)
        with self._lock:
            if key == self._last_key:
                self._count += 1
            else:
                self._last_key = key
                self._count = 1
            if self.limit and self._count > self.limit:
                raise ToolError(
                    f"Repeated identical call blocked after {self.limit} attempts: {tool_name}. "
                    "Reuse the previous result, change the arguments, or stop and reassess."
                )
            if self.repeat_limit and self.window_size:
                occurrences = Counter(self._recent)[key]
                if occurrences >= self.repeat_limit:
                    raise ToolError(
                        f"Repeated call blocked after {self.repeat_limit} occurrences within "
                        f"the last {self.window_size} MCP calls: {tool_name}. Reuse the prior "
                        "result or stop; alternating tools does not reset this limit."
                    )
                self._recent.append(key)
