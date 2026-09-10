"""Pure-Python AST and XML analyzer for local Odoo addons on disk."""

from __future__ import annotations

import ast
import logging
from pathlib import Path
from typing import Any

try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def _get_literal_value(node: ast.AST) -> Any:
    """Safely extract a literal or simple string/boolean value from an AST node."""
    if isinstance(node, ast.Constant):
        return node.value
    if isinstance(node, ast.Str):
        return node.s
    if isinstance(node, ast.Num):
        return node.n
    if isinstance(node, ast.NameConstant):
        return node.value
    if isinstance(node, ast.List):
        return [_get_literal_value(elt) for elt in node.elts]
    if isinstance(node, ast.Tuple):
        return tuple(_get_literal_value(elt) for elt in node.elts)
    if isinstance(node, ast.Dict):
        return {
            _get_literal_value(k): _get_literal_value(v)
            for k, v in zip(node.keys, node.values, strict=False)
            if k is not None
        }
    return None


def _extract_decorator_name(dec: ast.AST) -> str:
    """Format decorator name (e.g. 'api.depends')."""
    if isinstance(dec, ast.Name):
        return dec.id
    if isinstance(dec, ast.Attribute):
        return f"{_extract_decorator_name(dec.value)}.{dec.attr}"
    if isinstance(dec, ast.Call):
        return _extract_decorator_name(dec.func)
    return "decorator"


class _ModelVisitor(ast.NodeVisitor):
    """AST visitor extracting Odoo model definitions, fields, and methods."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.models: list[dict[str, Any]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        # Check if inherits from an Odoo model class or looks like an Odoo model
        model_info: dict[str, Any] = {
            "class_name": node.name,
            "file": self.filename,
            "line": node.lineno,
            "_name": None,
            "_inherit": None,
            "_inherits": None,
            "_description": None,
            "fields": {},
            "methods": [],
        }

        is_odoo_model = False

        # Inspect bases
        for base in node.bases:
            if isinstance(base, ast.Attribute):
                if base.attr in ("Model", "TransientModel", "AbstractModel"):
                    is_odoo_model = True
            elif isinstance(base, ast.Name) and "Model" in base.id:
                is_odoo_model = True

        for item in node.body:
            # Model attributes: _name, _inherit, _description, etc.
            if isinstance(item, ast.Assign):
                for target in item.targets:
                    if isinstance(target, ast.Name):
                        if target.id in (
                            "_name",
                            "_inherit",
                            "_inherits",
                            "_description",
                            "_order",
                            "_rec_name",
                        ):
                            val = _get_literal_value(item.value)
                            model_info[target.id] = val
                            is_odoo_model = True

                        # Field definitions: name = fields.Char(...)
                        elif isinstance(item.value, ast.Call):
                            call = item.value
                            func = call.func
                            if (
                                isinstance(func, ast.Attribute)
                                and isinstance(func.value, ast.Name)
                                and func.value.id == "fields"
                            ):
                                is_odoo_model = True
                                field_name = target.id
                                field_type = func.attr
                                field_kwargs: dict[str, Any] = {}

                                # First arg for relational fields is often comodel_name
                                if call.args and field_type in (
                                    "Many2one",
                                    "One2many",
                                    "Many2many",
                                ):
                                    comodel = _get_literal_value(call.args[0])
                                    if comodel:
                                        field_kwargs["comodel_name"] = comodel

                                for kw in call.keywords:
                                    if kw.arg:
                                        field_kwargs[kw.arg] = _get_literal_value(kw.value)

                                model_info["fields"][field_name] = {
                                    "type": field_type,
                                    "line": item.lineno,
                                    "attributes": field_kwargs,
                                }

            # Methods
            elif isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                decorators = [_extract_decorator_name(d) for d in item.decorator_list]
                model_info["methods"].append(
                    {
                        "name": item.name,
                        "line": item.lineno,
                        "decorators": decorators,
                    }
                )

        if is_odoo_model and (model_info["_name"] or model_info["_inherit"]):
            self.models.append(model_info)

        self.generic_visit(node)


def parse_python_file(path: Path) -> list[dict[str, Any]]:
    """Parse a single Python file and extract Odoo model definitions."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(content, filename=str(path))
    except Exception as exc:
        logger.debug("Could not parse Python file %s: %s", path, exc)
        return []

    visitor = _ModelVisitor(filename=str(path))
    visitor.visit(tree)
    return visitor.models


