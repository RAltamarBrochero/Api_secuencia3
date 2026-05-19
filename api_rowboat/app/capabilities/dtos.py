from __future__ import annotations

from pydantic import BaseModel, Field, validator
from typing import Any, Dict, List, Optional


class ProviderSummary(BaseModel):
    id: str
    name: str
    capabilities: List[str] = []


# ---------------------------------------------------------------------------
# Request schemas (v2 public contracts)
# ---------------------------------------------------------------------------

class ImageGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000, description="Descripción de la imagen a generar")
    negative_prompt: Optional[str] = Field(None, max_length=2000, description="Prompt negativo (opcional)")

    @validator("prompt")
    def prompt_not_blank(cls, v):
        if not v.strip():
            raise ValueError("prompt no puede estar vacío")
        return v.strip()


class ImageEditRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    input_image: str = Field(..., description="URL pública o basename del input en job storage")

    @validator("prompt")
    def prompt_not_blank(cls, v):
        if not v.strip():
            raise ValueError("prompt no puede estar vacío")
        return v.strip()


class ImageInpaintRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)
    input_image: str = Field(..., description="URL pública de la imagen base")
    mask_image: str = Field(..., description="URL pública de la máscara (blanco = zona a rellenar)")

    @validator("prompt")
    def prompt_not_blank(cls, v):
        if not v.strip():
            raise ValueError("prompt no puede estar vacío")
        return v.strip()


class ImageUpscaleRequest(BaseModel):
    input_image: str = Field(..., description="URL pública de la imagen a escalar")
    scale: Optional[float] = Field(2.0, ge=1.0, le=8.0, description="Factor de escala (1-8x)")


class ImageFaceSwapRequest(BaseModel):
    target_image: str = Field(..., description="URL pública de la imagen objetivo")
    source_face: str = Field(..., description="URL pública de la imagen con el rostro fuente")


class VideoProcessRequest(BaseModel):
    input_video: str = Field(..., description="URL pública del video a procesar")


class VideoGenerateRequest(BaseModel):
    prompt: str = Field(..., min_length=1, max_length=2000)

    @validator("prompt")
    def prompt_not_blank(cls, v):
        if not v.strip():
            raise ValueError("prompt no puede estar vacío")
        return v.strip()


class VideoLipSyncRequest(BaseModel):
    input_video: str = Field(..., description="URL pública o ruta del video fuente")
    input_audio: str = Field(..., description="URL pública o basename del audio de driving")


class AudioTTSRequest(BaseModel):
    text: str = Field(..., min_length=1, max_length=5000, description="Texto a sintetizar")
    voice: Optional[str] = Field(None, description="Preset de voz (depende del modelo)")

    @validator("text")
    def text_not_blank(cls, v):
        if not v.strip():
            raise ValueError("text no puede estar vacío")
        return v.strip()


class AudioSTTRequest(BaseModel):
    input_audio: str = Field(..., description="URL pública o basename en inputs del job")


class AudioEnhanceRequest(BaseModel):
    input_audio: str = Field(..., description="URL pública o basename en inputs del job")


# ---------------------------------------------------------------------------
# Response schemas
# ---------------------------------------------------------------------------

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
