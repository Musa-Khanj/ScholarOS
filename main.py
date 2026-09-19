"""
ScholarOS
Main Entry Point

Version : 1.0
Status  : Stable
Python  : 3.14+
"""

from __future__ import annotations

from scholaros.bootstrap import Bootstrap


def main() -> int:
    """
    ScholarOS entry point.
    """

    return Bootstrap().run()


if __name__ == "__main__":
    raise SystemExit(main())