"""Tests for odoo_boost.config (schema + settings)."""

from __future__ import annotations

import json

import pytest
from pydantic import ValidationError

from odoo_boost.config.schema import OdooBoostConfig
from odoo_boost.config.schema import OdooConnection as OdooConnectionConfig
from odoo_boost.config.settings import CONFIG_FILENAME, find_config_path, load_config, save_config

# ---------------------------------------------------------------------------
# Schema validation
# ---------------------------------------------------------------------------


class TestOdooConnectionConfig:
    def test_minimal_valid(self):
        cfg = OdooConnectionConfig(url="http://localhost:8069", database="mydb")
        assert cfg.username == "admin"
        assert cfg.password == "admin"
        assert cfg.protocol == "xmlrpc"

    def test_full_config(self):
        cfg = OdooConnectionConfig(
            url="https://odoo.example.com",
            database="prod",
            username="api_user",
            password="secret",
            protocol="xmlrpc",
        )
        assert cfg.url == "https://odoo.example.com"
        assert cfg.database == "prod"

    def test_missing_url_raises(self):
        with pytest.raises(ValidationError):
            OdooConnectionConfig(database="mydb")  # type: ignore[call-arg]

    def test_missing_database_raises(self):
        with pytest.raises(ValidationError):
            OdooConnectionConfig(url="http://localhost:8069")  # type: ignore[call-arg]


class TestOdooBoostConfig:
    def test_minimal(self, sample_connection_config):
        cfg = OdooBoostConfig(connection=sample_connection_config)
        assert cfg.odoo_version is None
        assert cfg.agents == []
        assert cfg.project_path == "."

    def test_full(self, sample_connection_config):
        cfg = OdooBoostConfig(
            connection=sample_connection_config,
            odoo_version="18.0",
            agents=["claude_code", "cursor"],
            project_path="/my/project",
        )
        assert cfg.odoo_version == "18.0"
        assert len(cfg.agents) == 2

    def test_roundtrip_json(self, sample_config):
        """model_dump_json → model_validate round-trip."""
        data = json.loads(sample_config.model_dump_json())
        restored = OdooBoostConfig.model_validate(data)
        assert restored.connection.url == sample_config.connection.url
        assert restored.agents == sample_config.agents

    def test_generate_flags_default_true(self, sample_connection_config):
        """Both generate flags should default to True."""
        cfg = OdooBoostConfig(connection=sample_connection_config)
        assert cfg.generate_mcp is True
        assert cfg.generate_ai_files is True

    def test_generate_flags_roundtrip(self, sample_connection_config):
        """JSON serialize/deserialize with False values."""
        cfg = OdooBoostConfig(
            connection=sample_connection_config,
            generate_mcp=False,
            generate_ai_files=False,
        )
        data = json.loads(cfg.model_dump_json())
        restored = OdooBoostConfig.model_validate(data)
        assert restored.generate_mcp is False
        assert restored.generate_ai_files is False

    def test_backward_compat_missing_flags(self, sample_connection_config):
        """Old config without generate flags parses with True defaults."""
        data = {
            "connection": sample_connection_config.model_dump(),
            "odoo_version": "18.0",
            "agents": ["claude_code"],
        }
        cfg = OdooBoostConfig.model_validate(data)
        assert cfg.generate_mcp is True
        assert cfg.generate_ai_files is True

    def test_extra_fields_ignored(self, sample_connection_config):
        """Extra fields in JSON should not break parsing."""
        data = {
            "connection": sample_connection_config.model_dump(),
            "unknown_field": 42,
        }
        cfg = OdooBoostConfig.model_validate(data)
        assert cfg.connection.url == sample_connection_config.url

    def test_mcp_defaults(self, sample_connection_config):
        cfg = OdooBoostConfig(connection=sample_connection_config)
        assert cfg.mcp_transport == "stdio"
        assert cfg.mcp_target == "auto"
        assert cfg.wsl_distro is None
        assert cfg.mcp_host == "127.0.0.1"
        assert cfg.mcp_port == 8765
        assert cfg.mcp_command is None

    def test_mcp_fields_roundtrip(self, sample_connection_config):
        cfg = OdooBoostConfig(
            connection=sample_connection_config,
            mcp_transport="http",
            mcp_target="wsl",
            wsl_distro="Ubuntu",
            mcp_host="0.0.0.0",
            mcp_port=9100,
            mcp_command=["docker", "run", "odoo-boost"],
        )
        restored = OdooBoostConfig.model_validate(json.loads(cfg.model_dump_json()))
        assert restored.mcp_transport == "http"
        assert restored.mcp_target == "wsl"
        assert restored.wsl_distro == "Ubuntu"
        assert restored.mcp_host == "0.0.0.0"
        assert restored.mcp_port == 9100
        assert restored.mcp_command == ["docker", "run", "odoo-boost"]

    def test_backward_compat_missing_mcp_fields(self, sample_connection_config):
        data = {
            "connection": sample_connection_config.model_dump(),
            "odoo_version": "18.0",
            "agents": ["claude_code"],
        }
        cfg = OdooBoostConfig.model_validate(data)
        assert cfg.mcp_transport == "stdio"
        assert cfg.mcp_target == "auto"

    def test_security_defaults(self, sample_connection_config):
        cfg = OdooBoostConfig(connection=sample_connection_config)
        assert cfg.mcp_token is None
        assert cfg.readonly is False
        assert cfg.allowed_roots == []
        assert cfg.allow_external_local_paths is False
        assert cfg.mcp_http_url is None
        assert cfg.odoo_ls_path is None

    def test_token_hidden_from_repr(self, sample_connection_config):
        cfg = OdooBoostConfig(connection=sample_connection_config, mcp_token="super-secret")
        assert "super-secret" not in repr(cfg)

    def test_compaction_defaults(self, sample_connection_config):
        cfg = OdooBoostConfig(connection=sample_connection_config)
        assert cfg.compact_responses is True
        assert cfg.max_response_chars == 40000
        assert cfg.redact_config_secrets is True
        assert cfg.lean_tools is True
        assert cfg.cache_local_scans is True
        assert cfg.max_consecutive_identical_calls == 2
        assert cfg.max_repeated_calls_per_window == 2
        assert cfg.repeated_call_window_size == 12

    def test_compaction_fields_roundtrip(self, sample_connection_config):
        cfg = OdooBoostConfig(
            connection=sample_connection_config,
            compact_responses=False,
            max_response_chars=1000,
            redact_config_secrets=False,
            lean_tools=True,
            cache_local_scans=False,
            max_consecutive_identical_calls=4,
            max_repeated_calls_per_window=3,
            repeated_call_window_size=10,
        )
        restored = OdooBoostConfig.model_validate(json.loads(cfg.model_dump_json()))
        assert restored.compact_responses is False
        assert restored.max_response_chars == 1000
        assert restored.redact_config_secrets is False
        assert restored.lean_tools is True
        assert restored.cache_local_scans is False
        assert restored.max_consecutive_identical_calls == 4
        assert restored.max_repeated_calls_per_window == 3
        assert restored.repeated_call_window_size == 10

    def test_negative_identical_call_limit_is_rejected(self, sample_connection_config):
        with pytest.raises(ValidationError):
            OdooBoostConfig(
                connection=sample_connection_config,
                max_consecutive_identical_calls=-1,
            )

    def test_security_fields_roundtrip(self, sample_connection_config):
        cfg = OdooBoostConfig(
            connection=sample_connection_config,
            mcp_token="tok",
            readonly=True,
            allowed_roots=["/srv/addons"],
            allow_external_local_paths=True,
        )
        restored = OdooBoostConfig.model_validate(json.loads(cfg.model_dump_json()))
        assert restored.mcp_token == "tok"
        assert restored.readonly is True
        assert restored.allowed_roots == ["/srv/addons"]
        assert restored.allow_external_local_paths is True


