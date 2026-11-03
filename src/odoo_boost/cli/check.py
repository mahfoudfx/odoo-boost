"""odoo-boost check – show local setup and test the Odoo connection."""

from __future__ import annotations

import sys
from pathlib import Path
from typing import Annotated, Any

import typer
from rich.console import Console
from rich.table import Table

from odoo_boost.__version__ import __version__
from odoo_boost.config.schema import OdooBoostConfig
from odoo_boost.config.schema import OdooConnection as OdooConnectionConfig
from odoo_boost.config.settings import find_config_path, load_config
from odoo_boost.connection.factory import create_connection
from odoo_boost.local_paths import resolve_path, venv_python
from odoo_boost.offline_docs import INDEX_FILE, METADATA_FILE

console = Console()


def _print_local_summary(
    cfg: OdooBoostConfig | None, config_path: Path | None, *, source_label: str = "CLI flags"
) -> None:
    """Report useful local facts without starting Odoo or scanning source trees."""
    table = Table(title="Odoo Boost Environment")
    table.add_column("Property", style="bold")
    table.add_column("Value")
    table.add_row("Odoo Boost", __version__)
    table.add_row("Python", f"{sys.version_info.major}.{sys.version_info.minor} ({sys.executable})")
    table.add_row(
        "Configuration", str(config_path.resolve()) if cfg and config_path else source_label
    )
    if cfg is not None:
        project = cfg.project_root
        table.add_row("Project", str(project))
        table.add_row("Target Odoo", cfg.odoo_version or "not configured")
        table.add_row("Environment profile", cfg.active_profile or "default connection")
        table.add_row("Readonly methods", str(cfg.readonly))
        if cfg.venv_path:
            venv = resolve_path(cfg.venv_path, project)
            state = "active" if Path(sys.prefix).resolve() == venv else "different interpreter"
            if not (venv / "pyvenv.cfg").is_file() or not venv_python(venv).is_file():
                state = "missing or invalid"
            table.add_row("Project VENV", f"{venv} ({state})")
        if cfg.odoo_conf_path:
            conf = resolve_path(cfg.odoo_conf_path, project)
            table.add_row("Odoo config", f"{conf} ({'found' if conf.is_file() else 'missing'})")
        if cfg.odoo_source_path:
            source = resolve_path(cfg.odoo_source_path, project)
            table.add_row("Odoo source", f"{source} ({'found' if source.is_dir() else 'missing'})")
        if cfg.odoo_docs_path:
            docs = resolve_path(cfg.odoo_docs_path, project)
            indexed = (docs / INDEX_FILE).is_file() and (docs / METADATA_FILE).is_file()
            table.add_row("Offline docs", f"{docs} ({'indexed' if indexed else 'index missing'})")
        table.add_row("MCP transport", cfg.mcp_transport)
        if cfg.agents:
            table.add_row("Agents", ", ".join(cfg.agents))
    console.print(table)


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
    """Show local setup and test the connection to an Odoo instance."""
    # Build connection config from CLI flags or config file
    cfg = None
    config_path = None
    if url and database:
        conn_cfg = OdooConnectionConfig(
            url=url,
            database=database,
            username=username or "admin",
            password=password or "admin",
        )
    else:
        try:
            config_path = config or find_config_path()
            cfg = load_config(config_path)
        except FileNotFoundError:
            _print_local_summary(None, None, source_label="not found")
            console.print(
                "[red]No connection details provided and no odoo-boost.json found.[/]\n"
                "Pass --url and --database, or run 'odoo-boost install' first."
            )
            raise typer.Exit(1) from None
        conn_cfg = cfg.connection

    _print_local_summary(cfg, config_path)
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
        if not ok:
            raise typer.Exit(1)
        return

    command = build_stdio_command(cfg, cfg.project_root)
    ok, detail = _probe_stdio(command)
    style = "green" if ok else "red"
    console.print(f"  [{style}]{detail}[/]")
    console.print(f"  [dim]{' '.join(command)}[/]")
    if not ok:
        raise typer.Exit(1)


def _validate_initialize_response(payload: Any) -> tuple[bool, str]:
    """Accept only the matching JSON-RPC response with a valid initialize result."""
    from mcp.types import InitializeResult
    from mcp_types.version import HANDSHAKE_PROTOCOL_VERSIONS
    from pydantic import ValidationError

    if (
        not isinstance(payload, dict)
        or payload.get("jsonrpc") != "2.0"
        or type(payload.get("id")) is not int
        or payload["id"] != 1
    ):
        return False, "Unexpected MCP initialize response"
    if "error" in payload:
        error = payload["error"]
        if isinstance(error, dict):
            return False, f"MCP initialize failed ({error.get('code')}): {error.get('message')}"
        return False, "MCP initialize failed with an invalid error response"
    try:
        result = InitializeResult.model_validate(payload.get("result"))
    except ValidationError:
        return False, "MCP server returned an invalid initialize result"
    if result.protocol_version not in HANDSHAKE_PROTOCOL_VERSIONS:
        return False, f"Unsupported protocol version from the MCP server: {result.protocol_version}"
    return True, "MCP server responded to initialize"


def _initialize_request() -> dict[str, Any]:
    """Build the same MCP handshake for stdio and HTTP probes."""
    return {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2025-06-18",
            "capabilities": {},
            "clientInfo": {"name": "odoo-boost-check", "version": "1"},
        },
    }


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

    initialize = _initialize_request()
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

    return _validate_initialize_response(payload)


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
    initialize = _initialize_request()
    try:
        response = httpx.post(url, timeout=timeout, headers=headers, json=initialize)
    except Exception as exc:
        return False, f"HTTP MCP server unreachable: {exc}"
    if response.status_code in (401, 403):
        return False, f"HTTP MCP server rejected the configured token (HTTP {response.status_code})"
    if response.status_code != 200:
        return False, f"HTTP endpoint did not accept MCP initialize (HTTP {response.status_code})"
    if "text/event-stream" in response.headers.get("content-type", ""):
        stream = response.text.replace("\r\n", "\n").replace("\r", "\n")
        for event in stream.split("\n\n"):
            data = "\n".join(
                line[5:].removeprefix(" ")
                for line in event.splitlines()
                if line.startswith("data:")
            )
            if not data:
                continue
            try:
                payload = json.loads(data)
            except json.JSONDecodeError:
                return False, "HTTP MCP stream returned invalid JSON"
            if isinstance(payload, dict) and payload.get("id") == 1:
                return _validate_initialize_response(payload)
        return False, "HTTP MCP stream returned no initialize response"
    try:
        payload = response.json()
    except (json.JSONDecodeError, ValueError):
        return False, "HTTP MCP server returned an invalid initialize response"
    return _validate_initialize_response(payload)
