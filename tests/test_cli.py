from typer.testing import CliRunner

from mergetrail import __version__
from mergetrail.cli import app

runner = CliRunner()


def test_cli_reports_version():
    result = runner.invoke(app, [])

    assert result.exit_code == 0
    assert __version__ in result.stdout
