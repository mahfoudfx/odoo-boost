"""Meaningful state/identity contracts for the maintainer inventory tool."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile


def load_inventory_module():
    path = Path(__file__).resolve().parents[1] / "tools" / "inventory_learning_sources.py"
    spec = importlib.util.spec_from_file_location("inventory_learning_sources", path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_preserves_review_and_invalidates_changed_content(tmp_path):
    module = load_inventory_module()
    references = tmp_path / "references"
    root = references / module.EXAMPLE_ROOTS["B15-CODE"]
    root.mkdir(parents=True)
    path = root / "model.py"
    path.write_text("value = 1\n")
    output = tmp_path / "output"
    module.inventory(references, output, "first")
    rows = [json.loads(line) for line in (output / "coverage.jsonl").read_text().splitlines()]
    original = rows[0]
    original.update(
        reading="read",
        official_verification="verified",
        execution="passed",
        lesson_ids=["L1"],
        revision="original-pinned-revision",
        review_events=[{"batch_id": "human-review", "scope": "model.py"}],
        content_reviews=[{"representative": "model.py"}],
    )
    (output / "coverage.jsonl").write_text(json.dumps(original) + "\n")
    module.inventory(references, output, "second")
    unchanged = json.loads((output / "coverage.jsonl").read_text())
    assert unchanged["reading"] == "read"
    assert unchanged["official_verification"] == "verified"
    assert unchanged["execution"] == "passed"
    assert unchanged["lesson_ids"] == ["L1"]
    assert unchanged["revision"] == "original-pinned-revision"
    assert unchanged["review_events"] == original["review_events"]
    path.write_text("value = 2\n")
    module.inventory(references, output, "third")
    changed = json.loads((output / "coverage.jsonl").read_text())
    assert changed["reading"] == "pending"
    assert changed["official_verification"] == "pending"
    assert changed["execution"] == "not-run"
    assert changed["lesson_ids"] == []
    assert changed["history"][-1]["content_sha256"] == original["content_sha256"]
    assert changed["history"][-1]["reading"] == "read"
    assert changed["history"][-1]["review_events"] == original["review_events"]
    assert changed["history"][-1]["content_reviews"] == original["content_reviews"]


def test_epub_sections_have_stable_separate_denominators(tmp_path):
    module = load_inventory_module()
    references = tmp_path / "references"
    book = references / module.BOOK_ROOTS["B15"]
    book.mkdir(parents=True)
    with ZipFile(book / "book.epub", "w") as archive:
        archive.writestr(
            "chapter.xhtml", '<h1 id="intro">Intro</h1><p>One</p><h2>Detail</h2><p>Two</p>'
        )
        archive.writestr("cover.png", b"image")
    output = tmp_path / "output"
    first = module.inventory(references, output, "first")
    before = (output / "coverage.jsonl").read_text()
    module.inventory(references, output, "later")
    assert (output / "coverage.jsonl").read_text() == before
    assert first["unit_counts_by_type"] == {
        "epub-artifact": 1,
        "epub-document": 1,
        "epub-section": 2,
    }
    rows = [json.loads(line) for line in before.splitlines()]
    sections = [row for row in rows if row["unit_type"] == "epub-section"]
    assert [row["locator"] for row in sections] == ["chapter.xhtml#h-2", "chapter.xhtml#intro"]
    assert all(row["reading"] == "pending" for row in rows)
    assert (
        next(row for row in rows if row["unit_type"] == "epub-artifact")["locator"] == "cover.png"
    )
    assert (
        next(s for s in first["sources"] if s.get("source_id") == "B15")["other_epub_artifacts"]
        == 1
    )


def test_static_scan_records_duplicates_without_executing_and_missing_inputs(tmp_path):
    module = load_inventory_module()
    references = tmp_path / "references"
    root = references / module.EXAMPLE_ROOTS["B17-CODE"]
    for chapter in ("Chapter01", "Chapter02"):
        addon = root / chapter / "demo"
        addon.mkdir(parents=True)
        (addon / "__manifest__.py").write_text("{'data': ['missing.xml']}")
        (addon / "bad.py").write_text("invalid =\n")
        (addon / "good.py").write_text("raise RuntimeError('must not execute')\n")
    output = tmp_path / "output"
    summary = module.inventory(references, output, "test")
    scan = json.loads((output / "static-scan.json").read_text())
    assert len(scan["parse_errors"]) == 2
    assert len(scan["missing_references"]) == 2
    assert scan["manifest_count"] == 2
    assert summary["reading_counts"] == {"pending": 6}
    rows = [json.loads(line) for line in (output / "coverage.jsonl").read_text().splitlines()]
    assert sum(row["duplicate_of"] is not None for row in rows) == 3
    (root / "Chapter01" / "demo" / "good.py").unlink()
    module.inventory(references, output, "removed")
    rows = [json.loads(line) for line in (output / "coverage.jsonl").read_text().splitlines()]
    missing = [row for row in rows if row["inventory"] == "missing"]
    assert len(missing) == 1
    assert missing[0]["history"][-1]["inventory"] == "present"


def test_recovered_page_gets_its_own_reading_unit_and_acquisition_link(tmp_path):
    module = load_inventory_module()
    references = tmp_path / "references"
    recovered = references / "cybrosys" / "recovered" / "chapter.txt"
    recovered.parent.mkdir(parents=True)
    recovered.write_text("Recovered book chapter")
    output = tmp_path / "output"
    output.mkdir()
    (output / "failed-urls.json").write_text(
        json.dumps(
            [
                {
                    "gap_id": "CY-FAIL-001",
                    "source_id": "CY18-ENT",
                    "url": "https://example.test/chapter",
                    "status": "recovered",
                    "recovered_file": "recovered/chapter.txt",
                    "original_error": "Missing container",
                }
            ]
        )
    )
    summary = module.inventory(references, output, "recovery")
    rows = [json.loads(line) for line in (output / "coverage.jsonl").read_text().splitlines()]
    acquisition = next(row for row in rows if row["unit_type"] == "acquisition-entry")
    page = next(row for row in rows if row["unit_type"] == "saved-page")
    assert acquisition["inventory"] == "recovered"
    assert acquisition["recovered_unit_id"] == page["unit_id"]
    assert page["reading"] == "pending"
    assert summary["unit_counts_by_type"] == {"saved-page": 1, "acquisition-entry": 1}


def test_aliases_resolve_canonical_content_and_owner_independent_of_order(tmp_path):
    module = load_inventory_module()
    references = tmp_path / "references"
    cybrosys = references / "cybrosys"
    canonical = cybrosys / "development" / "existing.txt"
    canonical.parent.mkdir(parents=True)
    canonical.write_text("Existing content")
    recovered = cybrosys / "recovered" / "chapter.txt"
    recovered.parent.mkdir()
    recovered.write_text("New recovered content")
    output = tmp_path / "output"
    output.mkdir()
    entries = [
        {
            "gap_id": "ALIAS-ORIGINAL",
            "source_id": "CY18-DEV",
            "url": "https://example.test/old",
            "status": "resolved-alias",
            "recovered_file": "development/existing.txt",
        },
        {
            "gap_id": "ALIAS-RECOVERED",
            "source_id": "CY18-DEV",
            "url": "https://example.test/alias",
            "status": "resolved-alias",
            "recovered_file": "recovered/chapter.txt",
        },
        {
            "gap_id": "RECOVERED-OWNER",
            "source_id": "CY18-ENT",
            "url": "https://example.test/owner",
            "status": "recovered",
            "recovered_file": "recovered/chapter.txt",
        },
    ]
    (output / "failed-urls.json").write_text(json.dumps(entries))
    summary = module.inventory(references, output, "test")
    rows = [json.loads(line) for line in (output / "coverage.jsonl").read_text().splitlines()]
    acquisitions = {row["gap_id"]: row for row in rows if row["unit_type"] == "acquisition-entry"}
    pages = [row for row in rows if row["unit_type"] == "saved-page"]
    assert len(pages) == 2
    assert acquisitions["ALIAS-ORIGINAL"]["recovered_unit_id"] == "CY18-DEV:page:existing.txt"
    assert (
        acquisitions["ALIAS-RECOVERED"]["recovered_unit_id"]
        == acquisitions["RECOVERED-OWNER"]["recovered_unit_id"]
    )
    assert next(row for row in pages if row.get("recovered_from"))["source_id"] == "CY18-ENT"
    assert summary["acquisition_counts"] == {"present": 2, "recovered": 1}


def test_section_hash_detects_markup_change_without_changing_identity():
    module = load_inventory_module()
    first = module.epub_sections(b'<h1 id="topic">Title</h1><a href="one">Link</a>')[0]
    second = module.epub_sections(b'<h1 id="topic">Title</h1><a href="two">Link</a>')[0]
    assert first["id"] == second["id"] == "topic"
    assert first["text"] == second["text"]
    assert module.digest(first["content"].encode()) != module.digest(second["content"].encode())
