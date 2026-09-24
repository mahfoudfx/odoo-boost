"""Manage version-matched local Odoo documentation text."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from odoo_boost.config.settings import find_config_path, load_config, save_config
from odoo_boost.offline_docs import (
    OfflineDocsError,
    available_packs,
    cached_docs,
    download_docs,
    install_checkout,
    install_pack,
    search_local_docs,
)
from odoo_boost.versions import normalize_version

docs_app = typer.Typer(help="Install and search versioned offline Odoo documentation.")
console = Console()


@docs_app.command("install")
def docs_install(
    version: Annotated[str, typer.Option("--version", "-v", help="Target Odoo series.")],
    source: Annotated[
        str, typer.Option("--source", help="packed, download, checkout, or archive")
    ] = "packed",
    path: Annotated[
        Path | None, typer.Option("--path", help="Checkout or archive path for that source")
    ] = None,
    cache_dir: Annotated[Path | None, typer.Option("--cache-dir", help="Shared cache root")] = None,
    config: Annotated[
        Path | None, typer.Option("--config", "-c", help="Project odoo-boost.json")
    ] = None,
) -> None:
    """Install only the requested series; reuse its cached content afterward."""
    try:
        if source == "packed":
            root = install_pack(version, cache_dir=cache_dir)
        elif source == "download":
            root = download_docs(version, cache_dir=cache_dir)
        elif source == "checkout" and path is not None:
            root = install_checkout(path, version, cache_dir=cache_dir)
        elif source == "archive" and path is not None:
            root = install_pack(version, cache_dir=cache_dir, pack_path=path)
        else:
            raise OfflineDocsError("Choose packed, download, checkout --path, or archive --path")
    except (OfflineDocsError, OSError) as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(1) from None

    config_path = config or find_config_path()
    if config_path is not None:
        try:
            cfg = load_config(config_path)
            if normalize_version(cfg.odoo_version) == normalize_version(version):
                save_config(cfg.model_copy(update={"odoo_docs_path": str(root)}), config_path)
                console.print(f"Configured offline docs in {config_path}")
            else:
                console.print(
                    "Project Odoo version differs; cache installed without changing project config."
                )
        except (OSError, ValueError) as exc:
            console.print(
                f"[red]Documentation is cached, but project config was not updated: {exc}[/]"
            )
            raise typer.Exit(1) from None
    console.print(f"Odoo {version} documentation ready: {root}")


@docs_app.command("status")
def docs_status(
    version: Annotated[str, typer.Option("--version", "-v", help="Target Odoo series.")],
    cache_dir: Annotated[Path | None, typer.Option("--cache-dir", help="Shared cache root")] = None,
) -> None:
    """Show the current cached revision and locally available packs."""
    try:
        root = cached_docs(version, cache_dir=cache_dir)
    except OfflineDocsError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(1) from None
    console.print(
        json.dumps(
            {"version": version, "cached": str(root) if root else None, "packs": available_packs()}
        )
    )


@docs_app.command("search")
def docs_search(
    query: Annotated[str, typer.Argument(help="Words to find in installed documentation")],
    version: Annotated[str, typer.Option("--version", "-v", help="Target Odoo series.")],
    section: Annotated[
        str, typer.Option("--section", help="all, developer, administration, or applications")
    ] = "all",
    cache_dir: Annotated[Path | None, typer.Option("--cache-dir", help="Shared cache root")] = None,
) -> None:
    """Return up to three short excerpts with source paths and online links."""
    try:
        root = cached_docs(version, cache_dir=cache_dir)
        if root is None:
            raise OfflineDocsError(f"No cached Odoo {version} documentation")
        result = search_local_docs(root, query, version=version, section=section)
    except OfflineDocsError as exc:
        console.print(f"[red]{exc}[/]")
        raise typer.Exit(1) from None
    console.print_json(data=result)
