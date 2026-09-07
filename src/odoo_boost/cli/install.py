"""odoo-boost install – interactive wizard to set up Odoo Boost."""

from __future__ import annotations

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from odoo_boost.agents import AGENTS, ALL_AGENT_IDS
from odoo_boost.config.schema import OdooBoostConfig, OdooConnection
from odoo_boost.config.settings import save_config
from odoo_boost.connection.factory import create_connection

console = Console()


def install() -> None:
    """Interactive wizard: configure connection, detect version, select agents, generate files."""
    console.print(
        Panel.fit(
            "[bold cyan]Odoo Boost – Install Wizard[/]\n"
            "Set up your Odoo project with AI coding agent support.",
            border_style="cyan",
        )
    )

    # --- Step 1: Connection details ---
    console.print("\n[bold]Step 1:[/] Odoo connection details\n")

    url = Prompt.ask("  Odoo URL", default="http://localhost:8069")
    database = Prompt.ask("  Database name")
    username = Prompt.ask("  Username", default="admin")
    password = Prompt.ask("  Password / API key", default="admin", password=True)

    conn_cfg = OdooConnection(
        url=url,
        database=database,
        username=username,
        password=password,
    )

    # --- Step 2: Test connection & detect version ---
    console.print("\n[bold]Step 2:[/] Testing connection…\n")

    conn = create_connection(conn_cfg)
    try:
        version_info = conn.get_version()
        server_version = version_info.get("server_version", "unknown")
        console.print(f"  Server version: [cyan]{server_version}[/]")
    except Exception as exc:
        console.print(f"  [red]Failed to reach server:[/] {exc}")
        raise typer.Exit(1) from None

    try:
        uid = conn.authenticate()
        console.print(f"  Authenticated as UID: [cyan]{uid}[/]")
    except Exception as exc:
        console.print(f"  [red]Authentication failed:[/] {exc}")
        raise typer.Exit(1) from None

    # Detect Odoo version series (e.g. "17.0", "18.0")
    odoo_version = version_info.get("server_serie", server_version.split("-")[0])
    console.print(f"  Detected Odoo version: [cyan]{odoo_version}[/]")

    import shutil

    ls_bin = shutil.which("odoo-ls")
    if ls_bin:
        console.print(f"  Detected Odoo Language Server: [green]{ls_bin}[/]")
    else:
        console.print(
            "  Odoo Language Server: [dim]not on PATH (using built-in pure-Python AST scanner)[/]"
        )

    # --- Step 3: Select agents ---
    console.print("\n[bold]Step 3:[/] Select AI agents to configure\n")

    for i, (aid, acls) in enumerate(AGENTS.items(), 1):
        console.print(f"  {i}. {acls.display_name} ({aid})")

    console.print()
    selection = Prompt.ask(
        "  Enter agent numbers (comma-separated) or 'all'",
        default="all",
    )

    if selection.strip().lower() == "all":
        selected_agents = list(ALL_AGENT_IDS)
    else:
        ids_list = list(AGENTS.keys())
        selected_agents = []
        for part in selection.split(","):
            part = part.strip()
            try:
                idx = int(part) - 1
                if 0 <= idx < len(ids_list):
                    selected_agents.append(ids_list[idx])
            except ValueError:
                if part in AGENTS:
                    selected_agents.append(part)

    if not selected_agents:
        console.print("[red]No agents selected. Aborting.[/]")
        raise typer.Exit(1)

    console.print(f"  Selected: [cyan]{', '.join(selected_agents)}[/]")

    # --- Step 4: Generation options ---
    console.print("\n[bold]Step 4:[/] Generation options\n")

    generate_mcp = Confirm.ask("  Generate MCP config files?", default=True)
    generate_ai_files = Confirm.ask("  Generate AI guidelines and skill files?", default=True)

    if not generate_mcp and not generate_ai_files:
        console.print("  [dim]Both disabled — only odoo-boost.json will be created.[/]")

    # --- Step 5: Generate config + files ---
    console.print("\n[bold]Step 5:[/] Generating files…\n")

    project_path = Path.cwd()

    config = OdooBoostConfig(
        connection=conn_cfg,
        odoo_version=odoo_version,
        agents=selected_agents,
        project_path=str(project_path),
        generate_mcp=generate_mcp,
        generate_ai_files=generate_ai_files,
    )

    # Save config
    config_path = save_config(config)
    console.print(f"  [green]Created[/] {config_path.relative_to(project_path)}")

    # Install each agent
    for agent_id in selected_agents:
        agent_cls = AGENTS[agent_id]
        agent = agent_cls(config=config, project_path=project_path)
        created = agent.install()
        for p in created:
            try:
                rel = p.relative_to(project_path)
            except ValueError:
                rel = p
            console.print(f"  [green]Created[/] {rel}")

    # --- Done ---
    console.print(
        Panel.fit(
            "[bold green]Installation complete![/]\n\n"
            "Next steps:\n"
            "  1. Start coding with your AI agent\n"
            "  2. The MCP server will auto-start when your agent needs it\n"
            "  3. Run [cyan]odoo-boost check[/] to verify the connection anytime\n"
            "  4. Run [cyan]odoo-boost update[/] to re-sync generated files",
            border_style="green",
        )
    )
