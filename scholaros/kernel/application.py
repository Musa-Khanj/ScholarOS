from __future__ import annotations

from pathlib import Path

from scholaros.kernel.bootstrap import Bootstrap
from scholaros.kernel.context import KernelContext
from scholaros.kernel.kernel import Kernel


class ScholarOS:

    def __init__(self, root: Path) -> None:

        self.context = KernelContext(
            root_path=root,
            workspace=root / "workspace",
            config_path=root / "configs",
            data_path=root / "data",
            cache_path=root / ".cache",
            temp_path=root / ".temp",
        )

        self.kernel = Kernel()

    def start(self) -> None:
        Bootstrap.initialize(self.kernel)

    def stop(self) -> None:
        Bootstrap.shutdown(self.kernel)