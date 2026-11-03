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
    skill_id,
)


class TestListSkills:
    def test_returns_list(self):
        skills = list_skills()
        assert isinstance(skills, list)

    def test_count(self):
        assert len(list_skills()) == 25

    def test_categories(self):
        core = list_skills(category="core")
        assert len(core) == 11
        assert set(core) == set(CORE_SKILLS)

        workflows = list_skills(category="workflows")
        assert len(workflows) == 6
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
            "extending_models",
            "translation_edits",
            "xml_views",
            "security_rules",
            "owl_components",
            "code_review",
            "pattern_library",
            "source_trace",
            "odoo_core_contribution",
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
        assert meta["name"] == "code-review"
        assert "security" in meta["description"].lower()
        assert meta["globs"] != ""
        assert "**/i18n/*.po" in parse_skill_metadata("translation_edits")["globs"]

    def test_generate_skills_routing(self):
        routing = generate_skills_routing()
        assert "# Odoo Boost Skills Catalog & Progressive Routing" in routing
        assert "`code-review`" in routing
        assert "`domain-accounting`" in routing
        assert "`creating-models`" in routing
        assert "`extending-models`" in routing
        assert "`translation-edits`" in routing

    def test_generate_category_routing_only_lists_installed_category(self):
        routing = generate_skills_routing(category="workflows")
        assert "`code-review`" in routing
        assert "`creating-models`" not in routing


