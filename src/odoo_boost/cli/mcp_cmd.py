"""odoo-boost mcp – start MCP server via stdio."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from odoo_boost.config.settings import load_config

console = Console(stderr=True)


def mcp(
    config: Annotated[
        Path | None, typer.Option("--config", "-c", help="Path to odoo-boost.json")
    ] = None,
) -> None:
    """Start the MCP server (stdio transport)."""
    try:
        cfg = load_config(config)
    except FileNotFoundError:
        console.print("[red]No odoo-boost.json found. Run 'odoo-boost install' first.[/]")
        raise typer.Exit(1) from None

    from odoo_boost.mcp_server.server import create_mcp_server

    console.print("[dim]Starting Odoo Boost MCP server…[/]")
    server = create_mcp_server(cfg)
    server.run(transport="stdio")
