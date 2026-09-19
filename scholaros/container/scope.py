"""
ScholarOS Container Scope.

Represents a dependency injection scope.
A Scope manages scoped instances and their disposal lifecycle while sharing the
service registry and builder with the root container.
"""

from __future__ import annotations

from typing import Any

from scholaros.container.builder import Builder
from scholaros.container.exceptions import (
    ScopeDisposedError,
    ServiceNotFound,
)
from scholaros.container.lifetime import ServiceLifetime
from scholaros.container.registry import ServiceRegistry


class Scope:
    """
    Represents a dependency injection scope.

    Manages scoped instances, lifetime resolution, and disposal of scoped services.
    """

    def __init__(
        self,
        registry: ServiceRegistry,
        builder: Builder,
    ) -> None:
        self._registry = registry
        self._builder = builder
        self._instances: dict[type, Any] = {}
        self._disposed = False

    @property
    def is_disposed(self) -> bool:
        """Return True if this scope has been disposed."""
        return self._disposed

    def resolve(self, interface: type) -> Any:
        """
        Resolve a service within the current scope.

        Raises
        ------
        ScopeDisposedError
            If this scope has already been disposed.
        ServiceNotFound
            If the interface is not registered in the service registry.
        """
        if self._disposed:
            raise ScopeDisposedError(
                f"Cannot resolve '{interface.__name__}' from a disposed scope."
            )

        if not self._registry.contains(interface):
            raise ServiceNotFound(interface.__name__)

        descriptor = self._registry.get(interface)

        # Scoped lifetime: cache instance locally in this scope
        if descriptor.lifetime == ServiceLifetime.SCOPED:
            instance = self._instances.get(interface)
            if instance is None:
                instance = self._build_instance(descriptor)
                self._instances[interface] = instance
            return instance

        # Transient lifetime: build a fresh instance every time
        if descriptor.lifetime == ServiceLifetime.TRANSIENT:
            return self._build_instance(descriptor)

        # Singleton lifetime: cached at the root descriptor/container level
        if descriptor.instance is None:
            descriptor.instance = self._build_instance(descriptor)
        return descriptor.instance

    def _build_instance(self, descriptor: Any) -> Any:
        """Construct an instance using the descriptor's factory, provider, or implementation."""
        if descriptor.factory is not None:
            return self._builder.build_factory(descriptor.factory)
        if descriptor.provider is not None:
            # Delegate directly through builder.build if ConstructorProvider
            from scholaros.container.provider import ConstructorProvider, FactoryProvider, InstanceProvider

            if isinstance(descriptor.provider, InstanceProvider):
                return descriptor.provider.instance
            if isinstance(descriptor.provider, FactoryProvider):
                return self._builder.build_factory(descriptor.provider.factory)
            if isinstance(descriptor.provider, ConstructorProvider):
                return self._builder.build(descriptor.provider.implementation)
            return descriptor.provider.provide(self.resolve)

        if descriptor.implementation is not None:
            return self._builder.build(descriptor.implementation)

        raise ServiceNotFound(descriptor.interface.__name__)

    def dispose(self) -> None:
        """
        Dispose the current scope.

        Calls dispose() or close() on any scoped instances that support it,
        clears all scoped instances, and marks this scope as disposed.
        """
        if self._disposed:
            return

        for instance in list(self._instances.values()):
            if hasattr(instance, "dispose") and callable(instance.dispose):
                try:
                    instance.dispose()
                except Exception:
                    pass
            elif hasattr(instance, "close") and callable(instance.close):
                try:
                    instance.close()
                except Exception:
                    pass

        self._instances.clear()
        self._disposed = True

    def __enter__(self) -> Scope:
        """Enter the scope context."""
        return self

    def __exit__(
        self,
        exc_type: type | None,
        exc_value: BaseException | None,
        traceback: object | None,
    ) -> None:
        """Exit the scope context and dispose resources."""
        self.dispose()

    @property
    def instances(self) -> dict[type, Any]:
        """
        Exposes the scoped instance cache.
        Intended for framework diagnostics and unit testing.
        """
        return self._instances


__all__ = [
    "Scope",
]