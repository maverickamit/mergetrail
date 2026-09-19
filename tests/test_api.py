from fastapi.testclient import TestClient

from mergetrail.api import ServerContext, create_app
from mergetrail.git.models import ChangeStatus


def client_for(repo) -> TestClient:
    app = create_app(ServerContext(repo=repo.path, base="main", head="feature"))
    return TestClient(app)


def test_review_returns_the_three_dot_file_list(fixture_repo):
    response = client_for(fixture_repo).get("/review")

    assert response.status_code == 200
    payload = response.json()
    paths = {file["path"] for file in payload["files"]}

    assert payload["base"] == "main"
    assert payload["head"] == "feature"
    assert payload["merge_base"] == fixture_repo.first_commit
    assert payload["additions"] == sum(file["additions"] for file in payload["files"])
    assert payload["deletions"] > 0
    assert "app.py" in paths
    assert "CHANGELOG.md" not in paths
    assert all(file["hunks"] == [] for file in payload["files"])


def test_files_matches_the_review_file_list(fixture_repo):
    client = client_for(fixture_repo)

    review_files = client.get("/review").json()["files"]
    listed = client.get("/files").json()

    assert listed == review_files


def test_file_includes_hunks_for_a_text_change(fixture_repo):
    payload = client_for(fixture_repo).get("/files/app.py").json()

    assert payload["path"] == "app.py"
    assert payload["status"] == ChangeStatus.modified
    assert len(payload["hunks"]) == 2
    assert '+GREETING = "hi there"' in payload["hunks"][0]["body"]
    assert payload["hunks"][0]["id"] != payload["hunks"][1]["id"]


def test_file_follows_a_rename(fixture_repo):
    payload = client_for(fixture_repo).get("/files/tools.py").json()

    assert payload["status"] == ChangeStatus.renamed
    assert payload["old_path"] == "util.py"
    assert payload["hunks"] == []


def test_file_skips_hunks_for_binaries(fixture_repo):
    payload = client_for(fixture_repo).get("/files/logo.bin").json()

    assert payload["is_binary"] is True
    assert payload["hunks"] == []


def test_unknown_file_is_not_found(fixture_repo):
    response = client_for(fixture_repo).get("/files/CHANGELOG.md")

    assert response.status_code == 404
    assert "CHANGELOG.md" in response.json()["detail"]


def test_bad_ref_is_a_client_error(fixture_repo):
    app = create_app(ServerContext(repo=fixture_repo.path, base="does-not-exist", head="feature"))

    response = TestClient(app, raise_server_exceptions=False).get("/review")

    assert response.status_code == 400
    assert "detail" in response.json()
