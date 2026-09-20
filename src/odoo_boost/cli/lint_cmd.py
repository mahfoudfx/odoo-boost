"""odoo-boost lint – run OCA standards linting on local Odoo code."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from odoo_boost.mcp_server.tools.lint_odoo_code import lint_odoo_code

console = Console()


def lint(
    path: Annotated[Path, typer.Argument(help="File or addon directory to lint")] = Path("."),
    strict: Annotated[
        bool, typer.Option("--strict", help="Fail on warnings as well as errors")
    ] = False,
) -> None:
    """Run OCA coding standard checks on Odoo modules (using pylint-odoo)."""
    console.print(f"[bold cyan]Running Odoo Boost Linter on:[/] {path}\n")

    res_str = lint_odoo_code(str(path))
    res = json.loads(res_str)

    if not isinstance(res, dict) or res.get("truncated"):
        console.print(
            "[bold red]Linter response was truncated; narrow the input or increase the response budget.[/]"
        )
        raise typer.Exit(1)

    if "error" in res:
        console.print(f"[bold red]Error:[/] {res['error']}")
        raise typer.Exit(1)

    engine = res.get("engine", "unknown")
    console.print(f"[dim]Linter engine: {engine}[/]")

    total_issues = res.get("total_issues", 0)
    if total_issues == 0 and res.get("success") is not False:
        console.print("[bold green]✓ No issues found by the available checks.[/]\n")
        return

    table = Table(title=f"Linter Results ({total_issues} issues found)")
    table.add_column("Type", style="bold")
    table.add_column("Code")
    table.add_column("Location")
    table.add_column("Message")

    # If pylint-odoo output
    if "errors" in res or "warnings" in res or "conventions" in res:
        for err in res.get("errors", []):
            table.add_row(
                "[red]Error[/]",
                err.get("symbol", err.get("code", "")),
                f"{err.get('path', '')}:{err.get('line', '')}",
                err.get("message", ""),
            )
        for warn in res.get("warnings", []):
            table.add_row(
                "[yellow]Warning[/]",
                warn.get("symbol", warn.get("code", "")),
                f"{warn.get('path', '')}:{warn.get('line', '')}",
                warn.get("message", ""),
            )
        for conv in res.get("conventions", []):
            table.add_row(
                "[blue]Convention[/]",
                conv.get("symbol", conv.get("code", "")),
                f"{conv.get('path', '')}:{conv.get('line', '')}",
                conv.get("message", ""),
            )
    elif "issues" in res:
        for issue in res.get("issues", []):
            t_style = "[red]Error[/]" if issue.get("type") == "error" else "[yellow]Warning[/]"
            table.add_row(
                t_style,
                issue.get("code", ""),
                f"{issue.get('file', '')}:{issue.get('line', '')}",
                issue.get("message", ""),
            )

    console.print(table)

    if (
        res.get("success") is False
        or res.get("errors_count", 0) > 0
        or (strict and total_issues > 0)
    ):
        raise typer.Exit(1)
