from scholaros.core.base import Component, ComponentMetadata
from scholaros.core.registry import Registry

class Dummy(Component):
    def initialize(self) -> None:
        pass

    def shutdown(self) -> None:
        pass

    def health(self) -> bool:
        return True





def test_registry():

    registry = Registry()

    component = Dummy(
        ComponentMetadata(
            name="dummy",
            version="1.0",
            description="dummy component",
            author="ScholarOS",
        )
    )

    registry.register(component)

    assert registry.exists("dummy")

    assert registry.get("dummy") is component

    assert len(registry) == 1