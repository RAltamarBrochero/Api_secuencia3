from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from ...capabilities.capability_names import (
    CAPABILITY_AUDIO_ENHANCE,
    CAPABILITY_AUDIO_STT,
    CAPABILITY_AUDIO_TTS,
    CAPABILITY_IMAGE_EDIT,
    CAPABILITY_IMAGE_FACE_SWAP,
    CAPABILITY_IMAGE_GENERATE,
    CAPABILITY_IMAGE_INPAINT,
    CAPABILITY_IMAGE_UPSCALE,
    CAPABILITY_VIDEO_GENERATE,
    CAPABILITY_VIDEO_LIP_SYNC,
    CAPABILITY_VIDEO_PROCESS,
)
from ...providers2.base import ProviderBase2
from ...providers2 import replicate_client
from ...config import settings
from ...services.job_manager import job_manager

_REPLICATE_MODELS: Dict[str, str] = {
    CAPABILITY_AUDIO_TTS: "suno-ai/bark:b76242b40d67c76ab6742e987628a2a9ac019e11d56ab96c4e91ce03b79b2787",
    CAPABILITY_AUDIO_ENHANCE: "lucataco/demucs:v0.3",
    CAPABILITY_IMAGE_GENERATE: "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    CAPABILITY_IMAGE_EDIT: "stability-ai/sdxl:39ed52f2a78e934b3ba6e2a89f5b1c712de7dfea535525255b1aa35c5565e08b",
    CAPABILITY_IMAGE_INPAINT: "stability-ai/stable-diffusion-inpainting:95b7223104132402a9ae91cc677285bc5eb997834bd2349fa486f53910fd68b3",
    CAPABILITY_IMAGE_UPSCALE: "nightmareai/real-esrgan:42fed1c4974146d4d2414e2be2c5277c7fcf05fcc3a73abf41610695738c1d7b",
    CAPABILITY_IMAGE_FACE_SWAP: "yan-ops/face-swap:d0a4c38a91c6ad3c0f54de0df7f4e0b31bafd43f2d47bef7c91c0dce3e6e03a",
    CAPABILITY_VIDEO_PROCESS: "lucataco/animate-diff:beecf59c4977affd4a2d56bf20b6a2848d28de7ea32c1e2e6ddb6af4ea8f8e23",
    CAPABILITY_VIDEO_GENERATE: "anotherjesse/zeroscope-v2-xl:9f747673945c62801b13b84701c783929c0ee784e4748ec062204894dda1a351",
    CAPABILITY_VIDEO_LIP_SYNC: "cjwbw/sadtalker:a519cc0cfebaaeade068b23899165a11ec76aaa1d2b313d40d214f204ec957a3",
}


def _error_response(message: str) -> Dict[str, Any]:
    return {"outputs": None, "error": message, "provider_result": {"provider": "replicate"}}


