"""Tests for official Odoo Language Server integration."""

from __future__ import annotations

import io
import json
import shutil
import tarfile
import zipfile
from pathlib import Path
from unittest.mock import MagicMock

import pytest

from odoo_boost import odoo_ls
from odoo_boost.config.schema import OdooBoostConfig, OdooConnection
from odoo_boost.mcp_server.tools import check_odoo_ls as check_module

_BASE = "https://github.com/odoo/odoo-ls/releases/download"


def _tar_binary(content: bytes = b"binary") -> bytes:
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w:gz") as archive:
        info = tarfile.TarInfo("odoo_ls_server")
        info.size = len(content)
        archive.addfile(info, io.BytesIO(content))
    return stream.getvalue()


def _typeshed_zip(extra: dict[str, bytes] | None = None) -> bytes:
    stream = io.BytesIO()
    files = {
        "stdlib/builtins.pyi": b"class object: ...\n",
        "stubs/six/six/__init__.pyi": b"",
        "README.md": b"ignored",
        **(extra or {}),
    }
    with zipfile.ZipFile(stream, "w") as archive:
        for name, content in files.items():
            archive.writestr(name, content)
    return stream.getvalue()


def _usable_binary(directory: Path, content: str = "") -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    binary = directory / "odoo_ls_server"
    binary.write_text(content)
    stdlib = directory / "typeshed" / "stdlib"
    stdlib.mkdir(parents=True)
    (stdlib / "builtins.pyi").write_text("")
    return binary


