"""Install and inspect the optional official Odoo Language Server."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from odoo_boost.odoo_ls import OFFICIAL_REPOSITORY, find_odoo_ls, install_official_odoo_ls

odoo_ls_app = typer.Typer(help="Manage the optional official Odoo Language Server.")
console = Console()


@odoo_ls_app.command("status")
def status() -> None:
    """Show whether Odoo LS is available and report its version."""
    binary = find_odoo_ls()
    if binary is None:
        console.print(
            f"[yellow]Odoo LS is not installed.[/] Official source: {OFFICIAL_REPOSITORY}"
        )
        raise typer.Exit(1)
    result = subprocess.run([str(binary), "--version"], capture_output=True, text=True, timeout=10)
    version = (result.stdout or result.stderr).strip()
    console.print(f"[green]Installed:[/] {binary}")
    console.print(f"[green]Version:[/] {version or 'unknown'}")


@odoo_ls_app.command("install")
def install(
    destination: Annotated[
        Path | None,
        typer.Option("--destination", "-d", help="Installation directory (default: user bin)."),
    ] = None,
    version: Annotated[
        str | None,
        typer.Option("--version", help="Official release tag; default is latest stable."),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", help="Replace an existing managed binary."),
    ] = False,
) -> None:
    """Install a platform binary from the official odoo/odoo-ls GitHub release."""
    try:
        path, tag = install_official_odoo_ls(destination, version=version, force=force)
    except Exception as exc:
        console.print(f"[red]Odoo LS installation failed:[/] {exc}")
        raise typer.Exit(1) from None
    console.print(f"[green]Installed official Odoo LS {tag}:[/] {path}")
    console.print("Set [cyan]odoo_ls_path[/] to this path if it is not on PATH.")
