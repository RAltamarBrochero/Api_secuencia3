from __future__ import annotations

from typing import Any, Dict, List, Optional

from ..capabilities.capability_names import ALL_CAPABILITIES
from ..interfaces.provider import MediaProvider
from ..providers2.registry import provider_registry2


class CapabilityRouter2:
    """Selecciona proveedor por capability con prioridad.

    Implementa el contrato TypeScript CapabilityRouter:
        resolve(capability, preferredProvider?): Promise<MediaProvider>

    Mantiene compatibilidad con los métodos previos usados por el orchestrator:
        route_provider_id(capability) -> Optional[str]
        list_capable_providers(capability) -> List[str]
    """

    def __init__(self) -> None:
        # Ordered preferences by capability — contrato TypeScript completo
        self._priority: Dict[str, List[str]] = {
            "image.generate":  ["comfyui", "replicate"],
            "image.edit":      ["comfyui", "replicate"],
            "image.inpaint":   ["comfyui", "replicate"],
            "image.upscale":   ["comfyui", "replicate"],
            "image.face_swap": ["comfyui", "replicate"],
            "video.process":   ["replicate", "comfyui"],
            "video.generate":  ["replicate"],
            "video.lip_sync":  ["replicate", "comfyui"],
            "audio.tts":       ["replicate"],
            "audio.stt":       ["replicate"],
            "audio.enhance":   ["replicate", "comfyui"],
        }

    # ------------------------------------------------------------------
    # Contrato TypeScript: resolve()
    # ------------------------------------------------------------------

    async def resolve(
        self,
        capability: str,
        preferred_provider: Optional[str] = None,
    ) -> MediaProvider:
        """Resuelve el provider óptimo para una capability.

        Equivale a:
            async resolve(capability: string, preferredProvider?: string): Promise<MediaProvider>

        Lógica:
        1. Si se especifica preferred_provider, lo valida y retorna directamente.
        2. Si no, recorre el priority map en orden haciendo health-check.
        3. Fallback: primer candidato disponible aunque no pase health-check.
        4. Si no hay candidatos lanza error.
        """
        if preferred_provider:
            provider = provider_registry2.get(preferred_provider)
            if provider is None:
                raise ValueError(f"Provider not found: {preferred_provider}")
            if not provider.supports(capability):
                raise ValueError(
                    f"Provider '{preferred_provider}' does not support capability '{capability}'"
                )
            return provider

        candidates = provider_registry2.find_by_capability(capability)
        ordered_ids = self._priority.get(capability, [])

        for provider_id in ordered_ids:
            provider = next((p for p in candidates if p.id == provider_id), None)
            if provider is None:
                continue
            try:
                healthy = await provider.health_check()
            except Exception:
                healthy = False
            if healthy:
                return provider

        # Fallback: si ninguno pasó health-check, devuelve el primero disponible
        if not candidates:
            raise RuntimeError(f"No provider available for capability: '{capability}'")

        return candidates[0]

    # ------------------------------------------------------------------
    # Métodos legacy — se mantienen para no romper multimedia_orchestrator
    # ------------------------------------------------------------------

    def route_provider_id(self, capability: str) -> Optional[str]:
        """Retorna el id del provider preferido para una capability (síncrono).

        Usado internamente por multimedia_orchestrator (no async).
        """
        providers = provider_registry2.list()
        if capability not in ALL_CAPABILITIES:
            return None

        allowed = {p.id for p in providers}
        for candidate in self._priority.get(capability, []):
            if (
                candidate in allowed
                and provider_registry2.get(candidate) is not None
                and provider_registry2.get(candidate).supports(capability)  # type: ignore[union-attr]
            ):
                return candidate

        # fallback: cualquiera que lo soporte
        for p in providers:
            if p.supports(capability):
                return p.id
        return None

    def list_capable_providers(self, capability: str) -> List[str]:
        """Retorna ids de todos los providers que soportan la capability."""
        return [p.id for p in provider_registry2.list() if p.supports(capability)]

