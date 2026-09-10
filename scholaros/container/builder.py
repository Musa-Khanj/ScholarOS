"""
ScholarOS Container Builder.

Responsible for wiring the complete application object graph through constructor
and factory dependency injection, delegating cycle detection and reflection
to DependencyResolver.
"""

from __future__ import annotations

from collections.abc import Callable
import inspect
from typing import Any, TypeAlias

from scholaros.container.exceptions import (
    ResolutionError,
)
from scholaros.container.resolver import DependencyResolver

Resolver: TypeAlias = Callable[[type], Any]


class Builder:
    """
    Wires and constructs dependency graphs for registered services.

    Coordinates object construction via DependencyResolver.
    Aware of object graph topology, constructor parameters, and factory execution.
    """

    def __init__(
        self,
        resolver: Resolver,
        dependency_resolver: DependencyResolver | None = None,
    ) -> None:
        """
        Initialize the Builder.

        Parameters
        ----------
        resolver:
            Function used to resolve dependencies from the container.
        dependency_resolver:
            Optional DependencyResolver instance; creates a new one if not provided.
        """
        self._resolver = resolver
        self._dependency_resolver = dependency_resolver or DependencyResolver()

    @property
    def dependency_resolver(self) -> DependencyResolver:
        """Return the underlying DependencyResolver."""
        return self._dependency_resolver

    def build(self, implementation: type) -> Any:
        """
        Construct an instance of the given implementation using constructor injection.
        """
        return self._dependency_resolver.instantiate(implementation, self._resolver)

    def build_factory(self, factory: Callable[..., Any], **kwargs: Any) -> Any:
        """
        Invoke a factory callable, resolving type-annotated or name-matched parameters through the container.
        """
        sig = inspect.signature(factory)
        resolved_kwargs = dict(kwargs)

        for param in sig.parameters.values():
            if param.kind in (inspect.Parameter.VAR_POSITIONAL, inspect.Parameter.VAR_KEYWORD):
                continue
            if param.name in resolved_kwargs:
                continue
            if param.default is not inspect.Parameter.empty:
                continue

            # First, check type annotation if provided
            if param.annotation is not inspect.Parameter.empty and isinstance(param.annotation, type):
                resolved_kwargs[param.name] = self._resolver(param.annotation)
            else:
                # If no annotation, check if resolver knows about container registry via attribute
                container_ref = getattr(self._resolver, "__self__", None)
                if container_ref is not None and hasattr(container_ref, "registry"):
                    matched_type = container_ref.registry.find_by_name(param.name)
                    if matched_type is not None:
                        resolved_kwargs[param.name] = self._resolver(matched_type)

        return factory(**resolved_kwargs)


    def wire_graph(self, root_types: list[type]) -> dict[type, Any]:
        """
        Wire and instantiate the complete dependency graph for a list of root service types.
        Returns a dictionary mapping each type to its constructed/resolved instance.
        """
        instances: dict[type, Any] = {}
        for root in root_types:
            instances[root] = self._resolver(root)
        return instances

    # Backwards compatibility helpers delegating to dependency_resolver
    def _enter_build(self, implementation: type) -> None:
        self._dependency_resolver.enter_resolution(implementation)

    def _exit_build(self) -> None:
        self._dependency_resolver.exit_resolution()

    def _get_signature(self, implementation: type) -> inspect.Signature:
        return self._dependency_resolver.get_signature(implementation)

    def _get_parameters(self, implementation: type) -> list[inspect.Parameter]:
        return self._dependency_resolver.get_parameters(implementation)

    def _get_type_hints(self, implementation: type) -> dict[str, Any]:
        return self._dependency_resolver.get_type_hints(implementation)

    def _resolve_parameters(self, implementation: type) -> dict[str, Any]:
        return self._dependency_resolver.resolve_parameters(implementation, self._resolver)


__all__ = [
    "Builder",
    "Resolver",
]