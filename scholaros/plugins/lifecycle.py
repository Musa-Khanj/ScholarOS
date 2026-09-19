"""
ScholarOS Plugin Lifecycle.

Centralizes and enforces all plugin lifecycle transitions:
DISCOVERED -> LOADED -> INITIALIZED -> STARTED -> STOPPED -> UNLOADED
"""

from __future__ import annotations

from enum import Enum
from typing import Final

from scholaros.plugins.exceptions import PluginLifecycleError


class PluginState(str, Enum):
    """
    Formal lifecycle states for a ScholarOS plugin.
    """

    DISCOVERED = "discovered"
    LOADED = "loaded"
    INITIALIZED = "initialized"
    STARTED = "started"
    STOPPED = "stopped"
    UNLOADED = "unloaded"


# Valid state transitions mapping: current_state -> set of reachable states
VALID_TRANSITIONS: Final[dict[PluginState, frozenset[PluginState]]] = {
    PluginState.DISCOVERED: frozenset({PluginState.LOADED, PluginState.UNLOADED}),
    PluginState.LOADED: frozenset({PluginState.INITIALIZED, PluginState.UNLOADED}),
    PluginState.INITIALIZED: frozenset({PluginState.STARTED, PluginState.STOPPED, PluginState.UNLOADED}),
    PluginState.STARTED: frozenset({PluginState.STOPPED}),
    PluginState.STOPPED: frozenset({PluginState.STARTED, PluginState.UNLOADED}),
    PluginState.UNLOADED: frozenset({PluginState.DISCOVERED, PluginState.LOADED}),
}


class LifecycleTracker:
    """
    Manages and validates lifecycle state transitions for plugins.
    """

    def __init__(self) -> None:
        self._states: dict[str, PluginState] = {}

    def get_state(self, plugin_id: str) -> PluginState:
        """
        Get current lifecycle state of a plugin.
        Defaults to UNLOADED if not tracked.
        """
        return self._states.get(plugin_id, PluginState.UNLOADED)

    def is_state(self, plugin_id: str, state: PluginState) -> bool:
        """Check if plugin is in a specific state."""
        return self.get_state(plugin_id) == state

    def is_active(self, plugin_id: str) -> bool:
        """Check if plugin is currently started and active."""
        return self.get_state(plugin_id) == PluginState.STARTED

    def can_transition(self, plugin_id: str, target_state: PluginState) -> bool:
        """
        Check if transitioning to target_state is permitted from current state.
        """
        current_state = self.get_state(plugin_id)
        if current_state == target_state:
            return True
        allowed = VALID_TRANSITIONS.get(current_state, frozenset())
        return target_state in allowed

    def transition_to(self, plugin_id: str, target_state: PluginState) -> None:
        """
        Transition plugin to target_state or raise PluginLifecycleError.
        """
        current_state = self.get_state(plugin_id)
        if current_state == target_state:
            return

        allowed = VALID_TRANSITIONS.get(current_state, frozenset())
        if target_state not in allowed:
            raise PluginLifecycleError(
                f"Invalid lifecycle transition for plugin {plugin_id!r}: "
                f"cannot move from {current_state.value} to {target_state.value}."
            )

        self._states[plugin_id] = target_state

    def register_discovered(self, plugin_id: str) -> None:
        """Set initial discovered state."""
        self._states[plugin_id] = PluginState.DISCOVERED

    def remove(self, plugin_id: str) -> None:
        """Remove a plugin from tracking."""
        self._states.pop(plugin_id, None)

    def clear(self) -> None:
        """Clear all tracked states."""
        self._states.clear()

    def snapshot(self) -> dict[str, PluginState]:
        """Return a copy of all current plugin states."""
        return dict(self._states)


__all__ = [
    "LifecycleTracker",
    "PluginState",
    "VALID_TRANSITIONS",
]
