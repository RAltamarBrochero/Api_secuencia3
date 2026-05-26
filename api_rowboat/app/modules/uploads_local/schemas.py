from __future__ import annotations

from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    basename: str


class BasenameRequest(BaseModel):
    basename: str = Field(..., min_length=1, description="Nombre base del archivo subido")