def parse_xml_file(path: Path) -> dict[str, Any]:
    """Parse an XML file and extract Odoo records, templates, views, and menuitems."""
    res: dict[str, Any] = {
        "records": [],
        "templates": [],
        "menuitems": [],
    }

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
        root = ET.fromstring(content)
    except Exception as exc:
        logger.debug("Could not parse XML file %s: %s", path, exc)
        return res

    for elem in root.iter():
        tag = elem.tag.split("}")[-1]  # strip namespace if present

        if tag == "record":
            rec_id = elem.attrib.get("id")
            model = elem.attrib.get("model")
            fields = [
                f.attrib.get("name") for f in elem.findall(".//field") if f.attrib.get("name")
            ]
            if rec_id:
                res["records"].append(
                    {
                        "id": rec_id,
                        "model": model,
                        "file": str(path),
                        "fields": fields,
                    }
                )

        elif tag == "template":
            tmpl_id = elem.attrib.get("id")
            if tmpl_id:
                res["templates"].append(
                    {
                        "id": tmpl_id,
                        "file": str(path),
                        "name": elem.attrib.get("name"),
                    }
                )

        elif tag == "menuitem":
            menu_id = elem.attrib.get("id")
            if menu_id:
                res["menuitems"].append(
                    {
                        "id": menu_id,
                        "name": elem.attrib.get("name"),
                        "parent": elem.attrib.get("parent"),
                        "action": elem.attrib.get("action"),
                        "file": str(path),
                    }
                )

    return res


def scan_addon(addon_path: str | Path) -> dict[str, Any]:
    """Scan an entire local addon directory on disk for models, fields, and XML definitions."""
    path = Path(addon_path).resolve()
    if not path.is_dir():
        return {"error": f"Path '{path}' is not a directory"}

    result: dict[str, Any] = {
        "addon_name": path.name,
        "path": str(path),
        "manifest": None,
        "models": [],
        "records": [],
        "templates": [],
        "menuitems": [],
        "python_files_count": 0,
        "xml_files_count": 0,
    }

    # Manifest check
    manifest_file = path / "__manifest__.py"
    if not manifest_file.exists():
        manifest_file = path / "__openerp__.py"
    if manifest_file.exists():
        try:
            m_content = manifest_file.read_text(encoding="utf-8", errors="replace")
            m_val = ast.literal_eval(m_content)
            if isinstance(m_val, dict):
                result["manifest"] = {
                    "name": m_val.get("name"),
                    "version": m_val.get("version"),
                    "depends": m_val.get("depends", []),
                    "data": m_val.get("data", []),
                    "license": m_val.get("license"),
                }
        except Exception as exc:
            logger.warning("Error evaluating manifest %s: %s", manifest_file, exc)
            result["manifest"] = {"raw": "Error evaluating manifest dictionary"}

    # Scan Python files
    for py_file in sorted(path.rglob("*.py")):
        # Skip hidden or build directories
        if any(part.startswith((".", "__pycache__", "build", "dist")) for part in py_file.parts):
            continue
        result["python_files_count"] += 1
        models = parse_python_file(py_file)
        result["models"].extend(models)

    # Scan XML files
    for xml_file in sorted(path.rglob("*.xml")):
        if any(part.startswith((".", "build", "dist")) for part in xml_file.parts):
            continue
        result["xml_files_count"] += 1
        xml_data = parse_xml_file(xml_file)
        result["records"].extend(xml_data["records"])
        result["templates"].extend(xml_data["templates"])
        result["menuitems"].extend(xml_data["menuitems"])

    return result


def find_local_xml_id(addon_path: str | Path, xml_id: str) -> dict[str, Any] | None:
    """Find a specific XML ID definition in the local addon directory."""
    path = Path(addon_path).resolve()
    target_id = xml_id.split(".")[-1] if "." in xml_id else xml_id

    for xml_file in sorted(path.rglob("*.xml")):
        if any(part.startswith((".", "build", "dist")) for part in xml_file.parts):
            continue
        data = parse_xml_file(xml_file)
        for rec in data["records"]:
            if rec["id"] == target_id:
                return {"type": "record", **rec}
        for tmpl in data["templates"]:
            if tmpl["id"] == target_id:
                return {"type": "template", **tmpl}
        for menu in data["menuitems"]:
            if menu["id"] == target_id:
                return {"type": "menuitem", **menu}

    return None


def find_model_in_local_files(addon_path: str | Path, model_name: str) -> dict[str, Any] | None:
    """Find a specific Odoo model definition in local Python files."""
    path = Path(addon_path).resolve()

    for py_file in sorted(path.rglob("*.py")):
        if any(part.startswith((".", "__pycache__", "build", "dist")) for part in py_file.parts):
            continue
        models = parse_python_file(py_file)
        for m in models:
            if m.get("_name") == model_name or m.get("_inherit") == model_name:
                return m

    return None
