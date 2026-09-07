"""odoo-boost update – re-sync generated files from saved config."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from odoo_boost.agents import AGENTS
from odoo_boost.config.settings import load_config

console = Console()


def update(
    config: Annotated[
        Path | None, typer.Option("--config", "-c", help="Path to odoo-boost.json")
    ] = None,
) -> None:
    """Re-generate agent files from existing odoo-boost.json config."""
    try:
        cfg = load_config(config)
    except FileNotFoundError:
        console.print("[red]No odoo-boost.json found. Run 'odoo-boost install' first.[/]")
        raise typer.Exit(1) from None

    project_path = Path(cfg.project_path).resolve() if cfg.project_path != "." else Path.cwd()

    console.print("[bold]Updating Odoo Boost files…[/]\n")

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
