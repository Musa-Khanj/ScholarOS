class ContainerError(Exception):
    """Base container exception."""


class ServiceAlreadyRegistered(ContainerError):
    """Raised when registering a duplicate service."""


class ServiceNotFound(ContainerError):
    """Raised when a service cannot be resolved."""