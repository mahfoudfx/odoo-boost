"""Consistent reporting for generated and removed project files."""

from __future__ import annotations

from collections.abc import Iterable
from pathlib import Path

from rich.console import Console


def report_paths(console: Console, paths: Iterable[Path], root: Path, label: str) -> None:
    for path in paths:
        relative = path.relative_to(root) if path.is_relative_to(root) else path
        console.print(f"  {label} {relative}")
