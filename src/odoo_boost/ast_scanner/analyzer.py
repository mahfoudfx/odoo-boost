"""Pure-Python AST and XML analyzer for local Odoo addons on disk."""

from __future__ import annotations

import ast
import logging
from functools import lru_cache
from pathlib import Path
from typing import Any

from odoo_boost.source_files import iter_source_files, source_allowed

try:
    import defusedxml.ElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

logger = logging.getLogger(__name__)


def _get_literal_value(node: ast.AST) -> Any:
    """Safely extract a literal or simple string/boolean value from an AST node."""
    if isinstance(node, ast.Constant):
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


def _field_definition(value: ast.AST, line: int) -> dict[str, Any] | None:
    """Extract fields.Type(...) calls, including positional relational targets."""
    if not isinstance(value, ast.Call) or not isinstance(value.func, ast.Attribute):
        return None
    if not isinstance(value.func.value, ast.Name) or value.func.value.id != "fields":
        return None
    field_type = value.func.attr
    attributes: dict[str, Any] = {}
    if value.args and field_type in ("Many2one", "One2many", "Many2many"):
        comodel = _get_literal_value(value.args[0])
        if comodel:
            attributes["comodel_name"] = comodel
    attributes.update({kw.arg: _get_literal_value(kw.value) for kw in value.keywords if kw.arg})
    return {"type": field_type, "line": line, "attributes": attributes}


class _ModelVisitor(ast.NodeVisitor):
    """AST visitor extracting Odoo model definitions, fields, and methods."""

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.models: list[dict[str, Any]] = []

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
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

                        elif field := _field_definition(item.value, item.lineno):
                            model_info["fields"][target.id] = field

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

        if model_info["_name"] or model_info["_inherit"]:
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


@lru_cache(maxsize=512)
def _parse_python_file_cached(path: str, mtime_ns: int, size: int) -> list[dict[str, Any]]:
    """Parse one Python file, keyed by stable file metadata."""
    del mtime_ns, size
    return parse_python_file(Path(path))


@lru_cache(maxsize=512)
def _parse_xml_file_cached(path: str, mtime_ns: int, size: int) -> dict[str, Any]:
    """Parse one XML file, keyed by stable file metadata."""
    del mtime_ns, size
    return parse_xml_file(Path(path))


def _cached_python(path: Path) -> list[dict[str, Any]]:
    stat = path.stat()
    return _parse_python_file_cached(str(path), stat.st_mtime_ns, stat.st_size)


def _cached_xml(path: Path) -> dict[str, Any]:
    stat = path.stat()
    return _parse_xml_file_cached(str(path), stat.st_mtime_ns, stat.st_size)


def scan_addon(addon_path: str | Path) -> dict[str, Any]:
    """Scan an entire local addon directory on disk for models, fields, and XML definitions."""
    path = Path(addon_path).resolve()
    return _scan_sources(path, sorted(iter_source_files(path, {".py", ".xml"})))


def _scan_sources(path: Path, sources: list[Path]) -> dict[str, Any]:
    """Assemble a scan from one inventory, also reused on an addon cache miss."""
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
    if manifest_file.exists() and source_allowed(manifest_file, path):
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

    for source in sources:
        if source.suffix == ".py":
            result["python_files_count"] += 1
            result["models"].extend(_cached_python(source))
        else:
            result["xml_files_count"] += 1
            xml_data = _cached_xml(source)
            for key in ("records", "templates", "menuitems"):
                result[key].extend(xml_data[key])

    return result


def _addon_fingerprint(path: Path) -> tuple[tuple[str, int, int], ...]:
    """Return a cheap signature that changes with relevant addon source files."""
    entries: list[tuple[str, int, int]] = []
    for source in sorted(iter_source_files(path, {".py", ".xml"})):
        try:
            stat = source.stat()
        except OSError:
            continue
        entries.append((source.relative_to(path).as_posix(), stat.st_mtime_ns, stat.st_size))
    return tuple(entries)


@lru_cache(maxsize=32)
def _scan_addon_cached(path: str, fingerprint: tuple[tuple[str, int, int], ...]) -> dict[str, Any]:
    """Cache parsed addon data; *fingerprint* provides automatic invalidation."""
    root = Path(path)
    return _scan_sources(root, [root / relative for relative, _, _ in fingerprint])


def scan_addon_cached(addon_path: str | Path) -> dict[str, Any]:
    """Scan an addon once and reuse the result while relevant files are unchanged."""
    path = Path(addon_path).resolve()
    return _scan_addon_cached(str(path), _addon_fingerprint(path))


def find_local_xml_id(addon_path: str | Path, xml_id: str) -> dict[str, Any] | None:
    """Find an XML ID, preserving explicit namespaces and addon ownership."""
    path = Path(addon_path).resolve()
    for xml_file in sorted(iter_source_files(path, {".xml"})):
        module = path.name
        for parent in xml_file.parents:
            if (parent / "__manifest__.py").is_file() or (parent / "__openerp__.py").is_file():
                module = parent.name
                break
            if parent == path:
                break
        data = _cached_xml(xml_file)
        for key, kind in (
            ("records", "record"),
            ("templates", "template"),
            ("menuitems", "menuitem"),
        ):
            for definition in data[key]:
                declared = definition["id"]
                qualified = declared if "." in declared else f"{module}.{declared}"
                matches = (
                    qualified == xml_id if "." in xml_id else qualified.split(".", 1)[-1] == xml_id
                )
                if matches:
                    return {"type": kind, **definition}
    return None


def model_matches(definition: dict[str, Any], model_name: str) -> bool:
    """Match a model declaration or any model extended through _inherit."""
    inherited = definition.get("_inherit")
    return (
        definition.get("_name") == model_name
        or inherited == model_name
        or isinstance(inherited, (list, tuple))
        and model_name in inherited
    )


def find_model_in_local_files(addon_path: str | Path, model_name: str) -> dict[str, Any] | None:
    """Find a specific Odoo model definition in local Python files."""
    path = Path(addon_path).resolve()

    for py_file in sorted(iter_source_files(path, {".py"})):
        models = _cached_python(py_file)
        for m in models:
            if model_matches(m, model_name):
                return m

    return None