class TestLoadSkill:
    def test_loaded_files_cannot_mutate_the_bundled_content_cache(self):
        from odoo_boost.skills.loader import load_skill_files

        files = load_skill_files("creating_models")
        original = files["SKILL.md"]
        files["SKILL.md"] = "Caller mutation"
        assert load_skill_files("creating_models")["SKILL.md"] == original

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
    def test_unchanged_update_preserves_file_and_manifest_timestamps(self, tmp_path):
        target = tmp_path / "skills"
        installed = install_skills(target)
        # Fixed timestamps make this check independent of filesystem clock resolution.
        import os

        for path in installed:
            os.utime(path, ns=(1_000_000_000, 1_000_000_000))
        assert install_skills(target) == installed
        assert all(path.stat().st_mtime_ns == 1_000_000_000 for path in installed)

    def test_reports_ownership_manifest_during_install_and_uninstall(self, tmp_path):
        from odoo_boost.generated_files import MANIFEST, remove_owned_files

        target = tmp_path / "skills"
        manifest = target / MANIFEST
        assert manifest in install_skills(target)
        assert manifest in remove_owned_files(target)
        assert not manifest.exists()

    def test_preserves_existing_custom_skill_and_routing(self, tmp_path):
        target = tmp_path / "skills"
        custom = target / "creating-models" / "SKILL.md"
        custom.parent.mkdir(parents=True)
        custom.write_text("My own model creation skill")
        routing = target / "SKILLS_ROUTING.md"
        routing.write_text("My own routing")

        installed = install_skills(target)

        assert custom.read_text() == "My own model creation skill"
        assert routing.read_text() == "My own routing"
        assert custom not in installed and routing not in installed

    def test_updates_owned_content_but_preserves_local_edits(self, tmp_path, monkeypatch):
        from odoo_boost.skills import loader

        target = tmp_path / "skills"
        monkeypatch.setattr(loader, "list_skills", lambda category=None: ["creating_models"])
        monkeypatch.setattr(loader, "load_skill_files", lambda name: {"SKILL.md": "version 1"})
        install_skills(target, write_routing=False)
        skill = target / "creating-models" / "SKILL.md"
        monkeypatch.setattr(loader, "load_skill_files", lambda name: {"SKILL.md": "version 2"})
        install_skills(target, write_routing=False)
        assert skill.read_text() == "version 2"

        skill.write_text("User's changes")
        monkeypatch.setattr(loader, "load_skill_files", lambda name: {"SKILL.md": "version 3"})
        install_skills(target, write_routing=False)
        assert skill.read_text() == "User's changes"

    def test_adopts_identical_legacy_content(self, tmp_path, monkeypatch):
        from odoo_boost.skills import loader

        target = tmp_path / "skills"
        skill = target / "creating-models" / "SKILL.md"
        skill.parent.mkdir(parents=True)
        skill.write_text("legacy version")
        monkeypatch.setattr(loader, "list_skills", lambda category=None: ["creating_models"])
        monkeypatch.setattr(loader, "load_skill_files", lambda name: {"SKILL.md": "legacy version"})
        install_skills(target, write_routing=False)
        monkeypatch.setattr(loader, "load_skill_files", lambda name: {"SKILL.md": "new version"})
        install_skills(target, write_routing=False)
        assert skill.read_text() == "new version"

    def test_uninstall_removes_unchanged_older_files_and_preserves_edits(self, tmp_path):
        from odoo_boost.agents.files import remove_generated_skills
        from odoo_boost.generated_files import write_owned_files

        target = tmp_path / "skills"
        write_owned_files(target, {"old-skill/SKILL.md": "old content", "edited.md": "original"})
        (target / "edited.md").write_text("edited")
        remove_generated_skills(target)
        assert not (target / "old-skill").exists()
        assert (target / "edited.md").read_text() == "edited"

    def test_guideline_references_preserve_edits(self, tmp_path):
        from odoo_boost.guidelines.composer import install_guideline_references

        target = tmp_path / "guidelines"
        install_guideline_references(target, "18.0")
        reference = target / "security.md"
        reference.write_text("Local security policy")
        install_guideline_references(target, "18.0")
        assert reference.read_text() == "Local security policy"

    def test_symlinked_installed_file_is_preserved_on_uninstall(self, tmp_path):
        from odoo_boost.agents.files import remove_generated_skills

        target = tmp_path / "skills"
        install_skills(target)
        skill = target / "creating-models" / "SKILL.md"
        outside = tmp_path / "custom.md"
        outside.write_text("custom")
        skill.unlink()
        skill.symlink_to(outside)

        remove_generated_skills(target)

        assert skill.is_symlink()
        assert outside.read_text() == "custom"

    def test_creates_files(self, tmp_path):
        target = tmp_path / "skills"
        created = install_skills(target)
        assert len(created) > len(list_skills())
        skill_files = [p for p in created if p.name == "SKILL.md"]
        assert len(skill_files) == len(list_skills())
        assert target.joinpath("pattern-library", "references", "INDEX.md").is_file()
        routing_files = [p for p in created if p.name == "SKILLS_ROUTING.md"]
        assert len(routing_files) == 1
        for path in created:
            assert path.exists()

    def test_install_without_routing(self, tmp_path):
        target = tmp_path / "skills"
        created = install_skills(target, write_routing=False)
        assert len(created) > len(list_skills())
        assert sum(path.name == "SKILL.md" for path in created) == len(list_skills())
        assert all(path.name != "SKILLS_ROUTING.md" for path in created)

    def test_install_by_category(self, tmp_path):
        target = tmp_path / "skills"
        created = install_skills(target, category="workflows", write_routing=False)
        assert sum(path.name == "SKILL.md" for path in created) == len(WORKFLOW_SKILLS)
        subdirs = sorted(d.name for d in target.iterdir() if d.is_dir())
        assert subdirs == sorted(name.replace("_", "-") for name in WORKFLOW_SKILLS)

    def test_category_routing_matches_installed_skills(self, tmp_path):
        target = tmp_path / "skills"
        install_skills(target, category="workflows")
        routing = (target / "SKILLS_ROUTING.md").read_text(encoding="utf-8")
        assert "`code-review`" in routing
        assert "`creating-models`" not in routing

    def test_target_dir_created(self, tmp_path):
        target = tmp_path / "new" / "nested" / "skills"
        install_skills(target)
        assert target.is_dir()

    def test_subdirs_match_skill_names(self, tmp_path):
        target = tmp_path / "skills"
        install_skills(target)
        subdirs = sorted(d.name for d in target.iterdir() if d.is_dir())
        assert subdirs == sorted(name.replace("_", "-") for name in _SKILL_DIRS)

    def test_installed_directory_matches_frontmatter_name(self, tmp_path):
        target = tmp_path / "skills"
        install_skills(target)
        for skill_name in list_skills():
            content = (target / skill_id(skill_name) / "SKILL.md").read_text(encoding="utf-8")
            assert f"name: {skill_id(skill_name)}" in content

    def test_idempotent(self, tmp_path):
        target = tmp_path / "skills"
        first = install_skills(target)
        second = install_skills(target)
        assert len(first) == len(second)
        for path in second:
            assert path.exists()

    def test_computed_field_reference_resolves_after_installation(self, tmp_path):
        import re

        target = tmp_path / "skills"
        install_skills(target)
        skill = target / "domain-computed-fields" / "SKILL.md"
        content = skill.read_text(encoding="utf-8")
        references = re.findall(r"\.\./[^\s`)]+/computed-field-patterns\.md", content)
        assert references, "Computed-field guidance must link to its detailed patterns"
        for relative in references:
            reference = (skill.parent / relative).resolve()
            assert reference.is_relative_to(target.resolve())
            assert reference.is_file(), f"Broken installed skill reference: {relative}"

    def test_content_matches_load(self, tmp_path):
        target = tmp_path / "skills"
        install_skills(target)
        for skill_name in list_skills():
            installed = (target / skill_name.replace("_", "-") / "SKILL.md").read_text(
                encoding="utf-8"
            )
            loaded = load_skill(skill_name)
            assert installed == loaded
