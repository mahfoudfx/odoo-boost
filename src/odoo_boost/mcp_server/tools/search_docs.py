"""MCP tool: search_docs – Odoo documentation links by topic/version."""

from __future__ import annotations

from contextlib import suppress

from odoo_boost.mcp_server.context import get_context
from odoo_boost.mcp_server.tools._common import json_response
from odoo_boost.versions import DOC_BASE, get_version_profile, normalize_version, version_guidance

# Static map of documentation topics to URLs.
# This covers the most common Odoo dev doc sections.
_DOC_BASE = DOC_BASE

_TOPICS: dict[str, dict[str, str]] = {
    "orm": {
        "title": "ORM API",
        "path": "/developer/reference/backend/orm.html",
        "description": "Model definitions, fields, CRUD, domains, recordsets.",
    },
    "fields": {
        "title": "Fields Reference",
        "path": "/developer/reference/backend/orm.html#fields",
        "description": "Field types, attributes, compute, related, default.",
    },
    "views": {
        "title": "Views",
        "path": "/developer/reference/backend/views.html",
        "description": "Form, tree/list, kanban, search, pivot, graph views.",
    },
    "actions": {
        "title": "Actions",
        "path": "/developer/reference/backend/actions.html",
        "description": "Window, server, URL, client actions.",
    },
    "security": {
        "title": "Security",
        "path": "/developer/reference/backend/security.html",
        "description": "Access rights, record rules, groups, ir.model.access.",
    },
    "controllers": {
        "title": "Controllers / HTTP",
        "path": "/developer/reference/backend/http.html",
        "description": "HTTP controllers, routing, JSON-RPC, requests.",
    },
    "qweb": {
        "title": "QWeb Templates",
        "path": "/developer/reference/backend/qweb.html",
        "description": "QWeb template engine, t-if, t-foreach, t-call.",
    },
    "owl": {
        "title": "OWL JavaScript Framework",
        "path": "/developer/reference/frontend/owl_components.html",
        "description": "OWL components, hooks, lifecycle, templating.",
    },
    "assets": {
        "title": "Assets & Bundles",
        "path": "/developer/reference/frontend/assets.html",
        "description": "JavaScript/CSS assets, asset bundles, inheritance.",
    },
    "testing": {
        "title": "Testing",
        "path": "/developer/reference/backend/testing.html",
        "description": "Python tests (TransactionCase, HttpCase), JS tests.",
    },
    "data": {
        "title": "Data Files",
        "path": "/developer/reference/backend/data.html",
        "description": "XML/CSV data files, noupdate, ref, eval.",
    },
    "reports": {
        "title": "Reports",
        "path": "/developer/reference/backend/reports.html",
        "description": "QWeb reports, PDF generation, report actions.",
    },
    "module": {
        "title": "Module Structure",
        "path": "/developer/tutorials/server_framework_101/01_architecture.html",
        "description": "Module manifest, directory structure, __manifest__.py.",
    },
    "web_services": {
        "title": "External API / Web Services",
        "path": "/developer/reference/external_api.html",
        "description": "XML-RPC, JSON-RPC external API.",
    },
    "mixins": {
        "title": "Mixins",
        "path": "/developer/reference/backend/mixins.html",
        "description": "mail.thread, mail.activity.mixin, portal.mixin.",
    },
}


def search_docs(
    topic: str = "",
    version: str = "",
) -> str:
    """Look up curated documentation links offline; does not fetch page contents.

    Args:
        topic: Topic keyword (e.g. 'orm', 'views', 'security', 'owl', 'testing').
               Leave empty to list all available topics.
        version: Target series; defaults to configured project version, never to latest.
    """
    if not version:
        with suppress(RuntimeError):
            version = get_context().config.odoo_version or ""
    profile = get_version_profile(version)
    metadata = {
        "version": normalize_version(version),
        "supported": profile is not None,
        "lookup": "curated_links",
    }
    if profile is None:
        metadata["warning"] = version_guidance(version)

    if not topic:
        # Return all topics
        all_topics = [
            {"topic": k, "title": v["title"], "description": v["description"]}
            for k, v in _TOPICS.items()
        ]
        return json_response({**metadata, "available_topics": all_topics})

    # Search by keyword
    matches = []
    topic_lower = topic.lower()
    for key, info in _TOPICS.items():
        if (
            topic_lower in key
            or topic_lower in info["title"].lower()
            or topic_lower in info["description"].lower()
        ):
            if profile is None:
                continue
            url = profile.documentation_url(key, info["path"])
            matches.append(
                {
                    "topic": key,
                    "title": info["title"],
                    "url": url,
                    "description": info["description"],
                }
            )

    if profile is None:
        return json_response({**metadata, "results": [], "documentation_root": _DOC_BASE})

    if not matches:
        return json_response(
            {
                **metadata,
                "message": f"No documentation found for '{topic}'.",
                "available_topics": list(_TOPICS.keys()),
            }
        )

    return json_response({**metadata, "results": matches})
