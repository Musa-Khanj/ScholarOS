"""
Unit and integration tests for the ScholarOS Services Architecture.
"""

from __future__ import annotations

import pytest

from scholaros.container import Container
from scholaros.events import EventBus
from scholaros.services import (
    CircularServiceDependencyError,
    DiscoveredService,
    HealthStatus,
    LifecycleTracker,
    Service,
    ServiceAlreadyRegisteredError,
    ServiceCollection,
    ServiceDependencyError,
    ServiceDependencyResolver,
    ServiceDescriptor,
    ServiceDiagnostics,
    ServiceDiscovery,
    ServiceFailed,
    ServiceHealth,
    ServiceHealthError,
    ServiceInitialized,
    ServiceLifecycleError,
    ServiceManager,
    ServiceMetadata,
    ServiceNotFoundError,
    ServiceProvider,
    ServiceRegistered,
    ServiceRestarted,
    ServiceShutdown,
    ServiceStarted,
    ServiceState,
    ServiceStopped,
    configure_services,
)
from scholaros.services.builtin import (
    AIService,
    CollaborationService,
    IndexingService,
    KnowledgeService,
    LoggingService,
    MemoryService,
    PluginService,
    ResearchService,
    SchedulerService,
    ToolService,
)


class MockServiceA(Service):
    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="ServiceA",
                version="1.0.0",
                description="Test Service A",
                tags=("tag1", "core"),
                capabilities=("read",),
            )
        )


class MockServiceB(Service):
    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="ServiceB",
                version="1.0.0",
                description="Test Service B",
                dependencies=("ServiceA",),
                tags=("tag2", "core"),
                capabilities=("write",),
            )
        )


class MockServiceC(Service):
    def __init__(self) -> None:
        super().__init__(
            ServiceMetadata(
                name="ServiceC",
                version="1.0.0",
                description="Test Service C",
                dependencies=("ServiceB",),
                tags=("tag1",),
                capabilities=("execute",),
            )
        )


class FailingService(Service):
    def __init__(self) -> None:
        super().__init__(ServiceMetadata(name="FailingService"))

    def start(self) -> None:
        super().start()
        raise RuntimeError("Failed to start")


# ---------------------------------------------------------------------------
# 1. Base Service Tests
# ---------------------------------------------------------------------------


def test_base_service_lifecycle():
    service = MockServiceA()
    assert service.status == ServiceState.REGISTERED
    assert not service.is_running()

    service.initialize()
    assert service.status == ServiceState.INITIALIZED

    service.start()
    assert service.status == ServiceState.RUNNING
    assert service.is_running()
    assert service.enabled is True

    health = service.health()
    assert isinstance(health, ServiceHealth)
    assert health.status == HealthStatus.HEALTHY

    service.stop()
    assert service.status == ServiceState.STOPPED
    assert not service.is_running()

    service.shutdown()
    assert service.status == ServiceState.SHUTDOWN


def test_base_service_error_handling():
    service = MockServiceA()
    service.set_error("Connection reset")
    assert service.last_error() == "Connection reset"
    assert service.status == ServiceState.FAILED


# ---------------------------------------------------------------------------
# 2. Lifecycle Tracker & State Transitions
# ---------------------------------------------------------------------------


def test_lifecycle_tracker_valid_transitions():
    tracker = LifecycleTracker()
    assert tracker.state == ServiceState.REGISTERED

    tracker.transition_to(ServiceState.INITIALIZED)
    assert tracker.state == ServiceState.INITIALIZED

    tracker.transition_to(ServiceState.STARTED)
    assert tracker.state == ServiceState.STARTED
    assert tracker.is_running()

    tracker.transition_to(ServiceState.RUNNING)
    assert tracker.state == ServiceState.RUNNING

    tracker.transition_to(ServiceState.STOPPING)
    assert tracker.state == ServiceState.STOPPING

    tracker.transition_to(ServiceState.STOPPED)
    assert tracker.state == ServiceState.STOPPED

    tracker.transition_to(ServiceState.SHUTDOWN)
    assert tracker.state == ServiceState.SHUTDOWN


def test_lifecycle_tracker_invalid_transition():
    tracker = LifecycleTracker(ServiceState.REGISTERED)
    with pytest.raises(ServiceLifecycleError):
        tracker.transition_to(ServiceState.RUNNING)


# ---------------------------------------------------------------------------
# 3. Dependency Resolver Tests
# ---------------------------------------------------------------------------


def test_dependency_resolver_startup_and_shutdown():
    resolver = ServiceDependencyResolver()
    graph = {
        "A": [],
        "B": ["A"],
        "C": ["B"],
    }
    startup = resolver.resolve_startup_order(graph)
    assert startup == ["A", "B", "C"]

    shutdown = resolver.resolve_shutdown_order(graph)
    assert shutdown == ["C", "B", "A"]


def test_dependency_resolver_cycle_detection():
    resolver = ServiceDependencyResolver()
    cycle = {
        "A": ["B"],
        "B": ["A"],
    }
    with pytest.raises(CircularServiceDependencyError):
        resolver.resolve_startup_order(cycle)


