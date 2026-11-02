"""Explicit disposable-database Odoo test execution."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any

from odoo_boost.config.schema import OdooBoostConfig


def run_tests(config: OdooBoostConfig, addon: Path, tags: str, database: str) -> dict[str, Any]:
    if (
        not config.test_database
        or database != config.test_database
        or database == config.connection.database
    ):
        return {
            "status": "unavailable",
            "error": "database must match test_database and differ from the connected database.",
        }
    if not tags.strip() or tags.startswith("-") or not (addon / "__manifest__.py").is_file():
        return {
            "status": "unavailable",
            "error": "Provide focused test tags and an addon directory containing __manifest__.py.",
        }
    if not config.odoo_source_path or not config.venv_path or not config.test_odoo_conf_path:
        return {
            "status": "unavailable",
            "error": "Configure odoo_source_path, venv_path and test_odoo_conf_path (dedicated test configuration).",
        }
    python = Path(config.venv_path) / (
        "Scripts/python.exe" if __import__("os").name == "nt" else "bin/python"
    )
    command = [
        str(python),
        str(Path(config.odoo_source_path) / "odoo-bin"),
        "-c",
        config.test_odoo_conf_path,
        "-d",
        database,
        "--db-filter",
        "^" + __import__("re").escape(database) + "$",
        "--test-enable",
        "--test-tags",
        tags,
        "--stop-after-init",
        "--no-http",
        "--max-cron-threads=0",
        "-u",
        addon.name,
    ]
    try:
        proc = subprocess.run(
            command,
            cwd=config.project_root,
            capture_output=True,
            text=True,
            timeout=config.test_timeout_seconds,
        )
    except (OSError, subprocess.SubprocessError) as exc:
        return {"status": "unavailable", "error": str(exc)}
    output = proc.stdout + "\n" + proc.stderr
    # Exit zero without evidence of executed tests is not a verified pass.
    import re

    counts = re.findall(r"(\d+) failed, (\d+) error\(s\) of (\d+) tests", output)
    executed = sum(int(n) for _, _, n in counts)
    failures = sum(int(f) + int(e) for f, e, _ in counts)
    return {
        "status": "failed"
        if proc.returncode or failures
        else ("passed" if executed else "partial"),
        "exit_code": proc.returncode,
        "tests_reported": executed,
        "failures_reported": failures,
        "database": database,
        "output_tail": output[-12000:],
        "note": "Uses dedicated test configuration; module must already be installed. No test summary means no verified pass.",
    }
