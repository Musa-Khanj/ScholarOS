"""
ScholarOS AI Provider Registry.

Stores and queries registered AI providers without lifecycle logic.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, Iterator

if TYPE_CHECKING:
    pass


class ProviderRegistry:
    """
    Pure repository for storing and querying AI providers.
    """

    def __init__(self) -> None:
        self._providers: dict[str, Any] = {}
        self._model_to_provider: dict[str, str] = {}

    def register(
        self,
        name_or_provider: str | Any,
        provider: Any | None = None,
        models: list[str] | None = None,
    ) -> None:
        """
        Register a provider.

        Supports both:
        - register("name", provider)
        - register(provider) [uses provider.name]
        """
        if isinstance(name_or_provider, str) and provider is not None:
            name = name_or_provider.strip().lower()
            prov = provider
        elif hasattr(name_or_provider, "name"):
            name = str(name_or_provider.name).strip().lower()
            prov = name_or_provider
        elif isinstance(name_or_provider, str) and provider is None:
            raise ValueError("Provider instance or callable must be supplied.")
        else:
            name = getattr(name_or_provider, "__name__", str(name_or_provider)).strip().lower()
            prov = name_or_provider

        if not name:
            raise ValueError("Provider name cannot be empty.")

        if name in self._providers:
            raise ValueError(f"Provider '{name}' is already registered.")

        self._providers[name] = prov

        if models:
            for m in models:
                self._model_to_provider[m.strip().lower()] = name

    def unregister(self, name: str) -> bool:
        """Unregister a provider by name."""
        canonical = name.strip().lower()
        if canonical in self._providers:
            del self._providers[canonical]
            # Remove associated model mappings
            keys_to_remove = [k for k, v in self._model_to_provider.items() if v == canonical]
            for k in keys_to_remove:
                del self._model_to_provider[k]
            return True
        return False

    def get(self, name: str) -> Any:
        """
        Retrieve provider by name. Case-insensitive.
        """
        canonical = name.strip().lower()
        try:
            return self._providers[canonical]
        except KeyError as exc:
            raise KeyError(f"Unknown provider '{name}'.") from exc

    def contains(self, name: str) -> bool:
        """Return True if provider with name exists."""
        return name.strip().lower() in self._providers

    def names(self) -> tuple[str, ...]:
        """Return tuple of all registered provider names."""
        return tuple(self._providers.keys())

    def get_by_capability(self, capability: str) -> list[Any]:
        """Return list of providers supporting the specified capability."""
        matches: list[Any] = []
        for prov in self._providers.values():
            if hasattr(prov, "supports") and prov.supports(capability):
                matches.append(prov)
            elif hasattr(prov, "capabilities") and capability in prov.capabilities:
                matches.append(prov)
        return matches

    def get_by_model(self, model_name: str) -> Any | None:
        """Look up provider assigned to a given model name."""
        canonical = model_name.strip().lower()
        if canonical in self._model_to_provider:
            return self._providers.get(self._model_to_provider[canonical])

        # Check default_model on providers
        for prov in self._providers.values():
            if getattr(prov, "default_model", None) == canonical:
                return prov
        return None

    def clear(self) -> None:
        """Remove all registered providers."""
        self._providers.clear()
        self._model_to_provider.clear()

    def __len__(self) -> int:
        return len(self._providers)

    def __contains__(self, name: str) -> bool:
        return self.contains(name)

    def __iter__(self) -> Iterator[tuple[str, Any]]:
        return iter(self._providers.items())

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(providers={list(self._providers.keys())})"


__all__ = [
    "ProviderRegistry",
]
