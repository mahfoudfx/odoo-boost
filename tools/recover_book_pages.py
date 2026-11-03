"""Retry registered Cybrosys gaps, retaining original errors and fetched evidence.

Run from the repository root. This maintainer tool is outside the runtime package.
Recovered means usable text was acquired, not that its technical claims were read.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
from html.parser import HTMLParser
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen


class BookBody(HTMLParser):
    """Extract the publisher's book-body; omit scripts, styles and navigation."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.stack: list[tuple[str, bool, bool]] = []
        self.parts: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        parent = self.stack[-1] if self.stack else ("", False, False)
        active = (
            parent[1]
            or "book-body" in (attributes.get("class") or "").split()
            or attributes.get("id") == "book-body"
        )
        hidden = parent[2] or tag in {"script", "style", "nav"}
        if tag not in {
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        }:
            self.stack.append((tag, active, hidden))
        if active and tag in {"p", "div", "li", "br", "h1", "h2", "h3", "h4", "pre"}:
            self.parts.append("\n")

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                if self.stack[index][1] and tag in {
                    "p",
                    "div",
                    "li",
                    "h1",
                    "h2",
                    "h3",
                    "h4",
                    "pre",
                    "table",
                    "tr",
                }:
                    self.parts.append("\n")
                del self.stack[index:]
                break

    def handle_data(self, data: str) -> None:
        if self.stack and self.stack[-1][1] and not self.stack[-1][2]:
            self.parts.append(data)

    def text(self) -> str:
        return (
            "\n".join(
                line
                for part in "".join(self.parts).splitlines()
                if (line := " ".join(part.split()))
            )
            + "\n"
        )


def fetch(url: str) -> tuple[bytes, str]:
    request = Request(url, headers={"User-Agent": "OdooBoost-source-review/1.0"})
    with urlopen(request, timeout=25) as response:
        return response.read(8_000_001), response.geturl()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--references", type=Path, default=Path("../references/odoo-books"))
    parser.add_argument(
        "--register", type=Path, default=Path("docs/source-learning/failed-urls.json")
    )
    parser.add_argument("--workers", type=int, default=3)
    parser.add_argument("--gap-id", action="append", help="Retry only this gap (repeatable)")
    parser.add_argument(
        "--candidate-map",
        type=Path,
        help="Reviewed publisher-navigation replacements keyed by gap ID",
    )
    parser.add_argument("--cached", action="store_true", help="Re-extract previously fetched HTML")
    args = parser.parse_args()
    rows = json.loads(args.register.read_text())
    candidates = json.loads(args.candidate_map.read_text()) if args.candidate_map else {}
    destination = args.references / "cybrosys" / "recovered"
    destination.mkdir(parents=True, exist_ok=True)

    def recover(row: dict) -> dict:
        row = dict(row)
        url = candidates.get(row["gap_id"], row["url"])
        attempt: dict = {"date": datetime.now(timezone.utc).isoformat(), "url": url}
        try:
            if args.cached:
                cached = row.get("fetched_html") or str(
                    Path(
                        row.get("recovered_file", f"recovered/{row['gap_id'].lower()}.txt")
                    ).with_suffix(".html")
                )
                body = (args.references / "cybrosys" / cached).read_bytes()
                final_url = row["attempts"][-1].get("final_url", url)
                attempt["cached_html"] = True
            else:
                body, final_url = fetch(url)
            if len(body) > 8_000_000:
                raise ValueError("Response exceeds 8 MB evidence limit")
            stem = row["gap_id"].lower()
            html_path = destination / f"{stem}.html"
            html_path.write_bytes(body)
            row["fetched_html"] = str(html_path.relative_to(args.references / "cybrosys"))
            page = BookBody()
            page.feed(body.decode("utf-8", errors="replace"))
            content = page.text()
            attempt.update(http_status=200, final_url=final_url, extracted_chars=len(content))
            if "/404/" in urlparse(final_url).path.lower():
                attempt["result"] = "soft-404"
                row["status"] = "unresolved-http"
            elif len(content.strip()) < 100:
                attempt["result"] = "needs-content-inspection"
                row["status"] = "unresolved-extraction"
            else:
                text_path = destination / f"{stem}.txt"
                text_path.write_text(content)
                attempt["result"] = "usable-book-body-saved"
                row.update(
                    status="recovered",
                    recovered_file=str(text_path.relative_to(args.references / "cybrosys")),
                    replacement_url=(final_url if final_url != row["url"] else None),
                    content_sha256=hashlib.sha256(text_path.read_bytes()).hexdigest(),
                    html_sha256=hashlib.sha256(body).hexdigest(),
                )
        except HTTPError as error:
            attempt.update(result="http-error", http_status=error.code, detail=str(error))
            row["status"] = "unresolved-http"
        except (URLError, TimeoutError, OSError, ValueError) as error:
            attempt.update(result="fetch-error", detail=str(error))
            row["status"] = "unresolved-fetch"
        row.setdefault("attempts", []).append(attempt)
        row["retry_result"] = attempt["result"]
        return row

    # Keep normalized slash variants as individual evidence records.
    selected = [
        row
        for row in rows
        if (
            row["gap_id"] in args.gap_id
            if args.gap_id
            else row["status"] not in {"recovered", "resolved-alias"}
        )
    ]
    updates = {}
    with ThreadPoolExecutor(max_workers=max(1, min(args.workers, 4))) as pool:
        for row in pool.map(recover, selected):
            updates[row["gap_id"]] = row
            print(row["gap_id"], row["status"], flush=True)
    result = [updates.get(row["gap_id"], row) for row in rows]
    args.register.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
