from enum import Enum


class LifecycleState(str, Enum):
    CREATED = "created"
    BOOTING = "booting"
    READY = "ready"
    STOPPING = "stopping"
    STOPPED = "stopped"