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
from odoo_boost.cli.gitignore import ignore_entry, managed_entries, update_gitignore
from odoo_boost.config.schema import OdooBoostConfig, OdooConnection
from odoo_boost.config.settings import save_config
from odoo_boost.connection.factory import create_connection
from odoo_boost.mcp_launcher import detect_wsl_distro, is_loopback_host, is_wsl
from odoo_boost.offline_docs import (
    OfflineDocsError,
    available_packs,
    cached_docs,
    download_docs,
    install_checkout,
    install_pack,
)
from odoo_boost.versions import detect_version, get_version_profile, version_guidance

console = Console()


def _detect_project_venv(project_path: Path) -> str | None:
    """Prefer an activated VENV; ignore unrelated launcher environments."""
    active = os.environ.get("VIRTUAL_ENV")
    if active and (Path(active) / "pyvenv.cfg").is_file():
        return str(Path(active).resolve())
    if sys.prefix != sys.base_prefix:
        interpreter_venv = Path(sys.prefix).resolve()
        if interpreter_venv.is_relative_to(project_path.resolve()):
            return str(interpreter_venv)
    return None


def _choose_offline_docs(version: str | None) -> Path | None:
    """Offer an exact-version local, packaged, or online documentation source."""
    if not version or get_version_profile(version) is None:
        console.print(
            "  [dim]Offline docs: choose a supported version later with 'odoo-boost docs'.[/]"
        )
        return None
    cached = cached_docs(version)
    choices = ["online", "path", "download"]
    if cached is not None:
        choices.insert(1, "cached")
    if version in available_packs():
        choices.insert(1, "packed")
    console.print("\n[bold]Step 4a:[/] Offline Odoo documentation\n")
    choice = Prompt.ask(
        "  Documentation source (online links, existing path, packaged snapshot, or download)",
        choices=choices,
        default="online",
    )
    try:
        if choice == "cached":
            return cached
        if choice == "packed":
            return install_pack(version)
        if choice == "download":
            return download_docs(version)
        if choice == "path":
            path = Path(Prompt.ask("  Existing Odoo documentation checkout path"))
            return install_checkout(path, version)
    except (OfflineDocsError, OSError) as exc:
        console.print(
            f"  [yellow]Offline docs unavailable: {exc}. Online links remain available.[/]"
        )
    return None


def install(
    skip_dev_tools: Annotated[
        bool,
        typer.Option(
            "--skip-dev-tools",
            help="Do not install Odoo LS and pylint-odoo during setup.",
        ),
    ] = False,
    gitignore: Annotated[
        bool | None,
        typer.Option("--gitignore/--no-gitignore", help="Add generated paths to .gitignore."),
    ] = None,
    skip_docs: Annotated[
        bool,
        typer.Option(
            "--skip-docs", help="Use online documentation links without the offline-docs prompt."
        ),
    ] = False,
    target_odoo_version: Annotated[
        str | None,
        typer.Option(
            "--target-odoo-version",
            help="Target source series when it differs from the connected server.",
        ),
    ] = None,
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
    if target_odoo_version:
        target_profile = get_version_profile(target_odoo_version)
        if target_profile is None:
            console.print(f"  [red]Unsupported target Odoo version: {target_odoo_version}[/]")
            raise typer.Exit(1)
        odoo_version = target_profile.series
        console.print(f"  Target source version: [cyan]{odoo_version}[/]")
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
    active_venv = _detect_project_venv(project_path)
    docs_path = None if skip_docs else _choose_offline_docs(odoo_version)

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
    allowed_roots: list[str] = [str(project_path)]
    if generate_mcp:
        console.print("\n[bold]Step 4c:[/] Tool hardening (optional)\n")
        readonly = Confirm.ask(
            "  Enable readonly mode? (blocks mutating execute_method calls)",
            default=False,
        )
        console.print("  Local file tools are restricted to the project root by default.")

    # --- Step 5: Generate config + files ---
    console.print("\n[bold]Step 5:[/] Generating files…\n")

    config = OdooBoostConfig(
        connection=conn_cfg,
        odoo_version=odoo_version,
        agents=selected_agents,
        project_path=str(project_path),
        venv_path=active_venv,
        odoo_docs_path=str(docs_path) if docs_path else None,
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
    generated_paths = [config_path]

    # Install each agent
    for agent_id in selected_agents:
        agent_cls = AGENTS[agent_id]
        agent = agent_cls(config=config, project_path=project_path)
        created = agent.install()
        generated_paths.extend(created)
        for p in created:
            try:
                rel = p.relative_to(project_path)
            except ValueError:
                rel = p
            console.print(f"  [green]Created[/] {rel}")

    # Claude Code also creates the shared AGENTS.md file.
    if "claude_code" in selected_agents and generate_ai_files:
        generated_paths.append(project_path / "AGENTS.md")
    entries = {ignore_entry(project_path, path) for path in generated_paths}
    existing = (
        set((project_path / ".gitignore").read_text(encoding="utf-8").splitlines())
        if (project_path / ".gitignore").is_file()
        else set()
    )
    proposed = entries - existing - managed_entries(project_path)
    if proposed:
        console.print("\n[bold]Suggested .gitignore entries:[/]")
        for entry in sorted(proposed):
            console.print(f"  {entry}", markup=False)
        if gitignore is True or (
            gitignore is None and Confirm.ask("  Add these entries to .gitignore?", default=False)
        ):
            update_gitignore(project_path, add=proposed)
            console.print("  [green]Updated[/] .gitignore")

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
