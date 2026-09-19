"""
ScholarOS Service System Exceptions.

Defines exception types for service registration, resolution, lifecycle,
dependency resolution, and health verification.
"""

from __future__ import annotations


class ServiceError(Exception):
    """Base exception for all service-related errors."""


class ServiceRegistrationError(ServiceError):
    """Raised when registering a service fails."""


class ServiceAlreadyRegisteredError(ServiceRegistrationError):
    """Raised when a service with the same name or type is already registered."""


class ServiceNotFoundError(ServiceError):
    """Raised when a requested service is not found."""


class ServiceLifecycleError(ServiceError):
    """Raised when an invalid lifecycle transition occurs."""


class ServiceDependencyError(ServiceError):
    """Raised when service dependencies cannot be satisfied."""


class CircularServiceDependencyError(ServiceDependencyError):
    """Raised when a circular dependency among services is detected."""


class ServiceHealthError(ServiceError):
    """Raised when health checks or status checks fail."""


__all__ = [
    "CircularServiceDependencyError",
    "ServiceAlreadyRegisteredError",
    "ServiceDependencyError",
    "ServiceError",
    "ServiceHealthError",
    "ServiceLifecycleError",
    "ServiceNotFoundError",
    "ServiceRegistrationError",
]
