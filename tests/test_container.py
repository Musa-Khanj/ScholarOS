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


def test_add_instance():
    class Config:
        def __init__(self, value: str):
            self.value = value

    container = Container()
    cfg = Config("scholaros-test")
    container.add_instance(Config, cfg)

    resolved = container.resolve(Config)
    assert resolved is cfg
    assert resolved.value == "scholaros-test"


def test_add_factory():
    class Engine:
        def __init__(self, power: int):
            self.power = power

    container = Container()
    container.add_factory(Engine, lambda: Engine(power=450))

    e1 = container.resolve(Engine)
    e2 = container.resolve(Engine)

    assert isinstance(e1, Engine)
    assert e1.power == 450
    assert e1 is not e2


def test_factory_with_dependency_injection():
    class Database:
        def __init__(self, host: str = "localhost"):
            self.host = host

    class Client:
        def __init__(self, db: Database):
            self.db = db

    container = Container()
    container.add_singleton(Database, Database)
    container.add_factory(Client, lambda db=None: Client(db=container.resolve(Database)))



    client = container.resolve(Client)
    assert isinstance(client, Client)
    assert isinstance(client.db, Database)


def test_scope_disposal_and_scope_disposed_error():
    from scholaros.container.exceptions import ScopeDisposedError

    disposed = []

    class DisposableService:
        def dispose(self):
            disposed.append(True)

    root = Container()
    root.add_scoped(DisposableService, DisposableService)

    scope = root.create_scope()
    service = scope.resolve(DisposableService)
    assert isinstance(service, DisposableService)
    assert len(disposed) == 0

    scope.dispose()
    assert len(disposed) == 1
    assert scope.is_disposed is True

    try:
        scope.resolve(DisposableService)
        assert False, "Should raise ScopeDisposedError"
    except ScopeDisposedError:
        assert True


def test_container_wire_graph():
    class Dependency:
        pass

    class ServiceWithDep:
        def __init__(self, dep: Dependency):
            self.dep = dep

    container = Container()
    container.add_singleton(Dependency, Dependency)
    container.add_singleton(ServiceWithDep, ServiceWithDep)

    wired = container.wire_graph()
    assert Dependency in wired
    assert ServiceWithDep in wired
    assert isinstance(wired[ServiceWithDep].dep, Dependency)


def test_dependency_resolver_traversal():
    from scholaros.container.resolver import DependencyResolver

    resolver = DependencyResolver()

    class Bottom:
        pass

    class Middle:
        def __init__(self, b: Bottom):
            self.b = b

    class Top:
        def __init__(self, m: Middle):
            self.m = m

    dep_map = {
        Top: [Middle],
        Middle: [Bottom],
        Bottom: [],
    }

    order = resolver.traverse_graph(Top, lambda t: dep_map.get(t, []))
    assert order == [Bottom, Middle, Top]