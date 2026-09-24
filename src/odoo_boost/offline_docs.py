"""Versioned local Odoo documentation packs and bounded offline search."""

from __future__ import annotations

import hashlib
import importlib.resources
import json
import os
import re
import shutil
import sqlite3
import subprocess
import tempfile
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO
from zipfile import BadZipFile, ZipFile

from odoo_boost.versions import get_version_profile, normalize_version

DOC_REPO = "https://github.com/odoo/documentation.git"
SOURCE_URL = "https://github.com/odoo/documentation"
SECTIONS = frozenset({"administration", "applications", "developer"})
MAX_PACK_UNCOMPRESSED = 100_000_000
METADATA_FILE = ".odoo-boost-docs.json"
INDEX_FILE = "index.sqlite3"


class OfflineDocsError(ValueError):
    """An offline documentation source is missing, invalid, or unavailable."""


def documentation_series(version: str | None) -> str:
    series = normalize_version(version)
    if series is None or get_version_profile(series) is None:
        raise OfflineDocsError(f"Unsupported Odoo documentation version: {version or 'unknown'}")
    return series


def default_cache_dir() -> Path:
    base = os.environ.get("XDG_CACHE_HOME")
    return (Path(base).expanduser() if base else Path.home() / ".cache") / "odoo-boost" / "docs"


def _pack_directory() -> Any | None:
    try:
        return importlib.resources.files("odoo_boost_docs") / "packs"
    except ModuleNotFoundError:
        source = (
            Path(__file__).resolve().parents[2]
            / "packages/odoo-boost-docs/src/odoo_boost_docs/packs"
        )
        return source if source.is_dir() else None


def available_packs() -> list[str]:
    directory = _pack_directory()
    if directory is None or not directory.is_dir():
        return []
    return sorted(p.name[:-4] for p in directory.iterdir() if p.name.endswith(".zip"))


def _pack_for(series: str) -> Any:
    directory = _pack_directory()
    pack = directory / f"{series}.zip" if directory is not None else None
    if pack is None or not pack.is_file():
        raise OfflineDocsError(f"No packaged documentation for Odoo {series}")
    return pack


def _valid_member(name: str) -> bool:
    parts = PurePosixPath(name).parts
    return (
        "\\" not in name
        and ".." not in parts
        and not name.startswith("/")
        and (
            name == "LICENSE"
            or (len(parts) >= 2 and parts[0] == "content" and name.endswith(".rst"))
        )
    )


def _build_index(root: Path) -> int:
    pages = sorted((root / "content").rglob("*.rst"))
    connection = sqlite3.connect(root / INDEX_FILE)
    try:
        connection.execute(
            "CREATE TABLE pages (id INTEGER PRIMARY KEY, path TEXT, section TEXT, title TEXT, body TEXT)"
        )
        for page in pages:
            relative = page.relative_to(root).as_posix()
            section = page.relative_to(root / "content").parts[0]
            title = page.stem.replace("_", " ").replace("-", " ")
            body = page.read_text(encoding="utf-8", errors="replace")
            connection.execute(
                "INSERT INTO pages (path, section, title, body) VALUES (?, ?, ?, ?)",
                (relative, section, title, body),
            )
        try:
            connection.execute(
                "CREATE VIRTUAL TABLE docs_fts USING fts5(title, body, content='pages', content_rowid='id')"
            )
            connection.execute("INSERT INTO docs_fts(docs_fts) VALUES ('rebuild')")
        except sqlite3.OperationalError:
            # SQLite without FTS5 still supports bounded LIKE searches.
            connection.execute("DROP TABLE IF EXISTS docs_fts")
        connection.commit()
    finally:
        connection.close()
    return len(pages)


