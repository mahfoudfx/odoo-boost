"""Skill loading and installation utilities."""

from __future__ import annotations

import importlib.resources
import logging
import re
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

CORE_SKILLS = [
    "creating_models",
    "xml_views",
    "security_rules",
    "owl_components",
    "controllers_routes",
    "report_development",
    "automated_actions",
    "testing",
    "pattern_library",
]

WORKFLOW_SKILLS = [
    "code_review",
    "source_trace",
    "odoo_core_contribution",
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

# Single source of truth derived from the category map, preserving order and
# removing duplicates (e.g. the 'domain_patterns' alias).
_SKILL_DIRS = list(dict.fromkeys(CORE_SKILLS + WORKFLOW_SKILLS + DOMAIN_SKILLS))


def list_skills(category: str | None = None) -> list[str]:
    """Return the list of available skill names, optionally filtered by category."""
    if category:
        cat_key = category.lower()
        if cat_key in SKILL_CATEGORIES:
            return list(SKILL_CATEGORIES[cat_key])
        return []
    return list(_SKILL_DIRS)


def skill_id(skill_name: str) -> str:
    """Return the portable Agent Skills identifier for a bundled skill."""
    return skill_name.replace("_", "-")


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
    if skill_name not in _SKILL_DIRS:
        raise FileNotFoundError(f"Unknown bundled skill: {skill_name}")
    ref = importlib.resources.files("odoo_boost.skills") / skill_name / "SKILL.md"
    return ref.read_text(encoding="utf-8")


def load_skill_files(skill_name: str) -> dict[str, str]:
    """Return every bundled text file for a skill, keyed by relative path."""
    if skill_name not in _SKILL_DIRS:
        raise FileNotFoundError(f"Unknown bundled skill: {skill_name}")
    root = importlib.resources.files("odoo_boost.skills") / skill_name
    files: dict[str, str] = {}

    def collect(node: Any, prefix: Path = Path()) -> None:
        for entry in node.iterdir():
            relative = prefix / entry.name
            if entry.is_dir():
                collect(entry, relative)
            elif entry.is_file():
                files[relative.as_posix()] = entry.read_text(encoding="utf-8")

    collect(root)
    return files


def parse_skill_metadata(skill_name: str) -> dict[str, str]:
    """Extract metadata (name, description, globs) from a skill's YAML frontmatter."""
    meta: dict[str, str] = {"name": skill_name, "description": "", "globs": ""}
    try:
        content = load_skill(skill_name)
    except (FileNotFoundError, TypeError, ModuleNotFoundError):
        logger.debug("Skill '%s' could not be loaded for metadata parsing.", skill_name)
        return meta

    fm_match = re.search(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    if not fm_match:
        return meta

    try:
        data: Any = yaml.safe_load(fm_match.group(1))
    except yaml.YAMLError:
        logger.warning("Skill '%s' has invalid YAML frontmatter.", skill_name)
        return meta

    if not isinstance(data, dict):
        return meta

    for key in ("name", "description", "globs"):
        value = data.get(key)
        if value is not None:
            if key == "globs" and isinstance(value, list):
                meta[key] = ", ".join(str(item).strip() for item in value)
            else:
                meta[key] = str(value).strip()

    return meta


def generate_skills_routing(category: str | None = None) -> str:
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

    for skill_name in list_skills(category=category):
        meta = parse_skill_metadata(skill_name)
        category = get_skill_category(skill_name)
        globs = meta.get("globs", "-") or "-"
        desc = meta.get("description", "").replace("|", "\\|").replace("\n", " ")
        lines.append(f"| `{skill_id(skill_name)}` | {category} | `{globs}` | {desc} |")

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
        dest = target_dir / skill_id(skill_name)
        for relative, content in load_skill_files(skill_name).items():
            skill_file = dest / relative
            skill_file.parent.mkdir(parents=True, exist_ok=True)
            skill_file.write_text(content, encoding="utf-8")
            created.append(skill_file)

    if write_routing:
        routing_file = target_dir / "SKILLS_ROUTING.md"
        routing_file.write_text(generate_skills_routing(category=category), encoding="utf-8")
        created.append(routing_file)

    return created
