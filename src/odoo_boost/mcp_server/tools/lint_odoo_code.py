"""MCP tool: lint_odoo_code – run OCA quality checks (pylint-odoo) or AST diagnostics."""

from __future__ import annotations

import ast
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

from odoo_boost.mcp_server.policy import enforce_path
from odoo_boost.mcp_server.tools._common import error_response, json_response

logger = logging.getLogger(__name__)


def _run_pylint_odoo(target_path: Path) -> dict[str, Any]:
    """Run pylint with pylint_odoo plugin enabled."""
    cmd = [
        sys.executable,
        "-m",
        "pylint",
        "--load-plugins=pylint_odoo",
        "--output-format=json",
        str(target_path),
    ]

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = proc.stdout.strip()
        if not output:
            return {"success": True, "messages_count": 0, "messages": []}

        try:
            messages = json.loads(output)
        except json.JSONDecodeError:
            return {
                "success": proc.returncode == 0,
                "raw_output": output,
                "stderr": proc.stderr,
            }

        # Filter and organize messages
        errors = [m for m in messages if m.get("type") in ("error", "fatal")]
        warnings = [m for m in messages if m.get("type") == "warning"]
        conventions = [m for m in messages if m.get("type") in ("convention", "refactor")]

        return {
            "success": len(errors) == 0,
            "engine": "pylint-odoo",
            "total_issues": len(messages),
            "errors_count": len(errors),
            "warnings_count": len(warnings),
            "conventions_count": len(conventions),
            "errors": errors[:30],
            "warnings": warnings[:30],
            "conventions": conventions[:30],
        }
    except subprocess.TimeoutExpired:
        return {"error": "Linter timed out after 60s."}
    except Exception as exc:
        logger.warning("Failed running pylint-odoo: %s", exc)
        return {"error": f"Failed running pylint-odoo: {exc}"}


def _run_fallback_ast_lint(target_path: Path) -> dict[str, Any]:
    """Basic fallback checks when pylint-odoo is not installed."""
    issues = []
    py_files = [target_path] if target_path.is_file() else list(target_path.rglob("*.py"))

    for py_file in py_files:
        try:
            content = py_file.read_text(encoding="utf-8", errors="replace")
            tree = ast.parse(content, filename=str(py_file))
        except Exception as exc:
            logger.debug("Could not parse %s: %s", py_file, exc)
            issues.append(
                {
                    "type": "error",
                    "file": str(py_file),
                    "line": 1,
                    "message": f"Syntax error: {exc}",
                }
            )
            continue

        for node in ast.walk(tree):
            # Check for cr.commit()
            if isinstance(node, ast.Call):
                func = node.func
                if isinstance(func, ast.Attribute) and func.attr == "commit":
                    if isinstance(func.value, ast.Attribute) and func.value.attr == "cr":
                        issues.append(
                            {
                                "type": "error",
                                "code": "E8102",
                                "file": str(py_file),
                                "line": node.lineno,
                                "message": "Avoid calling cr.commit() directly. Transaction should be managed by Odoo.",
                            }
                        )
                    elif isinstance(func.value, ast.Name) and func.value.id == "cr":
                        issues.append(
                            {
                                "type": "error",
                                "code": "E8102",
                                "file": str(py_file),
                                "line": node.lineno,
                                "message": "Avoid calling cr.commit() directly.",
                            }
                        )

            # Check for deprecated name_get
            elif isinstance(node, ast.FunctionDef) and node.name == "name_get":
                issues.append(
                    {
                        "type": "warning",
                        "code": "E8146",
                        "file": str(py_file),
                        "line": node.lineno,
                        "message": "'name_get' is deprecated since Odoo 17. Use '_compute_display_name' instead.",
                    }
                )

    return {
        "success": len([i for i in issues if i["type"] == "error"]) == 0,
        "engine": "ast-fallback",
        "total_issues": len(issues),
        "issues": issues,
    }


def lint_odoo_code(path: str) -> str:
    """Validate Odoo Python and XML files against OCA coding standards and deprecated APIs.

    Args:
        path: Path to file or addon directory to lint.
    """
    target = enforce_path(path)

    if not target.exists():
        return error_response(f"Path '{path}' does not exist.")

    # Check if pylint_odoo is available
    has_pylint_odoo = False
    try:
        import pylint_odoo  # noqa: F401

        has_pylint_odoo = True
    except ImportError:
        has_pylint_odoo = False

    res = _run_pylint_odoo(target) if has_pylint_odoo else _run_fallback_ast_lint(target)

    return json_response(res)
