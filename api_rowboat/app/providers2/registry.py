from __future__ import annotations

from typing import Dict, List, Optional

from ..interfaces.provider import MediaProvider


class ProviderRegistry2:
    """Registro centralizado de Media Providers.

    Equivale a:
        export class ProviderRegistry {
            private readonly providers = new Map<string, MediaProvider>();
            register(provider: MediaProvider): void { ... }
            get(providerId: string): MediaProvider | undefined { ... }
            list(): MediaProvider[] { ... }
            findByCapability(capability: string): MediaProvider[] { ... }
        }

    Nota: acepta cualquier objeto que cumpla el Protocol MediaProvider
    (duck-typing), lo que incluye los adapters existentes ProviderBase2.
    """

    def __init__(self) -> None:
        self._providers: Dict[str, MediaProvider] = {}

    def register(self, provider: MediaProvider) -> None:
        """Registra un provider. Si ya existe el id, lo reemplaza."""
        self._providers[provider.id] = provider

    def get(self, provider_id: str) -> Optional[MediaProvider]:
        """Retorna el provider por id, o None si no existe."""
        return self._providers.get(provider_id)

    def list(self) -> List[MediaProvider]:
        """Retorna todos los providers registrados."""
        return list(self._providers.values())

    def find_by_capability(self, capability: str) -> List[MediaProvider]:
        """Retorna los providers que soportan la capability indicada.

        Equivale a:
            findByCapability(capability: string): MediaProvider[]
        """
        return [p for p in self.list() if p.supports(capability)]

    # Alias camelCase para consistencia con el contrato TypeScript
    findByCapability = find_by_capability


provider_registry2 = ProviderRegistry2()
