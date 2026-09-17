"""Run git as a subprocess: no shell, fixed config, hard timeout."""

from __future__ import annotations

import asyncio
from collections.abc import Sequence
from pathlib import Path

DEFAULT_TIMEOUT = 30.0

# Forced on every call so output does not depend on the user's git config.
_STABLE_FLAGS = (
    "--no-pager",
    "-c",
    "core.quotepath=false",
    "-c",
    "color.ui=never",
)


class GitError(RuntimeError):
    """Base class for every failure in the git layer."""


class GitCommandError(GitError):
    """A git command exited non-zero."""

    def __init__(self, command: Sequence[str], returncode: int, stderr: str) -> None:
        self.command = list(command)
        self.returncode = returncode
        self.stderr = stderr.strip()
        super().__init__(f"git {' '.join(self.command)} exited {returncode}: {self.stderr}")


class GitTimeoutError(GitError):
    """A git command outlived its timeout and was killed."""

    def __init__(self, command: Sequence[str], timeout: float) -> None:
        self.command = list(command)
        self.timeout = timeout
        super().__init__(f"git {' '.join(self.command)} exceeded {timeout:g}s")


class NotARepositoryError(GitError):
    """A path is not inside a git work tree."""


def decode(raw: bytes) -> str:
    """Decode git output, tolerating paths that are not valid UTF-8."""
    return raw.decode("utf-8", errors="replace")


async def run_git(
    *args: str,
    cwd: Path | None = None,
    timeout: float = DEFAULT_TIMEOUT,
) -> str:
    """Run one git command and return its stdout.

    Raises GitCommandError on a non-zero exit and GitTimeoutError if it hangs.
    """
    process = await asyncio.create_subprocess_exec(
        "git",
        *_STABLE_FLAGS,
        *args,
        cwd=cwd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )

    try:
        stdout, stderr = await asyncio.wait_for(process.communicate(), timeout)
    except TimeoutError:
        process.kill()
        await process.wait()
        raise GitTimeoutError(args, timeout) from None

    if process.returncode != 0:
        raise GitCommandError(args, process.returncode or 1, decode(stderr))

    return decode(stdout)
