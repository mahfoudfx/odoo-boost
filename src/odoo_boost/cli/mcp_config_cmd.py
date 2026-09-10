"""odoo-boost mcp-config – regenerate MCP configs for a specific platform."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from odoo_boost.agents import AGENTS
from odoo_boost.config.schema import OdooBoostConfig
from odoo_boost.config.settings import load_config
from odoo_boost.mcp_launcher import build_http_url, build_stdio_command

console = Console()

_PLATFORMS = ["auto", "native", "windows", "http"]


def mcp_config(
    config: Annotated[
        Path | None, typer.Option("--config", "-c", help="Path to odoo-boost.json")
    ] = None,
    platform: Annotated[
        str,
        typer.Option(
            "--platform",
            "-p",
            help="Target platform: auto (native + windows companion), native, windows or http.",
        ),
    ] = "auto",
    agents: Annotated[
        str | None,
        typer.Option("--agents", help="Comma-separated agent ids (default: all in config)."),
    ] = None,
) -> None:
    """Regenerate only the MCP config files for a specific platform."""
    if platform not in _PLATFORMS:
        console.print(
            f"[red]Unknown platform '{platform}'.[/] Choose from: {', '.join(_PLATFORMS)}."
        )
        raise typer.Exit(1)

    try:
        cfg = load_config(config)
    except FileNotFoundError:
        console.print("[red]No odoo-boost.json found. Run 'odoo-boost install' first.[/]")
        raise typer.Exit(1) from None

    project_path = Path(cfg.project_path).resolve() if cfg.project_path != "." else Path.cwd()

    selected = [a.strip() for a in agents.split(",") if a.strip()] if agents else list(cfg.agents)

    effective = _effective_config(cfg, platform)
    transport = effective.mcp_transport

    if transport == "http":
        console.print(f"  HTTP endpoint: [cyan]{build_http_url(effective)}[/]")
        if effective.mcp_token:
            console.print(
                "  [yellow]Bearer token embedded in generated configs — "
                "keep them out of version control.[/]"
            )
    else:
        command = build_stdio_command(effective, project_path)
        console.print(f"  stdio command: [cyan]{' '.join(command)}[/]")

    console.print()
    for agent_id in selected:
        agent_cls = AGENTS.get(agent_id)
        if agent_cls is None:
            console.print(f"  [yellow]Unknown agent '{agent_id}', skipping.[/]")
            continue

        agent = agent_cls(config=effective, project_path=project_path)
        paths = agent.write_all_mcp_configs() if platform == "auto" else [agent.write_mcp_config()]
        for path in paths:
            console.print(f"  [green]Wrote[/] {_relative(path, project_path)}")

    console.print("\n[green]MCP config regenerated![/]")


def _effective_config(cfg: OdooBoostConfig, platform: str) -> OdooBoostConfig:
    """Return a config copy with the platform overrides applied."""
    updates: dict[str, object] = {}
    if platform == "native":
        updates = {"mcp_transport": "stdio", "mcp_target": "native"}
    elif platform == "windows":
        updates = {"mcp_transport": "stdio", "mcp_target": "wsl"}
    elif platform == "http":
        updates = {"mcp_transport": "http"}
    return cfg.model_copy(update=updates)


def _relative(path: Path, root: Path) -> Path | str:
    try:
        return path.relative_to(root)
    except ValueError:
        return path
