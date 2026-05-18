from __future__ import annotations

from typing import Any, Dict, List, Optional

from ...capabilities.capability_names import (
    CAPABILITY_AUDIO_STT,
    CAPABILITY_AUDIO_TTS,
    CAPABILITY_VIDEO_PROCESS,
    CAPABILITY_VIDEO_GENERATE,
    CAPABILITY_VIDEO_LIP_SYNC,
    CAPABILITY_AUDIO_ENHANCE,
)
from ...providers2.base import ProviderBase2
from ...providers2 import replicate_client
from ...config import settings
from ...services.job_manager import job_manager


class ReplicateAdapter2(ProviderBase2):
    def __init__(self):
        self._id = "replicate"

    @property
    def id(self) -> str:
        return self._id

    @property
    def name(self) -> str:
        return "Replicate (remoto)"

    def capabilities(self) -> List[str]:
        return [
            CAPABILITY_AUDIO_STT,
            CAPABILITY_AUDIO_TTS,
            CAPABILITY_AUDIO_ENHANCE,
            CAPABILITY_VIDEO_PROCESS,
            CAPABILITY_VIDEO_GENERATE,
            CAPABILITY_VIDEO_LIP_SYNC,
        ]

    def health(self) -> Dict[str, Any]:
        if not settings.replicate_enabled:
            return {"provider": self.id, "status": "disabled"}
        token = (settings.replicate_api_token or "").strip()
        if not token:
            return {"provider": self.id, "status": "disabled", "has_token": False}
        try:
            r = __import__("requests").get(
                "https://api.replicate.com/v1/account",
                headers={"Authorization": f"Bearer {token}"},
                timeout=10,
            )
            if r.status_code == 200:
                return {"provider": self.id, "status": "ok", "has_token": True}
            return {"provider": self.id, "status": "unauthorized", "has_token": True}
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
        if capability != CAPABILITY_AUDIO_STT:
            return {
                "outputs": None,
                "error": f"Replicate: capability '{capability}' no implementada.",
                "provider_result": {"provider": self.id},
            }

        if not settings.replicate_enabled:
            return {
                "outputs": None,
                "error": "Replicate deshabilitado (REPLICATE_ENABLED=false).",
                "provider_result": {"provider": self.id},
            }

        token = (settings.replicate_api_token or "").strip()
        if not token:
            return {
                "outputs": None,
                "error": "REPLICATE_API_TOKEN no configurado.",
                "provider_result": {"provider": self.id},
            }

        model_ref = (settings.replicate_default_model_audio_stt or "").strip()
        if not model_ref:
            return {
                "outputs": None,
                "error": "REPLICATE_DEFAULT_MODEL_AUDIO_STT no configurado.",
                "provider_result": {"provider": self.id},
            }

        input_audio = (payload.get("input_audio") or "").strip()
        if not input_audio:
            return {
                "outputs": None,
                "error": "Se requiere 'input_audio' (URL o basename en inputs del job).",
                "provider_result": {"provider": self.id},
            }

        try:
            audio_path = replicate_client.resolve_audio_input(
                input_audio,
                job_id,
                settings.jobs_storage_dir,
            )
            text = replicate_client.run_stt(token, model_ref, audio_path)
            out_path = job_manager.job_output_path(job_id, f"{job_id}_transcript.txt")
            with open(out_path, "w", encoding="utf-8") as f:
                f.write(text)
            return {
                "outputs": {"transcript_path": out_path},
                "error": None,
                "provider_result": {"provider": self.id},
            }
        except Exception as e:
            return {
                "outputs": None,
                "error": str(e),
                "provider_result": {"provider": self.id},
            }
