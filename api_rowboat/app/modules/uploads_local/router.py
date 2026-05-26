from __future__ import annotations

import os
import shutil
from fastapi import APIRouter, BackgroundTasks, File, HTTPException, UploadFile
from fastapi.responses import JSONResponse

from ...capabilities.capability_names import (
    CAPABILITY_AUDIO_STT,
    CAPABILITY_VIDEO_PROCESS,
)

from ...modules.uploads_local.schemas import BasenameRequest, UploadResponse
from ...modules.uploads_local.service import resolve_upload_path, save_upload
from ...config import settings
from ...services2.multimedia_orchestrator import media_orchestrator2
from ...services2.job_runner import run_media_job_by_background
from ...services.job_manager import job_manager


router_uploads_local = APIRouter(tags=["uploads-local", "v2"])


def _json_error(status_code: int, code: str, message: str, details: dict | None = None) -> JSONResponse:
    body: dict = {"error": {"code": code, "message": message}}
    if details:
        body["error"]["details"] = details
    return JSONResponse(status_code=status_code, content=body)


@router_uploads_local.post("/v2/upload", response_model=UploadResponse)
async def upload(file: UploadFile = File(...)):
    try:
        basename = save_upload(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    return UploadResponse(basename=basename)


def _ensure_in_job_inputs(basename: str, job_id: str) -> str:
    """Copy uploaded file from storage/uploads/ into the job inputs dir.

    v2 providers resolve local inputs by basename under storage/jobs/<job_id>/inputs.
    """
    src_path = resolve_upload_path(basename)
    dst_dir = os.path.join(settings.jobs_storage_dir, job_id, "inputs")
    os.makedirs(dst_dir, exist_ok=True)
    dst_path = os.path.join(dst_dir, os.path.basename(basename))
    shutil.copyfile(src_path, dst_path)
    return dst_path


def _check_provider_available(capability: str):
    provider_id = media_orchestrator2.router.route_provider_id(capability)
    if not provider_id:
        return _json_error(
            503,
            "NO_PROVIDER",
            f"No hay ningun provider disponible para la capability '{capability}'. Configura REPLICATE_API_TOKEN o COMFYUI_BASE_URL en el .env.",
        )
    return None


def _schedule_with_local_inputs(capability: str, basename: str, background_tasks: BackgroundTasks):
    # Create job first to know job_id so we can copy into its inputs dir.
    scheduled = media_orchestrator2.schedule_media_job(
        capability=capability,
        payload={"input_audio": basename} if capability == CAPABILITY_AUDIO_STT else {"input_video": basename} if capability == CAPABILITY_VIDEO_PROCESS else {"input_image": basename},
    )

    job_id = scheduled.get("job_id")
    if not job_id:
        return scheduled

    # Copy uploaded file into job inputs.
    try:
        _ensure_in_job_inputs(basename, job_id)
    except Exception as e:
        job_manager.update_job(job_id, status="failed", result={"error": str(e)})

    # Kick background runner if pending
    if scheduled.get("status") == "pending":
        background_tasks.add_task(run_media_job_by_background, job_id, capability, {})

    return scheduled


@router_uploads_local.post("/media/audio/stt", response_model=dict)
async def audio_stt(payload: BasenameRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_AUDIO_STT)
    if err:
        return err
    return _schedule_with_local_inputs(CAPABILITY_AUDIO_STT, payload.basename, background_tasks)


@router_uploads_local.post("/media/video/process", response_model=dict)
async def video_process(payload: BasenameRequest, background_tasks: BackgroundTasks):
    err = _check_provider_available(CAPABILITY_VIDEO_PROCESS)
    if err:
        return err
    return _schedule_with_local_inputs(CAPABILITY_VIDEO_PROCESS, payload.basename, background_tasks)


@router_uploads_local.post("/media/image/process", response_model=dict)
async def image_process(payload: BasenameRequest, background_tasks: BackgroundTasks):
    """Compat: `/media/image/process` actúa como alias de `image.edit` (por ahora).

    En el router v2 actual no existe la capability `image.process`; existen generate/edit/inpaint/upscale/face-swap.
    """
    # Usamos image.edit como procesamiento genérico.
    from ...capabilities.capability_names import CAPABILITY_IMAGE_EDIT

    err = _check_provider_available(CAPABILITY_IMAGE_EDIT)
    if err:
        return err

    # Como esta es una API wrapper por basename, no tenemos prompt.
    # Así que programamos job igual y permitimos que el provider maneje payload vacío.
    # Si tu provider requiere prompt, extiende este endpoint con campos adicionales.
    scheduled = media_orchestrator2.schedule_media_job(
        capability=CAPABILITY_IMAGE_EDIT,
        payload={"input_image": payload.basename},
    )

    job_id = scheduled.get("job_id")
    if job_id:
        try:
            _ensure_in_job_inputs(payload.basename, job_id)
        except Exception as e:
            job_manager.update_job(job_id, status="failed", result={"error": str(e)})

        if scheduled.get("status") == "pending":
            background_tasks.add_task(
                run_media_job_by_background,
                job_id,
                CAPABILITY_IMAGE_EDIT,
                scheduled.get("payload") or {},
            )

    return scheduled


