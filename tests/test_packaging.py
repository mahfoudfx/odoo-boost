"""Packaging integrity checks (type marker + bundled data files)."""

from __future__ import annotations

import importlib.resources


class TestPackageData:
    def test_py_typed_marker(self):
        assert importlib.resources.files("odoo_boost").joinpath("py.typed").is_file()

    def test_bundled_guidelines(self):
        assert (
            importlib.resources.files("odoo_boost")
            .joinpath("guidelines", "core", "coding_style.md")
            .is_file()
        )

    def test_bundled_skills(self):
        from odoo_boost.skills.loader import list_skills

        assert len(list_skills()) == 20
        assert (
            importlib.resources.files("odoo_boost")
            .joinpath("skills", "creating_models", "SKILL.md")
            .is_file()
        )
