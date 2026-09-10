"""
ScholarOS Services Package.

Comprehensive service architecture for ScholarOS, providing:
- Base Service and metadata contracts
- Discrete lifecycle management and event dispatch
- Topological dependency startup and shutdown resolution
- Service discovery and registration
- Health inspection and runtime diagnostics
- DI container integration
- Built-in service interfaces
"""

from __future__ import annotations

from scholaros.services.dependency import ServiceDependencyResolver
from scholaros.services.descriptor import ServiceDescriptor
from scholaros.services.diagnostics import ServiceDiagnostics
from scholaros.services.discovery import DiscoveredService, ServiceDiscovery
from scholaros.services.exceptions import (
    CircularServiceDependencyError,
    ServiceAlreadyRegisteredError,
    ServiceDependencyError,
    ServiceError,
    ServiceHealthError,
    ServiceLifecycleError,
    ServiceNotFoundError,
    ServiceRegistrationError,
)
from scholaros.services.health import HealthStatus, ServiceHealth
from scholaros.services.lifecycle import (
    LifecycleTracker,
    ServiceFailed,
    ServiceInitialized,
    ServiceLifecycleEvent,
    ServiceRegistered,
    ServiceRestarted,
    ServiceShutdown,
    ServiceStarted,
    ServiceState,
    ServiceStopped,
)
from scholaros.services.manager import ServiceManager
from scholaros.services.metadata import ServiceMetadata
from scholaros.services.provider import ServiceProvider, configure_services
from scholaros.services.registry import ServiceRegistry
from scholaros.services.service import Service
from scholaros.services.service_collection import ServiceCollection

__all__ = [
    # Core Service & Metadata
    "CircularServiceDependencyError",
    "DiscoveredService",
    "HealthStatus",
    "LifecycleTracker",
    "Service",
    "ServiceAlreadyRegisteredError",
    "ServiceCollection",
    "ServiceDependencyError",
    "ServiceDependencyResolver",
    "ServiceDescriptor",
    "ServiceDiagnostics",
    "ServiceDiscovery",
    "ServiceError",
    # Events
    "ServiceFailed",
    "ServiceHealth",
    "ServiceHealthError",
    "ServiceInitialized",
    "ServiceLifecycleError",
    # Lifecycle & States
    "ServiceLifecycleEvent",
    "ServiceManager",
    "ServiceMetadata",
    "ServiceNotFoundError",
    # DI Provider
    "ServiceProvider",
    "ServiceRegistered",
    "ServiceRegistrationError",
    # Storage & Management
    "ServiceRegistry",
    "ServiceRestarted",
    "ServiceShutdown",
    "ServiceStarted",
    "ServiceState",
    "ServiceStopped",
    "configure_services",
]