from __future__ import annotations

from typing import Annotated

import typer

from odoo_boost.__version__ import __version__

app = typer.Typer(
    name="odoo-boost",
    help="AI coding agents with deep introspection into running Odoo instances.",
    no_args_is_help=True,
)


def _version_callback(value: bool) -> None:
    if value:
        typer.echo(f"odoo-boost {__version__}")
        raise typer.Exit()


@app.callback()
def _main(
    version: Annotated[
        bool,
        typer.Option(
            "--version",
            "-v",
            help="Show version and exit.",
            callback=_version_callback,
            is_eager=True,
        ),
    ] = False,
) -> None:
    """Odoo Boost - AI coding agents for Odoo development."""


# Import commands so they register with the app
from odoo_boost.cli.check import check  # noqa: E402
from odoo_boost.cli.install import install  # noqa: E402
from odoo_boost.cli.lint_cmd import lint  # noqa: E402
from odoo_boost.cli.mcp_cmd import mcp  # noqa: E402
from odoo_boost.cli.update import update  # noqa: E402

app.command()(check)
app.command()(install)
app.command()(update)
app.command()(lint)
app.command(name="mcp")(mcp)


def main() -> None:
    app()
