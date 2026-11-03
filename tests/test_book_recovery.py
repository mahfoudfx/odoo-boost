"""Acquisition correctness: selector variants and false-success HTTP responses."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path


def load_recovery_module():
    path = Path(__file__).resolve().parents[1] / "tools" / "recover_book_pages.py"
    spec = importlib.util.spec_from_file_location("recover_book_pages", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_extracts_class_and_id_without_navigation_or_scripts():
    module = load_recovery_module()
    for selector in ['class="main book-body"', 'id="book-body" class="main"']:
        parser = module.BookBody()
        parser.feed(
            "<nav>Outside menu</nav><div " + selector + "><h2>Chapter</h2>"
            '<p>Useful &amp; exact <b>content</b>.</p><img src="x.png">'
            "<script>secret noise</script><nav>Inner menu</nav>"
            "<p>Second paragraph.</p></div><footer>Footer</footer>"
        )
        assert parser.text() == "Chapter\nUseful & exact content.\nSecond paragraph.\n"


def test_recovery_rejects_soft404_and_preserves_original_error(tmp_path, monkeypatch):
    module = load_recovery_module()
    register = tmp_path / "failures.json"
    register.write_text(
        json.dumps(
            [
                {
                    "gap_id": "CY-FAIL-001",
                    "url": "https://example.test/chapter/",
                    "original_error": "Missing chapter content",
                    "status": "pending-recovery",
                }
            ]
        )
    )
    monkeypatch.setattr(
        module,
        "fetch",
        lambda url: (
            b'<div class="book-body">' + b"Error page body. " * 20 + b"</div>",
            "https://example.test/404/Default.aspx",
        ),
    )
    monkeypatch.setattr(
        "sys.argv", ["recover", "--references", str(tmp_path), "--register", str(register)]
    )
    module.main()
    row = json.loads(register.read_text())[0]
    assert row["original_error"] == "Missing chapter content"
    assert row["status"] == "unresolved-http"
    assert row["attempts"][-1]["result"] == "soft-404"
    assert row["attempts"][-1]["http_status"] == 200
    assert "recovered_file" not in row
    assert (tmp_path / "cybrosys" / row["fetched_html"]).is_file()


def test_recovery_saves_evidence_and_default_retry_keeps_resolved_rows(tmp_path, monkeypatch):
    module = load_recovery_module()
    register = tmp_path / "failures.json"
    register.write_text(
        json.dumps(
            [
                {
                    "gap_id": "CY-FAIL-001",
                    "url": "https://example.test/chapter/",
                    "original_error": "Missing chapter content",
                    "status": "pending-recovery",
                },
                {
                    "gap_id": "CY-FAIL-002",
                    "url": "https://example.test/old/",
                    "original_error": "404",
                    "status": "resolved-alias",
                    "attempts": [],
                },
            ]
        )
    )
    calls = []

    def fetch(url):
        calls.append(url)
        return b'<div id="book-body">' + b"Useful chapter content. " * 10 + b"</div>", url

    monkeypatch.setattr(module, "fetch", fetch)
    monkeypatch.setattr(
        "sys.argv", ["recover", "--references", str(tmp_path), "--register", str(register)]
    )
    module.main()
    module.main()
    rows = json.loads(register.read_text())
    assert calls == ["https://example.test/chapter/"]
    assert rows[0]["status"] == "recovered"
    assert (tmp_path / "cybrosys" / rows[0]["recovered_file"]).read_text().startswith("Useful")
    assert rows[1]["status"] == "resolved-alias"
    assert rows[1]["attempts"] == []

    # Earlier recovered rows predate the explicit fetched_html metadata field.
    del rows[0]["fetched_html"]
    register.write_text(json.dumps(rows))
    monkeypatch.setattr(
        "sys.argv",
        [
            "recover",
            "--references",
            str(tmp_path),
            "--register",
            str(register),
            "--cached",
            "--gap-id",
            "CY-FAIL-001",
        ],
    )
    module.main()
    refreshed = json.loads(register.read_text())[0]
    assert refreshed["status"] == "recovered"
    assert refreshed["attempts"][-1]["cached_html"] is True
    assert calls == ["https://example.test/chapter/"]
