"""
Tests for scholaros.core.commands
"""

from __future__ import annotations

import pytest

from scholaros.core.commands import (
    Command,
    CommandBus,
)

#
# ============================================================
# Command
# ============================================================
#


def test_command_name():
    """
    Command stores its name.
    """

    command = Command(
        name="search",
    )

    assert command.name == "search"


def test_command_payload_defaults():
    """
    Payload defaults to an empty dict.
    """

    command = Command(
        name="search",
    )

    assert command.payload == {}


def test_command_metadata_defaults():
    """
    Metadata defaults to an empty dict.
    """

    command = Command(
        name="search",
    )

    assert command.metadata == {}


def test_command_payload_assignment():
    """
    Payload is stored correctly.
    """

    payload = {
        "query": "AI",
    }

    command = Command(
        name="search",
        payload=payload,
    )

    assert command.payload == payload


def test_command_metadata_assignment():
    """
    Metadata is stored correctly.
    """

    metadata = {
        "user": "musa",
    }

    command = Command(
        name="search",
        metadata=metadata,
    )

    assert command.metadata == metadata


def test_empty_command_name_raises():
    """
    Empty names are rejected.
    """

    with pytest.raises(
        ValueError,
    ):
        Command(
            name="",
        )


def test_blank_command_name_raises():
    """
    Whitespace names are rejected.
    """

    with pytest.raises(
        ValueError,
    ):
        Command(
            name="   ",
        )


def test_command_repr():
    """
    repr() is developer friendly.
    """

    command = Command(
        name="search",
    )

    representation = repr(
        command,
    )

    assert representation.startswith(
        "Command("
    )


#
# ============================================================
# CommandBus
# ============================================================
#


def test_command_bus_initially_empty():
    """
    A new bus has no handlers.
    """

    bus = CommandBus()

    assert len(bus) == 0


def test_has_handler_initially_false():
    """
    No handlers exist initially.
    """

    bus = CommandBus()

    assert bus.has_handler(
        "search",
    ) is False


def test_command_names_initially_empty():
    """
    No registered command names.
    """

    bus = CommandBus()

    assert bus.command_names() == ()


def test_handlers_initially_empty():
    """
    handlers() returns an empty dict.
    """

    bus = CommandBus()

    assert bus.handlers() == {}