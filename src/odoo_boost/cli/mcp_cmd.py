"""odoo-boost mcp – start the MCP server (stdio or HTTP)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from odoo_boost.config.settings import load_config
from odoo_boost.mcp_launcher import build_http_url, is_loopback_host

console = Console(stderr=True)

_TRANSPORTS = {
    "stdio": "stdio",
    "http": "streamable-http",
    "streamable-http": "streamable-http",
    "sse": "sse",
}


def mcp(
    config: Annotated[
        Path | None, typer.Option("--config", "-c", help="Path to odoo-boost.json")
    ] = None,
    transport: Annotated[
        str,
        typer.Option(
            "--transport",
            "-t",
            help="Transport: stdio (default), http, streamable-http or sse.",
        ),
    ] = "stdio",
    host: Annotated[
        str | None,
        typer.Option("--host", help="Bind host for HTTP transports (default: config value)."),
    ] = None,
    port: Annotated[
        int | None,
        typer.Option("--port", help="Bind port for HTTP transports (default: config value)."),
    ] = None,
    token: Annotated[
        str | None,
        typer.Option(
            "--token",
            help="Bearer token required from HTTP clients (or $ODOO_BOOST_MCP_TOKEN).",
        ),
    ] = None,
) -> None:
    """Start the MCP server.

    Uses stdio by default. For a cross-OS setup (e.g. an IDE on Windows
    connecting to a server inside WSL) run with ``--transport http`` and point
    the IDE at the printed URL.
    """
    resolved = _TRANSPORTS.get(transport.lower())
    if resolved is None:
        console.print(f"[red]Unknown transport '{transport}'.[/] Choose from: stdio, http, sse.")
        raise typer.Exit(1)

    try:
        cfg = load_config(config)
    except FileNotFoundError:
        console.print("[red]No odoo-boost.json found. Run 'odoo-boost install' first.[/]")
        raise typer.Exit(1) from None

    if resolved == "stdio":
        from odoo_boost.mcp_server.server import create_mcp_server

        console.print("[dim]Starting Odoo Boost MCP server (stdio)…[/]")
        create_mcp_server(cfg).run(transport="stdio")
        return

    bind_host = host or cfg.mcp_host
    bind_port = port or cfg.mcp_port

    resolved_token = token or os.environ.get("ODOO_BOOST_MCP_TOKEN") or cfg.mcp_token
    if not is_loopback_host(bind_host) and not resolved_token:
        console.print(
            f"[red]Refusing to bind {bind_host}:{bind_port} without authentication.[/]\n"
            "Pass [cyan]--token <secret>[/], set [cyan]ODOO_BOOST_MCP_TOKEN[/], or configure "
            "[cyan]mcp_token[/] in odoo-boost.json. Use 127.0.0.1 for local-only access."
        )
        raise typer.Exit(1)

    cfg = cfg.model_copy(
        update={
            "mcp_host": bind_host,
            "mcp_port": bind_port,
            "mcp_token": resolved_token,
        }
    )

    from odoo_boost.mcp_server.server import create_mcp_server

    server = create_mcp_server(cfg)

    if resolved_token:
        console.print("[green]Bearer token authentication enabled.[/]")

    if resolved == "streamable-http":
        console.print(
            f"[dim]Odoo Boost MCP server listening on "
            f"[cyan]{build_http_url(cfg)}[/] "
            f"(bind {bind_host})[/]"
        )
        server.run(transport="streamable-http", host=bind_host, port=bind_port)
    else:
        console.print(
            f"[dim]Odoo Boost MCP server listening on "
            f"[cyan]http://{bind_host}:{bind_port}/sse[/] (bind {bind_host})[/]"
        )
        server.run(transport="sse", host=bind_host, port=bind_port)
