"""MCP tool: search_docs – Odoo documentation links by topic/version."""

from __future__ import annotations

import re

from odoo_boost.mcp_server.tools._common import json_response

# Static map of documentation topics to URLs.
# This covers the most common Odoo dev doc sections.
_DOC_BASE = "https://www.odoo.com/documentation"

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


def _normalize_version(version: str) -> str:
    """Extract the major version from user input ('18.0.1' -> '18')."""
    match = re.match(r"\s*(\d+)", version or "")
    return match.group(1) if match else "18"


def search_docs(
    topic: str = "",
    version: str = "",
) -> str:
    """Search Odoo documentation and return relevant links.

    Args:
        topic: Topic keyword (e.g. 'orm', 'views', 'security', 'owl', 'testing').
               Leave empty to list all available topics.
        version: Odoo version (e.g. '17.0', '18.0', '19.0'). Defaults to latest.
    """
    ver = _normalize_version(version)

    if not topic:
        # Return all topics
        all_topics = [
            {"topic": k, "title": v["title"], "description": v["description"]}
            for k, v in _TOPICS.items()
        ]
        return json_response({"available_topics": all_topics})

    # Search by keyword
    matches = []
    topic_lower = topic.lower()
    for key, info in _TOPICS.items():
        if (
            topic_lower in key
            or topic_lower in info["title"].lower()
            or topic_lower in info["description"].lower()
        ):
            url = f"{_DOC_BASE}/{ver}{info['path']}"
            matches.append(
                {
                    "topic": key,
                    "title": info["title"],
                    "url": url,
                    "description": info["description"],
                }
            )

    if not matches:
        return json_response(
            {
                "message": f"No documentation found for '{topic}'.",
                "available_topics": list(_TOPICS.keys()),
            }
        )

    return json_response({"results": matches})
