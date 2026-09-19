"""
ScholarOS
CLI Parser

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Builds the ScholarOS command-line
argument parser.
"""

from __future__ import annotations

import argparse


def build_parser() -> argparse.ArgumentParser:
    """
    Build and return the ScholarOS
    command-line argument parser.
    """

    parser = argparse.ArgumentParser(
        prog="scholaros",
        description=(
            "ScholarOS - a modular "
            "multi-agent AI research "
            "operating system."
        ),
    )

    parser.add_argument(
        "--version",
        action="version",
        version=_version_text(),
    )

    subparsers = parser.add_subparsers(
        dest="command",
        title="commands",
    )

    info_parser = subparsers.add_parser(
        "info",
        help="Show ScholarOS package information.",
    )
    info_parser.set_defaults(
        handler="info",
    )

    status_parser = subparsers.add_parser(
        "status",
        help="Show basic ScholarOS runtime status.",
    )
    status_parser.set_defaults(
        handler="status",
    )

    init_parser = subparsers.add_parser(
        "init",
        help="Initialize user configuration and data directories.",
    )
    init_parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite existing configuration file if present.",
    )
    init_parser.set_defaults(
        handler="init",
    )

    gui_parser = subparsers.add_parser(
        "gui",
        help="Launch the ScholarOS desktop GUI application.",
    )
    gui_parser.set_defaults(
        handler="gui",
    )

    config_parser = subparsers.add_parser(
        "config",
        help="Display platform directory paths and configuration status.",
    )
    config_parser.set_defaults(
        handler="config",
    )

    run_parser = subparsers.add_parser(
        "run",
        help="Execute an AI research query directly from the terminal.",
    )
    run_parser.add_argument(
        "query",
        type=str,
        help="Research query prompt.",
    )
    run_parser.add_argument(
        "--provider",
        type=str,
        default=None,
        help="AI provider override.",
    )
    run_parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name override.",
    )
    run_parser.set_defaults(
        handler="run",
    )

    return parser


def _version_text() -> str:
    """
    Return the ScholarOS version text.
    """

    try:
        from scholaros import __version__

        return f"ScholarOS {__version__}"

    except ImportError:
        return "ScholarOS"
