"""
ScholarOS AI Message Structures.

Defines typed conversation messages, roles, and serialization utilities.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class MessageRole(str, Enum):
    """Roles for messages exchanged with AI models."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"
    FUNCTION = "function"


# Shorthand alias
Role = MessageRole


@dataclass(slots=True, frozen=True)
class Message:
    """
    Typed message in an AI conversation.
    """

    role: MessageRole | str
    content: str
    name: str | None = None
    tool_call_id: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if isinstance(self.role, str):
            try:
                object.__setattr__(self, "role", MessageRole(self.role.lower()))
            except ValueError:
                pass

    @classmethod
    def system(cls, content: str, name: str | None = None) -> Message:
        """Create a system message."""
        return cls(role=MessageRole.SYSTEM, content=content, name=name)

    @classmethod
    def user(cls, content: str, name: str | None = None) -> Message:
        """Create a user message."""
        return cls(role=MessageRole.USER, content=content, name=name)

    @classmethod
    def assistant(cls, content: str, name: str | None = None) -> Message:
        """Create an assistant message."""
        return cls(role=MessageRole.ASSISTANT, content=content, name=name)

    @classmethod
    def tool(cls, content: str, tool_call_id: str, name: str | None = None) -> Message:
        """Create a tool result message."""
        return cls(role=MessageRole.TOOL, content=content, tool_call_id=tool_call_id, name=name)

    def to_dict(self) -> dict[str, Any]:
        """Convert message to dictionary representation."""
        role_val = self.role.value if isinstance(self.role, Enum) else str(self.role)
        d: dict[str, Any] = {"role": role_val, "content": self.content}
        if self.name is not None:
            d["name"] = self.name
        if self.tool_call_id is not None:
            d["tool_call_id"] = self.tool_call_id
        if self.metadata:
            d["metadata"] = self.metadata
        return d

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Message:
        """Construct Message from dictionary."""
        return cls(
            role=data["role"],
            content=data["content"],
            name=data.get("name"),
            tool_call_id=data.get("tool_call_id"),
            metadata=data.get("metadata", {}),
        )


__all__ = [
    "Message",
    "MessageRole",
    "Role",
]
