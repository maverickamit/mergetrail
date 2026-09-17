"""Split a unified patch into hunks and give each one a stable id."""

from __future__ import annotations

import hashlib
import re

from mergetrail.git.models import Hunk

HUNK_ID_LENGTH = 16

_HEADER = re.compile(r"^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@")


def hunk_id(path: str, header: str, body: str) -> str:
    """Hash a hunk so the same change always resolves to the same cache key."""
    digest = hashlib.sha256("\n".join((path, header, body)).encode("utf-8"))
    return digest.hexdigest()[:HUNK_ID_LENGTH]


def parse_hunks(path: str, patch: str) -> list[Hunk]:
    """Turn `git diff` output for a single file into hunks.

    Everything before the first `@@` is git's file preamble and is dropped. A
    `diff --git` line ends the file, so a multi-file patch yields only the first.
    """
    hunks: list[Hunk] = []
    header: str | None = None
    body: list[str] = []

    def flush() -> None:
        if header is None:
            return
        match = _HEADER.match(header)
        if match is None:  # pragma: no cover - flush is only called on a matched header
            return
        old_start, old_lines, new_start, new_lines = match.groups()
        text = "\n".join(body)
        hunks.append(
            Hunk(
                id=hunk_id(path, header, text),
                header=header,
                old_start=int(old_start),
                old_lines=int(old_lines) if old_lines is not None else 1,
                new_start=int(new_start),
                new_lines=int(new_lines) if new_lines is not None else 1,
                body=text,
            )
        )

    for line in patch.splitlines():
        if _HEADER.match(line):
            flush()
            header = line
            body = []
        elif line.startswith("diff --git") and header is not None:
            break
        elif header is not None:
            body.append(line)

    flush()
    return hunks
