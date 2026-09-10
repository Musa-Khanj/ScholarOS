"""
ScholarOS Container.

Central Dependency Injection Container.
Responsible for:
- Service registration (singleton, transient, scoped, instance, factory)
- Service resolution
- Singleton lifetime management
- Scope creation
- Object graph wiring delegation
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from scholaros.container.builder import Builder
from scholaros.container.exceptions import (
    ResolutionError,
    ServiceNotFound,
)
from scholaros.container.lifetime import (
    ServiceLifetime,
)
from scholaros.container.provider import (
    ConstructorProvider,
    FactoryProvider,
    InstanceProvider,
)
from scholaros.container.registry import (
    ServiceRegistry,
)
from scholaros.container.resolver import (
    DependencyResolver,
)
from scholaros.container.scope import Scope


class Container:
    """
    Root dependency injection container.

    Central DI container responsible for registration, resolution,
    singleton lifetime management, scope creation, and object graph wiring.
    """

    def __init__(self) -> None:
        self.registry = ServiceRegistry()
        self.resolver = DependencyResolver()
        self.builder = Builder(
            resolver=self.resolve,
            dependency_resolver=self.resolver,
        )
        self._disposed = False

    def add_singleton(
        self,
        interface: type,
        implementation: type,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a singleton service."""
        self.registry.register(
            interface,
            implementation,
            ServiceLifetime.SINGLETON,
            metadata=metadata,
        )

    def add_transient(
        self,
        interface: type,
        implementation: type,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a transient service."""
        self.registry.register(
            interface,
            implementation,
            ServiceLifetime.TRANSIENT,
            metadata=metadata,
        )

    def add_scoped(
        self,
        interface: type,
        implementation: type,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a scoped service."""
        self.registry.register(
            interface,
            implementation,
            ServiceLifetime.SCOPED,
            metadata=metadata,
        )

    def add_instance(
        self,
        interface: type,
        instance: Any,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a pre-existing singleton instance."""
        self.registry.register_instance(
            interface,
            instance,
            metadata=metadata,
        )

    def add_factory(
        self,
        interface: type,
        factory: Callable[..., Any],
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
        metadata: dict[str, Any] | None = None,
    ) -> None:
        """Register a factory callable for a service interface."""
        self.registry.register_factory(
            interface,
            factory,
            lifetime=lifetime,
            metadata=metadata,
        )

    def create_scope(self) -> Scope:
        """Create a new dependency injection scope."""
        return Scope(
            registry=self.registry,
            builder=self.builder,
        )

    def resolve(self, service_type: type) -> Any:
        """
        Resolve a registered service.

        Singleton services are cached by the root container.
        Scoped services must be resolved through a Scope.
        """
        if not self.registry.contains(service_type):
            raise ServiceNotFound(service_type.__name__)

        descriptor = self.registry.get(service_type)

        # Scoped services cannot be resolved from root
        if descriptor.lifetime == ServiceLifetime.SCOPED:
            raise RuntimeError(
                "Scoped services must be resolved from a Scope."
            )

        # Singleton lifetime
        if descriptor.lifetime == ServiceLifetime.SINGLETON:
            if descriptor.instance is None:
                descriptor.instance = self._build_descriptor(descriptor)
            return descriptor.instance

        # Transient lifetime
        return self._build_descriptor(descriptor)

    def resolve_optional(self, service_type: type, default: Any = None) -> Any:
        """
        Resolve a service if registered; otherwise return default.
        """
        if not self.registry.contains(service_type):
            return default
        try:
            return self.resolve(service_type)
        except ServiceNotFound:
            return default

    def wire_graph(self, root_types: list[type] | None = None) -> dict[type, Any]:
        """
        Wire and resolve the complete application object graph.
        If root_types is None, resolves all registered singleton services.
        """
        if root_types is None:
            root_types = [
                d.interface
                for d in self.registry.descriptors()
                if d.lifetime == ServiceLifetime.SINGLETON
            ]
        return self.builder.wire_graph(root_types)

    def _build_descriptor(self, descriptor: Any) -> Any:
        """Instantiate a descriptor using its factory, provider, or implementation."""
        if descriptor.instance is not None:
            return descriptor.instance

        if descriptor.factory is not None:
            return self.builder.build_factory(descriptor.factory)

        if descriptor.provider is not None:
            if isinstance(descriptor.provider, InstanceProvider):
                return descriptor.provider.instance
            if isinstance(descriptor.provider, FactoryProvider):
                return self.builder.build_factory(descriptor.provider.factory)
            if isinstance(descriptor.provider, ConstructorProvider):
                return self.builder.build(descriptor.provider.implementation)
            return descriptor.provider.provide(self.resolve)

        if descriptor.implementation is not None:
            return self.builder.build(descriptor.implementation)

        raise ResolutionError(f"No implementation or factory defined for {descriptor.interface.__name__}")

    def dispose(self) -> None:
        """
        Dispose the root container and all singleton instances that support disposal.
        """
        if self._disposed:
            return

        for descriptor in self.registry.descriptors():
            if descriptor.instance is not None:
                inst = descriptor.instance
                if hasattr(inst, "dispose") and callable(inst.dispose):
                    try:
                        inst.dispose()
                    except Exception:
                        pass
                elif hasattr(inst, "close") and callable(inst.close):
                    try:
                        inst.close()
                    except Exception:
                        pass
                descriptor.instance = None

        self._disposed = True

    def __enter__(self) -> Container:
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        self.dispose()

    @property
    def services(self) -> ServiceRegistry:
        """
        Exposes the service registry.
        Intended for framework diagnostics and unit testing.
        """
        return self.registry


__all__ = [
    "Container",
]