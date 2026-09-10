"""Logging configuration for Odoo Boost.

All log records go to **stderr**. This is critical for the stdio MCP transport,
where stdout is reserved for the JSON-RPC protocol stream.
"""

from __future__ import annotations

import logging
import os
import sys

LOGGER_NAME = "odoo_boost"
DEFAULT_LEVEL = "WARNING"
_configured = False


def configure_logging(level: str | None = None) -> int:
    """Configure the ``odoo_boost`` logger and return the effective level.

    Resolution order: explicit *level* argument, ``ODOO_BOOST_LOG_LEVEL``
    environment variable, then ``WARNING``. Unknown values fall back to
    ``WARNING`` rather than raising, so a bad env var cannot break startup.
    """
    global _configured

    requested = (level or os.environ.get("ODOO_BOOST_LOG_LEVEL") or DEFAULT_LEVEL).upper()
    numeric = getattr(logging, requested, None)
    if not isinstance(numeric, int):
        numeric = logging.WARNING

    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(numeric)

    if not _configured:
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
        logger.addHandler(handler)
        logger.propagate = False
        _configured = True

    return numeric
