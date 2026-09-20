"""Compatibility is explicit, inherited and isolated between target releases."""

from __future__ import annotations

import json

import pytest

from odoo_boost.guidelines.composer import (
    compose_agent_guidelines,
    compose_guidelines,
    install_guideline_references,
)
from odoo_boost.mcp_server.tools.search_docs import search_docs
from odoo_boost.versions import (
    VERSION_REGISTRY,
    VersionSpec,
    detect_version,
    get_version_profile,
    normalize_version,
)


@pytest.mark.parametrize(
    ("raw", "series"),
    [
        ("17", "17.0"),
        (" 18.0.1.2.3 ", "18.0"),
        ("19.0+e", "19.0"),
        ("20.0alpha", None),
        ("20.0", "20.0"),
        ("saas~18.2", "18.2"),
        ("18.2", "18.2"),
        ("latest", None),
        ("../18", None),
        (None, None),
    ],
)
def test_normalization(raw, series):
    assert normalize_version(raw) == series


def test_detection_uses_series_then_build():
    assert detect_version({"server_serie": "saas~18.2", "server_version": "18.0"}) == "18.2"
    assert detect_version({"server_version": "18.0+e"}) == "18.0"
    assert detect_version({"server_serie": "unknown", "server_version": "19.0"}) == "19.0"
    assert detect_version({}) is None


@pytest.mark.parametrize(
    ("version", "tag", "modifiers", "display", "route"),
    [
        ("14.0", "tree", "attrs/states", "name_get", "json"),
        ("15.0", "tree", "attrs/states", "name_get", "json"),
        ("16.0", "tree", "attrs/states", "name_get", "json"),
        ("17.0", "tree", "inline expressions", "_compute_display_name", "json"),
        ("18.0", "list", "inline expressions", "_compute_display_name", "json"),
        ("19.0", "list", "inline expressions", "_compute_display_name", "jsonrpc"),
    ],
)
def test_version_isolation(version, tag, modifiers, display, route):
    profile = get_version_profile(version)
    assert profile is not None
    assert profile.features["list_view_tag"] == tag
    assert profile.features["view_modifiers"] == modifiers
    assert profile.features["display_name"] == display
    assert profile.features["json_route_type"] == route
    content = compose_agent_guidelines(version, ".agents/skills/guidelines")
    assert f"list_view_tag: {tag}" in content
    assert f"json_route_type: {route}" in content
    with pytest.raises(TypeError):
        profile.features["list_view_tag"] = "invalid"


@pytest.mark.parametrize("version", [None, "invalid", "20.0", "18.2", "saas~19.1"])
def test_unknown_versions_never_inherit(version, tmp_path):
    assert get_version_profile(version) is None
    for content in (compose_guidelines(version), compose_agent_guidelines(version, "refs")):
        assert "unverified" in content
        assert "Do not assume compatibility" in content
    installed = install_guideline_references(tmp_path, version)
    assert not any(path.parent.name == "versions" for path in installed)
    result = json.loads(search_docs("orm", version=version or "unknown"))
    assert result["results"] == []
    assert result["supported"] is False


def test_all_registered_notes_are_packaged(tmp_path):
    for series in VERSION_REGISTRY:
        profile = get_version_profile(series)
        installed = install_guideline_references(tmp_path / series, series)
        assert tmp_path / series / profile.guideline_file in installed


def test_new_registration_does_not_require_consumer_changes(monkeypatch, tmp_path):
    """A future release needs registration and a note, not consumer branches."""
    from odoo_boost.guidelines import composer

    previous = get_version_profile("19.0")
    monkeypatch.setitem(
        VERSION_REGISTRY,
        "20.0",
        VersionSpec(
            parent="19.0",
            features={"json_route_type": "future-test-type"},
            doc_paths={"orm": "/future/orm.html"},
        ),
    )
    original_read = composer._read_resource
    monkeypatch.setattr(
        composer,
        "_read_resource",
        lambda path: (
            "## Odoo 20 test-only delta" if path == "versions/v20.md" else original_read(path)
        ),
    )
    profile = get_version_profile("20.0")
    assert profile.features["list_view_tag"] == "list"
    assert get_version_profile("19.0") == previous
    assert "future-test-type" in compose_agent_guidelines("20.0", "refs")
    assert tmp_path / "versions/v20.md" in install_guideline_references(tmp_path, "20.0")
    result = json.loads(search_docs("orm", version="20.0"))
    assert result["results"][0]["url"].endswith("/20.0/future/orm.html")


def test_invalid_inheritance_fails_loudly(monkeypatch):
    monkeypatch.setitem(VERSION_REGISTRY, "20.0", VersionSpec(parent="20.0"))
    with pytest.raises(ValueError, match="Cyclic"):
        get_version_profile("20.0")


def test_docs_use_config_without_runtime_call(server_context, monkeypatch):
    server_context.config.odoo_version = "17.0"
    monkeypatch.setattr(
        server_context.connection, "get_version", lambda: pytest.fail("runtime call")
    )
    result = json.loads(search_docs("views"))
    assert result["version"] == "17.0"
    assert result["results"][0]["url"].endswith(
        "/17.0/developer/reference/user_interface/view_architectures.html"
    )


def test_doc_path_changes_are_isolated():
    for version, suffix in [("18.0", "external_api.html"), ("19.0", "external_rpc_api.html")]:
        result = json.loads(search_docs("web_services", version=version))
        assert result["results"][0]["url"].endswith(suffix)
