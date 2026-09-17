"""Read local branch diffs by shelling out to git."""

from mergetrail.git.hunks import hunk_id, parse_hunks
from mergetrail.git.models import ChangeStatus, FileChange, Hunk, Review
from mergetrail.git.repo import (
    build_review,
    changed_files,
    discover_repository,
    file_hunks,
    merge_base,
    ref_exists,
    resolve_commit,
    resolve_default_base,
)
from mergetrail.git.runner import (
    GitCommandError,
    GitError,
    GitTimeoutError,
    NotARepositoryError,
    run_git,
)

__all__ = [
    "ChangeStatus",
    "FileChange",
    "GitCommandError",
    "GitError",
    "GitTimeoutError",
    "Hunk",
    "NotARepositoryError",
    "Review",
    "build_review",
    "changed_files",
    "discover_repository",
    "file_hunks",
    "hunk_id",
    "merge_base",
    "parse_hunks",
    "ref_exists",
    "resolve_commit",
    "resolve_default_base",
    "run_git",
]
