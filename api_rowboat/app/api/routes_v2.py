from __future__ import annotations

import os
from fastapi import APIRouter, BackgroundTasks, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from typing import Any, Dict

from ..capabilities.capability_names import (
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
    ALL_CAPABILITIES,
)
from ..capabilities.dtos import (
    CapabilityListResponse,
    ProvidersListResponse,
    ProviderHealthResponse,
    MediaJobResponse,
    JobStatusResponse,
    ProviderSummary,
    ImageGenerateRequest,
    ImageEditRequest,
    ImageInpaintRequest,
    ImageUpscaleRequest,
    ImageFaceSwapRequest,
    VideoProcessRequest,
    VideoGenerateRequest,
    VideoLipSyncRequest,
    AudioTTSRequest,
    AudioSTTRequest,
    AudioEnhanceRequest,
)

from ..providers2.registry import provider_registry2
from ..services2.multimedia_orchestrator import media_orchestrator2
from ..services2.job_runner import run_media_job_by_background
from ..services.job_manager import job_manager
from ..config import settings


router_v2 = APIRouter(tags=["v2"])


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _json_error(status_code: int, code: str, message: str, details: dict | None = None) -> JSONResponse:
    body: Dict[str, Any] = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


def _check_provider_available(capability: str):
    """Returns a JSONResponse error if no provider is wired for this capability, else None."""
    provider_id = media_orchestrator2.router.route_provider_id(capability)
    if not provider_id:
        return _json_error(
            503,
            "NO_PROVIDER",
            f"No hay ningún provider disponible para la capability '{capability}'. "
            "Configura REPLICATE_API_TOKEN o COMFYUI_BASE_URL en el .env.",
        )
    return None


# ---------------------------------------------------------------------------
# Providers & capabilities
# ---------------------------------------------------------------------------

@router_v2.get("/providers", response_model=ProvidersListResponse)
async def providers():
    items = []
    for p in provider_registry2.list():
        items.append(ProviderSummary(id=p.id, name=p.name, capabilities=p.capabilities()))
    return {"providers": items}


@router_v2.get("/providers/{provider_id}/health", response_model=ProviderHealthResponse)
async def provider_health(provider_id: str):
    p = provider_registry2.get(provider_id)
    if not p:
        raise HTTPException(status_code=404, detail="provider not found")
    h = p.health()
    return ProviderHealthResponse(
        provider_id=provider_id,
        status=h.get("status", "unknown"),
        details=h,
    )


@router_v2.get("/capabilities", response_model=CapabilityListResponse)
async def capabilities():
    return {"capabilities": ALL_CAPABILITIES}


# ---------------------------------------------------------------------------
# Job helpers
# ---------------------------------------------------------------------------

def _job_to_status_response(job: Dict[str, Any]) -> JobStatusResponse:
    payload = job.get("payload") or {}
    return JobStatusResponse(
        job_id=job.get("id"),
        status=job.get("status"),
        type=job.get("type"),
        capability=payload.get("capability"),
        outputs=job.get("outputs"),
        error=(job.get("result") or {}).get("error"),
    )


def _schedule(capability: str, payload: dict, background_tasks: BackgroundTasks) -> MediaJobResponse:
    scheduled = media_orchestrator2.schedule_media_job(capability=capability, payload=payload)
    job_id = scheduled["job_id"]
    if scheduled.get("status") == "pending" and job_id:
        background_tasks.add_task(
            run_media_job_by_background,
            job_id,
            capability,
            payload,
        )
    return MediaJobResponse(**scheduled)


# ---------------------------------------------------------------------------
# Media endpoints — image
# ---------------------------------------------------------------------------

@router_v2.post("/media/image/generate", response_model=MediaJobResponse)
async def image_generate(payload: ImageGenerateRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_IMAGE_GENERATE)
    if err:
        return err
    return _schedule(CAPABILITY_IMAGE_GENERATE, payload.dict(), background_tasks)


@router_v2.post("/media/image/edit", response_model=MediaJobResponse)
async def image_edit(payload: ImageEditRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_IMAGE_EDIT)
    if err:
        return err
    return _schedule(CAPABILITY_IMAGE_EDIT, payload.dict(), background_tasks)


@router_v2.post("/media/image/inpaint", response_model=MediaJobResponse)
async def image_inpaint(payload: ImageInpaintRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_IMAGE_INPAINT)
    if err:
        return err
    return _schedule(CAPABILITY_IMAGE_INPAINT, payload.dict(), background_tasks)


@router_v2.post("/media/image/upscale", response_model=MediaJobResponse)
async def image_upscale(payload: ImageUpscaleRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_IMAGE_UPSCALE)
    if err:
        return err
    return _schedule(CAPABILITY_IMAGE_UPSCALE, payload.dict(), background_tasks)


