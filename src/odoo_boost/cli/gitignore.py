"""Manage only the ignore entries explicitly accepted for Odoo Boost."""

from __future__ import annotations

from pathlib import Path

START = "# Odoo Boost managed entries (start)"
END = "# Odoo Boost managed entries (end)"


def ignore_entry(project_path: Path, path: Path) -> str:
    """Return a root-relative Git pattern for a generated path."""
    relative = path.absolute().relative_to(project_path.absolute())
    return "/" + relative.as_posix() + ("/" if path.is_dir() else "")


def managed_entries(project_path: Path) -> set[str]:
    gitignore = project_path / ".gitignore"
    if not gitignore.is_file():
        return set()
    lines = gitignore.read_text(encoding="utf-8").splitlines()
    if lines.count(START) != 1 or lines.count(END) != 1:
        return set()
    start, end = lines.index(START), lines.index(END)
    return set(lines[start + 1 : end]) if start < end else set()


def update_gitignore(
    project_path: Path, *, add: set[str] | None = None, remove: set[str] | None = None
) -> None:
    """Update the marked block, preserving all other .gitignore content."""
    gitignore = project_path / ".gitignore"
    content = gitignore.read_text(encoding="utf-8") if gitignore.exists() else ""
    lines = content.splitlines()
    if lines.count(START) > 1 or lines.count(END) > 1:
        raise ValueError("Ambiguous Odoo Boost .gitignore markers")
    has_block = START in lines and END in lines
    if (START in lines) != (END in lines):
        raise ValueError("Incomplete Odoo Boost .gitignore block")
    if has_block:
        start, end = lines.index(START), lines.index(END)
        if start >= end:
            raise ValueError("Invalid Odoo Boost .gitignore block")
        entries = set(lines[start + 1 : end])
    else:
        entries = set()
    entries.update(add or ())
    entries.difference_update(remove or ())
    if has_block:
        lines[start : end + 1] = [START, *sorted(entries), END] if entries else []
        updated = "\n".join(lines).rstrip("\n") + "\n" if lines else ""
    elif entries:
        separator = "" if not content or content.endswith("\n") else "\n"
        updated = (
            content
            + separator
            + ("\n" if content else "")
            + "\n".join([START, *sorted(entries), END, ""])
        )
    else:
        return
    if updated != content:
        gitignore.write_text(updated, encoding="utf-8")
