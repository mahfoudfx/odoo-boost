"""Install and inspect the optional official Odoo Language Server."""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from odoo_boost.odoo_ls import (
    OFFICIAL_REPOSITORY,
    find_odoo_ls,
    install_official_odoo_ls,
    is_usable,
    latest_release_tag,
    typeshed_dir,
)

odoo_ls_app = typer.Typer(help="Manage the optional official Odoo Language Server.")
console = Console()


def binary_version(binary: Path) -> str | None:
    """Return the bare release number reported by ``binary --version``."""
    try:
        result = subprocess.run(
            [str(binary), "--version"], capture_output=True, text=True, timeout=10
        )
    except (OSError, subprocess.SubprocessError):
        return None
    words = (result.stdout or result.stderr).split()
    return words[-1] if words else None


@odoo_ls_app.command("status")
def status() -> None:
    """Show whether Odoo LS is installed, usable and up to date."""
    binary = find_odoo_ls()
    if binary is None:
        console.print(
            f"[yellow]Odoo LS is not installed.[/] Official source: {OFFICIAL_REPOSITORY}\n"
            "Run [cyan]odoo-boost odoo-ls install[/]."
        )
        raise typer.Exit(1)
    version = binary_version(binary)
    console.print(f"[green]Installed:[/] {binary}")
    console.print(f"[green]Version:[/] {version or 'unknown'}")
    try:
        latest: str | None = latest_release_tag()
    except Exception:
        latest = None
    if latest is None:
        console.print("[dim]Latest release: unknown (GitHub not reachable)[/]")
    elif version == latest:
        console.print(f"[green]Latest release:[/] {latest} (up to date)")
    else:
        console.print(
            f"[yellow]Latest release:[/] {latest}. "
            "Run [cyan]odoo-boost odoo-ls install[/] to update."
        )
    if not is_usable(binary):
        console.print(
            f"[red]Unusable:[/] typeshed stubs missing at {typeshed_dir(binary)}; "
            "Odoo LS stops during initialization and reports no diagnostics.\n"
            "Run [cyan]odoo-boost odoo-ls install[/] to repair it."
        )
        raise typer.Exit(1)
    console.print(f"[green]Typeshed stubs:[/] {typeshed_dir(binary)}")


@odoo_ls_app.command("install")
def install(
    destination: Annotated[
        Path | None,
        typer.Option(
            "--destination",
            "-d",
            help="Install directory for the binary and its stubs (default: user data dir).",
        ),
    ] = None,
    version: Annotated[
        str | None,
        typer.Option("--version", help="Official release tag; default is latest stable."),
    ] = None,
    force: Annotated[
        bool,
        typer.Option("--force", help="Reinstall even when the release is already installed."),
    ] = False,
) -> None:
    """Install, update or repair Odoo LS from the official odoo/odoo-ls release."""
    try:
        result = install_official_odoo_ls(destination, version=version, force=force)
    except Exception as exc:
        console.print(f"[red]Odoo LS installation failed:[/] {exc}")
        raise typer.Exit(1) from None
    if result.changed:
        console.print(f"[green]Installed official Odoo LS {result.tag}:[/] {result.path}")
    else:
        console.print(f"[green]Odoo LS {result.tag} is already installed:[/] {result.path}")
    if result.link is not None:
        console.print(f"[green]Linked on PATH:[/] {result.link}")
    if find_odoo_ls() != result.path.resolve():
        console.print(
            f"Another Odoo LS comes first on PATH; set [cyan]odoo_ls_path[/] to {result.path} "
            "to use this one."
        )