@router_v2.post("/media/image/face-swap", response_model=MediaJobResponse)
async def image_face_swap(payload: ImageFaceSwapRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_IMAGE_FACE_SWAP)
    if err:
        return err
    return _schedule(CAPABILITY_IMAGE_FACE_SWAP, payload.dict(), background_tasks)


# ---------------------------------------------------------------------------
# Media endpoints — video
# ---------------------------------------------------------------------------

@router_v2.post("/media/video/process", response_model=MediaJobResponse)
async def video_process(payload: VideoProcessRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_VIDEO_PROCESS)
    if err:
        return err
    return _schedule(CAPABILITY_VIDEO_PROCESS, payload.dict(), background_tasks)


@router_v2.post("/media/video/generate", response_model=MediaJobResponse)
async def video_generate(payload: VideoGenerateRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_VIDEO_GENERATE)
    if err:
        return err
    return _schedule(CAPABILITY_VIDEO_GENERATE, payload.dict(), background_tasks)


@router_v2.post("/media/video/lip-sync", response_model=MediaJobResponse)
async def video_lip_sync(payload: VideoLipSyncRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_VIDEO_LIP_SYNC)
    if err:
        return err
    return _schedule(CAPABILITY_VIDEO_LIP_SYNC, payload.dict(), background_tasks)


# ---------------------------------------------------------------------------
# Media endpoints — audio
# ---------------------------------------------------------------------------

@router_v2.post("/media/audio/tts", response_model=MediaJobResponse)
async def audio_tts(payload: AudioTTSRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_AUDIO_TTS)
    if err:
        return err
    return _schedule(CAPABILITY_AUDIO_TTS, payload.dict(), background_tasks)


@router_v2.post("/media/audio/stt", response_model=MediaJobResponse)
async def audio_stt(payload: AudioSTTRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_AUDIO_STT)
    if err:
        return err
    # Validate STT model configured
    model_ref = (settings.replicate_default_model_audio_stt or "").strip()
    if not model_ref:
        return _json_error(
            503,
            "MISSING_CONFIG",
            "REPLICATE_DEFAULT_MODEL_AUDIO_STT no configurado. "
            "Ejemplo: openai/whisper:30414ee7c4fffc37e260fcab7842b5be470b9b840f2b608f5baa9bbef9a259ed",
        )
    return _schedule(CAPABILITY_AUDIO_STT, payload.dict(), background_tasks)


@router_v2.post("/media/audio/enhance", response_model=MediaJobResponse)
async def audio_enhance(payload: AudioEnhanceRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_AUDIO_ENHANCE)
    if err:
        return err
    return _schedule(CAPABILITY_AUDIO_ENHANCE, payload.dict(), background_tasks)


# ---------------------------------------------------------------------------
# Job status, outputs, cancel
# ---------------------------------------------------------------------------

@router_v2.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_v2(job_id: str):
    job = job_manager.enrich_job_for_api(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return _job_to_status_response(job)


@router_v2.get("/jobs/{job_id}/manifest")
async def get_job_manifest(job_id: str):
    """Return the outputs manifest.json for a job."""
    dirs = job_manager._job_dirs(job_id)
    manifest_path = os.path.join(dirs["outputs_dir"], "manifest.json")
    if not os.path.isfile(manifest_path):
        raise HTTPException(status_code=404, detail="manifest not found — job may still be running or has no outputs")
    return FileResponse(manifest_path, media_type="application/json", filename="manifest.json")


@router_v2.get("/jobs/{job_id}/outputs/{basename}")
async def download_job_output_v2(job_id: str, basename: str):
    """Download a specific output file for a job."""
    if not basename:
        raise HTTPException(status_code=400, detail="basename is required")

    safe_name = os.path.basename(basename)
    dirs = job_manager._job_dirs(job_id)
    out_path = os.path.join(dirs["outputs_dir"], safe_name)

    if not os.path.isfile(out_path):
        raise HTTPException(status_code=404, detail=f"output '{safe_name}' not found for job {job_id}")

    return FileResponse(out_path, filename=safe_name)


@router_v2.post("/jobs/{job_id}/cancel", response_model=JobStatusResponse)
async def cancel_job_v2(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    current_status = job.get("status")

    # Terminal states — idempotent
    if current_status in ("completed", "failed", "cancelled"):
        enriched = job_manager.enrich_job_for_api(job_id)
        return _job_to_status_response(enriched or job)

    # Safe cancel: only pending/running → cancelled
    job_manager.update_job(
        job_id,
        status="cancelled",
        result={"error": "cancelled by user"},
    )
    enriched = job_manager.enrich_job_for_api(job_id)
    return _job_to_status_response(enriched or job)
