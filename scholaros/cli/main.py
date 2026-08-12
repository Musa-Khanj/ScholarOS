"""
ScholarOS
CLI Main

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
CLI application entry point.
"""

from __future__ import annotations

import sys
from typing import Sequence, TextIO

from scholaros.cli.commands import (
    run_info,
    run_status,
)
from scholaros.cli.parser import (
    build_parser,
)


def main(
    argv: Sequence[str] | None = None,
    output: TextIO | None = None,
) -> int:
    """
    Execute the ScholarOS CLI.

    Parameters
    ----------
    argv:
        Optional command-line arguments.
    output:
        Optional output stream used primarily
        for testing.
    """

    if output is None:
        output = sys.stdout

    parser = build_parser()

    args = parser.parse_args(
        list(argv)
        if argv is not None
        else None,
    )

    if args.command == "info":
        return run_info(
            output,
        )

    if args.command == "status":
        return run_status(
            output,
        )

    parser.print_help(
        file=output,
    )

    return 0
