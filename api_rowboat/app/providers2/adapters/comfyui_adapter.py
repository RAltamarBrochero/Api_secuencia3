from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...capabilities.capability_names import (
    CAPABILITY_IMAGE_FACE_SWAP,
    CAPABILITY_IMAGE_GENERATE,
    CAPABILITY_IMAGE_INPAINT,
    CAPABILITY_IMAGE_UPSCALE,
)
from ...providers2.base import ProviderBase2
from ...providers2 import comfyui_client
from ...config import settings
from ...services.job_manager import job_manager


class ComfyUIAdapter2(ProviderBase2):
    def __init__(self):
        self._id = "comfyui"

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return "ComfyUI (local/híbrido)"

    def capabilities(self) -> List[str]:
        return [
            CAPABILITY_IMAGE_GENERATE,
            CAPABILITY_IMAGE_INPAINT,
            CAPABILITY_IMAGE_UPSCALE,
            CAPABILITY_IMAGE_FACE_SWAP,
        ]

    def health(self) -> Dict[str, Any]:
        if not settings.comfyui_enabled:
            return {"provider": self.id, "status": "disabled"}
        base = (settings.comfyui_base_url or "").strip()
        if not base:
            return {"provider": self.id, "status": "disabled", "reason": "COMFYUI_BASE_URL vacío"}
        try:
            comfyui_client.check_available(base)
            return {"provider": self.id, "status": "ok", "comfyui_base_url": base}
        except Exception as e:
            return {"provider": self.id, "status": "unreachable", "error": str(e)}

    def run_capability(
        self,
        capability: str,
        payload: Dict[str, Any],
        *,
        job_id: str,
        input_paths: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        if capability != CAPABILITY_IMAGE_GENERATE:
            return {
                "outputs": None,
                "error": f"ComfyUI: capability '{capability}' no implementada.",
                "provider_result": {"provider": self.id},
            }

        if not settings.comfyui_enabled:
            return {
                "outputs": None,
                "error": "ComfyUI deshabilitado (COMFYUI_ENABLED=false).",
                "provider_result": {"provider": self.id},
            }

        base = (settings.comfyui_base_url or "").strip()
        if not base:
            return {
                "outputs": None,
                "error": "COMFYUI_BASE_URL no configurado.",
                "provider_result": {"provider": self.id},
            }

        prompt = (payload.get("prompt") or "").strip()
        if not prompt:
            return {
                "outputs": None,
                "error": "Se requiere 'prompt' en el payload.",
                "provider_result": {"provider": self.id},
            }

        try:
            dest = job_manager.job_output_path(job_id, f"{job_id}_comfyui.png")
            meta = comfyui_client.generate_image_to_path(
                base,
                settings.comfyui_workflow_image_generate,
                prompt,
                dest,
                negative_prompt=payload.get("negative_prompt"),
            )
            return {
                "outputs": {"image_path": dest},
                "error": None,
                "provider_result": {"provider": self.id, "prompt_id": meta.get("prompt_id")},
            }
        except Exception as e:
            return {
                "outputs": None,
                "error": str(e),
                "provider_result": {"provider": self.id},
            }
