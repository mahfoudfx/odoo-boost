"""Tests for odoo_boost.mcp_launcher (WSL/HTTP resolution)."""

from __future__ import annotations

import sys
from pathlib import Path

from odoo_boost.config.schema import OdooBoostConfig
from odoo_boost.config.schema import OdooConnection as OdooConnectionConfig
from odoo_boost.mcp_launcher import (
    build_http_url,
    build_stdio_command,
    config_path_for,
    detect_wsl_distro,
    is_loopback_host,
    is_wsl,
)


def _config(**overrides) -> OdooBoostConfig:
    base = {
        "connection": OdooConnectionConfig(url="http://localhost:8069", database="db"),
        "project_path": ".",
    }
    base.update(overrides)
    return OdooBoostConfig(**base)


class TestWslDetection:
    def test_detects_wsl_distro_env(self):
        assert is_wsl({"WSL_DISTRO_NAME": "Ubuntu"}) is True

    def test_detects_wsl_interop_env(self):
        assert is_wsl({"WSL_INTEROP": "/run/WSL/1_interop"}) is True

    def test_distro_from_env(self):
        assert detect_wsl_distro({"WSL_DISTRO_NAME": "Debian"}) == "Debian"

    def test_distro_none_without_env(self):
        assert detect_wsl_distro({}) is None


class TestIsLoopbackHost:
    def test_loopback_hosts(self):
        assert is_loopback_host("127.0.0.1") is True
        assert is_loopback_host("localhost") is True
        assert is_loopback_host("::1") is True

    def test_remote_hosts(self):
        assert is_loopback_host("0.0.0.0") is False
        assert is_loopback_host("192.168.1.20") is False


class TestBuildStdioCommand:
    def test_native_includes_explicit_config(self, tmp_path: Path):
        cmd = build_stdio_command(_config(), tmp_path)
        assert cmd[0] == sys.executable
        assert cmd[1:4] == ["-m", "odoo_boost", "mcp"]
        assert cmd[-2] == "-c"
        assert cmd[-1] == str(config_path_for(tmp_path))

    def test_windows_target_wraps_in_wsl(self, tmp_path: Path):
        cmd = build_stdio_command(_config(mcp_target="wsl", wsl_distro="Ubuntu"), tmp_path)
        assert cmd[0] == "wsl.exe"
        assert cmd[1:3] == ["-d", "Ubuntu"]
        assert cmd[3] == "--cd"
        assert cmd[4] == str(tmp_path)
        assert cmd[5] == "--"
        assert sys.executable in cmd

    def test_windows_flag_overrides_target(self, tmp_path: Path):
        cmd = build_stdio_command(_config(mcp_target="native"), tmp_path, windows=True)
        assert cmd[0] == "wsl.exe"

    def test_wsl_target_falls_back_to_default_distro(self, tmp_path: Path, monkeypatch):
        monkeypatch.delenv("WSL_DISTRO_NAME", raising=False)
        cmd = build_stdio_command(_config(mcp_target="wsl"), tmp_path)
        assert "Ubuntu" in cmd

    def test_custom_command_used_verbatim(self, tmp_path: Path):
        cmd = build_stdio_command(_config(mcp_command=["docker", "run", "x"]), tmp_path)
        assert cmd == ["docker", "run", "x"]


class TestBuildHttpUrl:
    def test_default_host(self):
        assert build_http_url(_config()) == "http://127.0.0.1:8765/mcp"

    def test_custom_host_and_port(self):
        cfg = _config(mcp_host="0.0.0.0", mcp_port=9999)
        assert build_http_url(cfg) == "http://127.0.0.1:9999/mcp"

    def test_remote_host_preserved(self):
        cfg = _config(mcp_host="192.168.1.10", mcp_port=8000)
        assert build_http_url(cfg) == "http://192.168.1.10:8000/mcp"
