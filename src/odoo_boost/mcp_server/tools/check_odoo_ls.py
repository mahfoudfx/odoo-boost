"""MCP tool: check_odoo_ls – check Odoo Language Server presence and diagnostics."""

from __future__ import annotations

import logging
import shutil
import subprocess

from odoo_boost.mcp_server.policy import enforce_path
from odoo_boost.mcp_server.tools._common import (
    compact_text,
    error_response,
    json_response,
    resolve_full,
)

logger = logging.getLogger(__name__)


def check_odoo_ls(path: str = ".", response_format: str | None = None) -> str:
    """Run diagnostics using Odoo Language Server (odoo-ls) if installed.

    Args:
        path: Path to file or addon directory to check (default current directory).
        response_format: 'compact' (default) truncates output, 'full' keeps it.
    """
    full = resolve_full(response_format)
    ls_bin = shutil.which("odoo-ls")
    if not ls_bin:
        return json_response(
            {
                "installed": False,
                "message": (
                    "odoo-ls binary not found on PATH. "
                    "Odoo Boost is using built-in pure-Python AST scanner and OCA linter instead."
                ),
                "suggestion": "To install Odoo Language Server, visit https://github.com/odoo/odoo-ls",
            }
        )

    target = enforce_path(path)
    try:
        proc = subprocess.run(
            [ls_bin, "check", str(target)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = proc.stdout.strip()
        stderr = proc.stderr.strip()
        max_chars = 0 if full else 2000
        return json_response(
            {
                "installed": True,
                "binary": ls_bin,
                "exit_code": proc.returncode,
                "output": compact_text(output, max_chars),
                "output_length": len(output),
                "stderr": compact_text(stderr, max_chars),
                "stderr_length": len(stderr),
                "response_format": "full" if full else "compact",
            }
        )
    except Exception as exc:
        logger.warning("Error running odoo-ls: %s", exc)
        return error_response(f"Error running odoo-ls: {exc}", installed=True, binary=ls_bin)
