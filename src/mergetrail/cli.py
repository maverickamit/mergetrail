"""Command line entry point for MergeTrail."""

from __future__ import annotations

import asyncio
from pathlib import Path

import typer
import uvicorn

from mergetrail import __version__
from mergetrail.api import ServerContext, create_app
from mergetrail.api.app import DEFAULT_HOST, DEFAULT_PORT
from mergetrail.git import GitError, NotARepositoryError, build_review, discover_repository

app = typer.Typer(
    add_completion=False,
    help="Understand and review large pull requests in your browser.",
)


def _version_option(value: bool) -> None:
    if value:
        typer.echo(f"mergetrail {__version__}")
        raise typer.Exit()


@app.command()
def main(
    base: str | None = typer.Option(
        None,
        "--base",
        help="Base branch or commit. Defaults to origin/HEAD, then main/master/develop/trunk.",
    ),
    head: str = typer.Option("HEAD", "--head", help="Branch or commit under review."),
    repo: Path | None = typer.Option(
        None,
        "--repo",
        exists=True,
        file_okay=False,
        resolve_path=True,
        help="Repository to open. Defaults to the current directory.",
    ),
    port: int = typer.Option(DEFAULT_PORT, "--port", min=1, max=65535),
    open_browser: bool = typer.Option(
        True,
        "--open/--no-open",
        help="Open the review URL in a browser.",
    ),
    _version: bool = typer.Option(
        False,
        "--version",
        callback=_version_option,
        is_eager=True,
        help="Show the version and exit.",
    ),
) -> None:
    """Serve a local JSON API for the current branch versus `--base`."""
    try:
        repo_path, resolved_base, resolved_head = asyncio.run(
            _prepare_review(repo or Path.cwd(), base, head)
        )
    except NotARepositoryError as error:
        typer.secho(str(error), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from error
    except GitError as error:
        typer.secho(str(error), err=True, fg=typer.colors.RED)
        raise typer.Exit(code=1) from error

    origin = f"http://{DEFAULT_HOST}:{port}"
    typer.echo(f"Reviewing {resolved_base}...{resolved_head} in {repo_path}")
    typer.echo(f"GET {origin}/review")
    typer.echo(f"GET {origin}/files")
    typer.echo(f"GET {origin}/files/{{path}}")

    if open_browser:
        typer.launch(f"{origin}/review")

    uvicorn.run(
        create_app(ServerContext(repo=repo_path, base=resolved_base, head=resolved_head)),
        host=DEFAULT_HOST,
        port=port,
        log_level="info",
    )


async def _prepare_review(
    start: Path, base: str | None, head: str
) -> tuple[Path, str, str]:
    """Resolve the repo and fail fast if git cannot build a review."""
    repo_path = await discover_repository(start)
    review = await build_review(repo_path, base=base, head=head)
    return repo_path, review.base, review.head
