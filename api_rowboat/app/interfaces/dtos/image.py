"""
interfaces/dtos/image.py
========================
DTOs mínimos de operaciones de imagen.

Equivalen exactamente a:
    export interface ImageGenerateDto { ... }
    export interface MediaInputRef    { ... }
    export interface ImageEditDto     { ... }

Uso:
    from api_rowboat.app.interfaces.dtos.image import (
        ImageGenerateDto,
        MediaInputRef,
        ImageEditDto,
    )
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional


# ---------------------------------------------------------------------------
# Tipos auxiliares (union types del contrato TS)
# ---------------------------------------------------------------------------

ProviderChoice = Literal["comfyui", "replicate"]
OutputFormat = Literal["png", "jpg", "webp"]


# ---------------------------------------------------------------------------
# ImageGenerateDto
# ---------------------------------------------------------------------------


@dataclass
class ImageGenerateDto:
    """DTO para image.generate.

    Equivale a:
        export interface ImageGenerateDto {
            provider?:       'comfyui' | 'replicate';
            prompt:          string;
            negativePrompt?: string;
            width?:          number;
            height?:         number;
            steps?:          number;
            seed?:           number;
            outputFormat?:   'png' | 'jpg' | 'webp';
            async?:          boolean;
            options?:        Record<string, unknown>;
        }
    """

    prompt: str                                          # requerido
    provider: Optional[ProviderChoice] = None           # provider?
    negative_prompt: Optional[str] = None               # negativePrompt?
    width: Optional[int] = None
    height: Optional[int] = None
    steps: Optional[int] = None
    seed: Optional[int] = None
    output_format: Optional[OutputFormat] = None        # outputFormat?
    async_mode: bool = False                            # async? (async es keyword en Python)
    options: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# MediaInputRef  (compartido por ImageEditDto e ImageInpaintDto)
# ---------------------------------------------------------------------------


@dataclass
class MediaInputRef:
    """Referencia a un medio de entrada (url, path local o base64).

    Equivale a:
        export interface MediaInputRef {
            url?:    string;
            path?:   string;
            base64?: string;
        }

    Al menos uno de los tres campos debe estar presente.
    """

    url: Optional[str] = None
    path: Optional[str] = None
    base64: Optional[str] = None

    def __post_init__(self) -> None:
        if not any([self.url, self.path, self.base64]):
            raise ValueError(
                "MediaInputRef requiere al menos uno de: url, path, base64"
            )


# ---------------------------------------------------------------------------
# ImageEditDto  (cubre edit e inpaint — mask es opcional)
# ---------------------------------------------------------------------------


@dataclass
class ImageEditDto:
    """DTO para image.edit e image.inpaint.

    Equivale a:
        export interface ImageEditDto {
            provider?: 'comfyui' | 'replicate';
            image:     MediaInputRef;
            prompt:    string;
            mask?:     MediaInputRef;
            strength?: number;
            async?:    boolean;
            options?:  Record<string, unknown>;
        }

    Cuando `mask` está presente se trata como inpaint.
    """

    image: MediaInputRef                                 # requerido
    prompt: str                                          # requerido
    provider: Optional[ProviderChoice] = None
    mask: Optional[MediaInputRef] = None                 # mask? → inpaint mode
    strength: Optional[float] = None                    # 0.0–1.0
    async_mode: bool = False                            # async?
    options: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Exports explícitos
# ---------------------------------------------------------------------------

__all__ = [
    "ProviderChoice",
    "OutputFormat",
    "ImageGenerateDto",
    "MediaInputRef",
    "ImageEditDto",
]
