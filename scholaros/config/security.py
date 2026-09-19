"""
ScholarOS Configuration Security & Sensitive Value Handling.

Provides utilities for masking and securely handling sensitive configuration
values such as API keys, tokens, and secrets.
"""

from __future__ import annotations

from typing import Any


def mask_secret(
    value: str | None,
    visible_start: int = 3,
    visible_end: int = 4,
) -> str:
    """
    Mask a sensitive string value for safe logging or UI display.

    Parameters
    ----------
    value : str | None
        The sensitive string to mask.
    visible_start : int
        Number of leading characters to leave visible.
    visible_end : int
        Number of trailing characters to leave visible.

    Returns
    -------
    str
        Masked string representation, or empty string if None or empty.
    """
    if not value:
        return ""

    val = str(value)
    length = len(val)

    # For short strings, redact completely to avoid leaking character distribution
    if length <= (visible_start + visible_end):
        return "***"

    start = val[:visible_start]
    end = val[-visible_end:]
    return f"{start}***{end}"


class SecretStr:
    """
    Container for sensitive strings that prevents accidental leakage in
    repr, str, or log outputs.
    """

    __slots__ = ("_secret",)

    def __init__(self, secret: str) -> None:
        self._secret = str(secret)

    def get_secret_value(self) -> str:
        """Return the underlying unmasked secret value."""
        return self._secret

    def __repr__(self) -> str:
        return f"SecretStr('{mask_secret(self._secret)}')"

    def __str__(self) -> str:
        return mask_secret(self._secret)

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, SecretStr):
            return self._secret == other._secret
        if isinstance(other, str):
            return self._secret == other
        return False

    def __hash__(self) -> int:
        return hash(self._secret)

    def __len__(self) -> int:
        return len(self._secret)

    def __bool__(self) -> bool:
        return bool(self._secret)


__all__ = [
    "SecretStr",
    "mask_secret",
]
