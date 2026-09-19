"""
ScholarOS Research Exceptions.

Defines the typed exception hierarchy for the ScholarOS Research subsystem.
"""

from __future__ import annotations

from scholaros.core.exceptions import ScholarOSError


class ResearchError(ScholarOSError):
    """Base exception for all research subsystem errors."""


class ResearchExecutionError(ResearchError):
    """Raised when research execution fails."""


class ResearchPipelineError(ResearchError):
    """Raised when a research pipeline operation fails."""


class ResearchConfigurationError(ResearchError):
    """Raised when research pipeline or agent configuration is invalid."""


__all__ = [
    "ResearchConfigurationError",
    "ResearchError",
    "ResearchExecutionError",
    "ResearchPipelineError",
]
