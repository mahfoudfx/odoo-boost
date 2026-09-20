"""MCP tool: list_routes – website pages and URL rewrites."""

from __future__ import annotations

import logging
import xmlrpc.client

from odoo_boost.mcp_server.context import get_connection
from odoo_boost.mcp_server.tools._common import json_response

logger = logging.getLogger(__name__)


def list_routes(
    filter_url: str = "",
    limit: int = 100,
) -> str:
    """List website pages and URL rewrites visible through the ORM.

    This does not enumerate Python controller decorators. Source status reports
    unavailable website models and permission failures explicitly.

    Args:
        filter_url: Optional substring filter on URL path.
        limit: Maximum number of routes to return (default 100).
    """
    conn = get_connection()

    routes: list[dict] = []
    unavailable: dict[str, str] = {}

    # 1. Try website.page (if website module is installed)
    try:
        domain: list = []
        if filter_url:
            domain.append(("url", "ilike", filter_url))

        pages = conn.search_read(
            "website.page",
            domain=domain,
            fields=["name", "url", "is_published", "website_id"],
            limit=limit,
            order="url",
        )
        for p in pages:
            routes.append(
                {
                    "type": "page",
                    "url": p.get("url", ""),
                    "name": p.get("name", ""),
                    "published": p.get("is_published", False),
                }
            )
    except xmlrpc.client.Fault as exc:
        logger.debug("website.page unavailable: %s", exc)
        unavailable["website.page"] = (
            "access denied" if "AccessError" in exc.faultString else "model unavailable"
        )

    # 2. Try ir.http routing rules (available on all versions)
    try:
        domain = []
        if filter_url:
            domain.append("|")
            domain.append(("url_from", "ilike", filter_url))
            domain.append(("url_to", "ilike", filter_url))

        url_rewrites = conn.search_read(
            "website.rewrite",
            domain=domain,
            fields=["name", "url_from", "url_to"],
            limit=limit,
        )
        for r in url_rewrites:
            routes.append(
                {
                    "type": "rewrite",
                    "url": r.get("url_from", ""),
                    "target": r.get("url_to", ""),
                    "name": r.get("name", ""),
                }
            )
    except xmlrpc.client.Fault as exc:
        logger.debug("website.rewrite unavailable: %s", exc)
        unavailable["website.rewrite"] = (
            "access denied" if "AccessError" in exc.faultString else "model unavailable"
        )

    result = {
        "total": len(routes),
        "routes": routes,
        "unavailable": unavailable,
        "complete": not unavailable,
        "scope": "website.page and website.rewrite ORM records only; Python controllers excluded",
    }
    return json_response(result)
