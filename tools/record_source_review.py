#!/usr/bin/env python3
"""Merge explicit reading/lesson evidence into the maintainer source ledger.

Run the inventory tool first. This merger refuses stale content, preserves prior
reading depth and execution state, and does not turn byte duplicates into reviews.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib.util
import json
import os
import tempfile
from collections import defaultdict
from pathlib import Path
from typing import Any
from zipfile import ZipFile


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_rows(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def append_unique(row: dict[str, Any], field: str, value: Any) -> None:
    values = row.setdefault(field, [])
    if value not in values:
        values.append(value)


def normalize_title(value: str) -> str:
    return " ".join(value.split()).casefold()


class SourceIndex:
    """Resolve precise source locators without treating a section as a chapter."""

    def __init__(self, rows: list[dict[str, Any]]) -> None:
        self.rows = rows
        self.by_path: dict[str, list[dict[str, Any]]] = defaultdict(list)
        self.by_id = {row["unit_id"]: row for row in rows}
        self.checked: set[str] = set()
        self.members: dict[tuple[str, str], bytes] = {}
        self.sections: dict[tuple[str, str], dict[str, bytes]] = {}
        for row in rows:
            if row.get("source_path") and row.get("unit_type") != "acquisition-entry":
                self.by_path[str(Path(row["source_path"]).resolve())].append(row)

    def resolve(self, locator: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """Return explicit units and parent documents requiring only partial credit."""
        archive_path, separator, remainder = locator.partition("!")
        if not separator:
            archive_path, separator, remainder = locator.partition("::")
        if not separator:
            path = str(Path(locator.split("#", 1)[0]).resolve())
            rows = self.by_path.get(path, [])
            # Naming an EPUB archive does not establish reading any member.
            return [r for r in rows if not r.get("unit_type", "").startswith("epub-")], []
        rows = self.by_path.get(str(Path(archive_path).resolve()), [])
        member, anchor_mark, anchor = remainder.partition("#")
        parents = [
            r for r in rows if r.get("unit_type") == "epub-document" and r["locator"] == member
        ]
        if not anchor_mark:
            artifacts = [
                r for r in rows if r.get("unit_type") == "epub-artifact" and r["locator"] == member
            ]
            return parents + artifacts, []
        sections = [
            r
            for r in rows
            if r.get("unit_type") == "epub-section" and r["locator"].split("#", 1)[0] == member
        ]
        selected = []
        for value in anchor.split(";"):
            value = value.strip()
            matches = [r for r in sections if r["locator"].split("#", 1)[1] == value]
            if not matches:
                matches = [
                    r
                    for r in sections
                    if normalize_title(r.get("title", "")) == normalize_title(value)
                ]
            # Ambiguous repeated headings receive only document-level partial credit.
            if len(matches) == 1 and matches[0] not in selected:
                selected.append(matches[0])
        return selected, parents

    def validate(self, row: dict[str, Any]) -> None:
        identity = row["unit_id"]
        if identity in self.checked:
            return
        path = Path(row["source_path"])
        kind = row.get("unit_type", "")
        if kind.startswith("epub-"):
            member = row["locator"].split("#", 1)[0]
            key = (str(path), member)
            if key not in self.members:
                with ZipFile(path) as archive:
                    self.members[key] = archive.read(member)
            data = self.members[key]
            if kind == "epub-section":
                if key not in self.sections:
                    spec = importlib.util.spec_from_file_location(
                        "learning_inventory",
                        Path(__file__).with_name("inventory_learning_sources.py"),
                    )
                    if spec is None or spec.loader is None:
                        raise ValueError("Cannot load the inventory section parser")
                    module = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(module)
                    self.sections[key] = {
                        section["id"]: section["content"].encode()
                        for section in module.epub_sections(data)
                    }
                section_id = row["locator"].split("#", 1)[1]
                if section_id not in self.sections[key]:
                    raise ValueError(f"Missing inventoried section: {identity}; rerun inventory")
                data = self.sections[key][section_id]
        else:
            data = path.read_bytes()
        if digest(data) != row["content_sha256"]:
            raise ValueError(f"Content changed since inventory: {identity}; rerun inventory")
        self.checked.add(identity)


def lesson_payload(row: dict[str, Any]) -> dict[str, Any]:
    return {k: v for k, v in row.items() if k not in {"batch_id", "review_events"}}


def atomic_rows(path: Path, rows: list[dict[str, Any]]) -> None:
    with tempfile.NamedTemporaryFile(
        mode="w", dir=path.parent, delete=False, encoding="utf-8"
    ) as file:
        for row in rows:
            file.write(json.dumps(row, ensure_ascii=False) + "\n")
        temporary = Path(file.name)
    try:
        os.replace(temporary, path)
    finally:
        temporary.unlink(missing_ok=True)


def record_reviews(evidence_paths: list[Path], output: Path, batch_id: str) -> dict[str, Any]:
    coverage_path, lessons_path = output / "coverage.jsonl", output / "lessons.jsonl"
    coverage = load_rows(coverage_path)
    lessons = load_rows(lessons_path) if lessons_path.exists() else []
    before = copy.deepcopy(coverage)
    index = SourceIndex(coverage)
    if len(index.by_id) != len(coverage):
        raise ValueError("Coverage has duplicate unit IDs")
    by_lesson = {row["lesson_id"]: row for row in lessons}
    if len(by_lesson) != len(lessons):
        raise ValueError("Ledger has duplicate lesson IDs")
    added = 0
    unmapped: set[str] = set()

    def apply_reading(row: dict[str, Any], depth: str, event: dict[str, Any]) -> None:
        index.validate(row)
        order = {"pending": 0, "partial": 1, "duplicate-reviewed": 2, "read": 3}
        if order.get(depth, 0) > order.get(row.get("reading", "pending"), 0):
            row["reading"] = depth
        if depth == "read" and not row.get("lesson_ids"):
            row.setdefault("disposition", "context-reviewed")
        append_unique(
            row, "review_events", {**event, "action": depth, "unit_sha256": row["content_sha256"]}
        )

    for evidence_path in evidence_paths:
        raw = evidence_path.read_bytes()
        evidence = json.loads(raw)
        event = {
            "batch_id": batch_id,
            "evidence_path": str(evidence_path.resolve()),
            "evidence_sha256": digest(raw),
        }
        for field, depth in (("fully_read_files", "read"), ("partial_files", "partial")):
            for locator in evidence.get(field, []):
                selected, parents = index.resolve(locator)
                if not selected and not parents:
                    unmapped.add(locator)
                for row in selected:
                    # A source range remains partial even in a full-file list.
                    bounded = "#" in locator or "::" in locator or "!" in locator
                    apply_reading(row, "partial" if bounded else depth, {**event, "scope": locator})
                for row in parents:
                    apply_reading(row, "partial", {**event, "scope": locator})
        for detail in evidence.get("partial_locators", []):
            if isinstance(detail, dict) and detail.get("file"):
                selected, parents = index.resolve(detail["file"])
                for row in selected + parents:
                    apply_reading(row, "partial", {**event, "scope": detail})
        for detail in evidence.get("content_review_map", []):
            selected, _ = index.resolve(detail["path"])
            representatives, _ = index.resolve(detail["representative"])
            if not selected or not representatives:
                unmapped.add(detail["path"])
                continue
            for row in selected + representatives:
                index.validate(row)
                if row["content_sha256"] != detail["content_sha256"]:
                    raise ValueError(f"Content evidence hash mismatch: {detail['path']}")
            for row in selected:
                # Content identity is evidence only; context review needs an explicit assertion.
                content_event = {**event, **detail}
                append_unique(row, "content_reviews", content_event)
                if detail.get("duplicate_context_reviewed") is True:
                    row["duplicate_context_reviewed"] = True
                    apply_reading(row, "duplicate-reviewed", {**event, "scope": detail["path"]})
        for incoming in evidence.get("lessons", []):
            lesson = copy.deepcopy(incoming)
            lesson.setdefault("input_locators", [])
            unit_ids: set[str] = set(lesson.get("unit_ids", []))
            external: list[str] = []
            for locator in lesson["input_locators"]:
                selected, parents = index.resolve(locator)
                if not selected and not parents:
                    external.append(locator)
                    unmapped.add(locator)
                for row in selected + parents:
                    index.validate(row)
                    unit_ids.add(row["unit_id"])
            if unit_ids - index.by_id.keys():
                raise ValueError(f"Unknown unit IDs in {lesson['lesson_id']}")
            lesson["unit_ids"] = sorted(unit_ids)
            if external:
                lesson["external_inputs"] = external
            lesson["batch_id"] = batch_id
            lesson_id = lesson["lesson_id"]
            existing = by_lesson.get(lesson_id)
            if existing is not None:
                if lesson_payload(existing) != lesson_payload(lesson):
                    raise ValueError(
                        f"Conflicting payload for lesson {lesson_id}; use a correction ID"
                    )
                lesson = existing
            else:
                lessons.append(lesson)
                by_lesson[lesson_id] = lesson
                added += 1
            append_unique(lesson, "review_events", event)
            for identity in lesson["unit_ids"]:
                row = index.by_id[identity]
                index.validate(row)
                append_unique(row, "lesson_ids", lesson_id)
                if row.get("official_verification", "pending") in {"pending", "unresolved"}:
                    row["official_verification"] = "qualified"
                append_unique(
                    row,
                    "review_events",
                    {**event, "action": "lesson-linked", "lesson_id": lesson_id},
                )
    # All input validation/conflict detection happens before replacing either ledger.
    atomic_rows(lessons_path, lessons)
    atomic_rows(coverage_path, coverage)
    return {
        "coverage_units": len(coverage),
        "lessons": len(lessons),
        "added_lessons": added,
        "updated_units": sum(a != b for a, b in zip(before, coverage, strict=True)),
        "read_units": sum(r.get("reading") == "read" for r in coverage),
        "partial_units": sum(r.get("reading") == "partial" for r in coverage),
        "unmapped_inputs": sorted(unmapped),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--evidence", type=Path, action="append", required=True)
    parser.add_argument("--output", type=Path, default=Path("docs/source-learning"))
    parser.add_argument("--batch-id", required=True)
    args = parser.parse_args()
    print(json.dumps(record_reviews(args.evidence, args.output, args.batch_id), indent=2))


if __name__ == "__main__":
    main()
