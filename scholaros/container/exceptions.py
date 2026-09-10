"""
ScholarOS Container Exceptions.

Container-specific exceptions for dependency injection, registration,
resolution, and lifetime management.
"""

from __future__ import annotations


class ContainerError(Exception):
    """Base exception for all container-related errors."""


class RegistrationError(ContainerError):
    """Raised when a service registration fails or is invalid."""


class ServiceAlreadyRegistered(RegistrationError):
    """Raised when attempting to register a service that is already registered."""


class ResolutionError(ContainerError):
    """Raised when an error occurs while resolving a service."""


class ServiceNotFound(ResolutionError):
    """Raised when a requested service cannot be found in the container."""


class CircularDependencyError(ResolutionError):
    """Raised when a circular dependency is detected in the dependency graph."""


class InvalidServiceError(ResolutionError):
    """Raised when a service cannot be constructed or configured properly."""


class ScopeDisposedError(ResolutionError):
    """Raised when attempting to resolve a service from a disposed scope."""


__all__ = [
    "CircularDependencyError",
    "ContainerError",
    "InvalidServiceError",
    "RegistrationError",
    "ResolutionError",
    "ScopeDisposedError",
    "ServiceAlreadyRegistered",
    "ServiceNotFound",
]
