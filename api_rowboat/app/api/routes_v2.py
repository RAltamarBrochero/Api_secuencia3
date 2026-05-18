from __future__ import annotations

from fastapi import APIRouter, BackgroundTasks, HTTPException
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


router_v2 = APIRouter(tags=["v2"])


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
    return ProviderHealthResponse(
        provider_id=provider_id,
        status=p.health().get("status", "unknown"),
        details=p.health(),
    )


@router_v2.get("/capabilities", response_model=CapabilityListResponse)
async def capabilities():
    return {"capabilities": ALL_CAPABILITIES}


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


@router_v2.post("/media/image/generate", response_model=MediaJobResponse)
async def image_generate(payload: ImageGenerateRequest, background_tasks: BackgroundTasks):
    return _schedule(CAPABILITY_IMAGE_GENERATE, payload.dict(), background_tasks)


@router_v2.post("/media/image/edit", response_model=MediaJobResponse)
async def image_edit(payload: ImageEditRequest, background_tasks: BackgroundTasks):
    return _schedule(CAPABILITY_IMAGE_EDIT, payload.dict(), background_tasks)


@router_v2.post("/media/image/inpaint", response_model=MediaJobResponse)
async def image_inpaint(payload: ImageInpaintRequest, background_tasks: BackgroundTasks):
    return _schedule(CAPABILITY_IMAGE_INPAINT, payload.dict(), background_tasks)


@router_v2.post("/media/image/upscale", response_model=MediaJobResponse)
async def image_upscale(payload: ImageUpscaleRequest, background_tasks: BackgroundTasks):
    return _schedule(CAPABILITY_IMAGE_UPSCALE, payload.dict(), background_tasks)


@router_v2.post("/media/image/face-swap", response_model=MediaJobResponse)
async def image_face_swap(payload: ImageFaceSwapRequest, background_tasks: BackgroundTasks):
    return _schedule(CAPABILITY_IMAGE_FACE_SWAP, payload.dict(), background_tasks)


@router_v2.post("/media/video/process", response_model=MediaJobResponse)
async def video_process(payload: VideoProcessRequest, background_tasks: BackgroundTasks):
    return _schedule(CAPABILITY_VIDEO_PROCESS, payload.dict(), background_tasks)


@router_v2.post("/media/video/generate", response_model=MediaJobResponse)
async def video_generate(payload: VideoGenerateRequest, background_tasks: BackgroundTasks):
    return _schedule(CAPABILITY_VIDEO_GENERATE, payload.dict(), background_tasks)


@router_v2.post("/media/video/lip-sync", response_model=MediaJobResponse)
async def video_lip_sync(payload: VideoLipSyncRequest, background_tasks: BackgroundTasks):
    return _schedule(CAPABILITY_VIDEO_LIP_SYNC, payload.dict(), background_tasks)


@router_v2.post("/media/audio/tts", response_model=MediaJobResponse)
async def audio_tts(payload: AudioTTSRequest, background_tasks: BackgroundTasks):
    return _schedule(CAPABILITY_AUDIO_TTS, payload.dict(), background_tasks)


@router_v2.post("/media/audio/stt", response_model=MediaJobResponse)
async def audio_stt(payload: AudioSTTRequest, background_tasks: BackgroundTasks):
    return _schedule(CAPABILITY_AUDIO_STT, payload.dict(), background_tasks)


@router_v2.post("/media/audio/enhance", response_model=MediaJobResponse)
async def audio_enhance(payload: AudioEnhanceRequest, background_tasks: BackgroundTasks):
    return _schedule(CAPABILITY_AUDIO_ENHANCE, payload.dict(), background_tasks)


@router_v2.get("/jobs/{job_id}", response_model=JobStatusResponse)
async def get_job_v2(job_id: str):
    job = job_manager.enrich_job_for_api(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return _job_to_status_response(job)


@router_v2.post("/jobs/{job_id}/cancel", response_model=JobStatusResponse)
async def cancel_job_v2(job_id: str):
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")

    if job.get("status") in ("completed", "failed"):
        return _job_to_status_response(job)

    job_manager.update_job(
        job_id,
        status="cancelled",
        result={"error": "cancelled by user"},
        outputs=None,
    )
    enriched = job_manager.enrich_job_for_api(job_id)
    return _job_to_status_response(enriched or job)
