"""
ScholarOS Container Package.

Public Dependency Injection API for ScholarOS.
"""

from scholaros.container.builder import Builder
from scholaros.container.container import Container
from scholaros.container.descriptor import ServiceDescriptor
from scholaros.container.exceptions import (
    CircularDependencyError,
    ContainerError,
    InvalidServiceError,
    RegistrationError,
    ResolutionError,
    ScopeDisposedError,
    ServiceAlreadyRegistered,
    ServiceNotFound,
)
from scholaros.container.lifetime import (
    Scoped,
    ServiceLifetime,
    Singleton,
    Transient,
)
from scholaros.container.provider import (
    ConstructorProvider,
    FactoryProvider,
    InstanceProvider,
    LazyProvider,
    ServiceProvider,
)
from scholaros.container.registry import ServiceRegistry
from scholaros.container.resolver import DependencyResolver
from scholaros.container.scope import Scope

__all__ = [
    # Core Container & Scope
    "Builder",
    "Container",
    "DependencyResolver",
    "Scope",
    "ServiceDescriptor",
    "ServiceRegistry",
    # Lifetimes
    "Scoped",
    "ServiceLifetime",
    "Singleton",
    "Transient",
    # Providers
    "ConstructorProvider",
    "FactoryProvider",
    "InstanceProvider",
    "LazyProvider",
    "ServiceProvider",
    # Exceptions
    "CircularDependencyError",
    "ContainerError",
    "InvalidServiceError",
    "RegistrationError",
    "ResolutionError",
    "ScopeDisposedError",
    "ServiceAlreadyRegistered",
    "ServiceNotFound",
]