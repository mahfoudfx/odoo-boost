"""Skill loading and installation utilities."""

from __future__ import annotations

import importlib.resources
import re
from pathlib import Path

CORE_SKILLS = [
    "creating_models",
    "xml_views",
    "security_rules",
    "owl_components",
    "controllers_routes",
    "report_development",
    "automated_actions",
    "testing",
]

WORKFLOW_SKILLS = [
    "code_review",
    "upgrade_analysis",
    "spec_driven_dev",
    "conventional_commit",
]

DOMAIN_SKILLS = [
    "domain_accounting",
    "domain_stock",
    "domain_multi_company",
    "domain_mail_chatter",
    "domain_wizards",
    "domain_crons_automation",
    "domain_computed_fields",
    "domain_inheritance",
]

SKILL_CATEGORIES: dict[str, list[str]] = {
    "core": CORE_SKILLS,
    "workflows": WORKFLOW_SKILLS,
    "domain": DOMAIN_SKILLS,
    "domain_patterns": DOMAIN_SKILLS,
}

_SKILL_DIRS = CORE_SKILLS + WORKFLOW_SKILLS + DOMAIN_SKILLS


def list_skills(category: str | None = None) -> list[str]:
    """Return the list of available skill names, optionally filtered by category."""
    if category:
        cat_key = category.lower()
        if cat_key in SKILL_CATEGORIES:
            return list(SKILL_CATEGORIES[cat_key])
        return []
    return list(_SKILL_DIRS)


def get_skill_category(skill_name: str) -> str:
    """Return the category name for a given skill."""
    if skill_name in CORE_SKILLS:
        return "Core"
    if skill_name in WORKFLOW_SKILLS:
        return "Workflows"
    if skill_name in DOMAIN_SKILLS:
        return "Domain Patterns"
    return "Custom"


def load_skill(skill_name: str) -> str:
    """Read and return the SKILL.md content for a skill."""
    ref = importlib.resources.files("odoo_boost.skills") / skill_name / "SKILL.md"
    return ref.read_text(encoding="utf-8")


def parse_skill_metadata(skill_name: str) -> dict[str, str]:
    """Extract metadata (name, description, globs) from a skill's frontmatter."""
    try:
        content = load_skill(skill_name)
    except Exception:
        return {"name": skill_name, "description": "", "globs": ""}

    meta: dict[str, str] = {"name": skill_name, "description": "", "globs": ""}
    # Extract YAML frontmatter between --- and ---
    fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if fm_match:
        fm_text = fm_match.group(1)
        name_match = re.search(r"^name:\s*(.+)$", fm_text, re.MULTILINE)
        if name_match:
            meta["name"] = name_match.group(1).strip()
        desc_match = re.search(r"^description:\s*(.+)$", fm_text, re.MULTILINE)
        if desc_match:
            meta["description"] = desc_match.group(1).strip()
        globs_match = re.search(r"^globs:\s*(.+)$", fm_text, re.MULTILINE)
        if globs_match:
            meta["globs"] = globs_match.group(1).strip()

    return meta


def generate_skills_routing() -> str:
    """Generate a markdown routing table summarizing all available skills.

    This table serves as a fast-lookup index for LLM agents to progressively
    retrieve only relevant skill documents.
    """
    lines = [
        "# Odoo Boost Skills Catalog & Progressive Routing",
        "",
        "Use this index to identify and load specialized Odoo instructions on demand.",
        "",
        "| Skill Directory | Category | Trigger / Globs | Description |",
        "|---|---|---|---|",
    ]

    for skill_name in _SKILL_DIRS:
        meta = parse_skill_metadata(skill_name)
        category = get_skill_category(skill_name)
        globs = meta.get("globs", "-") or "-"
        desc = meta.get("description", "")
        lines.append(f"| `{skill_name}` | {category} | `{globs}` | {desc} |")

    lines.append("")
    return "\n".join(lines)


def install_skills(
    target_dir: Path,
    category: str | None = None,
    write_routing: bool = True,
) -> list[Path]:
    """Copy skill directories into *target_dir* and optionally write routing table.

    Returns a list of created file paths.
    """
    target_dir.mkdir(parents=True, exist_ok=True)
    created: list[Path] = []
    skills = list_skills(category=category)

    for skill_name in skills:
        dest = target_dir / skill_name
        dest.mkdir(parents=True, exist_ok=True)

        content = load_skill(skill_name)
        skill_file = dest / "SKILL.md"
        skill_file.write_text(content, encoding="utf-8")
        created.append(skill_file)

    if write_routing:
        routing_file = target_dir / "SKILLS_ROUTING.md"
        routing_file.write_text(generate_skills_routing(), encoding="utf-8")
        created.append(routing_file)

    return created
