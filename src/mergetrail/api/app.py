"""FastAPI app that exposes a local git review as JSON."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from mergetrail import __version__
from mergetrail.git import (
    FileChange,
    GitCommandError,
    GitError,
    GitTimeoutError,
    NotARepositoryError,
    Review,
    build_review,
    file_hunks,
)

DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765
STATIC_DIR = Path(__file__).resolve().parents[1] / "static"


@dataclass(frozen=True)
class ServerContext:
    """The repo and refs this process is serving."""

    repo: Path
    base: str | None = None
    head: str = "HEAD"


def create_app(context: ServerContext) -> FastAPI:
    app = FastAPI(
        title="MergeTrail",
        version=__version__,
        description="Local JSON API for a three-dot branch review.",
    )
    app.state.context = context

    @app.exception_handler(NotARepositoryError)
    async def not_a_repo(_request: Request, exc: NotARepositoryError) -> JSONResponse:
        return JSONResponse({"detail": str(exc)}, status_code=400)

    @app.exception_handler(GitTimeoutError)
    async def git_timeout(_request: Request, exception: GitTimeoutError) -> JSONResponse:
        return JSONResponse({"detail": str(exception)}, status_code=504)

    @app.exception_handler(GitError)
    async def git_error(_request: Request, exc: GitError) -> JSONResponse:
        status = 400 if isinstance(exc, GitCommandError) else 500
        return JSONResponse({"detail": str(exc)}, status_code=status)

    @app.get("/review", response_model=Review)
    async def review() -> Review:
        """File list and resolved refs. Hunks are fetched per file."""
        return await _load_review(context)

    @app.get("/files", response_model=list[FileChange])
    async def files() -> list[FileChange]:
        loaded = await _load_review(context)
        return loaded.files

    @app.get("/files/{path:path}", response_model=FileChange)
    async def file(path: str) -> FileChange:
        """One file's patch, split into hunks."""
        loaded = await _load_review(context)
        match = next((changed for changed in loaded.files if changed.path == path), None)
        if match is None:
            raise HTTPException(status_code=404, detail=f"{path} is not in this review")
        if match.is_binary:
            return match
        hunks = await file_hunks(
            context.repo,
            loaded.merge_base,
            loaded.head_sha,
            match.path,
            match.old_path,
        )
        return match.model_copy(update={"hunks": hunks})

    _mount_ui(app)
    return app


async def _load_review(context: ServerContext) -> Review:
    return await build_review(context.repo, base=context.base, head=context.head)


def _mount_ui(app: FastAPI) -> None:
    """Serve the built Vite app without stealing the JSON routes."""
    index = STATIC_DIR / "index.html"
    if not index.is_file():
        @app.get("/")
        async def ui_missing() -> JSONResponse:
            return JSONResponse(
                {"detail": "Review UI is not built. From ui/, run npm run build."},
                status_code=503,
            )

        return

    app.mount("/", StaticFiles(directory=STATIC_DIR, html=True), name="ui")
