"""The shape of a review, shared by the git layer and the HTTP API."""

from __future__ import annotations

from enum import StrEnum

from pydantic import BaseModel, Field


class ChangeStatus(StrEnum):
    added = "added"
    modified = "modified"
    deleted = "deleted"
    renamed = "renamed"
    copied = "copied"
    type_changed = "type_changed"


class Hunk(BaseModel):
    """One `@@` block of a file's patch."""

    id: str = Field(description="Stable hash of the path and hunk content, used as a cache key")
    header: str
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    body: str


class FileChange(BaseModel):
    """One file's entry in the review, without its patch."""

    path: str
    old_path: str | None = None
    status: ChangeStatus
    additions: int = 0
    deletions: int = 0
    is_binary: bool = False
    hunks: list[Hunk] = Field(default_factory=list)


class Review(BaseModel):
    """Everything needed to render a branch review."""

    repo_path: str
    base: str = Field(description="Base ref as requested, e.g. 'main' or 'origin/main'")
    head: str
    merge_base: str = Field(description="Commit the branch diverged from, resolved to a sha")
    head_sha: str
    files: list[FileChange] = Field(default_factory=list)

    @property
    def additions(self) -> int:
        return sum(file.additions for file in self.files)

    @property
    def deletions(self) -> int:
        return sum(file.deletions for file in self.files)
