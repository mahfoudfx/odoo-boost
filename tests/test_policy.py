"""Tests for odoo_boost.mcp_server.policy (readonly + path confinement)."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from mcp.server.mcpserver.exceptions import ToolError

from odoo_boost.mcp_server.context import ServerContext, reset_context, set_context
from odoo_boost.mcp_server.policy import enforce_method, enforce_path
from odoo_boost.mcp_server.tools.execute_method import execute_method
from odoo_boost.mcp_server.tools.inspect_local_addon import inspect_local_addon


@pytest.fixture()
def policy_config(mock_connection, sample_config):
    """Set the global context with a mutable sample config."""

    def _set(**updates):
        cfg = sample_config.model_copy(update=updates)
        set_context(ServerContext(connection=mock_connection, config=cfg))
        return cfg

    _set()
    yield _set
    reset_context()


class TestEnforceMethod:
    def test_default_allows_mutating(self, policy_config):
        enforce_method("unlink")
        enforce_method("write")
        enforce_method("_private")

    def test_readonly_blocks_mutating(self, policy_config):
        policy_config(readonly=True)
        with pytest.raises(ToolError):
            enforce_method("unlink")
        with pytest.raises(ToolError):
            enforce_method("write")
        with pytest.raises(ToolError):
            enforce_method("_private")

    def test_readonly_allows_reads(self, policy_config):
        policy_config(readonly=True)
        enforce_method("search_read")
        enforce_method("fields_get")

    def test_readonly_blocks_unknown_public_methods(self, policy_config):
        policy_config(readonly=True)
        with pytest.raises(ToolError, match="readonly allowlist"):
            enforce_method("action_mark_paid")


class TestEnforcePath:
    def test_external_paths_require_explicit_opt_in(self, policy_config, tmp_path: Path):
        policy_config(
            project_path=str(tmp_path),
            allowed_roots=[],
            allow_external_local_paths=False,
        )
        with pytest.raises(ToolError):
            enforce_path("/etc/hosts")

    def test_external_path_opt_in_allows_anything(self, policy_config, tmp_path: Path):
        policy_config(allowed_roots=[], allow_external_local_paths=True)
        outside = Path("/etc/hosts")
        assert enforce_path(str(outside)) == outside.resolve()

    def test_allowed_root_permits_inside(self, policy_config, tmp_path: Path):
        policy_config(allowed_roots=[str(tmp_path)])
        assert enforce_path(str(tmp_path / "addon")) == (tmp_path / "addon").resolve()

    def test_allowed_root_rejects_outside(self, policy_config, tmp_path: Path):
        policy_config(allowed_roots=[str(tmp_path)])
        with pytest.raises(ToolError):
            enforce_path("/etc")


class TestToolIntegration:
    def test_execute_method_blocked_in_readonly(self, policy_config):
        policy_config(readonly=True)
        with pytest.raises(ToolError):
            execute_method("res.partner", "unlink", args="[1]")

    def test_execute_method_read_allowed(self, policy_config):
        policy_config(readonly=True)
        result = json.loads(execute_method("res.partner", "fields_get"))
        assert result["method"] == "fields_get"

    def test_inspect_local_addon_confined(self, policy_config, tmp_path: Path):
        policy_config(allowed_roots=[str(tmp_path)])
        with pytest.raises(ToolError):
            inspect_local_addon("/etc")

    def test_inspect_refuses_directory_without_addon_manifest(self, policy_config, tmp_path: Path):
        policy_config(allowed_roots=[str(tmp_path)])
        (tmp_path / "model.py").write_text("from odoo import models\n")
        result = json.loads(inspect_local_addon(str(tmp_path)))
        assert "Refusing broad recursive scan" in result["error"]

    def test_collection_scan_requires_explicit_override(self, policy_config, tmp_path: Path):
        policy_config(allowed_roots=[str(tmp_path)])
        (tmp_path / "model.py").write_text("from odoo import models\n")
        result = json.loads(inspect_local_addon(str(tmp_path), allow_collection_scan=True))
        assert result["python_files_count"] == 1
