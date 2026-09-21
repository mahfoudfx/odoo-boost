"""Assembles guidelines from markdown parts into a single document."""

from __future__ import annotations

import importlib.resources
from pathlib import Path

from odoo_boost.versions import get_version_profile, version_guidance

_CORE_FILES = [
    "operating_rules.md",
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
    """Build a compact adaptive router; detailed expert topics stay on disk."""
    lines = [
        "# Odoo Boost: adaptive development workflow",
        "",
        "Solve the user's business request with the smallest correct change. Detect the",
        "mode from the task; the user does not need to name a mode.",
        "",
        "## Version contract (always active)",
        "",
        version_guidance(version),
        "Never substitute another release's XML, ORM, controller, or frontend syntax.",
        "If a required fact is absent or the version is unverified, inspect the target source",
        "or load the target version note before editing.",
        "",
        "## Fast mode (default for small iterative edits)",
        "",
        "Use for labels, translations, adding/renaming/moving a field or column, simple",
        "visibility/readonly expressions, and a small local method or view adjustment.",
        "",
        "1. Inspect the target file and its closest inherited definition. Reuse the existing",
        "   local pattern and preserve the surrounding style.",
        "2. Make the direct edit. Do not create a plan, launch live/database tools, load broad",
        "   guidelines, or scan the whole repository unless the edit exposes uncertainty.",
        "3. Use 2-4 tool calls normally. Do not reread unchanged files or repeat a call. For a",
        "   visual-only view change, a browser refresh by the user can be sufficient feedback.",
        "4. Check the diff and the edited syntax. Run a focused check only when it adds useful",
        "   evidence; do not manufacture tests for a reversible presentation-only change.",
        "",
        "## Deep mode",
        "",
        "Use for a new module, multi-model business workflow, accounting/stock/security work,",
        "migration, unfamiliar inheritance, architectural refactor, persistent data change,",
        "performance investigation, audit, or a failed fast-mode attempt.",
        "",
        "1. State the business outcome, version, invariants, and smallest viable scope.",
        "2. Read only the relevant topic references and routed skills below. Trace overrides,",
        "   security, consumers, and side effects when the change crosses those boundaries.",
        "3. Start compact and deepen progressively. Reassess every 8 tool calls; stop at 24",
        "   unless an exhaustive audit was requested or new evidence justifies continuing.",
        "4. Implement, run risk-appropriate checks, and review the final diff.",
        "",
        "Escalate from fast to deep only when scope or evidence matches a deep trigger. Security",
        "boundaries, access control, public controllers, `sudo()`, raw SQL, accounting entries,",
        "and stock valuation always require their focused reference or skill.",
        "",
        "## On-demand references",
        "",
        "Paths are relative to the project root. Open only what the current task needs.",
        f"Skill routing: `{Path(reference_dir).parent.as_posix()}/SKILLS_ROUTING.md`.",
        f"Operating and investigation rules: `{reference_dir}/operating_rules.md`.",
        "",
    ]
    for filename in _CORE_FILES:
        if filename == "operating_rules.md":
            continue
        title = next(
            (
                line.lstrip("# ").strip()
                for line in _read_resource(filename).splitlines()
                if line.startswith("#")
            ),
            filename.removesuffix(".md"),
        )
        lines.append(f"- {title}: `{reference_dir}/{filename}`")
    version_file = _version_file(version)
    if version_file:
        lines.append(f"- Odoo {version} version notes: `{reference_dir}/{version_file}`")
    lines.extend(
        [
            "",
            "The complete combined expert reference is available through",
            "`odoo://guidelines/oca`; use it for broad audits, not routine edits.",
        ]
    )
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
