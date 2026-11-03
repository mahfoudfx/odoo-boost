"""Reusable Odoo lint execution, independent of CLI and MCP presentation."""

from __future__ import annotations

import ast
import json
import logging
import subprocess
import sys
from pathlib import Path
from typing import Any

from odoo_boost.source_files import iter_source_files
from odoo_boost.versions import get_version_profile

logger = logging.getLogger(__name__)


def _run_pylint_odoo(target_path: Path, version: str | None = None) -> dict[str, Any]:
    """Run pylint with pylint_odoo plugin enabled."""
    cmd = [
        sys.executable,
        "-m",
        "pylint",
        "--load-plugins=pylint_odoo",
        "--output-format=json",
        str(target_path),
    ]

    profile = get_version_profile(version)
    if profile:
        cmd.insert(-1, f"--valid-odoo-versions={profile.series}")

    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = proc.stdout.strip()
        if not output:
            if proc.returncode:
                return {
                    "success": False,
                    "engine": "pylint-odoo",
                    "error": f"Linter exited with status {proc.returncode}: {proc.stderr.strip()}",
                }
            return {"success": True, "engine": "pylint-odoo", "total_issues": 0, "messages": []}

        try:
            messages = json.loads(output)
        except json.JSONDecodeError:
            return {
                "success": False,
                "error": "Linter returned invalid JSON.",
                "raw_output": output,
                "stderr": proc.stderr,
            }

        if not isinstance(messages, list) or any(not isinstance(m, dict) for m in messages):
            return {"success": False, "error": "Linter returned an invalid diagnostic payload."}
        if proc.returncode & 32:
            return {"success": False, "error": f"Linter usage error: {proc.stderr.strip()}"}

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
            "errors": errors,
            "warnings": warnings,
            "conventions": conventions,
        }
    except subprocess.TimeoutExpired:
        return {"error": "Linter timed out after 60s."}
    except Exception as exc:
        logger.warning("Failed running pylint-odoo: %s", exc)
        return {"error": f"Failed running pylint-odoo: {exc}"}


def _run_fallback_ast_lint(target_path: Path, version: str | None = None) -> dict[str, Any]:
    """Basic fallback checks when pylint-odoo is not installed."""
    issues = []
    profile = get_version_profile(version)
    name_get_deprecated = bool(
        profile and profile.features.get("display_name") == "_compute_display_name"
    )
    py_files = (
        ([target_path] if target_path.suffix == ".py" else [])
        if target_path.is_file()
        else iter_source_files(target_path, {".py"})
    )

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
                    cursor = func.value
                    if (
                        isinstance(cursor, ast.Attribute)
                        and cursor.attr == "cr"
                        or isinstance(cursor, ast.Name)
                        and cursor.id == "cr"
                    ):
                        message = "Avoid calling cr.commit() directly."
                        if isinstance(cursor, ast.Attribute):
                            message += " Transaction should be managed by Odoo."
                        issues.append(
                            {
                                "type": "error",
                                "code": "E8102",
                                "file": str(py_file),
                                "line": node.lineno,
                                "message": message,
                            }
                        )

            # Check for deprecated name_get
            elif (
                name_get_deprecated
                and isinstance(node, ast.FunctionDef)
                and node.name == "name_get"
            ):
                issues.append(
                    {
                        "type": "warning",
                        "code": "E8146",
                        "file": str(py_file),
                        "line": node.lineno,
                        "message": "'name_get' is deprecated since Odoo 17. Use '_compute_display_name' instead.",
                    }
                )

    from odoo_boost.static_checks import check_static

    checked = check_static(target_path, version)
    seen = {(i["file"], i["line"], i["message"]) for i in issues}
    issues.extend(i for i in checked["issues"] if (i["file"], i["line"], i["message"]) not in seen)
    return {
        "coverage": checked["coverage"],
        "limitations": checked["limitations"],
        "success": not any(issue["type"] == "error" for issue in issues),
        "engine": "ast-fallback",
        "total_issues": len(issues),
        "issues": issues,
    }


def run_lint(target: Path, *, version: str | None = None) -> dict[str, Any]:
    """Return complete diagnostics; callers decide how to display or compact them."""
    if not target.exists():
        return {"error": f"Path '{target}' does not exist."}
    if target.is_file() and target.suffix != ".py":
        return _run_fallback_ast_lint(target, version)
    try:
        import pylint_odoo  # noqa: F401
    except ImportError:
        return _run_fallback_ast_lint(target, version)
    return _run_pylint_odoo(target, version)
