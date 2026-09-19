"""
ScholarOS Path Security & Safe File Handling.

Defends against path traversal attacks (e.g. `../`), symlink escapes,
unbounded file reads, and race-condition write vulnerabilities.
"""

from __future__ import annotations

import os
from pathlib import Path
import uuid

from scholaros.security.exceptions import PathTraversalError, SecurityError


def validate_safe_path(
    target: Path | str,
    base_dir: Path | str,
    allow_symlinks: bool = False,
) -> Path:
    """
    Validate that target path is safely contained within base_dir.

    Parameters
    ----------
    target : Path | str
        Target file or directory path.
    base_dir : Path | str
        The enclosing root boundary directory.
    allow_symlinks : bool
        Whether to permit symlinks resolving within base_dir.

    Returns
    -------
    Path
        Canonical, validated absolute Path.

    Raises
    ------
    PathTraversalError
        If target escapes the boundary of base_dir.
    """
    target_str = str(target)
    if "\0" in target_str:
        raise PathTraversalError("Null byte detected in path string.")

    base_resolved = Path(base_dir).resolve()
    target_path = Path(target)

    # If target is absolute, check containment directly; otherwise anchor to base_dir
    if target_path.is_absolute():
        resolved_target = target_path.resolve()
    else:
        resolved_target = (base_resolved / target_path).resolve()

    # Enforce boundary containment
    try:
        # relative_to will raise ValueError if resolved_target is not within base_resolved
        resolved_target.relative_to(base_resolved)
    except ValueError:
        raise PathTraversalError(
            f"Path traversal detected: '{target}' resolves outside boundary '{base_dir}'."
        )

    # Symlink verification if disallowed
    if not allow_symlinks and resolved_target.is_symlink():
        raise PathTraversalError(
            f"Symlink rejected for security policy: '{resolved_target}'."
        )

    return resolved_target


def safe_read_text(
    path: Path | str,
    base_dir: Path | str | None = None,
    max_bytes: int = 10_485_760,
    encoding: str = "utf-8",
) -> str:
    """
    Safely read text file within boundary constraints and size limits.

    Parameters
    ----------
    path : Path | str
        Path to file.
    base_dir : Path | str | None
        Optional boundary root directory.
    max_bytes : int
        Maximum permitted file size (default: 10MB) to prevent memory exhaustion attacks.
    encoding : str
        Character encoding.

    Returns
    -------
    str
        File text content.
    """
    target_path = validate_safe_path(path, base_dir) if base_dir is not None else Path(path).resolve()

    if not target_path.exists():
        raise FileNotFoundError(f"File not found: {target_path}")

    size = target_path.stat().st_size
    if size > max_bytes:
        raise SecurityError(
            f"File size ({size} bytes) exceeds safety limit of {max_bytes} bytes."
        )

    return target_path.read_text(encoding=encoding)


def safe_write_text(
    path: Path | str,
    content: str,
    base_dir: Path | str | None = None,
    atomic: bool = True,
    encoding: str = "utf-8",
) -> Path:
    """
    Safely write text to file with path validation and atomic write replacement.

    Parameters
    ----------
    path : Path | str
        Target file path.
    content : str
        String content to write.
    base_dir : Path | str | None
        Optional boundary root directory.
    atomic : bool
        If True, writes to temporary file and renames atomically to avoid partial corruption.
    encoding : str
        Character encoding.

    Returns
    -------
    Path
        Canonical path to written file.
    """
    target_path = validate_safe_path(path, base_dir) if base_dir is not None else Path(path).resolve()
    target_path.parent.mkdir(parents=True, exist_ok=True)

    if not atomic:
        target_path.write_text(content, encoding=encoding)
        return target_path

    # Atomic write using temporary file in same directory
    temp_name = f".tmp_{target_path.stem}_{uuid.uuid4().hex}.tmp"
    temp_path = target_path.parent / temp_name

    try:
        temp_path.write_text(content, encoding=encoding)
        # os.replace provides atomic rename on POSIX and Windows (Python 3.3+)
        os.replace(temp_path, target_path)
    finally:
        if temp_path.exists():
            try:
                temp_path.unlink()
            except Exception:
                pass

    return target_path


__all__ = [
    "safe_read_text",
    "safe_write_text",
    "validate_safe_path",
]
