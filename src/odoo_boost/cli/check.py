"""odoo-boost check – test connection to an Odoo instance."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from odoo_boost.config.schema import OdooBoostConfig
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
    mcp: Annotated[
        bool,
        typer.Option("--mcp", help="Also verify the generated MCP server can start."),
    ] = False,
) -> None:
    """Test the connection to an Odoo instance."""
    # Build connection config from CLI flags or config file
    cfg = None
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

    # 5. Optional MCP launcher verification
    if mcp:
        _check_mcp(cfg, console)


def _check_mcp(cfg: OdooBoostConfig | None, console: Console) -> None:
    """Verify the generated MCP configuration can actually be launched."""
    from odoo_boost.mcp_launcher import build_http_url, build_stdio_command

    if cfg is None:
        console.print(
            "[yellow]--mcp requires an odoo-boost.json config (run 'odoo-boost install').[/]"
        )
        return

    console.print("[bold]Checking MCP configuration...[/]\n")

    if cfg.mcp_transport == "http":
        url = build_http_url(cfg)
        ok, detail = _probe_http(url, token=cfg.mcp_token)
        style = "green" if ok else "red"
        console.print(f"  [{style}]{detail}[/]  ({url})")
        return

    project_path = Path(cfg.project_path).resolve() if cfg.project_path != "." else Path.cwd()
    command = build_stdio_command(cfg, project_path)
    ok, detail = _probe_stdio(command)
    style = "green" if ok else "red"
    console.print(f"  [{style}]{detail}[/]")
    console.print(f"  [dim]{' '.join(command)}[/]")


def _probe_stdio(command: list[str], timeout: float = 20.0) -> tuple[bool, str]:
    """Spawn the stdio server and perform an MCP initialize handshake."""
    import json
    import subprocess
    import threading

    try:
        proc = subprocess.Popen(
            command,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
    except OSError as exc:
        return False, f"Could not start MCP server: {exc}"

    result: dict[str, str] = {}

    def _read() -> None:
        try:
            assert proc.stdout is not None
            result["line"] = proc.stdout.readline()
        except Exception as exc:  # pragma: no cover - defensive
            result["error"] = str(exc)

    reader = threading.Thread(target=_read, daemon=True)
    reader.start()

    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "odoo-boost-check", "version": "1"},
        },
    }
    try:
        assert proc.stdin is not None
        proc.stdin.write(json.dumps(initialize) + "\n")
        proc.stdin.flush()
    except Exception as exc:
        proc.kill()
        return False, f"Could not write to MCP server: {exc}"

    reader.join(timeout)
    proc.kill()

    if "error" in result:
        return False, f"MCP read error: {result['error']}"
    line = result.get("line", "").strip()
    if not line:
        return False, "MCP server did not respond (timeout)"

    try:
        payload = json.loads(line)
    except json.JSONDecodeError:
        return False, f"Invalid MCP response: {line[:120]}"

    if "result" in payload or "error" in payload:
        return True, "MCP server responded to initialize"
    return False, f"Unexpected MCP response: {line[:120]}"


def _probe_http(url: str, timeout: float = 5.0, token: str | None = None) -> tuple[bool, str]:
    """Perform a real Streamable HTTP MCP initialize request."""
    import json

    import httpx

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    initialize = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "odoo-boost-check", "version": "1"},
        },
    }
    try:
        response = httpx.post(url, timeout=timeout, headers=headers, json=initialize)
    except Exception as exc:
        return False, f"HTTP MCP server unreachable: {exc}"
    if response.status_code in (401, 403):
        return False, f"HTTP MCP server rejected the configured token (HTTP {response.status_code})"
    if response.status_code != 200:
        return False, f"HTTP endpoint did not accept MCP initialize (HTTP {response.status_code})"
    if "text/event-stream" in response.headers.get("content-type", ""):
        if '"result"' in response.text or "event: message" in response.text:
            return True, "HTTP MCP server responded to initialize"
        return False, "HTTP MCP stream returned no initialize response"
    try:
        payload = response.json()
    except (json.JSONDecodeError, ValueError):
        return False, "HTTP MCP server returned an invalid initialize response"
    if isinstance(payload, dict) and ("result" in payload or "error" in payload):
        return True, "HTTP MCP server responded to initialize"
    return False, "HTTP MCP server returned an unexpected initialize response"
