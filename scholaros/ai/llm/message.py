from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class MessageRole(str, Enum):
    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"


@dataclass(slots=True, frozen=True)
class Message:
    role: MessageRole
    content: str