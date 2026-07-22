from __future__ import annotations

from scholaros.kernel.container import ServiceContainer
from scholaros.kernel.lifecycle import LifecycleState


class Kernel:
    def __init__(self) -> None:
        self.container = ServiceContainer()
        self.state = LifecycleState.CREATED

    def boot(self) -> None:
        self.state = LifecycleState.BOOTING

        for service in self.container._services.values():
            service.initialize()
            service.start()

        self.state = LifecycleState.READY

    def shutdown(self) -> None:
        self.state = LifecycleState.STOPPING

        for service in reversed(list(self.container._services.values())):
            service.stop()
            service.shutdown()

        self.state = LifecycleState.STOPPED