def _check_token(token: str) -> Optional[str]:
    if not settings.replicate_enabled:
        return "Replicate deshabilitado (REPLICATE_ENABLED=false)."
    if not token:
        return "REPLICATE_API_TOKEN no configurado. Añade REPLICATE_API_TOKEN=r8_... al .env."
    return None


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
            CAPABILITY_IMAGE_GENERATE,
            CAPABILITY_IMAGE_EDIT,
            CAPABILITY_IMAGE_INPAINT,
            CAPABILITY_IMAGE_UPSCALE,
            CAPABILITY_IMAGE_FACE_SWAP,
            CAPABILITY_VIDEO_PROCESS,
            CAPABILITY_VIDEO_GENERATE,
            CAPABILITY_VIDEO_LIP_SYNC,
        ]

    def health(self) -> Dict[str, Any]:
        token = (settings.replicate_api_token or "").strip()
        err = _check_token(token)
        if err:
            return {"provider": self.id, "status": "disabled", "reason": err}
        try:
            import requests as _req
            r = _req.get(
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
        token = (settings.replicate_api_token or "").strip()
        err = _check_token(token)
        if err:
            return _error_response(err)
        try:
            return self._dispatch(capability, payload, token, job_id, input_paths or {})
        except Exception as e:
            return _error_response(str(e))

    def _dispatch(self, capability, payload, token, job_id, input_paths):
        if capability == CAPABILITY_AUDIO_STT:
            return self._run_stt(payload, token, job_id)
        if capability == CAPABILITY_AUDIO_TTS:
            return self._run_tts(payload, token, job_id)
        if capability == CAPABILITY_AUDIO_ENHANCE:
            return self._run_audio_enhance(payload, token, job_id)
        if capability == CAPABILITY_IMAGE_GENERATE:
            return self._run_image_generate(payload, token, job_id)
        if capability == CAPABILITY_IMAGE_EDIT:
            return self._run_image_edit(payload, token, job_id)
        if capability == CAPABILITY_IMAGE_INPAINT:
            return self._run_image_inpaint(payload, token, job_id)
        if capability == CAPABILITY_IMAGE_UPSCALE:
            return self._run_image_upscale(payload, token, job_id)
        if capability == CAPABILITY_IMAGE_FACE_SWAP:
            return self._run_face_swap(payload, token, job_id)
        if capability == CAPABILITY_VIDEO_PROCESS:
            return self._run_video_process(payload, token, job_id)
        if capability == CAPABILITY_VIDEO_GENERATE:
            return self._run_video_generate(payload, token, job_id)
        if capability == CAPABILITY_VIDEO_LIP_SYNC:
            return self._run_lip_sync(payload, token, job_id)
        return _error_response(f"Capability '{capability}' no implementada en Replicate adapter.")

    # ---- Helpers ----

    def _pred_to_image(self, token, model_ref, input_data, job_id, suffix):
        import requests as _req
        version = replicate_client._parse_version(model_ref)
        pred_id = replicate_client.create_prediction(token, version, input_data)
        output = replicate_client.wait_prediction(token, pred_id)
        img_url = output if isinstance(output, str) else (output[0] if isinstance(output, list) else None)
        if not img_url:
            return _error_response("Replicate no devolvió URL de imagen.")
        resp = _req.get(img_url, timeout=120)
        ext = ".webp" if "webp" in resp.headers.get("content-type", "") else ".png"
        out_path = job_manager.job_output_path(job_id, f"{job_id}_{suffix}{ext}")
        with open(out_path, "wb") as f:
            f.write(resp.content)
        return {"outputs": {"image_path": out_path}, "error": None, "provider_result": {"provider": self.id}}

    def _pred_to_video(self, token, model_ref, input_data, job_id, suffix):
        import requests as _req
        version = replicate_client._parse_version(model_ref)
        pred_id = replicate_client.create_prediction(token, version, input_data)
        output = replicate_client.wait_prediction(token, pred_id)
        video_url = output if isinstance(output, str) else (output[0] if isinstance(output, list) else None)
        if not video_url:
            return _error_response("Replicate no devolvió URL de video.")
        resp = _req.get(video_url, timeout=300)
        out_path = job_manager.job_output_path(job_id, f"{job_id}_{suffix}.mp4")
        with open(out_path, "wb") as f:
            f.write(resp.content)
        return {"outputs": {"video_path": out_path}, "error": None, "provider_result": {"provider": self.id}}

    # ---- Audio ----

    def _run_stt(self, payload, token, job_id):
        model_ref = (settings.replicate_default_model_audio_stt or "").strip()
        if not model_ref:
            return _error_response(
                "REPLICATE_DEFAULT_MODEL_AUDIO_STT no configurado. "
                "Ejemplo: openai/whisper:30414ee7c4fffc37e260fcab7842b5be470b9b840f2b608f5baa9bbef9a259ed"
            )
        input_audio = (payload.get("input_audio") or "").strip()
        if not input_audio:
            return _error_response("Se requiere 'input_audio' (URL pública o basename en inputs del job).")
        audio_path = replicate_client.resolve_audio_input(input_audio, job_id, settings.jobs_storage_dir)
        text = replicate_client.run_stt(token, model_ref, audio_path)
        out_path = job_manager.job_output_path(job_id, f"{job_id}_transcript.txt")
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)
        return {"outputs": {"transcript_path": out_path}, "error": None, "provider_result": {"provider": self.id}}

    def _run_tts(self, payload, token, job_id):
        text = (payload.get("text") or "").strip()
        if not text:
            return _error_response("Se requiere 'text' para audio.tts.")
        import requests as _req
        version = replicate_client._parse_version(_REPLICATE_MODELS[CAPABILITY_AUDIO_TTS])
        input_data = {"prompt": text}
        if payload.get("voice"):
            input_data["voice_preset"] = payload["voice"]
        pred_id = replicate_client.create_prediction(token, version, input_data)
        output = replicate_client.wait_prediction(token, pred_id)
        audio_url = output if isinstance(output, str) else (output[0] if isinstance(output, list) else None)
        if not audio_url:
            return _error_response("Replicate TTS no devolvió URL de audio.")
        resp = _req.get(audio_url, timeout=120)
        out_path = job_manager.job_output_path(job_id, f"{job_id}_tts.wav")
        with open(out_path, "wb") as f:
            f.write(resp.content)
        return {"outputs": {"audio_path": out_path}, "error": None, "provider_result": {"provider": self.id}}

    def _run_audio_enhance(self, payload, token, job_id):
        input_audio = (payload.get("input_audio") or "").strip()
        if not input_audio:
            return _error_response("Se requiere 'input_audio' para audio.enhance.")
        import requests as _req
        audio_path = replicate_client.resolve_audio_input(input_audio, job_id, settings.jobs_storage_dir)
        with open(audio_path, "rb") as f:
            r = _req.post(
                "https://api.replicate.com/v1/files",
                headers={"Authorization": f"Bearer {token}"},
                files={"content": (os.path.basename(audio_path), f, "audio/mpeg")},
                timeout=120,
            )
        if r.status_code not in (200, 201):
            return _error_response(f"No se pudo subir audio a Replicate ({r.status_code}).")
        file_url = (r.json() or {}).get("urls", {}).get("get")
        version = replicate_client._parse_version(_REPLICATE_MODELS[CAPABILITY_AUDIO_ENHANCE])
        pred_id = replicate_client.create_prediction(token, version, {"audio": file_url, "two_stems": "vocals"})
        output = replicate_client.wait_prediction(token, pred_id)
        audio_url = output if isinstance(output, str) else (output[0] if isinstance(output, list) else None)
        if not audio_url:
            return _error_response("Replicate enhance no devolvió URL.")
        resp = _req.get(audio_url, timeout=120)
        out_path = job_manager.job_output_path(job_id, f"{job_id}_enhanced.mp3")
        with open(out_path, "wb") as f:
            f.write(resp.content)
        return {"outputs": {"audio_path": out_path}, "error": None, "provider_result": {"provider": self.id}}

    # ---- Image ----

    def _run_image_generate(self, payload, token, job_id):
        prompt = (payload.get("prompt") or "").strip()
        if not prompt:
            return _error_response("Se requiere 'prompt' para image.generate.")
        input_data = {"prompt": prompt}
        if payload.get("negative_prompt"):
            input_data["negative_prompt"] = payload["negative_prompt"]
        return self._pred_to_image(token, _REPLICATE_MODELS[CAPABILITY_IMAGE_GENERATE], input_data, job_id, "generated")

    def _run_image_edit(self, payload, token, job_id):
        prompt = (payload.get("prompt") or "").strip()
        input_image = (payload.get("input_image") or "").strip()
        if not prompt:
            return _error_response("Se requiere 'prompt' para image.edit.")
        if not input_image:
            return _error_response("Se requiere 'input_image' para image.edit.")
        return self._pred_to_image(token, _REPLICATE_MODELS[CAPABILITY_IMAGE_EDIT], {"prompt": prompt, "image": input_image}, job_id, "edited")

    def _run_image_inpaint(self, payload, token, job_id):
        prompt = (payload.get("prompt") or "").strip()
        input_image = (payload.get("input_image") or "").strip()
        mask_image = (payload.get("mask_image") or "").strip()
        if not all([prompt, input_image, mask_image]):
            return _error_response("Se requieren 'prompt', 'input_image' y 'mask_image' para image.inpaint.")
        return self._pred_to_image(token, _REPLICATE_MODELS[CAPABILITY_IMAGE_INPAINT], {"prompt": prompt, "image": input_image, "mask": mask_image}, job_id, "inpainted")

    def _run_image_upscale(self, payload, token, job_id):
        input_image = (payload.get("input_image") or "").strip()
        if not input_image:
            return _error_response("Se requiere 'input_image' para image.upscale.")
        return self._pred_to_image(token, _REPLICATE_MODELS[CAPABILITY_IMAGE_UPSCALE], {"image": input_image, "scale": payload.get("scale", 2.0)}, job_id, "upscaled")

    def _run_face_swap(self, payload, token, job_id):
        target_image = (payload.get("target_image") or "").strip()
        source_face = (payload.get("source_face") or "").strip()
        if not target_image or not source_face:
            return _error_response("Se requieren 'target_image' y 'source_face' para image.face_swap.")
        return self._pred_to_image(token, _REPLICATE_MODELS[CAPABILITY_IMAGE_FACE_SWAP], {"target_image": target_image, "swap_image": source_face}, job_id, "faceswap")

    # ---- Video ----

    def _run_video_process(self, payload, token, job_id):
        input_video = (payload.get("input_video") or "").strip()
        if not input_video:
            return _error_response("Se requiere 'input_video' para video.process.")
        return self._pred_to_video(token, _REPLICATE_MODELS[CAPABILITY_VIDEO_PROCESS], {"video": input_video}, job_id, "processed")

    def _run_video_generate(self, payload, token, job_id):
        prompt = (payload.get("prompt") or "").strip()
        if not prompt:
            return _error_response("Se requiere 'prompt' para video.generate.")
        return self._pred_to_video(token, _REPLICATE_MODELS[CAPABILITY_VIDEO_GENERATE], {"prompt": prompt, "num_frames": 24}, job_id, "generated")

    def _run_lip_sync(self, payload, token, job_id):
        input_video = (payload.get("input_video") or "").strip()
        input_audio = (payload.get("input_audio") or "").strip()
        if not input_video or not input_audio:
            return _error_response("Se requieren 'input_video' e 'input_audio' para video.lip_sync.")
        return self._pred_to_video(token, _REPLICATE_MODELS[CAPABILITY_VIDEO_LIP_SYNC], {"source_image": input_video, "driven_audio": input_audio}, job_id, "lipsync")
