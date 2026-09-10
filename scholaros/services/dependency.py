"""
ScholarOS Service Dependency Resolver.

Computes topological startup and shutdown sequences, validates dependency
completeness, and detects circular service dependencies.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import TYPE_CHECKING, Iterable, Mapping

from scholaros.services.exceptions import (
    CircularServiceDependencyError,
    ServiceDependencyError,
)

if TYPE_CHECKING:
    from scholaros.services.descriptor import ServiceDescriptor


class ServiceDependencyResolver:
    """
    Resolves dependency graphs between services.
    """

    def resolve_startup_order(
        self,
        service_dependencies: Mapping[str, Iterable[str]],
    ) -> list[str]:
        """
        Compute startup sequence in topological order using Kahn's algorithm.
        Dependencies start before dependent services.

        Raises
        ------
        CircularServiceDependencyError
            If a cycle is detected.
        ServiceDependencyError
            If a required dependency is missing.
        """
        # Validate that all required dependencies exist in the mapping
        available = set(service_dependencies.keys())
        for name, deps in service_dependencies.items():
            missing = set(deps) - available
            if missing:
                missing_str = ", ".join(sorted(missing))
                raise ServiceDependencyError(
                    f"Service '{name}' requires unsatisfied dependencies: {missing_str}."
                )

        # Build in-degree counts and adjacency list
        in_degree: dict[str, int] = {name: 0 for name in service_dependencies}
        dependents: dict[str, set[str]] = defaultdict(set)

        for name, deps in service_dependencies.items():
            for dep in deps:
                if dep == name:
                    raise CircularServiceDependencyError(
                        f"Self-referencing dependency detected for service '{name}'."
                    )
                in_degree[name] += 1
                dependents[dep].add(name)

        # Queue nodes with in_degree == 0 (no dependencies)
        queue: deque[str] = deque(sorted([name for name, deg in in_degree.items() if deg == 0]))
        order: list[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)

            for dependent in sorted(dependents[node]):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(order) < len(service_dependencies):
            unresolved = set(service_dependencies.keys()) - set(order)
            unresolved_str = ", ".join(sorted(unresolved))
            raise CircularServiceDependencyError(
                f"Circular dependency detected involving services: {unresolved_str}."
            )

        return order

    def resolve_shutdown_order(
        self,
        service_dependencies: Mapping[str, Iterable[str]],
    ) -> list[str]:
        """
        Compute shutdown sequence in reverse topological order.
        Dependent services stop before the services they depend on.
        """
        startup = self.resolve_startup_order(service_dependencies)
        return list(reversed(startup))


__all__ = [
    "ServiceDependencyResolver",
]
