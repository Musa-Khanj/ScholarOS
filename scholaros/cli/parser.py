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
