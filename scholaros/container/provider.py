"""
ScholarOS Container Service Providers.

Provides service factory abstractions, lazy creation mechanisms,
and factory-based registration providers for dependency injection.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
import inspect
import threading
from typing import Any, Callable, Generic, TypeVar

from scholaros.container.lifetime import ServiceLifetime

T = TypeVar("T")
ResolverFunc = Callable[[type], Any]


class ServiceProvider(ABC, Generic[T]):
    """
    Abstract base class for service providers.
    Encapsulates how an instance of a service is constructed or retrieved.
    """

    @property
    @abstractmethod
    def lifetime(self) -> ServiceLifetime:
        """Return the lifetime classification of this provider."""
        raise NotImplementedError

    @abstractmethod
    def provide(self, resolver: ResolverFunc, **kwargs: Any) -> T:
        """
        Produce or retrieve an instance of the service.
        """
        raise NotImplementedError


class InstanceProvider(ServiceProvider[T]):
    """
    Provides a pre-existing singleton instance.
    """

    def __init__(self, instance: T) -> None:
        self._instance = instance

    @property
    def lifetime(self) -> ServiceLifetime:
        return ServiceLifetime.SINGLETON

    @property
    def instance(self) -> T:
        return self._instance

    def provide(self, resolver: ResolverFunc, **kwargs: Any) -> T:
        return self._instance

    def __repr__(self) -> str:
        return f"InstanceProvider(instance={self._instance!r})"


class FactoryProvider(ServiceProvider[T]):
    """
    Provides a service instance by invoking a registered factory callable.
    Automatically inspects factory parameters to inject registered dependencies.
    """

    def __init__(
        self,
        factory: Callable[..., T],
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
    ) -> None:
        self._factory = factory
        self._lifetime = lifetime
        self._parameters: list[inspect.Parameter] | None = None

    @property
    def lifetime(self) -> ServiceLifetime:
        return self._lifetime

    @property
    def factory(self) -> Callable[..., T]:
        return self._factory

    def provide(self, resolver: ResolverFunc, **kwargs: Any) -> T:
        if self._parameters is None:
            sig = inspect.signature(self._factory)
            self._parameters = [
                p for p in sig.parameters.values()
                if p.kind not in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD)
            ]

        # If explicit kwargs provided, prefer them
        resolved_kwargs = dict(kwargs)
        for param in self._parameters:
            if param.name in resolved_kwargs:
                continue
            if param.annotation is not inspect.Parameter.empty and isinstance(param.annotation, type):
                resolved_kwargs[param.name] = resolver(param.annotation)

        return self._factory(**resolved_kwargs)

    def __repr__(self) -> str:
        return f"FactoryProvider(factory={self._factory!r}, lifetime={self._lifetime})"


class ConstructorProvider(ServiceProvider[T]):
    """
    Provides service instances by delegating construction through constructor injection.
    """

    def __init__(
        self,
        implementation: type[T],
        lifetime: ServiceLifetime = ServiceLifetime.TRANSIENT,
    ) -> None:
        self._implementation = implementation
        self._lifetime = lifetime

    @property
    def lifetime(self) -> ServiceLifetime:
        return self._lifetime

    @property
    def implementation(self) -> type[T]:
        return self._implementation

    def provide(self, resolver: ResolverFunc, **kwargs: Any) -> T:
        # Resolver will perform reflection and constructor injection
        instance = resolver(self._implementation)
        return instance  # type: ignore[no-any-return]

    def __repr__(self) -> str:
        return f"ConstructorProvider(implementation={self._implementation.__name__}, lifetime={self._lifetime})"


class LazyProvider(ServiceProvider[T]):
    """
    Wraps another provider to enable lazy, thread-safe creation on first access.
    """

    def __init__(self, inner: ServiceProvider[T]) -> None:
        self._inner = inner
        self._instance: T | None = None
        self._lock = threading.Lock()
        self._initialized = False

    @property
    def lifetime(self) -> ServiceLifetime:
        return self._inner.lifetime

    @property
    def is_created(self) -> bool:
        return self._initialized

    def provide(self, resolver: ResolverFunc, **kwargs: Any) -> T:
        if self._inner.lifetime == ServiceLifetime.SINGLETON:
            if not self._initialized:
                with self._lock:
                    if not self._initialized:
                        self._instance = self._inner.provide(resolver, **kwargs)
                        self._initialized = True
            return self._instance  # type: ignore[return-value]

        # Non-singleton delegates to inner provider on each call
        return self._inner.provide(resolver, **kwargs)

    def __repr__(self) -> str:
        return f"LazyProvider(inner={self._inner!r}, created={self._initialized})"


__all__ = [
    "ConstructorProvider",
    "FactoryProvider",
    "InstanceProvider",
    "LazyProvider",
    "ServiceProvider",
]
