"""
ScholarOS Bootstrap Package.

Provides application startup, logging initialization, and the central
composition root for constructing the production runtime.
"""

from __future__ import annotations

from scholaros.bootstrap.bootstrap import Bootstrap
from scholaros.bootstrap.runtime import RuntimeServices, bootstrap_runtime

__all__ = [
    "Bootstrap",
    "RuntimeServices",
    "bootstrap_runtime",
]
