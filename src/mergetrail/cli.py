"""Command line entry point for MergeTrail."""

from __future__ import annotations

import typer

from mergetrail import __version__

app = typer.Typer(
    add_completion=False,
    help="Understand and review large pull requests in your browser.",
)


@app.command()
def main() -> None:
    """Report the installed version."""
    typer.echo(f"mergetrail {__version__}")
