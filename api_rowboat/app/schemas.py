from pydantic import BaseModel
from typing import Any, Dict, Optional


class HealthResponse(BaseModel):
    status: str
    version: str


class JobCreate(BaseModel):
    type: str
    payload: Optional[Dict[str, Any]] = None


class JobResponse(BaseModel):
    id: str
    type: str
    status: str
    payload: Optional[Dict[str, Any]] = None
    result: Optional[Any] = None

    # Compatibility: keep the same field meaning (Dict[str, str] of absolute paths when available)
    outputs: Optional[Dict[str, str]] = None

    # Explicit fields used by GET /jobs/{id} (routes/views computed in routes.py)
    input_files: Optional[Dict[str, str]] = None  # basename -> absolute path
    output_files: Optional[Dict[str, str]] = None  # basename -> absolute path
    outputs_routes: Optional[Dict[str, str]] = None  # output basename -> download route

    # v1 paths convention (storage/jobs/<job_id>/...)
    inputs_dir: Optional[str] = None
    outputs_dir: Optional[str] = None
    tmp_dir: Optional[str] = None

    # Backward-friendly: sometimes services store single input path
    input_path: Optional[str] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class TranscribeResponse(BaseModel):
    job_id: str
    status: str
    result: Optional[Dict[str, Any]] = None


class ImageGenerateRequest(BaseModel):
    prompt: str

