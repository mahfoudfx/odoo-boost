"""Interpreter paths must match a project's actual virtual-environment layout."""

from __future__ import annotations

import pytest

from odoo_boost.local_paths import venv_python


@pytest.mark.parametrize(
    ("layout", "expected"),
    [("posix", "bin/python"), ("windows", "Scripts/python.exe"), ("scripts_file", "bin/python")],
)
def test_venv_interpreter_matches_directory_layout(tmp_path, layout, expected):
    if layout == "windows":
        (tmp_path / "Scripts").mkdir()
    elif layout == "scripts_file":
        (tmp_path / "Scripts").write_text("A file is not a Windows VENV directory")
    else:
        (tmp_path / "bin").mkdir()

    assert venv_python(tmp_path).as_posix() == (tmp_path / expected).as_posix()
