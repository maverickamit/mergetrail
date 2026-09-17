"""Build a throwaway git repository that exercises every kind of change."""

from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path

# Pinned so the fixture ignores the developer's global git config.
_CONFIG = (
    "-c",
    "user.name=MergeTrail Test",
    "-c",
    "user.email=test@mergetrail.invalid",
    "-c",
    "commit.gpgsign=false",
)

BINARY_V1 = bytes(range(0, 64))
BINARY_V2 = bytes(range(64, 128))


def git(repo: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *_CONFIG, *args],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def app_source(greeting: str = "hello", farewell: str = "bye") -> str:
    """Source with two edit points far enough apart to produce separate hunks."""
    lines = [
        '"""Fixture module."""',
        "",
        f'GREETING = "{greeting}"',
        "",
        *[f"FILLER_{n} = {n}" for n in range(1, 31)],
        "",
        f'FAREWELL = "{farewell}"',
        "",
    ]
    return "\n".join(lines)


@dataclass
class Fixture:
    """Where the fixture repo lives and which commits matter."""

    path: Path
    first_commit: str
    main_only_commit: str


def build_fixture_repo(root: Path) -> Fixture:
    """Create a repo where `feature` diverges from `main`, and `main` moves on.

    The extra commit on `main` is the point: a three-dot review must not show it.
    """
    repo = root / "project"
    repo.mkdir()
    git(repo, "init", "--initial-branch=main")

    (repo / "app.py").write_text(app_source())
    (repo / "README.md").write_text("# Project\n\nOriginal readme.\n")
    (repo / "util.py").write_text("def helper():\n    return 1\n")
    (repo / "logo.bin").write_bytes(BINARY_V1)
    git(repo, "add", ".")
    git(repo, "commit", "-m", "Add app")
    first_commit = git(repo, "rev-parse", "HEAD").strip()

    git(repo, "checkout", "-b", "feature")
    (repo / "app.py").write_text(app_source(greeting="hi there", farewell="farewell"))
    (repo / "helpers.py").write_text("def added():\n    return True\n")
    (repo / "logo.bin").write_bytes(BINARY_V2)
    git(repo, "rm", "--quiet", "README.md")
    git(repo, "mv", "util.py", "tools.py")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "Rework the app")

    git(repo, "checkout", "main")
    (repo / "CHANGELOG.md").write_text("# Changelog\n\nShipped something else.\n")
    git(repo, "add", ".")
    git(repo, "commit", "-m", "Land unrelated work on main")
    main_only_commit = git(repo, "rev-parse", "HEAD").strip()

    git(repo, "checkout", "feature")

    return Fixture(path=repo, first_commit=first_commit, main_only_commit=main_only_commit)