def _finish_install(
    staging: Path, series: str, revision: str, source_kind: str, cache: Path
) -> Path:
    if not (staging / "LICENSE").is_file() or not (staging / "content").is_dir():
        raise OfflineDocsError("Documentation source lacks LICENSE or content/")
    count = _build_index(staging)
    if count == 0:
        raise OfflineDocsError("Documentation source contains no RST pages")
    metadata = {
        "series": series,
        "revision": revision,
        "source_kind": source_kind,
        "source": SOURCE_URL,
        "license": "CC-BY-SA-4.0",
        "page_count": count,
    }
    (staging / METADATA_FILE).write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    series_root = cache / series
    target = series_root / revision
    if target.exists():
        shutil.rmtree(target)
    staging.replace(target)
    _set_current(series_root, revision)
    return target


def _set_current(series_root: Path, revision: str) -> None:
    current = series_root / "current.json"
    temporary = series_root / ".current.tmp"
    temporary.write_text(json.dumps({"revision": revision}) + "\n", encoding="utf-8")
    temporary.replace(current)


def _install_archive(stream: BinaryIO, series: str, cache: Path, source_kind: str) -> Path:
    with ZipFile(stream) as archive:
        try:
            if archive.getinfo("manifest.json").file_size > 8192:
                raise OfflineDocsError("Documentation pack manifest is too large")
            manifest = json.loads(archive.read("manifest.json"))
        except (KeyError, json.JSONDecodeError) as exc:
            raise OfflineDocsError("Documentation pack lacks a valid manifest") from exc
        if not isinstance(manifest, dict):
            raise OfflineDocsError("Documentation pack lacks a valid manifest")
        revision = manifest.get("revision", "")
        if (
            manifest.get("series") != series
            or manifest.get("format") != "rst-text-v1"
            or not isinstance(revision, str)
            or not re.fullmatch(r"[0-9a-f]{40}", revision)
        ):
            raise OfflineDocsError("Documentation pack version or revision is invalid")
        if len(set(archive.namelist())) != len(archive.namelist()):
            raise OfflineDocsError("Documentation pack contains duplicate paths")
        target = cache / series / revision
        if (target / METADATA_FILE).is_file() and (target / INDEX_FILE).is_file():
            _set_current(cache / series, revision)
            return target
        members = [info for info in archive.infolist() if info.filename != "manifest.json"]
        if sum(info.file_size for info in members) > MAX_PACK_UNCOMPRESSED:
            raise OfflineDocsError("Documentation pack exceeds the size limit")
        if any(not _valid_member(info.filename) or info.is_dir() for info in members):
            raise OfflineDocsError("Documentation pack contains an unexpected path")
        series_root = cache / series
        series_root.mkdir(parents=True, exist_ok=True)
        with tempfile.TemporaryDirectory(prefix=".docs-", dir=series_root) as temporary:
            staging = Path(temporary)
            for info in members:
                path = staging / info.filename
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(archive.read(info))
            return _finish_install(staging, series, revision, source_kind, cache)


def install_pack(
    series: str, *, cache_dir: Path | None = None, pack_path: Path | None = None
) -> Path:
    """Install a bundled or explicitly supplied documentation pack into shared cache."""
    series = documentation_series(series)
    pack = pack_path if pack_path is not None else _pack_for(series)
    try:
        with pack.open("rb") as stream:
            return _install_archive(stream, series, cache_dir or default_cache_dir(), "packaged")
    except BadZipFile as exc:
        raise OfflineDocsError(f"Invalid documentation archive: {pack}") from exc


def _source_revision(checkout: Path) -> str:
    if (checkout / ".git").exists():
        try:
            result = subprocess.run(
                ["git", "-C", str(checkout), "rev-parse", "HEAD"],
                capture_output=True,
                text=True,
                timeout=10,
                check=True,
            )
            if re.fullmatch(r"[0-9a-f]{40}", result.stdout.strip()):
                return result.stdout.strip()
        except (OSError, subprocess.SubprocessError):
            pass
    digest = hashlib.sha256()
    for path in [checkout / "LICENSE", *sorted((checkout / "content").rglob("*.rst"))]:
        digest.update(path.relative_to(checkout).as_posix().encode())
        digest.update(path.read_bytes())
    return digest.hexdigest()


