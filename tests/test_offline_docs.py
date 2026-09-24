"""Offline docs must match the target series and return bounded local evidence."""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import MagicMock, patch
from zipfile import ZIP_DEFLATED, ZipFile

import pytest
from typer.testing import CliRunner

from odoo_boost.cli.app import app
from odoo_boost.config.schema import OdooBoostConfig, OdooConnection
from odoo_boost.config.settings import load_config, save_config
from odoo_boost.mcp_server.context import ServerContext, bound_context
from odoo_boost.mcp_server.tools.search_docs import _TOPICS, search_docs
from odoo_boost.offline_docs import (
    OfflineDocsError,
    _pack_for,
    available_packs,
    cached_docs,
    install_pack,
    search_local_docs,
)
from odoo_boost.versions import get_version_profile


def _pack(path: Path, *, series: str = "18.0", extra: str | None = None) -> Path:
    with ZipFile(path, "w", ZIP_DEFLATED) as archive:
        archive.writestr(
            "manifest.json",
            json.dumps(
                {
                    "series": series,
                    "revision": "a" * 40,
                    "format": "rst-text-v1",
                    "source": "https://github.com/odoo/documentation",
                }
            ),
        )
        archive.writestr("LICENSE", "CC BY-SA 4.0")
        archive.writestr(
            "content/developer/reference/backend/orm.rst",
            "Computed fields\n~~~~~~~~~~~~~~~\nComputed fields use dependencies.\n",
        )
        archive.writestr("content/administration/hosting.rst", "Hosting options for Odoo\n")
        archive.writestr("content/applications/sales.rst", "Sales orders and quotations\n")
        if extra:
            archive.writestr(extra, "unexpected")
    return path


def test_pack_install_and_search_all_sections(tmp_path):
    archive = _pack(tmp_path / "docs.zip")
    cache = tmp_path / "cache"
    root = install_pack("18.0", pack_path=archive, cache_dir=cache)

    assert root == cached_docs("18.0", cache_dir=cache)
    assert (root / "LICENSE").is_file()
    result = search_local_docs(root, "computed fields", version="18.0", section="developer")
    assert len(result["results"]) == 1
    assert "dependencies" in result["results"][0]["excerpt"]
    assert result["results"][0]["source"].endswith("orm.rst:1")
    assert result["results"][0]["url"].endswith("/developer/reference/backend/orm.html")
    assert search_local_docs(root, "hosting", version="18.0", section="administration")["results"]
    assert search_local_docs(root, "sales", version="18.0", section="applications")["results"]
    with pytest.raises(OfflineDocsError, match="requested 19.0"):
        search_local_docs(root, "fields", version="19.0")


def test_pack_rejects_version_mismatch_and_traversal(tmp_path):
    archive = _pack(tmp_path / "docs.zip", extra="../escape.rst")
    with pytest.raises(OfflineDocsError, match="unexpected path"):
        install_pack("18.0", pack_path=archive, cache_dir=tmp_path / "cache")
    assert not (tmp_path / "escape.rst").exists()
    clean = _pack(tmp_path / "clean.zip", series="19.0")
    with pytest.raises(OfflineDocsError, match="version or revision"):
        install_pack("18.0", pack_path=clean, cache_dir=tmp_path / "cache")


def test_pack_rejects_invalid_archive(tmp_path):
    invalid = tmp_path / "invalid.zip"
    invalid.write_text("invalid archive", encoding="utf-8")
    with pytest.raises(OfflineDocsError, match="Invalid documentation archive"):
        install_pack("18.0", pack_path=invalid, cache_dir=tmp_path / "cache")


def test_search_docs_uses_local_index_only_on_query(tmp_path):
    root = install_pack("18.0", pack_path=_pack(tmp_path / "docs.zip"), cache_dir=tmp_path)
    config = OdooBoostConfig(
        connection=OdooConnection(url="http://localhost:8069", database="test"),
        odoo_version="18.0",
        odoo_docs_path=str(root),
    )
    with bound_context(ServerContext(connection=MagicMock(), config=config)):
        result = json.loads(search_docs(query="computed fields", section="developer"))
        links = json.loads(search_docs(topic="orm"))
    assert result["results"][0]["section"] == "developer"
    assert "local_source" in links["results"][0]


