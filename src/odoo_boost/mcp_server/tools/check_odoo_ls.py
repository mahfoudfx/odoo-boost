"""MCP tool: check_odoo_ls – check Odoo Language Server presence and diagnostics."""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path


def check_odoo_ls(path: str = ".") -> str:
    """Run diagnostics using Odoo Language Server (odoo-ls) if installed.

    Args:
        path: Path to file or addon directory to check (default current directory).
    """
    ls_bin = shutil.which("odoo-ls")
    if not ls_bin:
        return json.dumps(
            {
                "installed": False,
                "message": (
                    "odoo-ls binary not found on PATH. "
                    "Odoo Boost is using built-in pure-Python AST scanner and OCA linter instead."
                ),
                "suggestion": "To install Odoo Language Server, visit https://github.com/odoo/odoo-ls",
            },
            indent=2,
        )

    target = Path(path).resolve()
    try:
        proc = subprocess.run(
            [ls_bin, "check", str(target)],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return json.dumps(
            {
                "installed": True,
                "binary": ls_bin,
                "exit_code": proc.returncode,
                "output": proc.stdout.strip(),
                "stderr": proc.stderr.strip(),
            },
            indent=2,
        )
    except Exception as exc:
        return json.dumps(
            {
                "installed": True,
                "binary": ls_bin,
                "error": f"Error running odoo-ls: {exc}",
            },
            indent=2,
        )
