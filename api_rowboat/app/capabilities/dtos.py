from __future__ import annotations

from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional


class ProviderSummary(BaseModel):
    id: str
    name: str
    capabilities: List[str] = []


# ---------- Requests (v2 public contracts) ----------


class MediaJobBaseRequest(BaseModel):
    # Identificador del usuario que dispara el job (opcional)
    user_id: Optional[str] = None


class ImageGenerateRequest(BaseModel):
    prompt: str


class ImageEditRequest(BaseModel):
    prompt: str
    input_image: str = Field(..., description="Ruta interna o basename del input en job storage")


class ImageInpaintRequest(BaseModel):
    prompt: str
    input_image: str
    mask_image: str


class ImageUpscaleRequest(BaseModel):
    input_image: str
    scale: Optional[float] = 2.0


class ImageFaceSwapRequest(BaseModel):
    target_image: str
    source_face: str


class VideoProcessRequest(BaseModel):
    input_video: str


class VideoGenerateRequest(BaseModel):
    prompt: str


class VideoLipSyncRequest(BaseModel):
    input_video: str
    input_audio: str


class AudioTTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None


class AudioSTTRequest(BaseModel):
    input_audio: str


class AudioEnhanceRequest(BaseModel):
    input_audio: str


# ---------- Responses (v2 public contracts) ----------


class CapabilityListResponse(BaseModel):
    capabilities: List[str]


class ProvidersListResponse(BaseModel):
    providers: List[ProviderSummary]


class ProviderHealthResponse(BaseModel):
    provider_id: str
    status: str
    details: Optional[Dict[str, Any]] = None


class MediaJobResponse(BaseModel):
    job_id: str
    status: str
    capability: str
    provider_id: Optional[str] = None

    # Normalizado: rutas a disco (no payloads crudos de proveedores)
    outputs: Optional[Dict[str, str]] = None
    error: Optional[str] = None

    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class JobStatusResponse(BaseModel):
    job_id: str
    status: str
    type: str
    capability: Optional[str] = None

    outputs: Optional[Dict[str, str]] = None
    error: Optional[str] = None

