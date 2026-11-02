"""Change-scoped checks and normalized diagnostics shared by CLI and MCP."""

from __future__ import annotations

import json
import subprocess
from pathlib import Path
from typing import Any

from odoo_boost.diagnostics import run_lint
from odoo_boost.static_checks import check_static


def validation_plan(root: Path, base: str = "HEAD") -> dict[str, Any]:
    """Include tracked worktree/index changes and untracked source files."""
    if base.startswith("-"):
        raise ValueError("base must be a git revision, not an option")
    diff = subprocess.run(
        ["git", "-C", str(root), "diff", "--name-only", "-z", base, "--"],
        capture_output=True,
        timeout=15,
        check=True,
    )
    untracked = subprocess.run(
        ["git", "-C", str(root), "ls-files", "--others", "--exclude-standard", "-z"],
        capture_output=True,
        timeout=15,
        check=True,
    )
    files = sorted({p for p in (diff.stdout + untracked.stdout).decode().split("\0") if p})
    checks: set[str] = set()
    for name in files:
        suffix = Path(name).suffix
        if suffix == ".py":
            checks.update(["python-static", "pylint-odoo", "focused-odoo-tests"])
        if suffix in {".xml", ".csv"}:
            checks.update(["xml-acl-static", "odoo-ls"])
        if suffix in {".js", ".scss", ".css"}:
            checks.add("frontend-build-or-tests")
        if suffix in {".po", ".pot"}:
            checks.add("translation-validation")
        if "security/" in name or "controllers/" in name:
            checks.add("authorization-allowed-and-denied-tests")
    return {
        "base": base,
        "files": files,
        "recommended_checks": sorted(checks),
        "executed": False,
        "note": "Recommendations only. Review semantic risks, deleted files, compute dependencies and company boundaries.",
    }


def diagnose(
    target: Path, version: str | None = None, include_odoo_ls: bool = False
) -> dict[str, Any]:
    static = check_static(target, version)
    lint = run_lint(target, version=version)
    findings = list(static["issues"])
    engines: dict[str, Any] = {
        "static": {"status": static["status"], "coverage": static["coverage"]}
    }
    lint_issues = [
        i
        for key in ("messages", "issues", "errors", "warnings", "conventions")
        for i in lint.get(key, [])
    ]
    for issue in lint_issues:
        findings.append(
            {
                "file": str(Path(issue.get("path", issue.get("file", str(target)))).resolve()),
                "line": issue.get("line", 1),
                "code": issue.get("symbol", issue.get("code", "")),
                "type": issue.get("type", "warning"),
                "message": issue.get("message", ""),
                "engine": lint.get("engine", "lint"),
                "certainty": "review_required",
            }
        )
    engines["lint"] = {
        "status": "unavailable"
        if lint.get("error")
        else ("failed" if lint.get("success") is False else "passed"),
        "engine": lint.get("engine"),
        "error": lint.get("error"),
    }
    if include_odoo_ls:
        from odoo_boost.mcp_server.tools.check_odoo_ls import _compact, check_odoo_ls

        ls = json.loads(check_odoo_ls(str(target), response_format="full"))
        engines["odoo_ls"] = {
            "status": "unavailable"
            if not ls.get("installed") or ls.get("error")
            else (
                "partial"
                if ls.get("warning")
                else ("failed" if ls.get("success") is False else "passed")
            ),
            "message": ls.get("error", ls.get("warning", ls.get("message"))),
        }
        for issue in ls.get("diagnostics", []):
            compact = _compact(issue, target if target.is_dir() else target.parent)
            compact["file"] = str((target if target.is_dir() else target.parent) / compact["file"])
            findings.append(
                {
                    **compact,
                    "type": compact["severity"],
                    "engine": "odoo-ls",
                    "certainty": "review_required",
                }
            )
    else:
        engines["odoo_ls"] = {
            "status": "not_run",
            "message": "Enable include_odoo_ls for framework diagnostics.",
        }
    unique: dict[tuple, dict[str, Any]] = {}
    for issue in findings:
        key = (
            str(Path(issue["file"]).resolve()),
            issue["line"],
            issue.get("code"),
            issue["message"],
        )
        unique.setdefault(key, issue)
    findings = sorted(
        unique.values(), key=lambda i: (i["type"] not in {"error", "fatal"}, i["file"], i["line"])
    )
    failed = any(i["type"] in {"error", "fatal"} for i in findings) or any(
        e["status"] == "failed" for e in engines.values()
    )
    return {
        "status": "failed"
        if failed
        else (
            "partial"
            if any(e["status"] in {"partial", "not_run", "unavailable"} for e in engines.values())
            else "passed"
        ),
        "findings": findings,
        "total_findings": len(findings),
        "engines": engines,
        "limitations": static["limitations"],
    }