def test_dependency_resolver_missing_dependency():
    resolver = ServiceDependencyResolver()
    missing = {
        "A": ["MissingService"],
    }
    with pytest.raises(ServiceDependencyError):
        resolver.resolve_startup_order(missing)


# ---------------------------------------------------------------------------
# 4. Service Collection Tests
# ---------------------------------------------------------------------------


def test_service_collection_operations():
    s1 = MockServiceA()
    s2 = MockServiceB()
    s3 = MockServiceC()

    coll = ServiceCollection([s1, s2, s3])
    assert len(coll) == 3
    assert coll["ServiceA"] is s1
    assert coll[0] is s1
    assert "ServiceB" in coll

    # Filter by tag
    tag1_services = coll.filter_by_tag("tag1")
    assert len(tag1_services) == 2
    assert tag1_services.names() == ["ServiceA", "ServiceC"]

    # Filter by capability
    write_services = coll.filter_by_capability("write")
    assert len(write_services) == 1
    assert write_services[0] is s2

    # Bulk start and stop
    coll.start_all()
    assert s1.is_running()
    assert s2.is_running()
    assert s3.is_running()

    summary = coll.health_summary()
    assert summary["ServiceA"].status == HealthStatus.HEALTHY

    coll.stop_all()
    assert not s1.is_running()
    assert not s2.is_running()
    assert not s3.is_running()


# ---------------------------------------------------------------------------
# 5. Service Manager & Lifecycle Events
# ---------------------------------------------------------------------------


def test_service_manager_lifecycle_and_events():
    event_bus = EventBus()
    received_events = []
    event_bus.subscribe("*", lambda e: received_events.append(e.name))

    manager = ServiceManager(event_bus=event_bus)
    s1 = MockServiceA()
    s2 = MockServiceB()

    manager.register(s1)
    manager.register(s2)
    assert "ServiceRegistered" in received_events

    manager.initialize("ServiceA")
    assert "ServiceInitialized" in received_events

    manager.start("ServiceA")
    assert "ServiceStarted" in received_events
    assert s1.is_running()

    diag = manager.diagnostics("ServiceA")
    assert diag.uptime_seconds >= 0.0

    manager.restart("ServiceA")
    assert "ServiceRestarted" in received_events
    assert diag.restart_count == 1

    manager.stop("ServiceA")
    assert "ServiceStopped" in received_events
    assert not s1.is_running()

    manager.shutdown("ServiceA")
    assert "ServiceShutdown" in received_events


def test_service_manager_start_all_and_stop_all():
    manager = ServiceManager()
    s_a = MockServiceA()
    s_b = MockServiceB()
    s_c = MockServiceC()

    # Register in arbitrary order
    manager.register(s_c)
    manager.register(s_a)
    manager.register(s_b)

    started = manager.start_all()
    assert started == ["ServiceA", "ServiceB", "ServiceC"]
    assert s_a.is_running() and s_b.is_running() and s_c.is_running()

    stopped = manager.stop_all()
    assert stopped == ["ServiceC", "ServiceB", "ServiceA"]
    assert not s_a.is_running() and not s_b.is_running() and not s_c.is_running()


def test_service_manager_failure_tracking():
    event_bus = EventBus()
    events = []
    event_bus.subscribe("*", lambda e: events.append(e.name))

    manager = ServiceManager(event_bus=event_bus)
    failing = FailingService()
    manager.register(failing)

    with pytest.raises(RuntimeError):
        manager.start("FailingService")

    assert "ServiceFailed" in events
    diag = manager.diagnostics("FailingService")
    assert diag.failure_count == 1
    assert "Failed to start" in (diag.last_error or "")


# ---------------------------------------------------------------------------
# 6. Provider Layer (DI Container Integration)
# ---------------------------------------------------------------------------


def test_provider_layer_container_integration():
    container = Container()
    manager = ServiceManager()
    service = MockServiceA()
    manager.register(service)

    provider = ServiceProvider(manager=manager, container=container)
    resolved = provider.resolve(MockServiceA)
    assert resolved is service

    # Also resolve directly from container
    container_resolved = container.resolve(MockServiceA)
    assert container_resolved is service


def test_configure_services_helper():
    container = Container()
    manager = configure_services(container)
    assert isinstance(manager, ServiceManager)
    assert container.resolve(ServiceManager) is manager


# ---------------------------------------------------------------------------
# 7. Built-in Services
# ---------------------------------------------------------------------------


def test_builtin_services_instantiation():
    services = [
        AIService(),
        ToolService(),
        SchedulerService(),
        ResearchService(),
        KnowledgeService(),
        LoggingService(),
        MemoryService(),
        IndexingService(),
        CollaborationService(),
        PluginService(),
    ]
    for s in services:
        assert isinstance(s, Service)
        assert s.name.endswith("Service")
        assert len(s.metadata.capabilities) > 0
        assert s.status == ServiceState.REGISTERED
