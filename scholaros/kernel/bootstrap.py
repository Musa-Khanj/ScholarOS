from __future__ import annotations

from scholaros.kernel.kernel import Kernel


class Bootstrap:

    @staticmethod
    def initialize(kernel: Kernel) -> None:
        kernel.boot()

    @staticmethod
    def shutdown(kernel: Kernel) -> None:
        kernel.shutdown()