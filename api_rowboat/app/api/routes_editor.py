from fastapi import APIRouter, UploadFile, File, Form, BackgroundTasks, HTTPException
from typing import Optional

from ..services.job_manager import job_manager
from ..services.audio_editor_service import denoise_job, trim_job as audio_trim_job
from ..services.audio_editor_service import normalize_job, improve_job
from ..services.video_editor_service import trim_job as video_trim_job

router_editor = APIRouter()


@router_editor.post("/audio/denoise")
async def audio_denoise(
    file: UploadFile = File(...),
    intensity: float = Form(0.5),
    background_tasks: BackgroundTasks = None,
):
    if not file.filename:
        raise HTTPException(400, "No file uploaded")
    job = job_manager.create_job("audio:denoise", {"filename": file.filename, "intensity": intensity})
    path = job_manager.save_upload(job["id"], file)
    background_tasks.add_task(denoise_job, job["id"], path, intensity)
    return {"job_id": job["id"], "status": job["status"], "result": None}


@router_editor.post("/audio/trim")
async def audio_trim(
    file: UploadFile = File(...),
    start: float = Form(0.0),
    end: Optional[float] = Form(None),
    duration: Optional[float] = Form(None),
    background_tasks: BackgroundTasks = None,
):
    if not file.filename:
        raise HTTPException(400, "No file uploaded")
    if end is None and duration is None:
        raise HTTPException(400, "Provide 'end' or 'duration'")
    job = job_manager.create_job("audio:trim", {
        "filename": file.filename, "start": start, "end": end, "duration": duration,
    })
    path = job_manager.save_upload(job["id"], file)
    background_tasks.add_task(audio_trim_job, job["id"], path, start, end, duration)
    return {"job_id": job["id"], "status": job["status"], "result": None}


@router_editor.post("/audio/normalize")
async def audio_normalize(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
):
    if not file.filename:
        raise HTTPException(400, "No file uploaded")
    job = job_manager.create_job("audio:normalize", {"filename": file.filename})
    path = job_manager.save_upload(job["id"], file)
    background_tasks.add_task(normalize_job, job["id"], path)
    return {"job_id": job["id"], "status": job["status"], "result": None}


@router_editor.post("/audio/improve")
async def audio_improve(
    file: UploadFile = File(...),
    intensity: float = Form(0.5),
    background_tasks: BackgroundTasks = None,
):
    if not file.filename:
        raise HTTPException(400, "No file uploaded")
    job = job_manager.create_job("audio:improve", {"filename": file.filename, "intensity": intensity})
    path = job_manager.save_upload(job["id"], file)
    background_tasks.add_task(improve_job, job["id"], path, intensity)
    return {"job_id": job["id"], "status": job["status"], "result": None}


@router_editor.post("/video/trim")
async def video_trim(
    file: UploadFile = File(...),
    start: float = Form(0.0),
    end: Optional[float] = Form(None),
    duration: Optional[float] = Form(None),
    background_tasks: BackgroundTasks = None,
):
    if not file.filename:
        raise HTTPException(400, "No file uploaded")
    if end is None and duration is None:
        raise HTTPException(400, "Provide 'end' or 'duration'")
    job = job_manager.create_job("video:trim", {
        "filename": file.filename, "start": start, "end": end, "duration": duration,
    })
    path = job_manager.save_upload(job["id"], file)
    background_tasks.add_task(video_trim_job, job["id"], path, start, end, duration)
    return {"job_id": job["id"], "status": job["status"], "result": None}
