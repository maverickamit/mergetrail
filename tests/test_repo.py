from pathlib import Path

import pytest

from helpers import Fixture
from mergetrail.git import (
    ChangeStatus,
    FileChange,
    NotARepositoryError,
    build_review,
    changed_files,
    discover_repository,
    file_hunks,
    merge_base,
    resolve_default_base,
)


async def changed_by_path(repo: Path, base: str, head: str = "feature") -> dict[str, FileChange]:
    return {file.path: file for file in await changed_files(repo, base, head)}


async def test_discover_repository_walks_up_from_a_subdirectory(fixture_repo: Fixture):
    nested = fixture_repo.path / "deep" / "nested"
    nested.mkdir(parents=True)

    assert await discover_repository(nested) == fixture_repo.path.resolve()


async def test_discover_repository_rejects_a_plain_directory(tmp_path):
    outside = tmp_path / "not-a-repo"
    outside.mkdir()

    with pytest.raises(NotARepositoryError):
        await discover_repository(outside)


async def test_resolve_default_base_falls_back_to_main(fixture_repo: Fixture):
    assert await resolve_default_base(fixture_repo.path) == "main"


async def test_merge_base_is_the_fork_point_not_the_tip_of_main(fixture_repo: Fixture):
    fork_point = await merge_base(fixture_repo.path, "main", "feature")

    assert fork_point == fixture_repo.first_commit
    assert fork_point != fixture_repo.main_only_commit


async def test_review_excludes_work_landed_on_main_after_the_branch(fixture_repo: Fixture):
    review = await build_review(fixture_repo.path, base="main", head="feature")

    assert "CHANGELOG.md" not in {file.path for file in review.files}


async def test_changed_files_classifies_every_kind_of_change(fixture_repo: Fixture):
    fork_point = await merge_base(fixture_repo.path, "main", "feature")

    files = await changed_by_path(fixture_repo.path, fork_point)

    assert files["app.py"].status is ChangeStatus.modified
    assert files["helpers.py"].status is ChangeStatus.added
    assert files["README.md"].status is ChangeStatus.deleted
    assert files["tools.py"].status is ChangeStatus.renamed
    assert files["tools.py"].old_path == "util.py"


async def test_changed_files_counts_lines_and_flags_binaries(fixture_repo: Fixture):
    fork_point = await merge_base(fixture_repo.path, "main", "feature")

    files = await changed_by_path(fixture_repo.path, fork_point)

    assert files["app.py"].additions == 2
    assert files["app.py"].deletions == 2
    assert files["logo.bin"].is_binary is True
    assert files["logo.bin"].additions == 0
    assert files["helpers.py"].is_binary is False


async def test_file_hunks_splits_two_distant_edits(fixture_repo: Fixture):
    fork_point = await merge_base(fixture_repo.path, "main", "feature")

    hunks = await file_hunks(fixture_repo.path, fork_point, "feature", "app.py")

    assert len(hunks) == 2
    assert hunks[0].old_start == 1
    assert hunks[1].old_start > hunks[0].old_start
    assert '+GREETING = "hi there"' in hunks[0].body
    assert '+FAREWELL = "farewell"' in hunks[1].body
    assert hunks[0].id != hunks[1].id


async def test_file_hunks_follows_a_rename(fixture_repo: Fixture):
    fork_point = await merge_base(fixture_repo.path, "main", "feature")

    hunks = await file_hunks(
        fixture_repo.path, fork_point, "feature", "tools.py", old_path="util.py"
    )

    assert hunks == []


async def test_build_review_reports_the_refs_it_resolved(fixture_repo: Fixture):
    review = await build_review(fixture_repo.path, base="main", head="feature")

    assert review.base == "main"
    assert review.merge_base == fixture_repo.first_commit
    assert len(review.head_sha) == 40
    assert review.repo_path == str(fixture_repo.path)


async def test_build_review_defers_hunks_until_asked(fixture_repo: Fixture):
    lazy = await build_review(fixture_repo.path, base="main", head="feature")
    eager = await build_review(fixture_repo.path, base="main", head="feature", include_hunks=True)

    assert all(file.hunks == [] for file in lazy.files)
    assert next(file for file in eager.files if file.path == "app.py").hunks
    assert next(file for file in eager.files if file.path == "logo.bin").hunks == []


async def test_build_review_totals_the_line_counts(fixture_repo: Fixture):
    review = await build_review(fixture_repo.path, base="main", head="feature")

    assert review.additions == sum(file.additions for file in review.files)
    assert review.deletions > 0
