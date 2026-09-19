"""
ScholarOS Tools Subsystem.

Provides base abstractions, manifests, managers, and functional wrappers
for tools callable by agents and plugins.
"""

from __future__ import annotations

from scholaros.tools.loader import ToolLoader
from scholaros.tools.manager import ToolManager
from scholaros.tools.manifest import ToolManifest
from scholaros.tools.registry import ToolRegistry
from scholaros.tools.result import ToolResult
from scholaros.tools.tool import FunctionTool, Tool

__all__ = [
    "FunctionTool",
    "Tool",
    "ToolLoader",
    "ToolManager",
    "ToolManifest",
    "ToolRegistry",
    "ToolResult",
]
