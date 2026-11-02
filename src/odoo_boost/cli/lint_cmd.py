"""odoo-boost lint – run OCA standards linting on local Odoo code."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from odoo_boost.diagnostics import run_lint

console = Console()


def lint(
    path: Annotated[Path, typer.Argument(help="File or addon directory to lint")] = Path("."),
    strict: Annotated[
        bool, typer.Option("--strict", help="Fail on warnings as well as errors")
    ] = False,
) -> None:
    """Run OCA coding standard checks on Odoo modules (using pylint-odoo)."""
    console.print(f"[bold cyan]Running Odoo Boost Linter on:[/] {path}\n")

    res = run_lint(path.resolve())

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

    groups = (
        ("errors", "[red]Error[/]"),
        ("warnings", "[yellow]Warning[/]"),
        ("conventions", "[blue]Convention[/]"),
        ("issues", ""),
    )
    for key, label in groups:
        for issue in res.get(key, []):
            fallback_label = (
                "[red]Error[/]" if issue.get("type") == "error" else "[yellow]Warning[/]"
            )
            table.add_row(
                label or fallback_label,
                issue.get("symbol", issue.get("code", "")),
                f"{issue.get('path', issue.get('file', ''))}:{issue.get('line', '')}",
                issue.get("message", ""),
            )

    console.print(table)

    if (
        res.get("success") is False
        or res.get("errors_count", 0) > 0
        or (strict and total_issues > 0)
    ):
        raise typer.Exit(1)
