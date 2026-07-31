from scholaros.container import Container
from scholaros.container.exceptions import CircularDependencyError


class IA:
    pass


class IB:
    pass


class A(IA):

    def __init__(self, b: IB):
        self.b = b


class B(IB):

    def __init__(self, a: IA):
        self.a = a


def test_circular_dependency():

    container = Container()

    container.add_transient(IA, A)
    container.add_transient(IB, B)

    try:
        container.resolve(IA)

        assert False

    except CircularDependencyError:
        assert True

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

class IRepository:
    pass


class Repository(IRepository):
    pass


class IService2:
    pass


class Service2(IService2):
    def __init__(self, repository: IRepository):
        self.repository = repository


def test_constructor_injection():
    container = Container()

    container.add_singleton(IRepository, Repository)
    container.add_transient(IService2, Service2)

    service = container.resolve(IService2)

    assert isinstance(service.repository, Repository)

class IScoped:
    pass


class ScopedService(IScoped):
    pass

def test_scoped_lifetime():

    root = Container()

    root.add_scoped(
        IScoped,
        ScopedService,
    )

    scope = root.create_scope()

    a = scope.resolve(IScoped)
    b = scope.resolve(IScoped)

    assert a is b


def test_scoped_isolation():

    root = Container()

    root.add_scoped(
        IScoped,
        ScopedService,
    )

    scope1 = root.create_scope()
    scope2 = root.create_scope()

    a = scope1.resolve(IScoped)
    b = scope2.resolve(IScoped)

    assert a is not b

class ISingleton:
    pass


class SingletonService(ISingleton):
    pass


def test_singleton_shared_between_scopes():

    root = Container()

    root.add_singleton(
        ISingleton,
        SingletonService,
    )

    scope1 = root.create_scope()
    scope2 = root.create_scope()

    a = scope1.resolve(ISingleton)
    b = scope2.resolve(ISingleton)

    assert a is b

class ITransient:
    pass


class TransientService(ITransient):
    pass


def test_transient_not_shared_between_scopes():

    root = Container()

    root.add_transient(
        ITransient,
        TransientService,
    )

    scope1 = root.create_scope()
    scope2 = root.create_scope()

    a = scope1.resolve(ITransient)
    b = scope1.resolve(ITransient)
    c = scope2.resolve(ITransient)

    assert a is not b
    assert a is not c
    assert b is not c
    