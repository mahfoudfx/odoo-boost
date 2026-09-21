"""Registered Odoo series and inherited compatibility deltas.

Only explicitly registered series are supported. A future or SaaS series must
never inherit compatibility merely because its number is greater.
"""

from __future__ import annotations

import re
from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType
from typing import Any

DOC_BASE = "https://www.odoo.com/documentation"


@dataclass(frozen=True)
class VersionSpec:
    """One release's changes; paths are relative to its documentation root."""

    parent: str | None = None
    features: Mapping[str, str] = field(default_factory=dict)
    doc_paths: Mapping[str, str] = field(default_factory=dict)


# Define common behavior once in the baseline; each subsequent entry only changes
# what differs. Explicit parents allow a new branch without implicit inheritance.
VERSION_REGISTRY: dict[str, VersionSpec] = {
    "14.0": VersionSpec(
        features={
            "list_view_tag": "tree",
            "view_modifiers": "attrs/states",
            "relational_commands": "tuple commands",
            "asset_declaration": "XML asset templates",
            "display_name": "name_get",
            "json_route_type": "json",
            "search_group_attributes": "expand/string supported",
        },
        # Legacy documentation has a different layout. Use its verified index
        # where a deep link has not been verified, rather than a modern URL.
        doc_paths={
            "orm": "/developer/reference.html",
            "fields": "/developer/reference.html",
            "module": "/developer/reference.html",
            "views": "/developer/reference.html",
            "actions": "/developer/reference.html",
            "security": "/developer/reference.html",
            "controllers": "/developer/reference.html",
            "data": "/developer/reference.html",
            "web_services": "/developer/reference.html",
            "qweb": "/developer/reference.html",
            "reports": "/developer/reference.html",
            "mixins": "/developer/reference.html",
            "assets": "/developer/reference.html",
            "owl": "/developer/reference.html",
            "testing": "/developer/reference/addons/testing.html",
        },
    ),
    "15.0": VersionSpec(
        parent="14.0",
        features={"relational_commands": "Command", "asset_declaration": "manifest assets"},
        doc_paths={
            "orm": "/developer/reference/backend/orm.html",
            "fields": "/developer/reference/backend/orm.html#fields",
            "security": "/developer/reference/backend/security.html",
            "controllers": "/developer/reference/backend/http.html",
            "data": "/developer/reference/backend/data.html",
            "web_services": "/developer/reference/external_api.html",
            "testing": "/developer/reference/backend/testing.html",
            "module": "/developer/tutorials/getting_started.html",
            "views": "/developer/reference/backend/views.html",
            "actions": "/developer/reference/backend/actions.html",
            "qweb": "/developer/reference/frontend/qweb.html",
            "reports": "/developer/reference/backend/reports.html",
            "mixins": "/developer/reference/backend/mixins.html",
            "assets": "/developer/reference/frontend/assets.html",
            "owl": "/developer/reference/frontend/owl_components.html",
        },
    ),
    "16.0": VersionSpec(parent="15.0"),
    "17.0": VersionSpec(
        parent="16.0",
        features={"view_modifiers": "inline expressions", "display_name": "_compute_display_name"},
        doc_paths={
            "views": "/developer/reference/user_interface/view_architectures.html",
            "module": "/developer/tutorials/server_framework_101/01_architecture.html",
        },
    ),
    "18.0": VersionSpec(parent="17.0", features={"list_view_tag": "list"}),
    "19.0": VersionSpec(
        parent="18.0",
        features={"json_route_type": "jsonrpc", "search_group_attributes": "expand/string removed"},
        doc_paths={"web_services": "/developer/reference/external_rpc_api.html"},
    ),
    "20.0": VersionSpec(
        parent="19.0",
        features={
            "domain_composition": "fields.Domain",
            "route_auth": "bearer auth requires bearer_scope",
            "supported_python": "3.12-3.14",
            "minimum_postgresql": "16",
        },
    ),
}


@dataclass(frozen=True)
class VersionProfile:
    """Resolved facts for one registered series, with no mutable shared state."""

    series: str
    features: Mapping[str, str]
    doc_paths: Mapping[str, str]

    @property
    def guideline_file(self) -> str:
        return f"versions/v{self.series.split('.')[0]}.md"

    def documentation_url(self, topic: str, default_path: str) -> str:
        return f"{DOC_BASE}/{self.series}{self.doc_paths.get(topic, default_path)}"


def normalize_version(version: str | None) -> str | None:
    """Parse a major/series, module version or server build without guessing.

    Nonzero minor series (including SaaS) are preserved rather than silently
    treated as a supported on-premise release.
    """
    if not version:
        return None
    match = re.fullmatch(
        r"(?:saas[~-])?(\d{1,3})(?:\.(\d+))?(?:\.\d+)*(?:(?:[+~-].+)|(?:a|b|rc)\d*)?",
        version.strip(),
    )
    if match is None:
        return None
    return f"{int(match[1])}.{int(match[2] or 0)}"


def detect_version(version_info: Mapping[str, Any]) -> str | None:
    """Prefer the server's series; fall back to its build string."""
    for key in ("server_serie", "server_version"):
        value = version_info.get(key)
        if isinstance(value, str) and (series := normalize_version(value)):
            return series
    return None


def get_version_profile(version: str | None) -> VersionProfile | None:
    """Resolve explicit inheritance; unknown versions have no compatibility facts."""
    series = normalize_version(version)
    if series not in VERSION_REGISTRY:
        return None
    assert series is not None
    chain: list[VersionSpec] = []
    seen: set[str] = set()
    current: str | None = series
    while current is not None:
        if current in seen:
            raise ValueError(f"Cyclic Odoo version inheritance: {current}")
        seen.add(current)
        spec = VERSION_REGISTRY[current]
        chain.append(spec)
        current = spec.parent
    features: dict[str, str] = {}
    paths: dict[str, str] = {}
    for spec in reversed(chain):
        features.update(spec.features)
        paths.update(spec.doc_paths)
    return VersionProfile(series, MappingProxyType(features), MappingProxyType(paths))


def version_guidance(version: str | None) -> str:
    """Small effective compatibility summary for prompts and generated files."""
    profile = get_version_profile(version)
    if profile is None:
        label = normalize_version(version) or "unknown"
        return (
            f"Odoo version: {label} (unverified). Use shared guidance only where safe. "
            "Do not assume compatibility with the newest registered release. Inspect "
            "the target source/configuration, or runtime metadata when needed, before "
            "choosing version-specific APIs or syntax."
        )
    rules = "; ".join(f"{key}: {value}" for key, value in profile.features.items())
    return f"Odoo {profile.series} compatibility: {rules}. Target-version rules override generic examples."