def install_checkout(
    checkout: Path,
    series: str,
    *,
    cache_dir: Path | None = None,
    source_kind: str = "existing",
) -> Path:
    """Copy the text of a matching local checkout into the shared cache."""
    series = documentation_series(series)
    checkout = checkout.expanduser().resolve()
    if not (checkout / "LICENSE").is_file() or not (checkout / "content").is_dir():
        raise OfflineDocsError("Expected an Odoo documentation checkout with content/ and LICENSE")
    if (checkout / ".git").exists() and source_kind == "existing":
        try:
            branch = subprocess.run(
                ["git", "-C", str(checkout), "branch", "--show-current"],
                capture_output=True,
                text=True,
                timeout=10,
                check=False,
            )
            if branch.returncode == 0 and branch.stdout.strip() not in {"", series}:
                raise OfflineDocsError(
                    f"Documentation checkout is on branch {branch.stdout.strip()}, expected {series}"
                )
        except (OSError, subprocess.TimeoutExpired):
            pass
    revision = _source_revision(checkout) if source_kind == "download" else ""
    if source_kind != "download":
        digest = hashlib.sha256()
        for page in [checkout / "LICENSE", *sorted((checkout / "content").rglob("*.rst"))]:
            digest.update(page.relative_to(checkout).as_posix().encode())
            digest.update(page.read_bytes())
        revision = digest.hexdigest()
    cache = cache_dir or default_cache_dir()
    target = cache / series / revision
    if (target / METADATA_FILE).is_file() and (target / INDEX_FILE).is_file():
        _set_current(cache / series, revision)
        return target
    series_root = cache / series
    series_root.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=".docs-", dir=series_root) as temporary:
        staging = Path(temporary)
        shutil.copyfile(checkout / "LICENSE", staging / "LICENSE")
        for page in (checkout / "content").rglob("*.rst"):
            relative = page.relative_to(checkout)
            if not _valid_member(relative.as_posix()):
                continue
            dest = staging / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(page, dest)
        return _finish_install(staging, series, revision, source_kind, cache)


def download_docs(series: str, *, cache_dir: Path | None = None) -> Path:
    """Fetch only official RST text and license for the exact Odoo series."""
    series = documentation_series(series)
    with tempfile.TemporaryDirectory(prefix="odoo-boost-download-") as temporary:
        checkout = Path(temporary) / "documentation"
        commands = [
            [
                "git",
                "clone",
                "--depth",
                "1",
                "--filter=blob:none",
                "--sparse",
                "--branch",
                series,
                DOC_REPO,
                str(checkout),
            ],
            [
                "git",
                "-C",
                str(checkout),
                "sparse-checkout",
                "set",
                "--no-cone",
                "/content/**/*.rst",
                "/content/*.rst",
                "/LICENSE",
            ],
        ]
        for command in commands:
            try:
                result = subprocess.run(
                    command, capture_output=True, text=True, timeout=180, check=False
                )
            except (OSError, subprocess.TimeoutExpired) as exc:
                raise OfflineDocsError(f"Could not download Odoo documentation: {exc}") from exc
            if result.returncode != 0:
                raise OfflineDocsError(
                    f"Could not download Odoo {series} documentation: {result.stderr[-400:].strip()}"
                )
        return install_checkout(checkout, series, cache_dir=cache_dir, source_kind="download")


def cached_docs(series: str, *, cache_dir: Path | None = None) -> Path | None:
    """Return the current complete cache entry for a series, if one exists."""
    series = documentation_series(series)
    root = (cache_dir or default_cache_dir()) / series
    try:
        revision = json.loads((root / "current.json").read_text(encoding="utf-8"))["revision"]
    except (OSError, ValueError, KeyError):
        return None
    if not isinstance(revision, str) or not re.fullmatch(r"[0-9a-f]{40}|[0-9a-f]{64}", revision):
        return None
    target = root / revision
    return (
        target if (target / INDEX_FILE).is_file() and (target / METADATA_FILE).is_file() else None
    )


