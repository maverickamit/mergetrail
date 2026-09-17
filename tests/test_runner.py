import pytest

from helpers import Fixture
from mergetrail.git import GitCommandError, GitTimeoutError, run_git


async def test_run_git_returns_stdout(fixture_repo: Fixture):
    output = await run_git("rev-parse", "--abbrev-ref", "HEAD", cwd=fixture_repo.path)

    assert output.strip() == "feature"


async def test_run_git_reports_a_failed_command(fixture_repo: Fixture):
    with pytest.raises(GitCommandError) as error:
        await run_git("rev-parse", "--verify", "no-such-ref", cwd=fixture_repo.path)

    assert error.value.returncode != 0
    assert "no-such-ref" in str(error.value)


async def test_run_git_kills_a_command_that_outlives_its_timeout(fixture_repo: Fixture):
    with pytest.raises(GitTimeoutError):
        await run_git("rev-parse", "HEAD", cwd=fixture_repo.path, timeout=0.0005)
