"""
ScholarOS
Command Bus

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Provides the command dispatching infrastructure
for ScholarOS.

Unlike events, commands represent requests to
perform an action.

Each command has exactly one handler.

Examples
--------
- OpenChatCommand
- SearchCommand
- RunPluginCommand
- GenerateAnswerCommand
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

#
# ============================================================
# Command
# ============================================================
#


@dataclass(slots=True)
class Command:
    """
    Represents a command.

    Parameters
    ----------
    name:
        Command name.

    payload:
        Command payload.

    metadata:
        Optional metadata.
    """

    name: str

    payload: dict[str, Any] = field(
        default_factory=dict,
    )

    metadata: dict[str, Any] = field(
        default_factory=dict,
    )

    def __post_init__(
        self,
    ) -> None:
        """
        Validate command.
        """

        if not self.name.strip():
            raise ValueError(
                "Command name cannot be empty."
            )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"name={self.name!r}, "
            f"payload={self.payload!r}"
            f")"
        )


#
# ============================================================
# Command Bus
# ============================================================
#


CommandHandler = Callable[[Command], Any]


class CommandBus:
    """
    Executes application commands.

    Exactly one handler is registered
    for each command name.
    """

    def __init__(
        self,
    ) -> None:

        self._handlers: dict[
            str,
            CommandHandler,
        ] = {}

    #
    # --------------------------------------------------------
    # Registration
    # --------------------------------------------------------
    #

    def register(
        self,
        command_name: str,
        handler: CommandHandler,
    ) -> None:
        """
        Register a command handler.
        """

        if not command_name.strip():
            raise ValueError(
                "Command name cannot be empty."
            )

        if not callable(handler):
            raise TypeError(
                "Handler must be callable."
            )

        if command_name in self._handlers:
            raise ValueError(
                f"Handler already registered for "
                f"{command_name!r}."
            )

        self._handlers[
            command_name
        ] = handler

    def unregister(
        self,
        command_name: str,
    ) -> bool:
        """
        Remove a handler.

        Returns
        -------
        bool
            True if removed.
        """

        return (
            self._handlers.pop(
                command_name,
                None,
            )
            is not None
        )

    #
    # --------------------------------------------------------
    # Execution
    # --------------------------------------------------------
    #

    def execute(
        self,
        command: Command,
    ) -> Any:
        """
        Execute a command.

        Returns
        -------
        Any
            Handler result.
        """

        if not isinstance(
            command,
            Command,
        ):
            raise TypeError(
                "execute() expects Command."
            )

        handler = self._handlers.get(
            command.name,
        )

        if handler is None:
            raise LookupError(
                f"No handler registered for "
                f"{command.name!r}."
            )

        return handler(
            command,
        )

    #
    # --------------------------------------------------------
    # Introspection
    # --------------------------------------------------------
    #

    def has_handler(
        self,
        command_name: str,
    ) -> bool:
        """
        Return True if handler exists.
        """

        return (
            command_name
            in self._handlers
        )

    def handlers(
        self,
    ) -> dict[
        str,
        CommandHandler,
    ]:
        """
        Return registered handlers.

        A shallow copy is returned.
        """

        return dict(
            self._handlers,
        )

    def command_names(
        self,
    ) -> tuple[str, ...]:
        """
        Return registered command names.
        """

        return tuple(
            sorted(
                self._handlers.keys(),
            )
        )

    #
    # --------------------------------------------------------
    # Utilities
    # --------------------------------------------------------
    #

    def clear(
        self,
    ) -> None:
        """
        Remove all handlers.
        """

        self._handlers.clear()

    #
    # --------------------------------------------------------
    # Dunder methods
    # --------------------------------------------------------
    #

    def __contains__(
        self,
        command_name: object,
    ) -> bool:

        if not isinstance(
            command_name,
            str,
        ):
            return False

        return self.has_handler(
            command_name,
        )

    def __len__(
        self,
    ) -> int:

        return len(
            self._handlers,
        )

    def __repr__(
        self,
    ) -> str:
        """
        Developer representation.
        """

        return (
            f"{self.__class__.__name__}("
            f"handlers={len(self)}"
            f")"
        )