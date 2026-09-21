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
        "Solve the user's business request with the smallest correct change. Every task starts",
        "in first-pass coding, regardless of apparent complexity or the model's effort setting.",
        "Detect whether evidence requires escalation; the user does not need to name a level.",
        "If the user",
        "explicitly requests first-pass, medium, or high effort, honor that choice.",
        "",
        "## Version contract (always active)",
        "",
        version_guidance(version),
        "Never substitute another release's XML, ORM, controller, or frontend syntax.",
        "If a required fact is absent or the version is unverified, inspect the target source",
        "or load the target version note before editing.",
        "",
        "## First-pass coding (default)",
        "",
        "Use for well-scoped changes with a clear local implementation: labels, translations,",
        "fields or columns, view expressions, formatting, and small method adjustments. Also",
        "use it as the unconditional starting state for every bug fix and feature request.",
        "",
        "1. Inspect the target file and its closest inherited definition. Reuse the existing",
        "   local pattern and preserve the surrounding style.",
        "2. Make the direct edit. Do not create a plan, launch live/database tools, load broad",
        "   guidelines, scan the whole repository, or run tests by default. Escalate only when",
        "   concrete evidence shows that the local edit is insufficient or risky.",
        "   Never scan an Odoo checkout or addons collection for ordinary custom-addon work.",
        "   If core behavior is genuinely uncertain, inspect only the exact symbol/file needed.",
        "3. Use 2-4 tool calls normally. Before a fifth call, either make the edit or identify",
        "   the concrete unresolved dependency/risk that requires medium effort. After the",
        "   requested edit succeeds, stop. Do not add exploratory reads, broad verification,",
        "   cleanup, or unrelated fixes. Finish with at most a targeted diff/syntax",
        "   check. Do not reread unchanged files or repeat a call. For a",
        "   visual-only view change, a browser refresh by the user can be sufficient feedback.",
        "4. Preserve all always-active contracts, especially the configured Odoo version,",
        "   security basics, local conventions, and the user's scope.",
        "",
        "## Medium effort",
        "",
        "Use for a bounded feature spanning several files/models, unfamiliar inheritance, a",
        "localized refactor, packaging, integration work, persistent schema changes, or a",
        "first-pass attempt that revealed meaningful coupling.",
        "",
        "1. Keep a short internal scope and evidence map; do not create planning artifacts",
        "   unless the user requests them or coordination genuinely requires one.",
        "2. Read only the relevant routed skills/references and trace direct consumers,",
        "   overrides, security, and side effects for the affected boundary.",
        "3. Aim for 5-10 tool calls. Run focused checks for changed behavior and stop after",
        "   reviewing the relevant diff. Do not run the full suite or fix unrelated failures.",
        "",
        "## High effort",
        "",
        "Use for broad architectural refactors, production/release readiness, full packaging or",
        "shipping validation, migrations, security audits, accounting or stock valuation,",
        "data integrity risks, performance investigations, and explicitly exhaustive work.",
        "",
        "1. State the business outcome, version, invariants, risks, and smallest viable scope.",
        "2. Load the necessary expert references progressively and trace all affected boundaries.",
        "3. Use risk-appropriate tests and validation, including broader checks only when their",
        "   signal is relevant. Separate pre-existing or unrelated failures from this task.",
        "4. Reassess every 8 tool calls and stop at 24 unless an exhaustive audit was requested",
        "   or new evidence clearly justifies continuing. Review the final diff and residual risk.",
        "",
        "Escalate one level at a time only for a named dependency, failed direct approach, or",
        "specific risk; apparent complexity alone is insufficient. A high-risk task may",
        "escalate before editing, but still begins with the narrow first-pass inspection. Do",
        "not escalate merely to gain confidence. Security",
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
        "",
        "## Enforcement boundary",
        "",
        "These workflow levels are instructions, not guaranteed model behavior. Models including",
        "Gemini 3.7/3.8 may still enter heavy tool loops even at low effort. Odoo Boost can",
        "limit its own MCP surface, response sizes, and repeated MCP calls. It cannot observe or",
        "cap an agent's native file reads, searches, shell commands, tests, model turns, or total",
        "task tool calls. Stop conditions for those native operations depend on the agent obeying",
        "the generated project instructions.",
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