# ---------------------------------------------------------------------------
# Settings (find / load / save)
# ---------------------------------------------------------------------------


class TestFindConfigPath:
    def test_finds_in_current_dir(self, tmp_path):
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text("{}")
        assert find_config_path(tmp_path) == cfg_file

    def test_finds_in_parent(self, tmp_path):
        cfg_file = tmp_path / CONFIG_FILENAME
        cfg_file.write_text("{}")
        child = tmp_path / "sub" / "deep"
        child.mkdir(parents=True)
        assert find_config_path(child) == cfg_file

    def test_returns_none_when_missing(self, tmp_path):
        assert find_config_path(tmp_path) is None


class TestLoadSaveConfig:
    def test_save_and_load(self, tmp_path, sample_config):
        path = tmp_path / CONFIG_FILENAME
        save_config(sample_config, path)
        loaded = load_config(path)
        assert loaded.connection.url == sample_config.connection.url
        assert loaded.odoo_version == sample_config.odoo_version

    def test_load_missing_raises(self, tmp_path):
        with pytest.raises(FileNotFoundError):
            load_config(tmp_path / "nonexistent.json")

    def test_save_default_path(self, tmp_path, sample_config, monkeypatch):
        monkeypatch.chdir(tmp_path)
        result = save_config(sample_config)
        assert result.name == CONFIG_FILENAME
        assert result.exists()

    def test_save_restricts_permissions_on_posix(self, tmp_path, sample_config):
        import os
        import stat

        path = tmp_path / CONFIG_FILENAME
        save_config(sample_config, path)
        if os.name == "posix":
            mode = stat.S_IMODE(path.stat().st_mode)
            assert mode == 0o600
