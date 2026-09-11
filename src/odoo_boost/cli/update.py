"""odoo-boost update – re-sync generated files from saved config."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from odoo_boost.agents import AGENTS
from odoo_boost.agents.reconcile import clean_orphaned_agent_files, find_orphaned_agent_files
from odoo_boost.config.settings import load_config

console = Console()


def update(
    config: Annotated[
        Path | None, typer.Option("--config", "-c", help="Path to odoo-boost.json")
    ] = None,
    keep_orphans: Annotated[
        bool,
        typer.Option(
            "--keep-orphans",
            help="Keep files from removed agents instead of cleaning them up.",
        ),
    ] = False,
    yes: Annotated[
        bool,
        typer.Option(
            "--yes",
            "-y",
            help="Skip confirmation prompt when cleaning orphaned files.",
        ),
    ] = False,
) -> None:
    """Re-generate agent files from existing odoo-boost.json config."""
    try:
        cfg = load_config(config)
    except FileNotFoundError:
        console.print("[red]No odoo-boost.json found. Run 'odoo-boost install' first.[/]")
        raise typer.Exit(1) from None

    project_path = Path(cfg.project_path).resolve() if cfg.project_path != "." else Path.cwd()

    console.print("[bold]Updating Odoo Boost files…[/]\n")

    # Clean up orphaned files from removed agents
    orphans = find_orphaned_agent_files(cfg, project_path)
    if orphans and not keep_orphans:
        removed_agent_names = ", ".join(sorted(orphans.keys()))
        should_keep = False
        if not yes:
            should_keep = typer.confirm(
                f"Found files from removed agents ({removed_agent_names}). Keep them?",
                default=False,
            )
        if not should_keep:
            cleaned = clean_orphaned_agent_files(orphans, project_path)
            for p in cleaned:
                try:
                    rel = p.relative_to(project_path)
                except ValueError:
                    rel = p
                console.print(f"  [red]Removed orphaned[/] {rel}")

    if not cfg.generate_mcp:
        console.print("  [dim]MCP config generation disabled[/]")
    if not cfg.generate_ai_files:
        console.print("  [dim]AI file generation disabled[/]")

    for agent_id in cfg.agents:
        agent_cls = AGENTS.get(agent_id)
        if agent_cls is None:
            console.print(f"  [yellow]Unknown agent '{agent_id}', skipping.[/]")
            continue

        agent = agent_cls(config=cfg, project_path=project_path)
        created = agent.install()
        for p in created:
            try:
                rel = p.relative_to(project_path)
            except ValueError:
                rel = p
            console.print(f"  [green]Updated[/] {rel}")

    console.print("\n[green]Update complete![/]")
