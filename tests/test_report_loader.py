from scholaros.research.report_loader import (
    ReportLoader,
)
from scholaros.research.report_manager import (
    ReportManager,
)


def create_loader() -> ReportLoader:

    return ReportLoader()


def test_manager_property():

    loader = create_loader()

    assert isinstance(
        loader.manager,
        ReportManager,
    )


def test_manager_is_singleton():

    loader = create_loader()

    assert (
        loader.manager
        is loader.manager
    )


def test_repr():

    loader = create_loader()

    assert (
        repr(
            loader,
        )
        ==
        "ReportLoader("
        "manager="
        "ReportManager"
        ")"
    )