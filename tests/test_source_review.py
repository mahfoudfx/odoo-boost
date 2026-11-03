"""Contracts preventing the review merger from overstating source coverage."""

from __future__ import annotations

import hashlib
import importlib.util
import json
from pathlib import Path
from zipfile import ZipFile

import pytest


def load_tool(name="record_source_review"):
    path = Path(__file__).resolve().parents[1] / "tools" / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def save_rows(path, rows):
    path.write_text("".join(json.dumps(row) + "\n" for row in rows))


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def file_unit(path, identity="F", reading="pending"):
    return {
        "unit_id": identity,
        "source_path": str(path),
        "locator": path.name,
        "content_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "unit_type": "example-file",
        "reading": reading,
        "execution": "not-run",
        "official_verification": "pending",
        "lesson_ids": [],
        "duplicate_context_reviewed": False,
    }


def prepare(tmp_path, rows, evidence, lessons=None):
    output = tmp_path / "ledger"
    output.mkdir(exist_ok=True)
    save_rows(output / "coverage.jsonl", rows)
    save_rows(output / "lessons.jsonl", lessons or [])
    path = tmp_path / "evidence.json"
    path.write_text(json.dumps(evidence))
    return output, path


def test_exact_read_and_lesson_are_idempotent_without_runtime_promotion(tmp_path):
    source = tmp_path / "model.py"
    source.write_text("value = 1\n")
    evidence = {
        "fully_read_files": [str(source)],
        "lessons": [
            {
                "lesson_id": "L1",
                "input_locators": [str(source)],
                "origin": "code example",
                "decision": "Review batch semantics",
                "official_evidence": [{"result": "verified"}],
            }
        ],
    }
    output, path = prepare(tmp_path, [file_unit(source)], evidence)
    tool = load_tool()
    first = tool.record_reviews([path], output, "batch")
    snapshots = [(output / name).read_bytes() for name in ["coverage.jsonl", "lessons.jsonl"]]
    second = tool.record_reviews([path], output, "batch")
    assert first["added_lessons"] == 1 and second["added_lessons"] == 0
    assert second["updated_units"] == 0
    assert snapshots == [
        (output / name).read_bytes() for name in ["coverage.jsonl", "lessons.jsonl"]
    ]
    row = read_rows(output / "coverage.jsonl")[0]
    assert row["reading"] == "read" and row["disposition"] == "context-reviewed"
    assert row["official_verification"] == "qualified"
    assert row["execution"] == "not-run"
    assert read_rows(output / "lessons.jsonl")[0]["unit_ids"] == ["F"]


def test_changed_source_refuses_all_ledger_writes(tmp_path):
    source = tmp_path / "model.py"
    source.write_text("value = 1\n")
    row = file_unit(source)
    output, path = prepare(tmp_path, [row], {"fully_read_files": [str(source)]})
    snapshots = [(output / name).read_bytes() for name in ["coverage.jsonl", "lessons.jsonl"]]
    source.write_text("value = 2\n")
    with pytest.raises(ValueError, match="Content changed"):
        load_tool().record_reviews([path], output, "batch")
    assert snapshots == [
        (output / name).read_bytes() for name in ["coverage.jsonl", "lessons.jsonl"]
    ]


def test_partial_section_boundaries_and_prior_reading_survive(tmp_path):
    inventory = load_tool("inventory_learning_sources")
    archive = tmp_path / "book.epub"
    content = b'<html><h2 id="one">First topic</h2><p>A</p><h2 id="two">Other topic</h2><p>B</p><h2 id="three">Unread</h2></html>'
    with ZipFile(archive, "w") as zipfile:
        zipfile.writestr("chapter.xhtml", content)
    parent = file_unit(archive, "DOC")
    parent.update(
        unit_type="epub-document",
        locator="chapter.xhtml",
        content_sha256=hashlib.sha256(content).hexdigest(),
    )
    rows = [parent]
    for part in inventory.epub_sections(content):
        row = {
            **parent,
            "unit_id": part["id"],
            "unit_type": "epub-section",
            "locator": "chapter.xhtml#" + part["id"],
            "title": part["title"],
            "content_sha256": hashlib.sha256(part["content"].encode()).hexdigest(),
        }
        rows.append(row)
    already_read = tmp_path / "read.txt"
    already_read.write_text("Full text\n")
    rows.append(file_unit(already_read, "READ", "read"))
    first = str(archive) + "!chapter.xhtml#one"
    title = str(archive) + "::chapter.xhtml#Other topic; Missing topic"
    output, path = prepare(
        tmp_path,
        rows,
        {
            "partial_files": [first, title, str(already_read) + "#lines-1-1"],
            "lessons": [{"lesson_id": "L", "input_locators": [first]}],
        },
    )
    load_tool().record_reviews([path], output, "batch")
    result = {r["unit_id"]: r for r in read_rows(output / "coverage.jsonl")}
    assert [result[k]["reading"] for k in ["DOC", "one", "two", "three", "READ"]] == [
        "partial",
        "partial",
        "partial",
        "pending",
        "read",
    ]
    assert read_rows(output / "lessons.jsonl")[0]["unit_ids"] == ["DOC", "one"]
    assert result["one"]["review_events"][0]["scope"] == first
    assert not result["three"].get("review_events")


