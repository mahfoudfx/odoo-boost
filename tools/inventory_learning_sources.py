#!/usr/bin/env python3
"""Inventory local learning sources without treating automated inspection as reading.

Run from the project root. Only Python's standard library is required. Coverage
rows retain prior review state when their content is unchanged; changed/removed
inputs remain auditable. Source material is never imported or executed.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import xml.etree.ElementTree as ET
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
from typing import Any
from zipfile import ZipFile

EXAMPLE_ROOTS = {
    "B15-CODE": "Odoo 15 Development Essentials/Odoo-15-Development-Essentials-Examples",
    "E17-CODE": "Odoo-17-Development-Essentials/Odoo-17-Development-Essentials-Examples",
    "B17-CODE": "Odoo-17-Development-Cookbook-5E/Odoo-17-Development-Cookbook-5E-Examples",
    "B19-CODE": "Odoo-19-Development-Cookbook-6E/Odoo-19-Development-Cookbook-6E-Examples",
}
BOOK_ROOTS = {
    "B15": "Odoo 15 Development Essentials",
    "B17": "Odoo-17-Development-Cookbook-5E",
    "B19": "Odoo-19-Development-Cookbook-6E",
}
CYBROSYS_IDS = {
    "development": "CY18-DEV",
    "community": "CY18-COM",
    "enterprise": "CY18-ENT",
    "accounting": "CY18-ACC",
}
IGNORED = {".git", "__pycache__", ".DS_Store"}
REVIEW_FIELDS = (
    "reading",
    "official_verification",
    "execution",
    "lesson_ids",
    "duplicate_context_reviewed",
    "batch_id",
    "review_events",
    "content_reviews",
)


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_json(path: Path, default: Any) -> Any:
    return json.loads(path.read_text()) if path.exists() else default


def source_files(root: Path) -> list[Path]:
    return sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not path.is_symlink()
        and not IGNORED.intersection(path.relative_to(root).parts)
    )


class SectionParser(HTMLParser):
    """Split visible document text at headings, retaining stable heading IDs."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.sections: list[dict[str, str]] = []
        self.current: dict[str, str] | None = None
        self.heading: str | None = None
        self.hidden = 0
        self.used: Counter[str] = Counter()
        self.positions: list[tuple[int, int]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag in {"script", "style"}:
            self.hidden += 1
        if tag in {"h1", "h2", "h3", "h4", "h5", "h6"}:
            identity = dict(attrs).get("id") or f"h-{len(self.sections) + 1}"
            self.used[identity] += 1
            suffix = f"~{self.used[identity]}" if self.used[identity] > 1 else ""
            self.current = {"id": identity + suffix, "title": "", "text": ""}
            self.sections.append(self.current)
            self.positions.append(self.getpos())
            self.heading = tag

    def handle_endtag(self, tag: str) -> None:
        if tag in {"script", "style"}:
            self.hidden = max(0, self.hidden - 1)
        if tag == self.heading:
            self.heading = None

    def handle_data(self, data: str) -> None:
        if self.current is not None and not self.hidden:
            self.current["text"] += " " + data
            if self.heading:
                self.current["title"] += " " + data


def epub_sections(data: bytes) -> list[dict[str, str]]:
    parser = SectionParser()
    source = data.decode("utf-8", errors="replace")
    parser.feed(source)
    sections = [
        {key: " ".join(value.split()) if key != "id" else value for key, value in section.items()}
        for section in parser.sections
    ]
    line_offsets = [0]
    for line in source.splitlines(keepends=True):
        line_offsets.append(line_offsets[-1] + len(line))
    offsets = [line_offsets[line - 1] + column for line, column in parser.positions]
    for index, section in enumerate(sections):
        end = offsets[index + 1] if index + 1 < len(offsets) else len(source)
        # Include markup/attributes: changing a link or code attribute must
        # invalidate review even when the visible text stays the same.
        section["content"] = source[offsets[index] : end]
    return sections


def unit(
    source_id: str,
    identity: str,
    locator: str,
    data: bytes,
    revision: str,
    path: Path,
    batch_id: str,
    **extra: Any,
) -> dict[str, Any]:
    return {
        "unit_id": f"{source_id}:{identity}",
        "source_id": source_id,
        "revision": revision,
        "locator": locator,
        "content_sha256": digest(data),
        "source_path": str(path.resolve()),
        "kind": "code example",
        "inventory": "present",
        "reading": "pending",
        "official_verification": "pending",
        "execution": "not-run",
        "lesson_ids": [],
        "duplicate_of": None,
        "duplicate_context_reviewed": False,
        "batch_id": batch_id,
        "static_checks": [],
        **extra,
    }


def merge_review_state(new: dict[str, Any], old: dict[str, Any] | None) -> dict[str, Any]:
    """Preserve human evidence; invalidate it if the actual unit content changed."""
    if old is None:
        return new
    if old.get("content_sha256") == new.get("content_sha256") and old.get("inventory") == new.get(
        "inventory"
    ):
        merged = {**old, **new}
        for key in (*REVIEW_FIELDS, "revision", "history"):
            if key in old:
                merged[key] = old[key]
        return merged
    snapshot = {
        key: old.get(key)
        for key in (
            "content_sha256",
            "revision",
            "inventory",
            *REVIEW_FIELDS,
        )
    }
    new["history"] = [*old.get("history", []), snapshot]
    return new


def scan_file(path: Path, root: Path, row: dict[str, Any], scan: dict[str, Any]) -> None:
    """Parse syntax and manifest declarations only; never load addon code."""
    source = path.read_bytes()
    check = "python-parse" if path.suffix == ".py" else "xml-parse"
    try:
        if path.suffix == ".py":
            ast.parse(source, filename=row["locator"])
        elif path.suffix == ".xml":
            ET.fromstring(source)
        else:
            return
        row["static_checks"].append(check)
        scan["parsed"][check] += 1
    except (SyntaxError, ValueError, ET.ParseError) as error:
        scan["parse_errors"].append({"unit_id": row["unit_id"], "error": str(error)})
        return
    if path.name not in {"__manifest__.py", "__openerp__.py"}:
        return
    scan["manifest_count"] += 1
    try:
        manifest = ast.literal_eval(source.decode("utf-8-sig"))
        if not isinstance(manifest, dict):
            raise ValueError("manifest is not a literal dictionary")
    except (ValueError, SyntaxError, UnicodeError) as error:
        scan["unresolved_manifests"].append({"unit_id": row["unit_id"], "error": str(error)})
        return
    targets: list[tuple[str, Any]] = []
    for key in ("data", "demo"):
        value = manifest.get(key, [])
        if not isinstance(value, (list, tuple)):
            scan["unresolved_manifests"].append(
                {"unit_id": row["unit_id"], "error": f"{key} is not a file sequence"}
            )
            continue
        targets.extend((key, item) for item in value)
    assets = manifest.get("assets", {})
    if not isinstance(assets, dict):
        scan["unresolved_manifests"].append(
            {"unit_id": row["unit_id"], "error": "assets is not a dictionary"}
        )
        assets = {}
    for bundle, entries in assets.items():
        if isinstance(entries, set):
            scan["manifest_warnings"].append(
                {"unit_id": row["unit_id"], "error": f"{bundle} uses unordered set"}
            )
        if not isinstance(entries, (list, tuple, set)):
            scan["unresolved_manifests"].append(
                {"unit_id": row["unit_id"], "error": f"{bundle} is not an asset sequence"}
            )
            continue
        for entry in entries:
            # Operations such as replace/after can name external addon paths.
            candidates = (
                [entry]
                if isinstance(entry, str)
                else list(entry[1:])
                if isinstance(entry, tuple)
                else []
            )
            for candidate in candidates:
                if isinstance(candidate, str) and candidate.startswith(path.parent.name + "/"):
                    targets.append((bundle, candidate.split("/", 1)[1]))
    for kind, target in targets:
        if not isinstance(target, str):
            scan["unresolved_manifests"].append(
                {"unit_id": row["unit_id"], "error": f"{kind} contains non-string path"}
            )
            continue
        if Path(target).is_absolute() or ".." in Path(target).parts:
            scan["unresolved_manifests"].append(
                {"unit_id": row["unit_id"], "error": f"unsafe declared path {target}"}
            )
            continue
        if not any(candidate.is_file() for candidate in path.parent.glob(target)):
            scan["missing_references"].append(
                {"unit_id": row["unit_id"], "kind": kind, "target": target}
            )


def inventory(references: Path, output: Path, batch_id: str) -> dict[str, Any]:
    references = references.resolve()
    old_path = output / "coverage.jsonl"
    old = (
        {
            row["unit_id"]: row
            for row in (
                json.loads(line) for line in old_path.read_text().splitlines() if line.strip()
            )
        }
        if old_path.exists()
        else {}
    )
    rows: list[dict[str, Any]] = []
    source_summary: list[dict[str, Any]] = []
    scan: dict[str, Any] = {
        "batch_id": batch_id,
        "parsed": Counter(),
        "manifest_count": 0,
        "parse_errors": [],
        "unresolved_manifests": [],
        "missing_references": [],
        "manifest_warnings": [],
        "limits": [
            "Syntax and local literal declarations only; no Odoo installation or runtime validation.",
            "External-addon asset paths, dynamic expressions and XML schema semantics require review.",
            "Every file is inventoried; automated scanning never marks content read.",
        ],
    }
    for source_id, relative in EXAMPLE_ROOTS.items():
        root = references / relative
        files = source_files(root)
        archive = references / (
            "Odoo-15-Development-Essentials-Examples.zip"
            if source_id == "B15-CODE"
            else "Odoo-17-Development-Essentials-Examples.zip"
            if source_id == "E17-CODE"
            else "absent.zip"
        )
        fingerprint = (
            digest(archive.read_bytes())
            if archive.exists()
            else digest(
                b"".join(
                    path.relative_to(root).as_posix().encode()
                    + b"\0"
                    + hashlib.sha256(path.read_bytes()).digest()
                    for path in files
                )
            )
        )
        hashes: set[str] = set()
        for path in files:
            locator = path.relative_to(root).as_posix()
            metadata = path.name in {"README.md", "LICENSE", ".gitignore"}
            row = unit(
                source_id,
                f"example:{locator}",
                locator,
                path.read_bytes(),
                fingerprint,
                path,
                batch_id,
                unit_type="example-file",
                kind="source metadata"
                if metadata
                else "context asset"
                if path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".svg"}
                else "code example",
            )
            hashes.add(row["content_sha256"])
            scan_file(path, root, row, scan)
            rows.append(row)
        source_summary.append(
            {
                "source_id": source_id,
                "root": relative,
                "files": len(files),
                "distinct_contents": len(hashes),
                "revision": fingerprint,
                "available": root.is_dir(),
            }
        )
    for source_id, relative in BOOK_ROOTS.items():
        for epub in sorted((references / relative).glob("*.epub")):
            revision = digest(epub.read_bytes())
            docs = sections_count = artifacts = 0
            with ZipFile(epub) as archive:
                for member in sorted(name for name in archive.namelist() if not name.endswith("/")):
                    data = archive.read(member)
                    if Path(member).suffix.lower() not in {".html", ".xhtml", ".htm"}:
                        artifacts += 1
                        rows.append(
                            unit(
                                source_id,
                                f"artifact:{member}",
                                member,
                                data,
                                revision,
                                epub,
                                batch_id,
                                kind="context asset",
                                unit_type="epub-artifact",
                            )
                        )
                        continue
                    docs += 1
                    parent_id = f"{source_id}:epub:{member}"
                    rows.append(
                        unit(
                            source_id,
                            f"epub:{member}",
                            member,
                            data,
                            revision,
                            epub,
                            batch_id,
                            kind="book prose",
                            unit_type="epub-document",
                        )
                    )
                    for section in epub_sections(data):
                        locator = member + "#" + section["id"]
                        rows.append(
                            unit(
                                source_id,
                                f"section:{locator}",
                                locator,
                                section["content"].encode(),
                                revision,
                                epub,
                                batch_id,
                                kind="book prose",
                                unit_type="epub-section",
                                title=section["title"],
                                parent_unit_id=parent_id,
                            )
                        )
                        sections_count += 1
            source_summary.append(
                {
                    "source_id": source_id,
                    "epub": str(epub.relative_to(references)),
                    "revision": revision,
                    "documents": docs,
                    "sections": sections_count,
                    "other_epub_artifacts": artifacts,
                }
            )
    cybrosys = references / "cybrosys"
    manifest = read_json(cybrosys / "manifest.json", [])
    urls: dict[str, list[str]] = {}
    for entry in manifest:
        if entry.get("file"):
            urls.setdefault(entry["file"], []).append(entry["url"])
    pages_by_path: dict[Path, str] = {}
    for collection, source_id in CYBROSYS_IDS.items():
        pages = sorted((cybrosys / collection).rglob("*.txt"))
        for path in pages:
            locator = path.relative_to(cybrosys / collection).as_posix()
            data = path.read_bytes()
            row = unit(
                source_id,
                f"page:{locator}",
                locator,
                data,
                digest(data),
                path,
                batch_id,
                kind="book prose",
                unit_type="saved-page",
                urls=urls.get(path.relative_to(cybrosys).as_posix(), []),
            )
            html = path.with_suffix(".html")
            if html.is_file():
                row["html_artifact"] = {
                    "path": str(html.resolve()),
                    "sha256": digest(html.read_bytes()),
                }
            rows.append(row)
            pages_by_path[path.resolve()] = row["unit_id"]
        source_summary.append({"source_id": source_id, "saved_pages": len(pages)})
    failures = read_json(output / "failed-urls.json", [])

    def recovered_path(entry: dict[str, Any]) -> Path | None:
        value = entry.get("recovered_file")
        if not value:
            return None
        candidate = Path(value)
        choices = (
            [candidate]
            if candidate.is_absolute()
            else [cybrosys / candidate, references / candidate, candidate]
        )
        return next((path.resolve() for path in choices if path.is_file()), None)

    # Resolve owners before aliases, independent of acquisition-record order.
    recovery_owners = {
        path: entry
        for entry in failures
        if entry.get("status") == "recovered" and (path := recovered_path(entry)) is not None
    }
    for failure in failures:
        present = recovered_path(failure)
        if present and present not in pages_by_path:
            recovered_data = present.read_bytes()
            owner = recovery_owners.get(present, failure)
            # Recovered pages live outside the four original collection folders.
            # Their source ID is supplied by the original acquisition record.
            recovered_locator = (
                present.relative_to(cybrosys).as_posix()
                if present.is_relative_to(cybrosys)
                else f"recovered/{owner['gap_id']}/{present.name}"
            )
            recovered_row = unit(
                owner["source_id"],
                f"page:{recovered_locator}",
                recovered_locator,
                recovered_data,
                digest(recovered_data),
                present,
                batch_id,
                kind="book prose",
                unit_type="saved-page",
                recovered_from=owner["gap_id"],
                urls=[owner.get("replacement_url") or owner["url"]],
            )
            html = present.with_suffix(".html")
            if html.is_file():
                recovered_row["html_artifact"] = {
                    "path": str(html),
                    "sha256": digest(html.read_bytes()),
                }
            rows.append(recovered_row)
            pages_by_path[present] = recovered_row["unit_id"]
        row = unit(
            failure["source_id"],
            f"acquisition:{failure['gap_id']}",
            failure["url"],
            failure["url"].encode(),
            "acquisition-register",
            cybrosys / "manifest.json",
            batch_id,
            kind="acquisition gap",
            unit_type="acquisition-entry",
            inventory=("present" if failure.get("status") == "resolved-alias" else "recovered")
            if present
            else "missing",
            recovery_status=failure.get("status"),
            original_error=failure.get("original_error"),
            gap_id=failure["gap_id"],
        )
        if present:
            row["recovered_path"] = str(present)
            row["recovered_unit_id"] = pages_by_path.get(present)
            row["recovered_sha256"] = digest(present.read_bytes())
        rows.append(row)
    for entry in source_summary:
        if entry["source_id"] in CYBROSYS_IDS.values():
            entry["recovered_pages"] = sum(
                row["source_id"] == entry["source_id"] and bool(row.get("recovered_from"))
                for row in rows
            )
    seen: dict[tuple[str, str, str], str] = {}
    merged: list[dict[str, Any]] = []
    for row in rows:
        key = (row["source_id"], row["unit_type"], row["content_sha256"])
        row["duplicate_of"] = seen.get(key)
        seen.setdefault(key, row["unit_id"])
        merged.append(merge_review_state(row, old.get(row["unit_id"])))
    ids = {row["unit_id"] for row in merged}
    for identity, previous in old.items():
        if identity not in ids:
            removed = {
                **previous,
                "inventory": "missing",
                "reading": "pending",
                "official_verification": "unresolved",
                "execution": "not-run",
                "lesson_ids": [],
                "batch_id": batch_id,
            }
            merged.append(merge_review_state(removed, previous))
    merged.sort(key=lambda row: row["unit_id"])
    by_id = {row["unit_id"]: row for row in merged}
    scan["issue_groups"] = {}
    for category in ("parse_errors", "unresolved_manifests", "missing_references"):
        grouped: dict[str, dict[str, Any]] = {}
        for issue in scan[category]:
            detail = {key: value for key, value in issue.items() if key != "unit_id"}
            detail["content_sha256"] = by_id[issue["unit_id"]]["content_sha256"]
            identity = json.dumps(detail, sort_keys=True)
            group = grouped.setdefault(identity, {**detail, "unit_ids": [], "count": 0})
            group["unit_ids"].append(issue["unit_id"])
            group["count"] += 1
        scan["issue_groups"][category] = list(grouped.values())
    counts = Counter(row.get("unit_type", "legacy") for row in merged)
    summary = {
        "batch_id": batch_id,
        "references": str(references),
        "sources": source_summary,
        "unit_counts_by_type": dict(counts),
        "reading_counts": dict(Counter(row["reading"] for row in merged)),
        "acquisition_counts": dict(
            Counter(
                row["inventory"] for row in merged if row.get("unit_type") == "acquisition-entry"
            )
        ),
        "acquisition_status_counts": dict(
            Counter(entry.get("status", "unknown") for entry in failures)
        ),
        "limits": "Document, section, file and acquisition totals are separate denominators; automated inventory is not reading.",
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / "coverage.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in merged)
    )
    (output / "source-inventory-summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    (output / "static-scan.json").write_text(json.dumps(scan, indent=2) + "\n")
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--references", type=Path, default=Path("../references/odoo-books"))
    parser.add_argument("--output", type=Path, default=Path("docs/source-learning"))
    parser.add_argument("--batch-id", default="LEARN-2026-11-03-04")
    args = parser.parse_args()
    if not args.references.is_dir():
        parser.error(f"source directory does not exist: {args.references}")
    print(json.dumps(inventory(args.references, args.output, args.batch_id), indent=2))


if __name__ == "__main__":
    main()
