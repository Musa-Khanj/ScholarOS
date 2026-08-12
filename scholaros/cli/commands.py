"""
ScholarOS
CLI Commands

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Implements command-line presentation
operations without modifying the
ScholarOS core architecture.
"""

from __future__ import annotations

from typing import TextIO

import scholaros


def run_info(
    output: TextIO,
) -> int:
    """
    Display basic ScholarOS package
    information.
    """

    print(
        "ScholarOS",
        file=output,
    )
    print(
        f"Version: {scholaros.__version__}",
        file=output,
    )
    print(
        "Description: "
        "A modular multi-agent AI "
        "research operating system.",
        file=output,
    )

    return 0


def run_status(
    output: TextIO,
) -> int:
    """
    Display basic ScholarOS status.

    This command intentionally performs
    only a package-level health check.
    It does not start the kernel,
    runtime, LLM providers, or external
    services.
    """

    try:
        version = scholaros.__version__

    except AttributeError:
        print(
            "ScholarOS status: ERROR",
            file=output,
        )
        return 1

    print(
        "ScholarOS status: READY",
        file=output,
    )
    print(
        f"Version: {version}",
        file=output,
    )

    return 0