def test_identical_contents_do_not_complete_duplicate_context(tmp_path):
    representative = tmp_path / "first.py"
    repeated = tmp_path / "second.py"
    representative.write_text("value = 1\n")
    repeated.write_bytes(representative.read_bytes())
    rows = [file_unit(representative, "FIRST"), file_unit(repeated, "SECOND")]
    mapping = {
        "path": str(repeated),
        "representative": str(representative),
        "content_sha256": rows[1]["content_sha256"],
        "reading": "pending",
        "duplicate_context_reviewed": False,
    }
    output, path = prepare(
        tmp_path,
        rows,
        {
            "fully_read_files": [str(representative)],
            "content_review_map": [mapping],
        },
    )
    load_tool().record_reviews([path], output, "batch")
    first, second = read_rows(output / "coverage.jsonl")
    assert first["reading"] == "read"
    assert second["reading"] == "pending" and second["duplicate_context_reviewed"] is False
    assert second["content_reviews"][0]["representative"] == str(representative)


def test_conflicting_lesson_payload_fails_before_writing(tmp_path):
    source = tmp_path / "source.py"
    source.write_text("value = 1\n")
    old = {
        "lesson_id": "L1",
        "unit_ids": ["F"],
        "input_locators": [str(source)],
        "decision": "Original lesson",
        "batch_id": "old",
    }
    output, path = prepare(
        tmp_path,
        [file_unit(source)],
        {
            "fully_read_files": [str(source)],
            "lessons": [{**old, "decision": "Different interpretation"}],
        },
        [old],
    )
    before = (output / "coverage.jsonl").read_bytes(), (output / "lessons.jsonl").read_bytes()
    with pytest.raises(ValueError, match="Conflicting payload"):
        load_tool().record_reviews([path], output, "new")
    assert before == (
        (output / "coverage.jsonl").read_bytes(),
        (output / "lessons.jsonl").read_bytes(),
    )


def test_independent_runtime_evidence_preserves_original_execution_and_history(tmp_path):
    source = tmp_path / "book_example.py"
    source.write_text("value = 1\n")
    old = {"lesson_id": "EARLIER", "unit_ids": ["F"], "decision": "Prior retained lesson"}
    row = file_unit(source, reading="read")
    row.update(official_verification="verified", history=[{"reading": "partial"}])
    external = str(tmp_path / "independent_fixture.py")
    output, path = prepare(
        tmp_path,
        [row],
        {
            "partial_files": [str(source)],
            "lessons": [
                {
                    "lesson_id": "RUNTIME",
                    "origin": "official-only",
                    "input_locators": [external],
                    "official_evidence": [{"series": "18.0", "result": "runtime-verified"}],
                }
            ],
        },
        [old],
    )
    summary = load_tool().record_reviews([path], output, "runtime")
    changed = read_rows(output / "coverage.jsonl")[0]
    assert changed["reading"] == "read" and changed["execution"] == "not-run"
    assert changed["history"] == row["history"]
    assert changed["official_verification"] == "verified"
    lessons = read_rows(output / "lessons.jsonl")
    assert lessons[0] == old
    assert lessons[1]["unit_ids"] == [] and lessons[1]["external_inputs"] == [external]
    assert summary["unmapped_inputs"] == [external]
