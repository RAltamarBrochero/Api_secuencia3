"""
interfaces/dtos/video.py
========================
DTOs mínimos de operaciones de video.

Equivalen exactamente a:
    export interface VideoLipSyncDto { ... }

Uso:
    from api_rowboat.app.interfaces.dtos.video import VideoLipSyncDto
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional

from .image import MediaInputRef  # reutiliza el contrato compartido


# ---------------------------------------------------------------------------
# Tipos auxiliares
# ---------------------------------------------------------------------------

SyncMode = Literal["fast", "balanced", "quality"]
VideoProviderChoice = Literal["replicate", "comfyui"]


# ---------------------------------------------------------------------------
# VideoLipSyncDto
# ---------------------------------------------------------------------------


@dataclass
class VideoLipSyncDto:
    """DTO para video.lip_sync.

    Equivale a:
        export interface VideoLipSyncDto {
            provider?: 'replicate' | 'comfyui';
            video:     MediaInputRef;
            audio:     MediaInputRef;
            syncMode?: 'fast' | 'balanced' | 'quality';
            async?:    boolean;
            options?:  Record<string, unknown>;
        }
    """

    video: MediaInputRef                                    # requerido
    audio: MediaInputRef                                    # requerido
    provider: Optional[VideoProviderChoice] = None
    sync_mode: Optional[SyncMode] = None                   # syncMode?
    async_mode: bool = False                               # async?
    options: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Exports explícitos
# ---------------------------------------------------------------------------

__all__ = [
    "SyncMode",
    "VideoProviderChoice",
    "VideoLipSyncDto",
]
