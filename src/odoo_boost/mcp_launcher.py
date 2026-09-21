"""Resolve the MCP server command/URL across native, WSL, and HTTP setups.

Generated MCP configs used to embed the active Python interpreter path
(``sys.executable``). That works when the IDE and the interpreter live on the
same OS, but breaks when an IDE running on Windows tries to spawn an interpreter
that only exists inside WSL. This module centralises the platform logic so every
agent emits a working configuration:

* ``native``  – run the interpreter directly (WSL/Linux/macOS IDEs).
* ``wsl``     – wrap the interpreter in ``wsl.exe`` (Windows IDEs).
* ``http``    – connect to a running server over Streamable HTTP.
"""

from __future__ import annotations

import os
import sys
from collections.abc import Mapping
from pathlib import Path

from odoo_boost.config.schema import OdooBoostConfig

CONFIG_FILENAME = "odoo-boost.json"
WINDOWS_LAUNCHER = "wsl.exe"
DEFAULT_WSL_DISTRO = "Ubuntu"
HTTP_PATH = "/mcp"


def is_wsl(env: Mapping[str, str] | None = None) -> bool:
    """Return True when the current process runs inside Windows Subsystem for Linux."""
    environ = env if env is not None else os.environ
    if environ.get("WSL_DISTRO_NAME") or environ.get("WSL_INTEROP"):
        return True
    try:
        proc_version = Path("/proc/version").read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return False
    return "microsoft" in proc_version.lower()


def detect_wsl_distro(env: Mapping[str, str] | None = None) -> str | None:
    """Return the active WSL distribution name, if any."""
    environ = env if env is not None else os.environ
    return environ.get("WSL_DISTRO_NAME") or None


def is_loopback_host(host: str) -> bool:
    """Return True when *host* only exposes the server to the local machine."""
    return host.strip().lower() in {"127.0.0.1", "localhost", "::1", "[::1]"}


def config_path_for(project_path: Path) -> Path:
    """Absolute path to the ``odoo-boost.json`` belonging to *project_path*."""
    return project_path / CONFIG_FILENAME


def build_stdio_command(
    config: OdooBoostConfig,
    project_path: Path,
    *,
    windows: bool = False,
    python: str | None = None,
) -> list[str]:
    """Return the argv used to start the stdio MCP server.

    The explicit ``-c <config>`` path is always appended (unless a full
    ``mcp_command`` override is configured) so the server does not depend on the
    working directory the IDE happens to use.
    """
    if config.mcp_command:
        return list(config.mcp_command)

    interpreter = python or sys.executable
    inner = [
        interpreter,
        "-m",
        "odoo_boost",
        "mcp",
        "-c",
        str(config_path_for(project_path)),
    ]

    target = "wsl" if windows else config.mcp_target
    if target == "native":
        return inner

    if target == "wsl":
        distro = config.wsl_distro or detect_wsl_distro() or DEFAULT_WSL_DISTRO
        return [
            WINDOWS_LAUNCHER,
            "-d",
            distro,
            "--cd",
            str(project_path),
            "--",
            *inner,
        ]

    # 'auto' primary config is native; the Windows companion is built with
    # windows=True and therefore never reaches this branch.
    return inner


def build_http_url(config: OdooBoostConfig) -> str:
    """Return the Streamable HTTP endpoint advertised to MCP clients."""
    if config.mcp_http_url:
        return config.mcp_http_url.rstrip("/")
    host = config.mcp_host
    if host in ("0.0.0.0", "::", ""):
        host = "127.0.0.1"
    return f"http://{host}:{config.mcp_port}{HTTP_PATH}"
