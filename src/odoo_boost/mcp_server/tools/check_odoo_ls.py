"""MCP tool: run structured diagnostics with the official Odoo Language Server."""

from __future__ import annotations

import json
import logging
import subprocess
import tempfile
from pathlib import Path
from typing import Any

from odoo_boost.mcp_server.policy import enforce_path
from odoo_boost.mcp_server.tools._common import active_config, error_response, json_response
from odoo_boost.odoo_ls import OFFICIAL_REPOSITORY, find_odoo_ls

logger = logging.getLogger(__name__)


def check_odoo_ls(path: str = ".", response_format: str | None = None) -> str:
    """Run official Odoo LS CLI diagnostics and return structured results.

    Args:
        path: Addon or workspace directory to analyze.
        response_format: ``compact`` (default) returns at most 30 diagnostics;
            ``full`` returns every diagnostic emitted by Odoo LS.
    """
    config = active_config()
    binary = find_odoo_ls(config.odoo_ls_path if config else None)
    if binary is None:
        return json_response(
            {
                "installed": False,
                "message": "Official odoo_ls_server executable was not found.",
                "install_command": "odoo-boost odoo-ls install",
                "official_source": OFFICIAL_REPOSITORY,
            }
        )

    target = enforce_path(path)
    tracked = target if target.is_dir() else target.parent
    full = response_format == "full"
    with tempfile.TemporaryDirectory(prefix="odoo-boost-odoo-ls-") as temporary:
        output = Path(temporary) / "diagnostics.json"
        command = [
            str(binary),
            "--parse",
            "--tracked-folders",
            str(tracked),
            "--output",
            str(output),
            "--log-level",
            "warn",
        ]
        config_file = _find_config(tracked)
        if config_file:
            command.extend(["--config-path", str(config_file)])
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=120)
        except (OSError, subprocess.SubprocessError) as exc:
            logger.warning("Error running Odoo LS: %s", exc)
            return error_response(
                f"Error running Odoo LS: {exc}", installed=True, binary=str(binary)
            )
        if not output.is_file():
            return error_response(
                "Odoo LS produced no diagnostic output.",
                installed=True,
                binary=str(binary),
                exit_code=proc.returncode,
                stderr=proc.stderr[-2000:],
            )
        try:
            payload = json.loads(output.read_text(encoding="utf-8"))
            diagnostics = _diagnostics(payload)
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            return error_response(
                f"Invalid Odoo LS diagnostic output: {exc}",
                installed=True,
                binary=str(binary),
            )

    shown = diagnostics if full else diagnostics[:30]
    return json_response(
        {
            "installed": True,
            "official_source": OFFICIAL_REPOSITORY,
            "binary": str(binary),
            "exit_code": proc.returncode,
            "success": proc.returncode == 0,
            "diagnostic_count": len(diagnostics),
            "diagnostics": shown,
            "truncated": len(shown) < len(diagnostics),
            "response_format": "full" if full else "compact",
            "stderr": proc.stderr[-2000:] if proc.stderr else "",
        }
    )


def _find_config(start: Path) -> Path | None:
    current = start.resolve()
    for directory in (current, *current.parents):
        candidate = directory / "odools.toml"
        if candidate.is_file():
            return candidate
    return None


def _diagnostics(payload: Any) -> list[dict[str, Any]]:
    if not isinstance(payload, dict) or not isinstance(payload.get("events"), list):
        raise ValueError("expected an events array")
    result: list[dict[str, Any]] = []
    for event in payload["events"]:
        if not isinstance(event, dict) or event.get("type") != "diagnostic":
            continue
        uri = event.get("uri")
        items = event.get("diagnostics", [])
        if not isinstance(items, list):
            continue
        for item in items:
            if isinstance(item, dict):
                result.append({"uri": uri, **item})
    return result
