from __future__ import annotations

from scholaros.kernel.container import ServiceContainer
from scholaros.kernel.lifecycle import LifecycleState


class Kernel:
    def __init__(self) -> None:
        self.container = ServiceContainer()
        self.state = LifecycleState.CREATED

    def boot(self) -> None:
        self.state = LifecycleState.BOOTING

        for provider in self.container._services.values():
            instance = provider.implementation
            if hasattr(instance, "initialize") and callable(instance.initialize):
                instance.initialize()
            if hasattr(instance, "start") and callable(instance.start):
                instance.start()

        self.state = LifecycleState.READY

    def shutdown(self) -> None:
        self.state = LifecycleState.STOPPING

        for provider in reversed(list(self.container._services.values())):
            instance = provider.implementation
            if hasattr(instance, "stop") and callable(instance.stop):
                instance.stop()
            if hasattr(instance, "shutdown") and callable(instance.shutdown):
                instance.shutdown()

        self.state = LifecycleState.STOPPED