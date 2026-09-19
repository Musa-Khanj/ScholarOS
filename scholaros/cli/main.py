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
    run_config,
    run_gui,
    run_info,
    run_init,
    run_research,
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
        return run_info(output)

    if args.command == "status":
        return run_status(output)

    if args.command == "init":
        return run_init(output, force=getattr(args, "force", False))

    if args.command == "gui":
        return run_gui(output)

    if args.command == "config":
        return run_config(output)

    if args.command == "run":
        return run_research(
            output,
            query=args.query,
            provider=getattr(args, "provider", None),
            model=getattr(args, "model", None),
        )

    parser.print_help(
        file=output,
    )

    return 0
