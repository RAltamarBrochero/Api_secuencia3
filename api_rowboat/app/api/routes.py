from fastapi import APIRouter, UploadFile, File, BackgroundTasks, HTTPException
from typing import List

from ..schemas import (
    HealthResponse,
    JobCreate,
    JobResponse,
    TranscribeResponse,
    ImageGenerateRequest,
)
from ..services.job_manager import job_manager
from ..services.audio_service import audio_service
from ..services.image_service import image_service
from ..services.video_service import video_service

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health():
    return {"status": "ok", "version": "0.1.0"}


@router.post("/jobs", response_model=JobResponse)
async def create_job(payload: JobCreate, background_tasks: BackgroundTasks):
    job = job_manager.create_job(payload.type, payload.payload)
    # For extensibility, background execution can be delegated based on type
    background_tasks.add_task(job_manager.run_job, job["id"])
    return job


@router.get("/jobs", response_model=List[JobResponse])
async def list_jobs():
    return job_manager.list_jobs()


@router.get("/jobs/{job_id}/outputs/{output_name}")
async def download_job_output(job_id: str, output_name: str):
    # Simple download endpoint for v1 local outputs.
    # output_name is treated as basename to avoid path traversal.
    import os
    from fastapi.responses import FileResponse

    if not output_name:
        raise HTTPException(status_code=400, detail="output_name is required")

    output_name = os.path.basename(output_name)
    dirs = job_manager._job_dirs(job_id)
    out_path = os.path.join(dirs["outputs_dir"], output_name)

    if not os.path.exists(out_path):
        raise HTTPException(status_code=404, detail="output not found")

    return FileResponse(out_path, filename=output_name)


@router.get("/jobs/{job_id}", response_model=JobResponse)
async def get_job(job_id: str):
    job = job_manager.enrich_job_for_api(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="job not found")
    return job



@router.post("/audio/transcribe", response_model=TranscribeResponse)
async def transcribe_audio(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    if not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    job = job_manager.create_job("audio:transcribe", {"filename": file.filename})
    # Save to disk
    path = job_manager.save_upload(job["id"], file)
    background_tasks.add_task(audio_service.transcribe_file_job, job["id"], path)
    return {"job_id": job["id"], "status": job["status"], "result": None}


@router.post("/image/generate")
async def image_generate(payload: ImageGenerateRequest, background_tasks: BackgroundTasks):
    job = job_manager.create_job("image:generate", {"prompt": payload.prompt})
    background_tasks.add_task(image_service.generate_image_job, job["id"], payload.prompt)
    return {"job_id": job["id"], "status": job["status"]}


@router.post("/video/process-basic")
async def video_process_basic(file: UploadFile = File(...), background_tasks: BackgroundTasks = None):
    job = job_manager.create_job("video:process", {"filename": file.filename})
    path = job_manager.save_upload(job["id"], file)
    background_tasks.add_task(video_service.process_basic_job, job["id"], path)
    return {"job_id": job["id"], "status": job["status"]}
