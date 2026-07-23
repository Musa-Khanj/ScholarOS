from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from itertools import count
from typing import Any, Callable

_counter = count()


class Priority(IntEnum):
    CRITICAL = 0
    HIGH = 1
    NORMAL = 2
    LOW = 3
    BACKGROUND = 4


@dataclass(order=True, slots=True)
class Task:
    priority: Priority
    func: Callable[..., Any] = field(compare=False)
    args: tuple[Any, ...] = field(default_factory=tuple, compare=False)
    kwargs: dict[str, Any] = field(default_factory=dict, compare=False)
    order: int = field(default_factory=lambda: next(_counter))