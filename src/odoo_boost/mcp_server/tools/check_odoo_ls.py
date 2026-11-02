"""MCP tool: run structured diagnostics with the official Odoo Language Server."""

from __future__ import annotations

import json
import logging
import re
import subprocess
import tempfile
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import urlparse
from urllib.request import url2pathname

from odoo_boost.config.schema import OdooBoostConfig
from odoo_boost.mcp_server.policy import enforce_path
from odoo_boost.mcp_server.tools._common import (
    active_config,
    error_response,
    json_response,
    resolve_full,
)
from odoo_boost.odoo_ls import OFFICIAL_REPOSITORY, find_odoo_ls, is_usable, typeshed_dir
from odoo_boost.project_context import project_context

logger = logging.getLogger(__name__)

COMPACT_LIMIT = 30
_TIMEOUT_SECONDS = 300
_SEVERITY = {1: "error", 2: "warning", 3: "info", 4: "hint"}
_ODOO_VERSION_RE = re.compile(r"^Odoo version: (\S+)")
_INSTALL_COMMAND = "odoo-boost odoo-ls install"


def check_odoo_ls(path: str = ".", response_format: str | None = None) -> str:
    """Run official Odoo LS CLI diagnostics on a local addon or directory.

    Only diagnostics for files under ``path`` are returned, most severe first.
    Takes several seconds: Odoo LS loads the whole Odoo framework first.

    Args:
        path: Addon or workspace directory to analyze.
        response_format: ``compact`` (default) returns the 30 most severe
            diagnostics as one-line records plus counts per severity and code;
            ``full`` returns every diagnostic with its raw Odoo LS fields.
    """
    config = active_config()
    binary = find_odoo_ls(config.odoo_ls_path if config else None)
    if binary is None:
        return json_response(
            {
                "installed": False,
                "message": "Official odoo_ls_server executable was not found.",
                "install_command": _INSTALL_COMMAND,
                "official_source": OFFICIAL_REPOSITORY,
            }
        )
    if not is_usable(binary):
        return error_response(
            "Odoo LS cannot analyze code: its typeshed stubs are missing, so it stops "
            "during initialization and would report no diagnostics.",
            installed=True,
            binary=str(binary),
            expected_typeshed=str(typeshed_dir(binary)),
            install_command=_INSTALL_COMMAND,
        )

    target = enforce_path(path)
    tracked = (target if target.is_dir() else target.parent).resolve()
    full = resolve_full(response_format)
    config_file = _find_config(tracked)
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
            "--logs-directory",
            temporary,
        ]
        if config_file:
            command.extend(["--config-path", str(config_file)])
        elif config is not None:
            command.extend(_project_arguments(config))
        try:
            proc = subprocess.run(command, capture_output=True, text=True, timeout=_TIMEOUT_SECONDS)
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
            logs = _logs(payload)
        except (json.JSONDecodeError, OSError, ValueError) as exc:
            return error_response(
                f"Invalid Odoo LS diagnostic output: {exc}",
                installed=True,
                binary=str(binary),
            )

    odoo_version = next(
        (m.group(1) for m in (_ODOO_VERSION_RE.match(msg) for _, msg in logs) if m), None
    )
    in_scope = [item for item in diagnostics if _is_under(item.get("uri"), tracked)]
    in_scope.sort(key=_sort_key)
    shown: list[dict[str, Any]] = (
        in_scope if full else [_compact(item, tracked) for item in in_scope[:COMPACT_LIMIT]]
    )
    result: dict[str, Any] = {
        "installed": True,
        "binary": str(binary),
        "success": proc.returncode == 0,
        "odoo_version": odoo_version,
        "config": str(config_file) if config_file else None,
        "diagnostic_count": len(in_scope),
        "outside_path_count": len(diagnostics) - len(in_scope),
        "by_severity": dict(Counter(_severity(item) for item in in_scope)),
        "by_code": dict(Counter(str(item.get("code", "")) for item in in_scope).most_common(10)),
        "diagnostics": shown,
        "truncated": len(shown) < len(in_scope),
        "response_format": "full" if full else "compact",
    }
    if odoo_version is None:
        result["warning"] = (
            "Odoo LS did not load the Odoo framework, so model, field and XML checks did "
            "not run. Add an odools.toml with odoo_path, addons_paths and python_path "
            "next to the project, or set odoo_source_path, odoo_conf_path or venv_path "
            "in the Odoo Boost config."
        )
    if proc.returncode != 0:
        result["exit_code"] = proc.returncode
        result["stderr"] = proc.stderr[-2000:]
    return json_response(result)


def _project_arguments(config: OdooBoostConfig) -> list[str]:
    """Translate configured project paths into Odoo LS parse-mode options."""
    context = project_context(config)
    arguments: list[str] = []
    source = context.get("odoo_source")
    if source and source.get("exists"):
        arguments.extend(["--community-path", source["path"]])
    for addon in context.get("addons_path", []):
        if addon.get("exists"):
            arguments.extend(["--addons", addon["path"]])
    venv = context.get("venv")
    if venv and venv.get("valid"):
        arguments.extend(["--python", venv["python"]])
    return arguments


def _find_config(start: Path) -> Path | None:
    current = start.resolve()
    for directory in (current, *current.parents):
        candidate = directory / "odools.toml"
        if candidate.is_file():
            return candidate
    return None


def _uri_path(uri: Any) -> Path | None:
    if not isinstance(uri, str) or not uri.startswith("file:"):
        return None
    return Path(url2pathname(urlparse(uri).path))


def _is_under(uri: Any, root: Path) -> bool:
    path = _uri_path(uri)
    return path is not None and path.resolve().is_relative_to(root)


def _severity(item: dict[str, Any]) -> str:
    return _SEVERITY.get(item.get("severity", 3), "info")


def _start(item: dict[str, Any]) -> tuple[int, int]:
    start = item.get("range", {}).get("start", {})
    return int(start.get("line", 0)), int(start.get("character", 0))


def _sort_key(item: dict[str, Any]) -> tuple[int, str, tuple[int, int]]:
    severity = item.get("severity", 3)
    return (severity if isinstance(severity, int) else 3, str(item.get("uri", "")), _start(item))


def _compact(item: dict[str, Any], root: Path) -> dict[str, Any]:
    path = _uri_path(item.get("uri"))
    line, column = _start(item)
    record: dict[str, Any] = {
        "file": path.resolve().relative_to(root).as_posix() if path else item.get("uri"),
        "line": line + 1,
        "column": column + 1,
        "severity": _severity(item),
        "message": item.get("message", ""),
    }
    if item.get("code"):
        record["code"] = item["code"]
    return record


def _logs(payload: dict[str, Any]) -> list[tuple[int, str]]:
    return [
        (int(event.get("severity", 3)), str(event.get("message", "")))
        for event in payload["events"]
        if isinstance(event, dict) and event.get("type") == "log"
    ]


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
