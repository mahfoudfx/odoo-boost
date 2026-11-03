"""Static source index. Describes declarations, never claims runtime MRO resolution."""

from __future__ import annotations

import ast
from pathlib import Path
from typing import Any

from defusedxml import ElementTree as ET

from odoo_boost.source_files import iter_source_files


def literal(node: ast.AST | None) -> Any:
    try:
        return ast.literal_eval(node) if node is not None else None
    except (ValueError, TypeError, SyntaxError):
        return None


def source_index(root: Path) -> dict[str, Any]:
    models, routes, views, errors = [], [], [], []
    for path in iter_source_files(root, {".py", ".xml"}):
        location = str(path)
        try:
            if path.suffix == ".xml":
                tree = ET.parse(path)
                for record in tree.iter("record"):
                    if record.get("model") == "ir.ui.view":
                        fields = {f.get("name"): f for f in record.findall("field")}
                        parent = fields.get("inherit_id")
                        views.append(
                            {
                                "xml_id": record.get("id"),
                                "file": location,
                                "model": fields["model"].text if "model" in fields else None,
                                "inherit_id": parent.get("ref") if parent is not None else None,
                            }
                        )
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for cls in (n for n in ast.walk(tree) if isinstance(n, ast.ClassDef)):
                attrs = {}
                for node in cls.body:
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                attrs[target.id] = literal(node.value)
                methods = [
                    {"name": n.name, "line": n.lineno}
                    for n in cls.body
                    if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ]
                if attrs.get("_name") or attrs.get("_inherit") or attrs.get("_inherits"):
                    models.append(
                        {
                            "name": attrs.get("_name"),
                            "inherit": attrs.get("_inherit"),
                            "inherits": attrs.get("_inherits"),
                            "class": cls.name,
                            "file": location,
                            "line": cls.lineno,
                            "methods": methods,
                        }
                    )
                for method in (
                    n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
                ):
                    for dec in method.decorator_list:
                        if not isinstance(dec, ast.Call):
                            continue
                        func = dec.func
                        if (isinstance(func, ast.Attribute) and func.attr == "route") or (
                            isinstance(func, ast.Name) and func.id == "route"
                        ):
                            values = {k.arg: literal(k.value) for k in dec.keywords if k.arg}
                            routes.append(
                                {
                                    "file": location,
                                    "line": method.lineno,
                                    "class": cls.name,
                                    "method": method.name,
                                    "routes": literal(dec.args[0])
                                    if dec.args
                                    else values.pop("route", None),
                                    "options": values,
                                    "inherits_route": not dec.args
                                    and "route" not in {k.arg for k in dec.keywords},
                                }
                            )
        except Exception as exc:
            errors.append({"file": location, "error": str(exc)})
    return {
        "models": models,
        "routes": routes,
        "views": views,
        "errors": errors,
        "scope": str(root),
        "complete": not errors,
        "limitation": "Static declarations within this directory; runtime installation order, dynamic decorators, Python MRO and external ancestors are not resolved.",
    }
