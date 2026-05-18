from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from ..capabilities.capability_names import ALL_CAPABILITIES


class ProviderBase2(ABC):
    """Interface de providers para Fase 2.

    Restricción: no se exponen payloads crudos como API pública.
    El adapter traduce a outputs normalizados (rutas a disco + metadata opcional).
    """

    @property
    @abstractmethod
    def id(self) -> str:  # provider identifier
        raise NotImplementedError

    @property
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError

    @abstractmethod
    def capabilities(self) -> List[str]:
        raise NotImplementedError

    def supports(self, capability: str) -> bool:
        return capability in set(self.capabilities())

    @abstractmethod
    def health(self) -> Dict[str, Any]:
        raise NotImplementedError

    @abstractmethod
    def run_capability(
        self,
        capability: str,
        payload: Dict[str, Any],
        *,
        job_id: str,
        input_paths: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """Ejecuta la capability.

        Retorna un diccionario normalizado con formato:
        - outputs: Dict[str, str] (rutas a disco)
        - error: Optional[str]
        - provider_result: (interno, no público) opcional
        """
        raise NotImplementedError