def _excerpt(root: Path, relative: str, terms: list[str], max_chars: int) -> tuple[int, str]:
    lines = (root / relative).read_text(encoding="utf-8", errors="replace").splitlines()
    scores = [sum(term in line.casefold() for term in terms) for line in lines]
    best = max(range(len(lines)), key=lambda index: scores[index]) if lines else 0
    selected: list[str] = []
    for line in lines[best : best + 18]:
        if re.fullmatch(r"[=~^\-+*#`:.]{3,}", line.strip()):
            continue
        if line.strip() or selected:
            selected.append(line)
        if len("\n".join(selected)) >= min(240, max_chars):
            break
    return best + 1, "\n".join(selected).strip()[:max_chars]


def search_local_docs(
    root: Path,
    query: str,
    *,
    version: str,
    section: str = "all",
    limit: int = 3,
    excerpt_chars: int = 700,
) -> dict[str, Any]:
    """Search an installed text index and return small, source-cited excerpts."""
    series = documentation_series(version)
    root = root.expanduser().resolve()
    try:
        metadata = json.loads((root / METADATA_FILE).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise OfflineDocsError(
            "Offline docs are not indexed; install a pack or checkout first"
        ) from exc
    if metadata.get("series") != series:
        raise OfflineDocsError(
            f"Offline docs are Odoo {metadata.get('series')}, requested {series}"
        )
    if section not in SECTIONS | {"all"}:
        raise OfflineDocsError(f"Unknown documentation section: {section}")
    terms = re.findall(r"\w+", query.casefold())[:8]
    if not terms:
        raise OfflineDocsError("Search query must contain a word")
    if not (root / INDEX_FILE).is_file():
        raise OfflineDocsError("Offline docs index is missing; reinstall the selected version")
    connection = sqlite3.connect(root / INDEX_FILE)
    try:
        has_fts = connection.execute("SELECT 1 FROM sqlite_master WHERE name='docs_fts'").fetchone()
        filter_sql = " AND p.section = ?" if section != "all" else ""
        section_args = [section] if section != "all" else []
        if has_fts:
            for joiner in (" AND ", " OR "):
                expression = joiner.join(f'"{term}"' for term in terms)
                rows = connection.execute(
                    "SELECT p.path, p.section, p.title FROM docs_fts "
                    "JOIN pages p ON p.id = docs_fts.rowid WHERE docs_fts MATCH ?"
                    + filter_sql
                    + " ORDER BY bm25(docs_fts) LIMIT ?",
                    [expression, *section_args, max(1, min(limit, 10))],
                ).fetchall()
                if rows:
                    break
        else:
            conditions = " AND ".join("lower(p.body) LIKE ?" for _ in terms)
            rows = connection.execute(
                "SELECT p.path, p.section, p.title FROM pages p WHERE "
                + conditions
                + filter_sql
                + " LIMIT ?",
                [*(f"%{term}%" for term in terms), *section_args, max(1, min(limit, 10))],
            ).fetchall()
    finally:
        connection.close()
    results = []
    for relative, page_section, title in rows:
        line, excerpt = _excerpt(root, relative, terms, max(100, min(excerpt_chars, 1500)))
        web_path = relative.removeprefix("content/").removesuffix(".rst") + ".html"
        results.append(
            {
                "section": page_section,
                "title": title,
                "source": f"{root / relative}:{line}",
                "url": f"https://www.odoo.com/documentation/{series}/{web_path}",
                "excerpt": excerpt,
            }
        )
    return {"version": series, "revision": metadata["revision"], "results": results}