@pytest.fixture
def release(monkeypatch, tmp_path):
    """Serve a fake official release; returns the list of downloaded URLs."""
    monkeypatch.setattr(odoo_ls.platform, "system", lambda: "Linux")
    monkeypatch.setattr(odoo_ls.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(odoo_ls, "default_link_dir", lambda: tmp_path / "bin")
    tags = {"tag": "1.6.1"}
    downloads: list[str] = []

    def read_json(_url):
        tag = tags["tag"]
        return {
            "tag_name": tag,
            "assets": [
                {
                    "name": f"odoo-linux-x86_64-{tag}.tar.gz",
                    "browser_download_url": f"{_BASE}/{tag}/odoo-linux-x86_64-{tag}.tar.gz",
                },
                {"name": "typeshed.zip", "browser_download_url": f"{_BASE}/{tag}/typeshed.zip"},
            ],
        }

    def download(url):
        downloads.append(url)
        if url.endswith("typeshed.zip"):
            return _typeshed_zip()
        return _tar_binary(tags["tag"].encode())

    monkeypatch.setattr(odoo_ls, "_read_json", read_json)
    monkeypatch.setattr(odoo_ls, "_download", download)
    return tags, downloads


def test_official_asset_name_linux(monkeypatch):
    monkeypatch.setattr(odoo_ls.platform, "system", lambda: "Linux")
    monkeypatch.setattr(odoo_ls.platform, "machine", lambda: "x86_64")
    assert odoo_ls.official_asset_name("1.6.1") == "odoo-linux-x86_64-1.6.1.tar.gz"


def test_install_places_typeshed_next_to_binary(release, tmp_path):
    result = odoo_ls.install_official_odoo_ls(tmp_path / "ls")

    assert result.changed and result.tag == "1.6.1"
    assert result.path.read_bytes() == b"1.6.1"
    assert result.path.stat().st_mode & 0o111
    assert odoo_ls.is_usable(result.path)
    assert (tmp_path / "ls" / "typeshed" / "stubs" / "six" / "six" / "__init__.pyi").is_file()
    assert not (tmp_path / "ls" / "typeshed" / "README.md").exists()
    assert odoo_ls.installed_tag(tmp_path / "ls") == "1.6.1"
    assert result.link is None  # explicit destinations are not linked on PATH


def test_install_is_noop_when_current_and_upgrades_when_outdated(release, tmp_path):
    tags, downloads = release
    tags["tag"] = "1.5.0"
    odoo_ls.install_official_odoo_ls(tmp_path / "ls")
    downloads.clear()

    again = odoo_ls.install_official_odoo_ls(tmp_path / "ls")
    assert not again.changed and downloads == []

    tags["tag"] = "1.6.1"
    upgraded = odoo_ls.install_official_odoo_ls(tmp_path / "ls")
    assert upgraded.changed
    assert upgraded.path.read_bytes() == b"1.6.1"
    assert odoo_ls.installed_tag(tmp_path / "ls") == "1.6.1"
    assert [p.name for p in tmp_path.iterdir() if p.name.startswith(".")] == []


def test_install_repairs_managed_install_without_typeshed(release, tmp_path):
    odoo_ls.install_official_odoo_ls(tmp_path / "ls")
    shutil.rmtree(tmp_path / "ls" / "typeshed")

    result = odoo_ls.install_official_odoo_ls(tmp_path / "ls")
    assert result.changed and odoo_ls.is_usable(result.path)


def test_install_never_replaces_a_foreign_directory(release, tmp_path):
    foreign = tmp_path / "bin-of-user"
    foreign.mkdir()
    (foreign / "other-tool").write_text("keep")

    with pytest.raises(FileExistsError, match="not created by Odoo Boost"):
        odoo_ls.install_official_odoo_ls(foreign, force=True)
    assert (foreign / "other-tool").read_text() == "keep"


def test_default_install_links_on_path_and_replaces_stubless_binary(release, monkeypatch, tmp_path):
    monkeypatch.setattr(odoo_ls, "default_install_dir", lambda: tmp_path / "data" / "odoo-ls")
    legacy = tmp_path / "bin" / "odoo_ls_server"
    legacy.parent.mkdir()
    legacy.write_text("old binary without stubs")

    result = odoo_ls.install_official_odoo_ls()

    assert result.link == legacy
    assert legacy.is_symlink() and legacy.resolve() == result.path.resolve()


def test_default_install_keeps_a_working_foreign_binary_on_path(release, monkeypatch, tmp_path):
    monkeypatch.setattr(odoo_ls, "default_install_dir", lambda: tmp_path / "data" / "odoo-ls")
    foreign = _usable_binary(tmp_path / "editor-extension")
    link = tmp_path / "bin" / "odoo_ls_server"
    link.parent.mkdir()
    link.symlink_to(foreign)

    result = odoo_ls.install_official_odoo_ls()

    assert result.link is None
    assert link.resolve() == foreign.resolve()


def test_installer_rejects_non_official_download(monkeypatch, tmp_path):
    monkeypatch.setattr(odoo_ls.platform, "system", lambda: "Linux")
    monkeypatch.setattr(odoo_ls.platform, "machine", lambda: "x86_64")
    monkeypatch.setattr(
        odoo_ls,
        "_read_json",
        lambda _url: {
            "tag_name": "1.6.1",
            "assets": [
                {
                    "name": "odoo-linux-x86_64-1.6.1.tar.gz",
                    "browser_download_url": "https://example.com/untrusted.tar.gz",
                }
            ],
        },
    )
    with pytest.raises(RuntimeError, match="official"):
        odoo_ls.install_official_odoo_ls(tmp_path / "ls")


def test_typeshed_extraction_rejects_parent_paths(tmp_path):
    payload = _typeshed_zip({"stubs/../../escape.pyi": b"x"})
    with pytest.raises(RuntimeError, match="Unsafe path"):
        odoo_ls._extract_typeshed(payload, tmp_path / "typeshed")
    assert not (tmp_path / "escape.pyi").exists()


def test_find_prefers_usable_install_over_stubless_binary_on_path(monkeypatch, tmp_path):
    broken = tmp_path / "bin" / "odoo_ls_server"
    broken.parent.mkdir()
    broken.write_text("")
    managed = _usable_binary(tmp_path / "data" / "odoo-ls")
    monkeypatch.setattr(odoo_ls, "default_install_dir", lambda: managed.parent)
    monkeypatch.setattr(
        odoo_ls.shutil, "which", lambda name: str(broken) if name == "odoo_ls_server" else None
    )

    assert odoo_ls.find_odoo_ls() == managed.resolve()


def _fake_run(events, captured=None):
    def run(command, **_kwargs):
        if captured is not None:
            captured.extend(command)
        output = Path(command[command.index("--output") + 1])
        output.write_text(json.dumps({"events": events}))
        return MagicMock(returncode=0, stdout="", stderr="")

    return run


def _diagnostic(path: Path, line: int, severity: int, code: str) -> dict:
    return {
        "type": "diagnostic",
        "uri": path.as_uri(),
        "diagnostics": [
            {
                "message": f"{code} message",
                "severity": severity,
                "code": code,
                "range": {"start": {"line": line, "character": 4}},
            }
        ],
    }


_ODOO_LOADED = {"type": "log", "severity": 3, "message": "Odoo version: 18.0.0"}


def test_check_scopes_sorts_and_summarizes_diagnostics(monkeypatch, tmp_path):
    addon = tmp_path / "addon"
    (addon / "models").mkdir(parents=True)
    (tmp_path / "odools.toml").write_text('[[config]]\nname = "default"\n')
    binary = _usable_binary(tmp_path / "ls")
    monkeypatch.setattr(check_module, "find_odoo_ls", lambda _configured=None: binary)
    events = [
        _ODOO_LOADED,
        _diagnostic(tmp_path / "odoo" / "web.js", 1, 1, "eslint"),
        *[_diagnostic(addon / "static" / "x.js", n, 2, "eslint") for n in range(40)],
        _diagnostic(addon / "models" / "x.py", 9, 1, "OLS03014"),
    ]
    captured: list[str] = []
    monkeypatch.setattr(check_module.subprocess, "run", _fake_run(events, captured))

    result = json.loads(check_module.check_odoo_ls(str(addon)))

    assert captured[1] == "--parse"
    assert captured[captured.index("--config-path") + 1] == str(tmp_path / "odools.toml")
    assert result["odoo_version"] == "18.0.0" and "warning" not in result
    assert result["diagnostic_count"] == 41
    assert result["outside_path_count"] == 1
    assert result["by_severity"] == {"warning": 40, "error": 1}
    assert result["truncated"] is True and len(result["diagnostics"]) == 30
    assert result["diagnostics"][0] == {
        "file": "models/x.py",
        "line": 10,
        "column": 5,
        "severity": "error",
        "message": "OLS03014 message",
        "code": "OLS03014",
    }


def test_check_full_format_returns_raw_records(monkeypatch, tmp_path):
    binary = _usable_binary(tmp_path / "ls")
    monkeypatch.setattr(check_module, "find_odoo_ls", lambda _configured=None: binary)
    events = [_ODOO_LOADED, _diagnostic(tmp_path / "a.py", 0, 1, "OLS1")]
    monkeypatch.setattr(check_module.subprocess, "run", _fake_run(events))

    result = json.loads(check_module.check_odoo_ls(str(tmp_path), response_format="full"))

    assert result["diagnostics"][0]["uri"] == (tmp_path / "a.py").as_uri()
    assert result["truncated"] is False


def test_check_warns_when_odoo_framework_not_loaded(monkeypatch, tmp_path):
    binary = _usable_binary(tmp_path / "ls")
    monkeypatch.setattr(check_module, "find_odoo_ls", lambda _configured=None: binary)
    monkeypatch.setattr(check_module.subprocess, "run", _fake_run([]))

    result = json.loads(check_module.check_odoo_ls(str(tmp_path)))

    assert result["odoo_version"] is None
    assert "odools.toml" in result["warning"]


def test_check_passes_project_paths_without_odools_toml(monkeypatch, tmp_path):
    project = tmp_path / "project"
    source = tmp_path / "odoo"
    (source / "addons").mkdir(parents=True)
    venv = project / ".venv"
    (venv / "bin").mkdir(parents=True)
    (venv / "pyvenv.cfg").write_text("")
    (venv / "bin" / "python").write_text("")
    (project / "odoo.conf").write_text(f"[options]\naddons_path = {source / 'addons'}\n")
    config = OdooBoostConfig(
        connection=OdooConnection(url="http://localhost:8069", database="test"),
        project_path=str(project),
        venv_path=".venv",
        odoo_conf_path="odoo.conf",
        odoo_source_path=str(source),
    )
    binary = _usable_binary(tmp_path / "ls")
    monkeypatch.setattr(check_module, "active_config", lambda: config)
    monkeypatch.setattr(check_module, "enforce_path", lambda raw: Path(raw))
    monkeypatch.setattr(check_module, "find_odoo_ls", lambda _configured=None: binary)
    captured: list[str] = []
    monkeypatch.setattr(check_module.subprocess, "run", _fake_run([_ODOO_LOADED], captured))

    check_module.check_odoo_ls(str(project))

    assert "--config-path" not in captured
    assert captured[captured.index("--community-path") + 1] == str(source)
    assert captured[captured.index("--addons") + 1] == str(source / "addons")
    assert captured[captured.index("--python") + 1] == str(venv / "bin" / "python")


def test_check_refuses_binary_without_typeshed(monkeypatch, tmp_path):
    binary = tmp_path / "odoo_ls_server"
    binary.write_text("")
    monkeypatch.setattr(check_module, "find_odoo_ls", lambda _configured=None: binary)
    run = MagicMock()
    monkeypatch.setattr(check_module.subprocess, "run", run)

    result = json.loads(check_module.check_odoo_ls(str(tmp_path)))

    run.assert_not_called()
    assert "typeshed" in result["error"]
    assert result["install_command"] == "odoo-boost odoo-ls install"


def test_check_missing_binary_suggests_official_installer(monkeypatch):
    monkeypatch.setattr(check_module, "find_odoo_ls", lambda _configured=None: None)
    result = json.loads(check_module.check_odoo_ls())
    assert result["installed"] is False
    assert result["install_command"] == "odoo-boost odoo-ls install"
