from fastapi.testclient import TestClient

from mergetrail.api import ServerContext, create_app
from mergetrail.api.app import STATIC_DIR


def test_root_serves_the_review_ui(fixture_repo):
    client = TestClient(
        create_app(ServerContext(repo=fixture_repo.path, base="main", head="feature"))
    )
    response = client.get("/")
    index = STATIC_DIR / "index.html"

    if not index.is_file():
        assert response.status_code == 503
        return

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert b"root" in response.content


def test_json_routes_are_not_shadowed_by_the_ui(fixture_repo):
    response = TestClient(
        create_app(ServerContext(repo=fixture_repo.path, base="main", head="feature"))
    ).get("/review")

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert "files" in response.json()
