"""Tests for odoo_boost.ast_scanner (analyzer)."""

from __future__ import annotations

from pathlib import Path

from odoo_boost.ast_scanner.analyzer import (
    _scan_addon_cached,
    find_local_xml_id,
    find_model_in_local_files,
    parse_python_file,
    parse_xml_file,
    scan_addon,
    scan_addon_cached,
)


def test_parse_python_file(tmp_path: Path):
    py_code = """
from odoo import models, fields, api

class TestModel(models.Model):
    _name = "test.model"
    _description = "Test Model"

    name = fields.Char(string="Name", required=True)
    partner_id = fields.Many2one("res.partner", string="Partner")
    count = fields.Integer(default=0)

    @api.depends("name")
    def _compute_something(self):
        pass
"""
    py_file = tmp_path / "models.py"
    py_file.write_text(py_code)

    models = parse_python_file(py_file)
    assert len(models) == 1
    m = models[0]
    assert m["_name"] == "test.model"
    assert m["_description"] == "Test Model"
    assert "name" in m["fields"]
    assert m["fields"]["name"]["type"] == "Char"
    assert m["fields"]["name"]["attributes"]["required"] is True
    assert m["fields"]["partner_id"]["type"] == "Many2one"
    assert m["fields"]["partner_id"]["attributes"]["comodel_name"] == "res.partner"
    assert len(m["methods"]) == 1
    assert m["methods"][0]["name"] == "_compute_something"
    assert "api.depends" in m["methods"][0]["decorators"]


def test_parse_xml_file(tmp_path: Path):
    xml_code = """<?xml version="1.0" encoding="utf-8"?>
<odoo>
    <record id="view_test_model_form" model="ir.ui.view">
        <field name="name">test.model.form</field>
        <field name="model">test.model</field>
    </record>
    <template id="test_template">
        <div>Hello</div>
    </template>
    <menuitem id="menu_test" name="Test Menu" parent="base.menu_root"/>
</odoo>
"""
    xml_file = tmp_path / "views.xml"
    xml_file.write_text(xml_code)

    data = parse_xml_file(xml_file)
    assert len(data["records"]) == 1
    assert data["records"][0]["id"] == "view_test_model_form"
    assert data["records"][0]["model"] == "ir.ui.view"
    assert "name" in data["records"][0]["fields"]

    assert len(data["templates"]) == 1
    assert data["templates"][0]["id"] == "test_template"

    assert len(data["menuitems"]) == 1
    assert data["menuitems"][0]["id"] == "menu_test"


def test_scan_addon(tmp_path: Path):
    manifest = """{
    "name": "My Custom Addon",
    "version": "1.0.0",
    "depends": ["base"],
}
"""
    (tmp_path / "__manifest__.py").write_text(manifest)
    (tmp_path / "models.py").write_text("""
from odoo import models, fields

class MyCustom(models.Model):
    _name = "my.custom"
    title = fields.Char(string="Title")
""")
    (tmp_path / "views.xml").write_text("""
<odoo>
    <record id="my_custom_view" model="ir.ui.view">
        <field name="name">my.custom.view</field>
    </record>
</odoo>
""")

    scanned = scan_addon(tmp_path)
    assert scanned["addon_name"] == tmp_path.name
    assert scanned["manifest"]["name"] == "My Custom Addon"
    assert len(scanned["models"]) == 1
    assert scanned["models"][0]["_name"] == "my.custom"
    assert len(scanned["records"]) == 1
    assert scanned["records"][0]["id"] == "my_custom_view"

    # Test find_local_xml_id
    found_xml = find_local_xml_id(tmp_path, "my_custom.my_custom_view")
    assert found_xml is not None
    assert found_xml["id"] == "my_custom_view"

    # Test find_model_in_local_files
    found_model = find_model_in_local_files(tmp_path, "my.custom")
    assert found_model is not None
    assert found_model["class_name"] == "MyCustom"


def test_cached_scan_reuses_unchanged_files_and_invalidates(tmp_path: Path, monkeypatch):
    import odoo_boost.ast_scanner.analyzer as analyzer

    source = tmp_path / "model.py"
    source.write_text("from odoo import models\nclass A(models.Model):\n    _name = 'x.a'\n")
    original = analyzer.scan_addon
    calls = 0

    def counted(path):
        nonlocal calls
        calls += 1
        return original(path)

    _scan_addon_cached.cache_clear()
    monkeypatch.setattr(analyzer, "scan_addon", counted)
    assert scan_addon_cached(tmp_path)["models"][0]["_name"] == "x.a"
    assert scan_addon_cached(tmp_path)["models"][0]["_name"] == "x.a"
    assert calls == 1

    source.write_text("from odoo import models\nclass B(models.Model):\n    _name = 'x.changed'\n")
    assert scan_addon_cached(tmp_path)["models"][0]["_name"] == "x.changed"
    assert calls == 2
