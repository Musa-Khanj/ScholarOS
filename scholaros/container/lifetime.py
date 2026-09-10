"""
ScholarOS Container Service Lifetime.

Defines service lifetimes supported by the dependency injection container:
- Singleton: A single instance is created and shared across the entire container.
- Scoped: A single instance is created per Scope and disposed with the Scope.
- Transient: A new instance is created every time the service is resolved.
"""

from __future__ import annotations

from enum import Enum, auto


class ServiceLifetime(Enum):
    """Enumeration of service lifetimes."""

    SINGLETON = auto()
    SCOPED = auto()
    TRANSIENT = auto()

    def __repr__(self) -> str:
        return f"ServiceLifetime.{self.name}"


# Convenient aliases for public DI API
Singleton: ServiceLifetime = ServiceLifetime.SINGLETON
Scoped: ServiceLifetime = ServiceLifetime.SCOPED
Transient: ServiceLifetime = ServiceLifetime.TRANSIENT

__all__ = [
    "Scoped",
    "ServiceLifetime",
    "Singleton",
    "Transient",
]