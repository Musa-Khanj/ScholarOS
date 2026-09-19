"""
ScholarOS Container Dependency Resolver.

Responsible for:
- Constructor parameter inspection and dependency resolution
- Dependency graph traversal
- Circular dependency detection
- Automatic resolution of object instances and factory callables
"""

from __future__ import annotations

from collections.abc import Callable
import inspect
from typing import Any, get_type_hints

from scholaros.container.exceptions import (
    CircularDependencyError,
    InvalidServiceError,
)

ResolverFunc = Callable[[type], Any]


class DependencyResolver:
    """
    Resolves dependencies, traverses dependency graphs, and detects cycles.
    """

    def __init__(self) -> None:
        self._resolution_stack: list[type] = []
        self._signature_cache: dict[type, inspect.Signature] = {}
        self._parameter_cache: dict[type, list[inspect.Parameter]] = {}
        self._type_hints_cache: dict[type, dict[str, Any]] = {}

    @property
    def resolution_stack(self) -> tuple[type, ...]:
        """Return the current resolution stack as a tuple."""
        return tuple(self._resolution_stack)

    def enter_resolution(self, service_type: type) -> None:
        """
        Record entry into resolving a service type.

        Raises
        ------
        CircularDependencyError
            If service_type is already in the resolution stack.
        """
        if service_type in self._resolution_stack:
            cycle = " -> ".join(
                cls.__name__ for cls in (*self._resolution_stack, service_type)
            )
            raise CircularDependencyError(cycle)
        self._resolution_stack.append(service_type)

    def exit_resolution(self) -> None:
        """Exit the current resolution level."""
        if self._resolution_stack:
            self._resolution_stack.pop()

    def get_signature(self, implementation: type) -> inspect.Signature:
        """Return cached constructor signature."""
        sig = self._signature_cache.get(implementation)
        if sig is None:
            sig = inspect.signature(implementation)
            self._signature_cache[implementation] = sig
        return sig

    def get_parameters(self, implementation: type) -> list[inspect.Parameter]:
        """
        Return cached constructor parameters, excluding self, *args, and **kwargs.
        """
        params = self._parameter_cache.get(implementation)
        if params is None:
            sig = self.get_signature(implementation)
            params = [
                param
                for param in sig.parameters.values()
                if (
                    param.name != "self"
                    and param.kind
                    not in (
                        inspect.Parameter.VAR_POSITIONAL,
                        inspect.Parameter.VAR_KEYWORD,
                    )
                )
            ]
            self._parameter_cache[implementation] = params
        return params

    def get_type_hints(self, implementation: type) -> dict[str, Any]:
        """Return cached constructor type hints."""
        hints = self._type_hints_cache.get(implementation)
        if hints is None:
            init_fn = getattr(implementation, "__init__", None)
            if init_fn is not None:
                try:
                    hints = get_type_hints(init_fn)
                except Exception:
                    hints = {}
            else:
                hints = {}
            self._type_hints_cache[implementation] = hints
        return hints

    def resolve_parameters(
        self,
        implementation: type,
        resolver_func: ResolverFunc,
    ) -> dict[str, Any]:
        """
        Resolve constructor parameters for the given implementation.

        Parameters with default values are skipped.
        """
        parameters = self.get_parameters(implementation)
        type_hints = self.get_type_hints(implementation)
        kwargs: dict[str, Any] = {}

        for parameter in parameters:
            annotation = type_hints.get(parameter.name, parameter.annotation)

            if annotation is inspect.Parameter.empty:
                raise InvalidServiceError(
                    f"{implementation.__name__}.{parameter.name} has no type annotation."
                )

            # Skip parameters with defaults
            if parameter.default is not inspect.Parameter.empty:
                continue

            kwargs[parameter.name] = resolver_func(annotation)

        return kwargs

    def instantiate(
        self,
        implementation: type,
        resolver_func: ResolverFunc,
    ) -> Any:
        """
        Instantiate an implementation with constructor injection and cycle detection.
        """
        self.enter_resolution(implementation)
        try:
            kwargs = self.resolve_parameters(implementation, resolver_func)
            return implementation(**kwargs)
        finally:
            self.exit_resolution()

    def get_dependencies(self, implementation: type) -> list[type]:
        """
        Extract required dependency types for a given implementation without resolving them.
        """
        parameters = self.get_parameters(implementation)
        type_hints = self.get_type_hints(implementation)
        deps: list[type] = []

        for parameter in parameters:
            if parameter.default is not inspect.Parameter.empty:
                continue
            annotation = type_hints.get(parameter.name, parameter.annotation)
            if isinstance(annotation, type):
                deps.append(annotation)
        return deps

    def traverse_graph(
        self,
        root: type,
        dependency_provider: Callable[[type], list[type]],
    ) -> list[type]:
        """
        Topological / dependency-order traversal of the dependency graph starting from root.
        Returns dependencies in instantiation order (deepest dependencies first).
        """
        visited: set[type] = set()
        visiting: set[type] = set()
        order: list[type] = []

        def dfs(node: type) -> None:
            if node in visiting:
                raise CircularDependencyError(f"Cycle detected involving {node.__name__}")
            if node in visited:
                return

            visiting.add(node)
            for dep in dependency_provider(node):
                dfs(dep)
            visiting.remove(node)
            visited.add(node)
            order.append(node)

        dfs(root)
        return order


__all__ = [
    "DependencyResolver",
]
