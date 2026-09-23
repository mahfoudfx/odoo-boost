"""Assembles guidelines from markdown parts into a single document."""

from __future__ import annotations

import importlib.resources
from pathlib import Path

from odoo_boost.versions import get_version_profile, version_guidance

_CORE_FILES = [
    "operating_rules.md",
    "verification.md",
    "odoo_general.md",
    "module_structure.md",
    "orm_best_practices.md",
    "security.md",
    "views_and_ui.md",
    "controllers.md",
    "javascript_owl.md",
    "testing.md",
    "coding_style.md",
    "oca_standards.md",
]


def _read_resource(subpath: str) -> str:
    """Read a markdown file from the guidelines/core package data."""
    ref = importlib.resources.files("odoo_boost.guidelines") / "core" / subpath
    return ref.read_text(encoding="utf-8")


def _version_file(version: str | None) -> str | None:
    profile = get_version_profile(version)
    return profile.guideline_file if profile else None


def compose_agent_guidelines(version: str | None, reference_dir: str) -> str:
    """Build a small decision router; detailed procedures stay on disk."""
    lines = [
        "# Odoo Boost: working rules",
        "",
        "Make the smallest correct change that fulfills the request. Start at the named",
        "file or symbol; widen only for a dependency, uncertainty, or failed check.",
        "Preserve local conventions. Finish after reviewing the diff and checking the",
        "failure modes the change can realistically introduce.",
        "",
        "## Version and execution boundary",
        "",
        version_guidance(version),
        "Verify unknown version facts against the target source or version note.",
        "Do not run a live Odoo shell, database diagnostic, module upgrade, or server",
        "restart unless the user explicitly requests that operation. Focused offline",
        "checks are allowed.",
        "",
        "## Assurance and urgency",
        "",
        "Low (default): clear, local edits; inspect the target, edit, and check the diff",
        "plus the relevant syntax or behavior. Medium: bounded multi-file changes or",
        "uncertain inheritance; trace direct consumers and run focused checks. High:",
        "migrations, broad refactors, release work, security, data integrity, accounting,",
        "or stock valuation; inspect affected boundaries and validate proportionately.",
        "Escalate when evidence reveals coupling or risk; a small edit can remain low.",
        "Deadline (only when requested) favors the shortest route and brief output at",
        "any assurance level. Resolve required facts and retain the relevant checks.",
        "",
        "## On-demand references",
        "",
        "Paths are relative to the project root. Open only what the task needs.",
        f"Skill routing: `{Path(reference_dir).parent.as_posix()}/SKILLS_ROUTING.md`.",
        f"Operating details: `{reference_dir}/operating_rules.md`.",
        f"Checks by change type: `{reference_dir}/verification.md`.",
        f"Security boundaries: `{reference_dir}/security.md`.",
    ]
    version_file = _version_file(version)
    if version_file:
        lines.append(f"- Odoo {version} version notes: `{reference_dir}/{version_file}`")
    lines.append("")
    return "\n".join(lines) + "\n"


def install_guideline_references(target_dir: Path, version: str | None) -> list[Path]:
    """Write topic files used by the compact generated agent instructions."""
    filenames = list(_CORE_FILES)
    version_file = _version_file(version)
    if version_file:
        filenames.append(version_file)
    created = []
    for filename in filenames:
        path = target_dir / filename
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(_read_resource(filename), encoding="utf-8")
        created.append(path)
    return created


def compose_guidelines_index(version: str | None = None) -> str:
    """Return a compact index (titles and top headings) of the guidelines.

    Useful when an agent wants an overview without loading the full text.
    """
    lines = [
        "# Odoo Boost Guidelines Index",
        "",
        "Use the generated agent instructions to find local topic references.",
        "The `odoo://guidelines/oca` resource contains the full reference when needed.",
        version_guidance(version),
        "",
    ]

    for filename in _CORE_FILES:
        content = _read_resource(filename)
        title = ""
        headings: list[str] = []
        for line in content.splitlines():
            if line.startswith("# "):
                title = line[2:].strip()
            elif line.startswith("## ") and len(headings) < 8:
                headings.append(line[3:].strip())
        if title:
            lines.append(f"## {title}")
            lines.extend(f"- {heading}" for heading in headings)
            lines.append("")

    if version:
        lines.append(f"Version-specific notes: Odoo {version}")
        lines.append("")

    return "\n".join(lines)


def compose_guidelines(version: str | None = None) -> str:
    """Assemble all core guideline files plus a version-specific addendum.

    Args:
        version: Odoo version string (e.g. '17.0', '18.0', '19.0').
                 If None, no version-specific section is appended.

    Returns:
        A single markdown string with all guidelines concatenated.
    """
    parts: list[str] = []

    parts.append("# Odoo Development Guidelines\n")
    parts.append(
        "> Auto-generated by **Odoo Boost**. "
        "These guidelines help AI coding agents write idiomatic Odoo code.\n"
    )

    for filename in _CORE_FILES:
        content = _read_resource(filename)
        parts.append(content.strip())
        parts.append("")  # blank line separator

    parts.append(version_guidance(version))

    # Version-specific addendum
    version_file = _version_file(version)
    if version_file:
        parts.append(_read_resource(version_file).strip())
        parts.append("")

    return "\n\n".join(parts) + "\n"
