"""Read a branch review out of a local git repository."""

from __future__ import annotations

import asyncio
from pathlib import Path

from mergetrail.git.hunks import parse_hunks
from mergetrail.git.models import ChangeStatus, FileChange, Hunk, Review
from mergetrail.git.runner import GitError, NotARepositoryError, run_git

DEFAULT_CONTEXT_LINES = 3
DEFAULT_CONCURRENCY = 8

_FALLBACK_BASES = ("main", "master", "develop", "trunk")

_STATUS_CODES = {
    "A": ChangeStatus.added,
    "M": ChangeStatus.modified,
    "D": ChangeStatus.deleted,
    "R": ChangeStatus.renamed,
    "C": ChangeStatus.copied,
    "T": ChangeStatus.type_changed,
}


async def discover_repository(start: Path | None = None) -> Path:
    """Walk up from `start` to the root of its work tree."""
    start = (start or Path.cwd()).resolve()
    try:
        top_level = await run_git("rev-parse", "--show-toplevel", cwd=start)
    except GitError as error:
        raise NotARepositoryError(f"{start} is not inside a git repository") from error
    return Path(top_level.strip())


async def ref_exists(repo: Path, ref: str) -> bool:
    try:
        await run_git("rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}", cwd=repo)
    except GitError:
        return False
    return True


async def resolve_commit(repo: Path, ref: str) -> str:
    """Resolve a ref to a full commit sha."""
    output = await run_git("rev-parse", "--verify", f"{ref}^{{commit}}", cwd=repo)
    return output.strip()


async def resolve_default_base(repo: Path) -> str:
    """Guess the branch a pull request would target."""
    try:
        origin_head = await run_git("symbolic-ref", "--short", "refs/remotes/origin/HEAD", cwd=repo)
        return origin_head.strip()
    except GitError:
        pass

    for candidate in _FALLBACK_BASES:
        if await ref_exists(repo, candidate):
            return candidate

    raise GitError("could not determine a default base branch; pass one explicitly")


async def merge_base(repo: Path, base: str, head: str) -> str:
    """Find where `head` diverged from `base`.

    Reviewing against this commit rather than the tip of `base` is what makes the
    diff match a pull request: work landed on `base` after the branch started is
    not part of the change under review.
    """
    output = await run_git("merge-base", base, head, cwd=repo)
    return output.strip()


async def changed_files(repo: Path, base: str, head: str) -> list[FileChange]:
    """List the files `head` changes relative to `base`, with line counts."""
    statuses, counts = await asyncio.gather(
        run_git("diff", "--name-status", "-M", "-z", base, head, cwd=repo),
        run_git("diff", "--numstat", "-M", "-z", base, head, cwd=repo),
    )

    counts_by_path = _parse_numstat(counts)
    files: list[FileChange] = []

    for status_code, old_path, path in _parse_name_status(statuses):
        additions, deletions, is_binary = counts_by_path.get(path, (0, 0, False))
        files.append(
            FileChange(
                path=path,
                old_path=old_path,
                status=_STATUS_CODES.get(status_code, ChangeStatus.modified),
                additions=additions,
                deletions=deletions,
                is_binary=is_binary,
            )
        )

    return files


async def file_hunks(
    repo: Path,
    base: str,
    head: str,
    path: str,
    old_path: str | None = None,
    context: int = DEFAULT_CONTEXT_LINES,
) -> list[Hunk]:
    """Read one file's patch and split it into hunks."""
    pathspec = [p for p in (old_path, path) if p]
    patch = await run_git(
        "diff",
        f"-U{context}",
        "-M",
        base,
        head,
        "--",
        *pathspec,
        cwd=repo,
    )
    return parse_hunks(path, patch)


async def build_review(
    repo: Path,
    base: str | None = None,
    head: str = "HEAD",
    include_hunks: bool = False,
    context: int = DEFAULT_CONTEXT_LINES,
    concurrency: int = DEFAULT_CONCURRENCY,
) -> Review:
    """Assemble a review of `head` against the merge base with `base`.

    Refs are resolved to commit shas once and every later diff runs against
    those, so a commit landing mid-review cannot make the file list and the
    patches disagree.

    Hunks are left out by default: a large pull request should render its file
    list immediately and fetch patches per file as the reader opens them.
    """
    if base is None:
        base = await resolve_default_base(repo)

    fork_point, head_sha = await asyncio.gather(
        merge_base(repo, base, head),
        resolve_commit(repo, head),
    )
    files = await changed_files(repo, fork_point, head_sha)

    if include_hunks:
        files = await _attach_hunks(repo, fork_point, head_sha, files, context, concurrency)

    return Review(
        repo_path=str(repo),
        base=base,
        head=head,
        merge_base=fork_point,
        head_sha=head_sha,
        files=files,
    )


async def _attach_hunks(
    repo: Path,
    base: str,
    head: str,
    files: list[FileChange],
    context: int,
    concurrency: int,
) -> list[FileChange]:
    limit = asyncio.Semaphore(concurrency)

    async def load(file: FileChange) -> FileChange:
        if file.is_binary:
            return file
        async with limit:
            hunks = await file_hunks(repo, base, head, file.path, file.old_path, context)
        return file.model_copy(update={"hunks": hunks})

    return list(await asyncio.gather(*(load(file) for file in files)))


def _parse_name_status(output: str) -> list[tuple[str, str | None, str]]:
    """Read NUL-separated `--name-status` records.

    Renames and copies span three fields (`R100`, old, new); everything else
    spans two. `-z` avoids git's path quoting, so unicode paths survive intact.
    """
    fields = output.split("\0")
    records: list[tuple[str, str | None, str]] = []
    index = 0

    while index < len(fields) and fields[index]:
        code = fields[index][0]
        if code in ("R", "C"):
            records.append((code, fields[index + 1], fields[index + 2]))
            index += 3
        else:
            records.append((code, None, fields[index + 1]))
            index += 2

    return records


def _parse_numstat(output: str) -> dict[str, tuple[int, int, bool]]:
    """Read NUL-separated `--numstat` records into counts keyed by new path.

    Binary files report `-` instead of numbers, and renames leave the path
    fields empty so the old and new paths follow as separate records.
    """
    fields = output.split("\0")
    counts: dict[str, tuple[int, int, bool]] = {}
    index = 0

    while index < len(fields) and fields[index]:
        added, removed, inline_path = fields[index].split("\t", 2)
        if inline_path:
            path = inline_path
            index += 1
        else:
            path = fields[index + 2]
            index += 3

        is_binary = added == "-" or removed == "-"
        counts[path] = (
            0 if is_binary else int(added),
            0 if is_binary else int(removed),
            is_binary,
        )

    return counts
