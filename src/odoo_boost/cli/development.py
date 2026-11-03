"""CLI entry points for development diagnostics and environment profiles."""

from __future__ import annotations

import json
from pathlib import Path

import typer

from odoo_boost.config import load_config, save_config
from odoo_boost.test_runner import run_tests
from odoo_boost.validation import diagnose, validation_plan

profiles_app = typer.Typer(help="List or select named connection profiles.")


@profiles_app.command("list")
def profiles_list() -> None:
    config = load_config()
    typer.echo(
        json.dumps(
            {
                "active": config.active_profile,
                "profiles": [
                    {"name": name, "readonly": config.profile_readonly.get(name, True)}
                    for name in config.profiles
                ],
            },
            indent=2,
        )
    )


@profiles_app.command("use")
def profiles_use(name: str) -> None:
    config = load_config()
    if name not in config.profiles:
        raise typer.BadParameter(f"Unknown profile: {name}")
    config.active_profile = name
    config.connection = config.profiles[name].model_copy(deep=True)
    config.readonly = config.profile_readonly.get(name, True)
    save_config(config, config.config_path)
    typer.echo(f"Active profile: {name}. Restart MCP servers to apply the change.")


def diagnose_cmd(path: Path = Path("."), odoo_ls: bool = False) -> None:
    """Print unified diagnostics as JSON; partial coverage is explicit."""
    try:
        config = load_config()
    except FileNotFoundError:
        config = None
    from odoo_boost.mcp_server.context import ServerContext, bound_context

    if config:
        from odoo_boost.connection.factory import create_connection

        with bound_context(ServerContext(create_connection(config.connection), config)):
            result = diagnose(path.resolve(), config.odoo_version, odoo_ls)
    else:
        result = diagnose(path.resolve(), include_odoo_ls=odoo_ls)
    typer.echo(json.dumps(result, indent=2))
    if result["status"] == "failed":
        raise typer.Exit(1)


def changed_checks(path: Path = Path("."), base: str = "HEAD") -> None:
    """Recommend checks for tracked and untracked changes."""
    typer.echo(json.dumps(validation_plan(path.resolve(), base), indent=2))


def test_cmd(addon_path: Path, test_tags: str, database: str) -> None:
    """Run focused tests against the configured disposable test database."""
    result = run_tests(load_config(), addon_path.resolve(), test_tags, database)
    typer.echo(json.dumps(result, indent=2))
    if result["status"] != "passed":
        raise typer.Exit(1)
