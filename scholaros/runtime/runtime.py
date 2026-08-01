"""
ScholarOS
Runtime

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents the runtime environment for
ScholarOS.

Responsibilities
----------------
• Own Planner
• Own Execution
• Own Workflow
• Own Memory
• Own PluginManager
"""

from __future__ import annotations

from scholaros.execution import Execution
from scholaros.memory import Memory
from scholaros.planner import Planner
from scholaros.plugins.manager import PluginManager
from scholaros.workflow import Workflow
from scholaros.tools.manager import ToolManager
class Runtime:
    """
    Represents the ScholarOS runtime.
    """

    def __init__(
        self,
        planner: Planner,
        execution: Execution,
        workflow: Workflow,
        memory: Memory,
        plugins: PluginManager,
        tools: ToolManager,
    ) -> None:
        """
        Initialize the runtime.
        """

        self._planner = planner
        self._execution = execution
        self._workflow = workflow
        self._memory = memory
        self._plugins = plugins
        self._tools = tools

    @property
    def planner(
        self,
    ) -> Planner:
        """
        Return the configured planner.
        """

        return self._planner

    @property
    def execution(
        self,
    ) -> Execution:
        """
        Return the configured execution
        engine.
        """

        return self._execution

    @property
    def workflow(
        self,
    ) -> Workflow:
        """
        Return the configured workflow.
        """

        return self._workflow

    @property
    def tools(
        self,
    ) -> ToolManager:
        """
        Return the configured tool manager.
        """

        return self._tools

    @property
    def memory(
        self,
    ) -> Memory:
        """
        Return the configured runtime
        memory.
        """

        return self._memory

    @property
    def plugins(
        self,
    ) -> PluginManager:
        """
        Return the configured plugin
        manager.
        """

        return self._plugins

    def run(
        self,
    ) -> object:
        """
        Run the configured runtime.
        """

        return self._planner.plan()

    def __repr__(
        self,
    ) -> str:
        """
        Return a developer-friendly
        representation of the runtime.
        """

        return (
            f"{self.__class__.__name__}("
            f"planner={self.planner.__class__.__name__}, "
            f"execution={self.execution.__class__.__name__}, "
            f"workflow={self.workflow.__class__.__name__}, "
            f"memory={self.memory.__class__.__name__}, "
            f"plugins={self.plugins.__class__.__name__}, "
            f"tools={self.tools.__class__.__name__}"
            f")"
        )