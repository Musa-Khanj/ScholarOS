"""
ScholarOS Security Exceptions.

Defines exception types for the security subsystem, prompt injection defense,
path traversal validation, and plugin capability enforcement.
"""

from __future__ import annotations

from scholaros.core.exceptions import ScholarOSError


class SecurityError(ScholarOSError):
    """Base exception for all security violations in ScholarOS."""


class PromptInjectionError(SecurityError):
    """Raised when an adversarial prompt injection attempt is detected."""


class PathTraversalError(SecurityError):
    """Raised when a file path escapes the designated base directory."""


class CapabilityViolationError(SecurityError):
    """Raised when an untrusted component attempts an unauthorized capability."""


class SecretLeakError(SecurityError):
    """Raised when sensitive credentials or unmasked tokens are detected in unsafe context."""


__all__ = [
    "CapabilityViolationError",
    "PathTraversalError",
    "PromptInjectionError",
    "SecretLeakError",
    "SecurityError",
]
