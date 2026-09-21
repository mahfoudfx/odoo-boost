"""Tests for official Odoo Language Server integration."""

from __future__ import annotations

import io
import json
import tarfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from odoo_boost import odoo_ls
from odoo_boost.mcp_server.tools import check_odoo_ls as check_module


def _tar_binary(content: bytes = b"binary") -> bytes:
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:gz") as archive:
        info = tarfile.TarInfo("odoo_ls_server")
        info.size = len(content)
        archive.addfile(info, io.BytesIO(content))
    return stream.getvalue()


def test_official_asset_name_linux(monkeypatch):
    monkeypatch.setattr(odoo_ls.platform, "system", lambda: "Linux")
    monkeypatch.setattr(odoo_ls.platform, "machine", lambda: "x86_64")
    assert odoo_ls.official_asset_name("1.4.0") == "odoo-linux-x86_64-1.4.0.tar.gz"


def test_install_uses_exact_official_asset(monkeypatch, tmp_path):
    monkeypatch.setattr(odoo_ls.platform, "system", lambda: "Linux")
    monkeypatch.setattr(odoo_ls.platform, "machine", lambda: "x86_64")
    url = "https://github.com/odoo/odoo-ls/releases/download/1.4.0/odoo-linux-x86_64-1.4.0.tar.gz"
    monkeypatch.setattr(
        odoo_ls,
        "_read_json",
        lambda _url: {
            "tag_name": "1.4.0",
            "assets": [{"name": "odoo-linux-x86_64-1.4.0.tar.gz", "browser_download_url": url}],
        },
    )
    monkeypatch.setattr(
        odoo_ls, "_download", lambda actual: _tar_binary() if actual == url else b""
    )

    installed, version = odoo_ls.install_official_odoo_ls(tmp_path)

    assert version == "1.4.0"
    assert installed.read_bytes() == b"binary"
    assert installed.stat().st_mode & 0o111


def test_installer_rejects_non_official_download(monkeypatch, tmp_path):
    monkeypatch.setattr(odoo_ls.platform, "system", lambda: "Linux")
    monkeypatch.setattr(odoo_ls.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(
        odoo_ls,
        "_read_json",
        lambda _url: {
            "tag_name": "1.4.0",
            "assets": [
                {
                    "name": "odoo-linux-x86_64-1.4.0.tar.gz",
                    "browser_download_url": "https://example.com/untrusted.tar.gz",
                }
            ],
        },
    )
    with pytest.raises(RuntimeError, match="official"):
        odoo_ls.install_official_odoo_ls(tmp_path)


def test_check_runs_official_parse_mode(monkeypatch, tmp_path):
    binary = tmp_path / "odoo_ls_server"
    binary.write_text("")
    (tmp_path / "odools.toml").write_text('[[config]]\nname = "default"\n')
    monkeypatch.setattr(check_module, "find_odoo_ls", lambda _configured=None: binary)

    def run(command, **_kwargs):
        output = Path(command[command.index("--output") + 1])
        output.write_text(
            json.dumps(
                {
                    "events": [
                        {
                            "type": "diagnostic",
                            "uri": "file:///models/x.py",
                            "diagnostics": [{"message": "bad field", "severity": 1}],
                        }
                    ]
                }
            )
        )
        assert command[1] == "--parse"
        assert "--tracked-folders" in command
        assert "--config-path" in command
        return MagicMock(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(check_module.subprocess, "run", run)
    result = json.loads(check_module.check_odoo_ls(str(tmp_path)))

    assert result["installed"] is True
    assert result["diagnostic_count"] == 1
    assert result["diagnostics"][0]["message"] == "bad field"


def test_check_missing_binary_suggests_official_installer(monkeypatch):
    monkeypatch.setattr(check_module, "find_odoo_ls", lambda _configured=None: None)
    result = json.loads(check_module.check_odoo_ls())
    assert result["installed"] is False
    assert result["install_command"] == "odoo-boost odoo-ls install"
