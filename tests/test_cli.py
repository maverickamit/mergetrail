from pathlib import Path

from typer.testing import CliRunner

from mergetrail import __version__
from mergetrail.cli import app

runner = CliRunner()


def test_cli_reports_version():
    result = runner.invoke(app, ["--version"])

    assert result.exit_code == 0
    assert __version__ in result.stdout


def test_cli_starts_a_loopback_server(monkeypatch, fixture_repo):
    started: dict[str, object] = {}

    def fake_run(server_app, host: str, port: int, **_kwargs) -> None:
        started["app"] = server_app
        started["host"] = host
        started["port"] = port

    monkeypatch.setattr("mergetrail.cli.uvicorn.run", fake_run)

    result = runner.invoke(
        app,
        ["--repo", str(fixture_repo.path), "--base", "main", "--port", "9001", "--no-open"],
    )

    assert result.exit_code == 0, result.output
    assert started["host"] == "127.0.0.1"
    assert started["port"] == 9001
    assert "GET http://127.0.0.1:9001/review" in result.stdout
    assert "main...feature" in result.stdout or "main...HEAD" in result.stdout


def test_cli_rejects_a_directory_that_is_not_a_repo(tmp_path: Path):
    outside = tmp_path / "not-a-repo"
    outside.mkdir()

    result = runner.invoke(app, ["--repo", str(outside), "--no-open"])

    assert result.exit_code == 1
    assert "not inside a git repository" in result.output


def test_cli_rejects_an_unknown_base(fixture_repo):
    result = runner.invoke(
        app,
        ["--repo", str(fixture_repo.path), "--base", "missing-branch", "--no-open"],
    )

    assert result.exit_code == 1
    assert result.output
