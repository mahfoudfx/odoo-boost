"""Shared server context holding the Odoo connection and config."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass

from odoo_boost.config.schema import OdooBoostConfig
from odoo_boost.connection.base import OdooConnection


@dataclass
class ServerContext:
    """Holds connection + config for MCP tool handlers."""

    connection: OdooConnection
    config: OdooBoostConfig


# Context-local singleton set at server start. Using a ContextVar keeps state
# isolated per async task and avoids leaking between tests or server instances.
_ctx: ContextVar[ServerContext | None] = ContextVar("odoo_boost_context", default=None)


def set_context(ctx: ServerContext) -> None:
    _ctx.set(ctx)


@contextmanager
def bound_context(ctx: ServerContext) -> Iterator[None]:
    """Temporarily use one server's context for a handler invocation."""
    token = _ctx.set(ctx)
    try:
        yield
    finally:
        _ctx.reset(token)


def reset_context() -> None:
    """Clear the active context (mainly useful for tests)."""
    _ctx.set(None)


def get_context() -> ServerContext:
    ctx = _ctx.get()
    if ctx is None:
        raise RuntimeError("Server context not initialised.")
    return ctx


def get_connection() -> OdooConnection:
    return get_context().connection
