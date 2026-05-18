"""
interfaces/dtos/audio.py
========================
DTOs mínimos de operaciones de audio.

Equivalen exactamente a:
    export interface AudioSttDto { ... }
    export interface AudioTtsDto { ... }

Uso:
    from api_rowboat.app.interfaces.dtos.audio import AudioSttDto, AudioTtsDto
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional

from .image import MediaInputRef  # reutiliza el contrato compartido


# ---------------------------------------------------------------------------
# AudioSttDto  (Speech-to-Text)
# ---------------------------------------------------------------------------


@dataclass
class AudioSttDto:
    """DTO para audio.stt (transcripción).

    Equivale a:
        export interface AudioSttDto {
            provider?:      'replicate';
            audio:          MediaInputRef;
            language?:      string;
            timestamps?:    boolean;
            diarization?:   boolean;
            async?:         boolean;
            options?:       Record<string, unknown>;
        }
    """

    audio: MediaInputRef                                    # requerido
    provider: Optional[Literal["replicate"]] = None        # provider?
    language: Optional[str] = None
    timestamps: bool = False                               # timestamps?
    diarization: bool = False                              # diarization?
    async_mode: bool = False                               # async? (async es keyword en Python)
    options: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# AudioTtsDto  (Text-to-Speech)
# ---------------------------------------------------------------------------


@dataclass
class AudioTtsDto:
    """DTO para audio.tts (síntesis de voz).

    Equivale a:
        export interface AudioTtsDto {
            provider?: 'replicate';
            text:      string;
            voice?:    string;
            language?: string;
            speed?:    number;
            async?:    boolean;
            options?:  Record<string, unknown>;
        }
    """

    text: str                                               # requerido
    provider: Optional[Literal["replicate"]] = None
    voice: Optional[str] = None
    language: Optional[str] = None
    speed: Optional[float] = None                          # ej: 1.0 = normal
    async_mode: bool = False
    options: Dict[str, Any] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Exports explícitos
# ---------------------------------------------------------------------------

__all__ = [
    "AudioSttDto",
    "AudioTtsDto",
]
