from pathlib import Path

import pytest

from helpers import Fixture, build_fixture_repo


@pytest.fixture
def fixture_repo(tmp_path: Path) -> Fixture:
    return build_fixture_repo(tmp_path)
