"""
ScholarOS
Lifecycle State

Version : 1.0
Status  : In Development
Python  : 3.14+

Description
-----------
Represents the current lifecycle
state of ScholarOS.
"""

from __future__ import annotations

from enum import Enum


class LifecycleState(str, Enum):
    """
    Lifecycle states for ScholarOS.
    """

    CREATED = "created"
    INITIALIZED = "initialized"
    STARTING = "starting"
    RUNNING = "running"
    STOPPING = "stopping"
    STOPPED = "stopped"