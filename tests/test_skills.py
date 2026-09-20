"""Tests for odoo_boost.skills.loader."""

from __future__ import annotations

import pytest

from odoo_boost.skills.loader import (
    _SKILL_DIRS,
    CORE_SKILLS,
    DOMAIN_SKILLS,
    WORKFLOW_SKILLS,
    generate_skills_routing,
    get_skill_category,
    install_skills,
    list_skills,
    load_skill,
    parse_skill_metadata,
)


class TestListSkills:
    def test_returns_list(self):
        skills = list_skills()
        assert isinstance(skills, list)

    def test_count(self):
        assert len(list_skills()) == 20

    def test_categories(self):
        core = list_skills(category="core")
        assert len(core) == 8
        assert set(core) == set(CORE_SKILLS)

        workflows = list_skills(category="workflows")
        assert len(workflows) == 4
        assert set(workflows) == set(WORKFLOW_SKILLS)

        domain = list_skills(category="domain")
        assert len(domain) == 8
        assert set(domain) == set(DOMAIN_SKILLS)

    def test_invalid_category_returns_empty(self):
        assert list_skills(category="nonexistent_category") == []

    def test_known_skills_present(self):
        skills = list_skills()
        for expected in [
            "creating_models",
            "xml_views",
            "security_rules",
            "owl_components",
            "code_review",
            "upgrade_analysis",
            "domain_accounting",
            "domain_stock",
        ]:
            assert expected in skills

    def test_returns_copy(self):
        """list_skills() should not expose the internal list."""
        a = list_skills()
        b = list_skills()
        assert a == b
        a.append("fake")
        assert "fake" not in list_skills()

    def test_no_duplicate_dirs(self):
        assert len(_SKILL_DIRS) == len(set(_SKILL_DIRS))

    def test_filesystem_matches_categories(self):
        """Every skill directory on disk must be categorized (drift guard)."""
        import importlib.resources

        root = importlib.resources.files("odoo_boost.skills")
        on_disk = sorted(
            entry.name
            for entry in root.iterdir()
            if entry.is_dir() and not entry.name.startswith("__")
        )
        assert on_disk == sorted(_SKILL_DIRS)


class TestSkillMetadataAndRouting:
    def test_get_skill_category(self):
        assert get_skill_category("creating_models") == "Core"
        assert get_skill_category("code_review") == "Workflows"
        assert get_skill_category("domain_accounting") == "Domain Patterns"
        assert get_skill_category("custom_xyz") == "Custom"

    def test_parse_skill_metadata(self):
        meta = parse_skill_metadata("code_review")
        assert meta["name"] == "Odoo Code Review"
        assert "security" in meta["description"].lower()
        assert meta["globs"] != ""

    def test_generate_skills_routing(self):
        routing = generate_skills_routing()
        assert "# Odoo Boost Skills Catalog & Progressive Routing" in routing
        assert "`code_review`" in routing
        assert "`domain_accounting`" in routing
        assert "`creating_models`" in routing

    def test_generate_category_routing_only_lists_installed_category(self):
        routing = generate_skills_routing(category="workflows")
        assert "`code_review`" in routing
        assert "`creating_models`" not in routing


class TestLoadSkill:
    def test_load_each_skill(self):
        for skill_name in list_skills():
            content = load_skill(skill_name)
            assert isinstance(content, str)
            assert len(content) > 10  # not empty
            assert "SKILL" in content.upper() or "#" in content

    def test_unknown_skill_raises(self):
        with pytest.raises((FileNotFoundError, TypeError, ModuleNotFoundError)):
            load_skill("nonexistent_skill_xyz")

    def test_rejects_path_like_skill_name(self):
        with pytest.raises(FileNotFoundError, match="Unknown bundled skill"):
            load_skill("../guidelines/core/security.md")

    def test_routing_formats_glob_lists_for_readability(self):
        routing = generate_skills_routing()
        assert "`models/**/*.py, __manifest__.py`" in routing
        assert "['models/**/*.py'" not in routing


class TestInstallSkills:
    def test_creates_files(self, tmp_path):
        target = tmp_path / "skills"
        created = install_skills(target)
        # 20 skill files + 1 SKILLS_ROUTING.md = 21 files
        assert len(created) == 21
        skill_files = [p for p in created if p.name == "SKILL.md"]
        assert len(skill_files) == 20
        routing_files = [p for p in created if p.name == "SKILLS_ROUTING.md"]
        assert len(routing_files) == 1
        for path in created:
            assert path.exists()

    def test_install_without_routing(self, tmp_path):
        target = tmp_path / "skills"
        created = install_skills(target, write_routing=False)
        assert len(created) == 20
        for path in created:
            assert path.name == "SKILL.md"

    def test_install_by_category(self, tmp_path):
        target = tmp_path / "skills"
        created = install_skills(target, category="workflows", write_routing=False)
        assert len(created) == 4
        subdirs = sorted(d.name for d in target.iterdir() if d.is_dir())
        assert subdirs == sorted(WORKFLOW_SKILLS)

    def test_category_routing_matches_installed_skills(self, tmp_path):
        target = tmp_path / "skills"
        install_skills(target, category="workflows")
        routing = (target / "SKILLS_ROUTING.md").read_text(encoding="utf-8")
        assert "`code_review`" in routing
        assert "`creating_models`" not in routing

    def test_target_dir_created(self, tmp_path):
        target = tmp_path / "new" / "nested" / "skills"
        install_skills(target)
        assert target.is_dir()

    def test_subdirs_match_skill_names(self, tmp_path):
        target = tmp_path / "skills"
        install_skills(target)
        subdirs = sorted(d.name for d in target.iterdir() if d.is_dir())
        assert subdirs == sorted(_SKILL_DIRS)

    def test_idempotent(self, tmp_path):
        target = tmp_path / "skills"
        first = install_skills(target)
        second = install_skills(target)
        assert len(first) == len(second)
        for path in second:
            assert path.exists()

    def test_content_matches_load(self, tmp_path):
        target = tmp_path / "skills"
        install_skills(target)
        for skill_name in list_skills():
            installed = (target / skill_name / "SKILL.md").read_text(encoding="utf-8")
            loaded = load_skill(skill_name)
            assert installed == loaded
