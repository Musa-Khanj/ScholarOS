from scholaros.container import Container


class IService:
    pass


class Service(IService):
    pass


def test_singleton():

    c = Container()

    c.add_singleton(IService, Service)

    a = c.resolve(IService)
    b = c.resolve(IService)

    assert a is b


def test_transient():

    c = Container()

    c.add_transient(IService, Service)

    a = c.resolve(IService)
    b = c.resolve(IService)

    assert a is not b