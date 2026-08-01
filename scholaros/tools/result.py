from __future__ import annotations

from dataclasses import dataclass
from dataclasses import field


@dataclass(slots=True, frozen=True)
class ToolResult:
    success: bool

    output: object | None = None

    error: str | None = None

    metadata: dict[str, object] = field(
        default_factory=dict,
    )