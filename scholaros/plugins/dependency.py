"""
ScholarOS Plugin Dependency Resolver.

Resolves plugin dependency graphs, computes deterministic startup and
shutdown orders, and detects circular or unsatisfied dependencies.
"""

from __future__ import annotations

from collections import defaultdict, deque
from typing import Iterable, Mapping


from scholaros.plugins.exceptions import CircularDependencyError, DependencyError


class DependencyGraph:
    """
    Directed graph representing plugin dependencies.
    """

    def __init__(self) -> None:
        # plugin_id -> set of dependencies that this plugin requires
        self._dependencies: dict[str, set[str]] = {}

    def add_plugin(self, plugin_id: str, dependencies: Iterable[str] | None = None) -> None:
        """
        Add a plugin node and its required dependencies.
        """
        deps = set(dependencies or [])
        # Avoid self-dependency cycle
        if plugin_id in deps:
            raise CircularDependencyError(
                f"Self-referencing dependency detected for plugin {plugin_id!r}."
            )
        self._dependencies[plugin_id] = deps

    def remove_plugin(self, plugin_id: str) -> None:
        """Remove a plugin and any references to it."""
        self._dependencies.pop(plugin_id, None)
        for deps in self._dependencies.values():
            deps.discard(plugin_id)

    def get_dependencies(self, plugin_id: str) -> set[str]:
        """Return the immediate dependencies for a plugin."""
        return set(self._dependencies.get(plugin_id, set()))

    def validate_dependencies(self, available_ids: Iterable[str]) -> None:
        """
        Verify that all required dependencies exist in available_ids.
        Raises DependencyError if any are missing.
        """
        available = set(available_ids)
        for plugin_id, deps in self._dependencies.items():
            missing = deps - available
            if missing:
                missing_str = ", ".join(sorted(missing))
                raise DependencyError(
                    f"Plugin {plugin_id!r} requires missing dependencies: {missing_str}."
                )

    def detect_cycles(self) -> list[list[str]]:
        """
        Find cycles in the dependency graph using Tarjan's or DFS cycle detection.
        Returns a list of cycles found.
        """
        visited: dict[str, int] = {}  # 0: unvisited, 1: visiting, 2: visited
        cycles: list[list[str]] = []
        path: list[str] = []

        def dfs(node: str) -> None:
            visited[node] = 1
            path.append(node)

            for neighbor in self._dependencies.get(node, ()):
                if neighbor not in self._dependencies:
                    continue
                if visited.get(neighbor, 0) == 1:
                    # Found cycle
                    cycle_start = path.index(neighbor)
                    cycles.append(path[cycle_start:] + [neighbor])
                elif visited.get(neighbor, 0) == 0:
                    dfs(neighbor)

            path.pop()
            visited[node] = 2

        for node in list(self._dependencies):
            if visited.get(node, 0) == 0:
                dfs(node)

        return cycles

    def resolve_order(self) -> list[str]:
        """
        Compute deterministic startup order using topological sorting (Kahn's algorithm).
        Dependencies come before the plugins that depend on them.
        """
        cycles = self.detect_cycles()
        if cycles:
            first_cycle = " -> ".join(cycles[0])
            raise CircularDependencyError(
                f"Circular dependency detected: {first_cycle}"
            )

        # in_degree: number of unsatisfied dependencies for each plugin
        in_degree: dict[str, int] = {}
        # dependents: dependency -> plugins that depend on it
        dependents: dict[str, set[str]] = defaultdict(set)

        for plugin_id, deps in self._dependencies.items():
            # Only count dependencies that are inside the graph
            internal_deps = {d for d in deps if d in self._dependencies}
            in_degree[plugin_id] = len(internal_deps)
            for dep in internal_deps:
                dependents[dep].add(plugin_id)

        # Queue nodes with in_degree == 0 (no dependencies)
        queue: deque[str] = deque(sorted([p for p, deg in in_degree.items() if deg == 0]))
        order: list[str] = []

        while queue:
            node = queue.popleft()
            order.append(node)

            for dependent in sorted(dependents[node]):
                in_degree[dependent] -= 1
                if in_degree[dependent] == 0:
                    queue.append(dependent)

        if len(order) < len(self._dependencies):
            # Graph has cycle that wasn't caught by DFS
            remaining = set(self._dependencies) - set(order)
            raise CircularDependencyError(
                f"Cyclic dependency prevented ordering for plugins: {remaining}"
            )

        return order

    def resolve_shutdown_order(self) -> list[str]:
        """
        Return the shutdown sequence (reverse of startup order).
        Dependent plugins are stopped before the plugins they depend on.
        """
        startup = self.resolve_order()
        return list(reversed(startup))

    def clear(self) -> None:
        """Clear all dependencies."""
        self._dependencies.clear()


class DependencyResolver:
    """
    High-level resolver providing dependency resolution convenience methods.
    """

    def __init__(self) -> None:
        self.graph = DependencyGraph()

    def add(self, plugin_id: str, dependencies: Iterable[str] | None = None) -> None:
        """Add a plugin and its dependencies."""
        self.graph.add_plugin(plugin_id, dependencies)

    def resolve(self, available_plugins: Mapping[str, Iterable[str]]) -> list[str]:
        """
        Build graph and return execution order for a dictionary/mapping of plugin_id -> dependencies.
        """
        self.graph.clear()
        for p_id, deps in available_plugins.items():
            self.graph.add_plugin(p_id, deps)

        self.graph.validate_dependencies(available_plugins.keys())
        return self.graph.resolve_order()



__all__ = [
    "DependencyGraph",
    "DependencyResolver",
]
