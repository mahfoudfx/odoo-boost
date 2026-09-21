"""odoo-boost install – interactive wizard to set up Odoo Boost."""

from __future__ import annotations

import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt

from odoo_boost.agents import AGENTS, ALL_AGENT_IDS
from odoo_boost.config.schema import OdooBoostConfig, OdooConnection
from odoo_boost.config.settings import CONFIG_FILENAME, save_config
from odoo_boost.connection.factory import create_connection
from odoo_boost.mcp_launcher import detect_wsl_distro, is_loopback_host, is_wsl
from odoo_boost.versions import detect_version, get_version_profile, version_guidance

console = Console()


def install(
    skip_dev_tools: Annotated[
        bool,
        typer.Option(
            "--skip-dev-tools",
            help="Do not install Odoo LS and pylint-odoo during setup.",
        ),
    ] = False,
) -> None:
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
    password_default = os.environ.get("ODOO_BOOST_PASSWORD", "admin")
    password = Prompt.ask("  Password / API key", default=password_default, password=True)

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
    odoo_version = detect_version(version_info)
    console.print(f"  Detected Odoo version: [cyan]{odoo_version}[/]")
    if get_version_profile(odoo_version) is None:
        console.print(version_guidance(odoo_version), markup=False)

    from odoo_boost.odoo_ls import find_odoo_ls

    ls_bin = find_odoo_ls()
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
    install_dev_tools = not skip_dev_tools and Confirm.ask(
        "  Install Odoo LS and the OCA pylint-odoo checker?",
        default=True,
    )

    if not generate_mcp and not generate_ai_files:
        console.print("  [dim]Both disabled — only odoo-boost.json will be created.[/]")

    project_path = Path.cwd()

    # --- Step 4b: MCP transport / platform ---
    mcp_transport: Literal["stdio", "http"] = "stdio"
    mcp_target: Literal["auto", "native", "wsl"] = "native"
    wsl_distro: str | None = None
    mcp_host = "127.0.0.1"
    mcp_port = 8765
    mcp_token: str | None = None

    if generate_mcp:
        console.print("\n[bold]Step 4b:[/] MCP transport\n")

        wsl = is_wsl()
        detected_distro = detect_wsl_distro()
        if wsl:
            console.print(f"  [dim]WSL detected ({detected_distro or 'default'}).[/]")

        open_from_windows = Confirm.ask(
            "  Do you also open this project from IDEs running on Windows?",
            default=wsl,
        )
        if open_from_windows:
            mcp_target = "auto"
            wsl_distro = detected_distro or Prompt.ask("  WSL distribution", default="Ubuntu")

        use_http = Confirm.ask(
            "  Use HTTP transport instead of stdio? (shared server, best for cross-OS)",
            default=False,
        )
        if use_http:
            mcp_transport = "http"
            mcp_host = Prompt.ask("  HTTP bind host", default="127.0.0.1")
            port_raw = Prompt.ask("  HTTP port", default="8765")
            try:
                mcp_port = int(port_raw)
            except ValueError:
                console.print("  [yellow]Invalid port, using 8765.[/]")
                mcp_port = 8765

            if not is_loopback_host(mcp_host):
                console.print(
                    "  [yellow]Non-loopback bind requires a bearer token "
                    "(it will be embedded in generated configs).[/]"
                )
                mcp_token = Prompt.ask("  MCP bearer token", password=True)

    # --- Step 4c: Tool hardening (opt-in) ---
    readonly = False
    allowed_roots: list[str] = []
    if generate_mcp:
        console.print("\n[bold]Step 4c:[/] Tool hardening (optional)\n")
        readonly = Confirm.ask(
            "  Enable readonly mode? (blocks mutating execute_method calls)",
            default=False,
        )
        if Confirm.ask(
            "  Restrict local file tools to the project root?",
            default=False,
        ):
            allowed_roots = [str(project_path)]

    # --- Step 5: Generate config + files ---
    console.print("\n[bold]Step 5:[/] Generating files…\n")

    config = OdooBoostConfig(
        connection=conn_cfg,
        odoo_version=odoo_version,
        agents=selected_agents,
        project_path=str(project_path),
        generate_mcp=generate_mcp,
        generate_ai_files=generate_ai_files,
        mcp_transport=mcp_transport,
        mcp_target=mcp_target,
        wsl_distro=wsl_distro,
        mcp_host=mcp_host,
        mcp_port=mcp_port,
        mcp_token=mcp_token,
        readonly=readonly,
        allowed_roots=allowed_roots,
    )

    # Save config
    config_path = save_config(config)
    console.print(f"  [green]Created[/] {config_path.relative_to(project_path)}")
    console.print(
        "  [yellow]Credentials are stored in plaintext — keep odoo-boost.json out of version control.[/]"
    )
    _ensure_gitignore(project_path)

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

    if install_dev_tools:
        console.print("\n[bold]Step 6:[/] Installing Odoo development analysis tools…\n")
        _install_development_tools()

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


def _ensure_gitignore(project_path: Path) -> None:
    """Add odoo-boost.json to an existing .gitignore (best-effort)."""
    gitignore = project_path / ".gitignore"
    if not gitignore.is_file():
        return
    try:
        content = gitignore.read_text(encoding="utf-8")
    except OSError:  # pragma: no cover - defensive
        return
    if any(line.strip() == CONFIG_FILENAME for line in content.splitlines()):
        return
    separator = "" if content.endswith("\n") else "\n"
    gitignore.write_text(
        f"{content}{separator}\n# Odoo Boost\n{CONFIG_FILENAME}\n", encoding="utf-8"
    )
    console.print(f"  [green]Updated[/] .gitignore (added {CONFIG_FILENAME})")


def _install_development_tools() -> None:
    """Install optional diagnostics without making project setup depend on them."""
    from odoo_boost.odoo_ls import find_odoo_ls, install_official_odoo_ls

    if find_odoo_ls():
        console.print("  [green]Odoo LS already available.[/]")
    else:
        try:
            path, version = install_official_odoo_ls()
            console.print(f"  [green]Installed official Odoo LS {version}:[/] {path}")
        except Exception as exc:
            console.print(f"  [yellow]Could not install Odoo LS:[/] {exc}")

    if importlib.util.find_spec("pylint_odoo"):
        console.print("  [green]pylint-odoo already available.[/]")
        return
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "pylint-odoo>=10.0.11"],
            check=True,
            timeout=300,
        )
        console.print("  [green]Installed pylint-odoo.[/]")
    except (OSError, subprocess.SubprocessError) as exc:
        console.print(f"  [yellow]Could not install pylint-odoo:[/] {exc}")
