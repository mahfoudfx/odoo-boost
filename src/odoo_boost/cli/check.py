"""odoo-boost check – test connection to an Odoo instance."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from odoo_boost.config.schema import OdooConnection as OdooConnectionConfig
from odoo_boost.config.settings import load_config
from odoo_boost.connection.factory import create_connection

console = Console()


def check(
    url: Annotated[str | None, typer.Option(help="Odoo server URL")] = None,
    database: Annotated[str | None, typer.Option(help="Database name")] = None,
    username: Annotated[str | None, typer.Option(help="Username")] = None,
    password: Annotated[str | None, typer.Option(help="Password or API key")] = None,
    config: Annotated[
        Path | None, typer.Option("--config", "-c", help="Path to odoo-boost.json")
    ] = None,
) -> None:
    """Test the connection to an Odoo instance."""
    # Build connection config from CLI flags or config file
    if url and database:
        conn_cfg = OdooConnectionConfig(
            url=url,
            database=database,
            username=username or "admin",
            password=password or "admin",
        )
    else:
        try:
            cfg = load_config(config)
        except FileNotFoundError:
            console.print(
                "[red]No connection details provided and no odoo-boost.json found.[/]\n"
                "Pass --url and --database, or run 'odoo-boost install' first."
            )
            raise typer.Exit(1) from None
        conn_cfg = cfg.connection

    conn = create_connection(conn_cfg)

    # 1. Version check
    console.print("\n[bold]Checking Odoo connection...[/]\n")
    try:
        version_info = conn.get_version()
    except Exception as exc:
        console.print(f"[red]Failed to reach server:[/] {exc}")
        raise typer.Exit(1) from None

    server_version = version_info.get("server_version", "unknown")
    console.print(f"  Server version: [cyan]{server_version}[/]")

    # 2. Authentication
    try:
        uid = conn.authenticate()
    except Exception as exc:
        console.print(f"  [red]Authentication failed:[/] {exc}")
        raise typer.Exit(1) from None

    console.print(f"  Authenticated as UID: [cyan]{uid}[/]")

    # 3. Quick module count
    try:
        module_count = conn.search_count("ir.module.module", [("state", "=", "installed")])
        console.print(f"  Installed modules: [cyan]{module_count}[/]")
    except Exception:
        console.print("  [yellow]Could not count installed modules[/]")

    # 4. Summary table
    table = Table(title="Connection Summary")
    table.add_column("Property", style="bold")
    table.add_column("Value")
    table.add_row("URL", conn_cfg.url)
    table.add_row("Database", conn_cfg.database)
    table.add_row("Username", conn_cfg.username)
    table.add_row("Server Version", server_version)
    table.add_row("Protocol", conn_cfg.protocol)
    console.print()
    console.print(table)
    console.print("\n[green]Connection successful![/]\n")
