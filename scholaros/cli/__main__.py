"""
ScholarOS
CLI Module Entry Point

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides the module entry point for
the ScholarOS command-line interface.
"""

from __future__ import annotations

from scholaros.cli.main import main


if __name__ == "__main__":
    raise SystemExit(
        main()
    )
