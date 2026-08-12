from __future__ import annotations

from io import StringIO

import pytest

from scholaros.cli.main import main


def test_cli_help_without_command():

    output = StringIO()

    result = main(
        [],
        output,
    )

    assert result == 0

    assert "usage:" in output.getvalue()


def test_cli_version(
    capsys,
):

    output = StringIO()

    with pytest.raises(
        SystemExit,
    ) as exc_info:
        main(
            [
                "--version",
            ],
            output,
        )

    assert exc_info.value.code == 0

    captured = capsys.readouterr()

    assert (
        captured.out
        == "ScholarOS 1.0.0\n"
    )


def test_cli_info():

    output = StringIO()

    result = main(
        [
            "info",
        ],
        output,
    )

    assert result == 0

    content = output.getvalue()

    assert "ScholarOS" in content

    assert (
        "Version: 1.0.0"
        in content
    )


def test_cli_status():

    output = StringIO()

    result = main(
        [
            "status",
        ],
        output,
    )

    assert result == 0

    content = output.getvalue()

    assert (
        "ScholarOS status: READY"
        in content
    )

    assert (
        "Version: 1.0.0"
        in content
    )