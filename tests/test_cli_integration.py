from __future__ import annotations

import subprocess
import sys


def run_cli(
    *arguments: str,
) -> subprocess.CompletedProcess[str]:

    return subprocess.run(
        [
            sys.executable,
            "-m",
            "scholaros.cli",
            *arguments,
        ],
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_integration_version():

    result = run_cli(
        "--version",
    )

    assert result.returncode == 0

    assert (
        result.stdout
        == "ScholarOS 1.0.0\n"
    )

    assert result.stderr == ""


def test_cli_integration_info():

    result = run_cli(
        "info",
    )

    assert result.returncode == 0

    assert (
        "ScholarOS\n"
        in result.stdout
    )

    assert (
        "Version: 1.0.0\n"
        in result.stdout
    )

    assert (
        "Description: A modular "
        "multi-agent AI research "
        "operating system.\n"
        in result.stdout
    )

    assert result.stderr == ""


def test_cli_integration_status():

    result = run_cli(
        "status",
    )

    assert result.returncode == 0

    assert (
        "ScholarOS status: READY\n"
        in result.stdout
    )

    assert (
        "Version: 1.0.0\n"
        in result.stdout
    )

    assert result.stderr == ""


def test_cli_integration_without_command():

    result = run_cli()

    assert result.returncode == 0

    assert (
        "usage:"
        in result.stdout
    )

    assert result.stderr == ""


def test_cli_integration_unknown_command():

    result = run_cli(
        "unknown-command",
    )

    assert result.returncode != 0

    assert (
        "invalid choice"
        in result.stderr
    )


def test_cli_integration_help():

    result = run_cli(
        "--help",
    )

    assert result.returncode == 0

    assert (
        "usage:"
        in result.stdout
    )

    assert (
        "--version"
        in result.stdout
    )

    assert (
        "info"
        in result.stdout
    )

    assert (
        "status"
        in result.stdout
    )

    assert result.stderr == ""


def test_cli_integration_invalid_option():

    result = run_cli(
        "--invalid-option",
    )

    assert result.returncode != 0

    assert (
        "unrecognized arguments"
        in result.stderr
    )


def test_cli_integration_command_order():

    version = run_cli(
        "--version",
    )

    info = run_cli(
        "info",
    )

    status = run_cli(
        "status",
    )

    assert version.returncode == 0
    assert info.returncode == 0
    assert status.returncode == 0

    assert (
        version.stdout
        == "ScholarOS 1.0.0\n"
    )

    assert (
        "Version: 1.0.0"
        in info.stdout
    )

    assert (
        "ScholarOS status: READY"
        in status.stdout
    )