def test_docs_cli_archive_install_updates_matching_project_config(tmp_path):
    config = OdooBoostConfig(
        connection=OdooConnection(url="http://localhost:8069", database="test"),
        odoo_version="18.0",
        project_path=str(tmp_path),
    )
    config_file = save_config(config, tmp_path / "odoo-boost.json")
    archive = _pack(tmp_path / "docs.zip")
    result = CliRunner().invoke(
        app,
        [
            "docs",
            "install",
            "--version",
            "18.0",
            "--source",
            "archive",
            "--path",
            str(archive),
            "--cache-dir",
            str(tmp_path / "cache"),
            "--config",
            str(config_file),
        ],
    )
    assert result.exit_code == 0, result.output
    assert Path(load_config(config_file).odoo_docs_path or "").is_dir()


def test_docs_cli_reports_invalid_explicit_config_after_caching(tmp_path):
    archive = _pack(tmp_path / "docs.zip")
    result = CliRunner().invoke(
        app,
        [
            "docs",
            "install",
            "--version",
            "18.0",
            "--source",
            "archive",
            "--path",
            str(archive),
            "--cache-dir",
            str(tmp_path / "cache"),
            "--config",
            str(tmp_path / "missing.json"),
        ],
    )
    assert result.exit_code == 1
    assert "Documentation is cached, but project config was not updated" in result.output
    assert cached_docs("18.0", cache_dir=tmp_path / "cache") is not None


def test_installer_offers_pack_choice_when_available(tmp_path):
    with (
        patch("odoo_boost.cli.install.cached_docs", return_value=None),
        patch("odoo_boost.cli.install.available_packs", return_value=["18.0"]),
        patch("odoo_boost.cli.install.Prompt.ask", return_value="S") as ask,
        patch("odoo_boost.cli.install.install_pack", return_value=tmp_path) as install,
    ):
        from odoo_boost.cli.install import _choose_offline_docs

        assert _choose_offline_docs("18.0") == tmp_path
    install.assert_called_once_with("18.0")
    assert ask.call_args.kwargs["default"] == "D"
    assert ask.call_args.kwargs["case_sensitive"] is False


def test_installer_accepts_existing_path_letter(tmp_path):
    checkout = tmp_path / "documentation"
    with (
        patch("odoo_boost.cli.install.cached_docs", return_value=None),
        patch("odoo_boost.cli.install.available_packs", return_value=[]),
        patch("odoo_boost.cli.install.Prompt.ask", side_effect=["P", str(checkout)]),
        patch("odoo_boost.cli.install.install_checkout", return_value=tmp_path) as install,
    ):
        from odoo_boost.cli.install import _choose_offline_docs

        assert _choose_offline_docs("18.0") == tmp_path
    install.assert_called_once_with(checkout, "18.0")


def test_installer_keeps_online_links_when_download_fails():
    with (
        patch("odoo_boost.cli.install.cached_docs", return_value=None),
        patch("odoo_boost.cli.install.available_packs", return_value=[]),
        patch("odoo_boost.cli.install.Prompt.ask", return_value="download"),
        patch(
            "odoo_boost.cli.install.download_docs",
            side_effect=OfflineDocsError("network unavailable"),
        ),
    ):
        from odoo_boost.cli.install import _choose_offline_docs

        assert _choose_offline_docs("18.0") is None


def test_packaged_snapshots_cover_three_latest_series():
    assert {"18.0", "19.0", "20.0"}.issubset(available_packs())
    for series in ("18.0", "19.0", "20.0"):
        with _pack_for(series).open("rb") as stream, ZipFile(stream) as archive:
            manifest = json.loads(archive.read("manifest.json"))
            assert manifest["series"] == series
            assert manifest["page_count"] >= 1000
            assert archive.read("LICENSE")
            names = archive.namelist()
            assert any(name.startswith("content/developer/") for name in names)
            assert any(name.startswith("content/administration/") for name in names)
            assert any(name.startswith("content/applications/") for name in names)
            profile = get_version_profile(series)
            assert profile is not None
            for topic, details in _TOPICS.items():
                path = profile.doc_paths.get(topic, details["path"]).split("#", 1)[0]
                assert "content" + path.removesuffix(".html") + ".rst" in names
