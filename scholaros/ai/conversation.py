"""
ScholarOS AI Conversation Management.

Manages message histories, sliding windows, and multi-turn dialogues.
"""

from __future__ import annotations

from typing import Any, Iterator

from scholaros.ai.message import Message, MessageRole
from scholaros.ai.tokenizer import Tokenizer


class Conversation:
    """
    A sequence of typed messages representing a multi-turn conversation.
    """

    def __init__(
        self,
        messages: list[Message] | None = None,
        system_prompt: str | None = None,
    ) -> None:
        self._messages: list[Message] = []
        if system_prompt:
            self._messages.append(Message.system(system_prompt))
        if messages:
            self._messages.extend(messages)

    def add_user(self, content: str, name: str | None = None) -> Message:
        """Append a user message and return it."""
        msg = Message.user(content, name=name)
        self._messages.append(msg)
        return msg

    def add_assistant(self, content: str, name: str | None = None) -> Message:
        """Append an assistant message and return it."""
        msg = Message.assistant(content, name=name)
        self._messages.append(msg)
        return msg

    def add_system(self, content: str) -> Message:
        """Prepend or append a system message."""
        msg = Message.system(content)
        # If first message is already system, replace it
        if self._messages and self._messages[0].role == MessageRole.SYSTEM:
            self._messages[0] = msg
        else:
            self._messages.insert(0, msg)
        return msg

    def append(self, message: Message) -> None:
        """Append an arbitrary message."""
        self._messages.append(message)

    @property
    def messages(self) -> list[Message]:
        """Return a copy of all conversation messages."""
        return list(self._messages)

    @property
    def last_message(self) -> Message | None:
        """Return the most recent message, if any."""
        return self._messages[-1] if self._messages else None

    def window(self, max_tokens: int, tokenizer: Tokenizer | None = None) -> list[Message]:
        """
        Return the most recent messages fitting within max_tokens, preserving system prompt.
        """
        tok = tokenizer or Tokenizer()
        if not self._messages:
            return []

        system_msg: Message | None = None
        other_msgs: list[Message] = []

        if self._messages[0].role == MessageRole.SYSTEM:
            system_msg = self._messages[0]
            other_msgs = self._messages[1:]
        else:
            other_msgs = list(self._messages)

        budget = max_tokens
        if system_msg:
            budget -= tok.count(system_msg.content) + 4

        selected: list[Message] = []
        for msg in reversed(other_msgs):
            msg_tokens = tok.count(msg.content) + 4
            if budget - msg_tokens >= 0:
                selected.insert(0, msg)
                budget -= msg_tokens
            else:
                break

        if system_msg:
            selected.insert(0, system_msg)

        return selected

    def clear(self) -> None:
        """Clear all messages."""
        self._messages.clear()

    def to_dict(self) -> list[dict[str, Any]]:
        """Serialize conversation to list of message dictionaries."""
        return [m.to_dict() for m in self._messages]

    @classmethod
    def from_dict(cls, data: list[dict[str, Any]]) -> Conversation:
        """Construct Conversation from serialized message dictionaries."""
        msgs = [Message.from_dict(d) for d in data]
        return cls(messages=msgs)

    def __len__(self) -> int:
        return len(self._messages)

    def __iter__(self) -> Iterator[Message]:
        return iter(self._messages)

    def __getitem__(self, index: int) -> Message:
        return self._messages[index]

    def __repr__(self) -> str:
        return f"Conversation(messages={len(self._messages)})"


__all__ = [
    "Conversation",
]
