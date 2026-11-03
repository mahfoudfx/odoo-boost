"""Conservative local checks with explicit certainty and coverage."""

from __future__ import annotations

import ast
import csv
from pathlib import Path
from typing import Any

from defusedxml import ElementTree as ET

from odoo_boost.source_files import iter_source_files
from odoo_boost.source_trace import literal
from odoo_boost.versions import get_version_profile


def check_static(target: Path, version: str | None = None) -> dict[str, Any]:
    issues: list[dict[str, Any]] = []
    files = (
        [target] if target.is_file() else list(iter_source_files(target, {".py", ".xml", ".csv"}))
    )

    def add(path: Path, line: int, code: str, message: str, review: bool = False) -> None:
        issues.append(
            {
                "file": str(path),
                "line": line,
                "code": code,
                "message": message,
                "type": "warning" if review else "error",
                "certainty": "review_required" if review else "definite",
                "engine": "static",
            }
        )

    models: list[tuple[Path, int, str]] = []
    grants: set[str] = set()
    declarations: set[str] = set()
    references: list[tuple[Path, str]] = []
    profile = get_version_profile(version)
    for path in files:
        try:
            if path.name == "ir.model.access.csv":
                with path.open(encoding="utf-8-sig", newline="") as stream:
                    for row in csv.DictReader(stream):
                        if any(
                            row.get(f"perm_{p}") == "1"
                            for p in ("read", "write", "create", "unlink")
                        ):
                            grants.add(row.get("model_id:id", ""))
                continue
            if path.suffix == ".xml":
                tree = ET.parse(path)
                for node in tree.iter():
                    if node.get("id"):
                        declarations.add(node.get("id", ""))
                    if node.get("ref"):
                        references.append((path, node.get("ref", "")))
                    if (
                        profile
                        and profile.features.get("view_modifiers") == "inline expressions"
                        and ("attrs" in node.attrib or "states" in node.attrib)
                    ):
                        add(
                            path,
                            1,
                            "OBXML002",
                            "Legacy attrs/states modifier: verify target-version view syntax.",
                            True,
                        )
                continue
            if path.suffix != ".py":
                continue
            tree = ast.parse(path.read_text(encoding="utf-8"))
            if path.name in {"__manifest__.py", "__openerp__.py"}:
                manifest = (
                    literal(tree.body[0].value)
                    if tree.body and isinstance(tree.body[0], ast.Expr)
                    else None
                )
                if isinstance(manifest, dict):
                    for entry in manifest.get("data", []) + manifest.get("demo", []):
                        candidate = (path.parent / entry).resolve()
                        if (
                            not candidate.is_relative_to(path.parent.resolve())
                            or not candidate.is_file()
                        ):
                            add(
                                path,
                                1,
                                "OBMAN001",
                                f"Manifest file is missing or outside addon: {entry}",
                            )
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    attrs = {
                        t.id: literal(n.value)
                        for n in node.body
                        if isinstance(n, ast.Assign)
                        for t in n.targets
                        if isinstance(t, ast.Name)
                    }
                    transient = any(
                        isinstance(b, ast.Attribute)
                        and b.attr in {"TransientModel", "AbstractModel"}
                        for b in node.bases
                    )
                    if isinstance(attrs.get("_name"), str) and not transient:
                        models.append((path, node.lineno, attrs["_name"]))
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute):
                    if node.func.attr == "sudo":
                        add(
                            path,
                            node.lineno,
                            "OBSEC001",
                            "sudo() bypasses access checks; review authorization and company boundaries.",
                            True,
                        )
                    if node.func.attr in {"execute", "executemany"} and node.args:
                        arg = node.args[0]
                        if isinstance(arg, (ast.JoinedStr, ast.BinOp)) or (
                            isinstance(arg, ast.Call)
                            and isinstance(arg.func, ast.Attribute)
                            and arg.func.attr == "format"
                        ):
                            add(
                                path,
                                node.lineno,
                                "OBSEC002",
                                "Dynamically constructed SQL candidate; verify parameterization.",
                                True,
                            )
                    if node.func.attr == "route":
                        opts = {k.arg: literal(k.value) for k in node.keywords}
                        if opts.get("auth") in {"public", "none"} or opts.get("csrf") is False:
                            add(
                                path,
                                node.lineno,
                                "OBSEC003",
                                "Public/no-auth or CSRF-disabled route: review authentication, authorization and request validation.",
                                True,
                            )
        except Exception as exc:
            add(path, getattr(exc, "lineno", 1) or 1, "OBPARSE001", f"Cannot parse source: {exc}")
    if target.is_dir():
        for path, line, model in models:
            identifier = "model_" + model.replace(".", "_")
            if not any(g == identifier or g.endswith("." + identifier) for g in grants):
                add(
                    path,
                    line,
                    "OBACL001",
                    f"No local granting ACL found for {model}; check dependency ACLs and intended exposure.",
                    True,
                )
        for path, ref in references:
            if "." not in ref and ref not in declarations:
                add(
                    path,
                    1,
                    "OBXML003",
                    f"Unresolved local reference {ref}; verify dependency/load order.",
                    True,
                )
    return {
        "issues": issues,
        "status": "failed" if any(i["type"] == "error" for i in issues) else "passed",
        "coverage": [
            "Python/XML syntax",
            "manifest data/demo existence",
            "local ACL candidates",
            "SQL/sudo/controller review candidates",
            "local XML references",
        ],
        "limitations": [
            "No runtime XPath validation",
            "No proof of effective permissions or company isolation",
            "No complete SQL dataflow or N+1 detection",
            "ACL and reference checks require addon-directory scope",
        ],
    }
