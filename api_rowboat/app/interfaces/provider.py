"""
interfaces/provider.py
======================
Contrato canónico del sistema de Media Providers.

Equivale exactamente a las interfaces TypeScript:
  - ProviderExecutionContext
  - ProviderArtifact
  - ProviderExecutionResult
  - MediaProvider

Uso:
    from api_rowboat.app.interfaces.provider import (
        MediaProvider,
        ProviderExecutionContext,
        ProviderArtifact,
        ProviderExecutionResult,
    )

Nota de diseño:
  - MediaProvider se define como Protocol (typing.Protocol) para permitir
    duck-typing; los adapters existentes (ProviderBase2) son compatibles
    sin necesidad de herencia explícita.
  - Los value-objects son dataclasses inmutables para facilitar serialización.
  - Los tipos de status y artifact-type están expresados como Literal para
    autocompletado y validación estática.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Literal, Optional, Protocol, runtime_checkable


# ---------------------------------------------------------------------------
# Value-objects
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ProviderExecutionContext:
    """Contexto de trazabilidad que acompaña cada ejecución.

    Equivale a:
        export interface ProviderExecutionContext {
            requestId?: string;
            userId?:    string;
            traceId?:   string;
        }
    """

    request_id: Optional[str] = None  # requestId
    user_id: Optional[str] = None  # userId
    trace_id: Optional[str] = None  # traceId


# Tipo de artefacto — refleja exactamente el union type del contrato TS
ArtifactType = Literal[
    "image",
    "video",
    "audio",
    "mask",
    "transcript",
    "thumbnail",
    "other",
]

# Estado del job — refleja el union type del contrato TS
JobStatus = Literal[
    "queued",
    "running",
    "succeeded",
    "failed",
    "cancelled",
]


@dataclass
class ProviderArtifact:
    """Artefacto producido por un provider después de ejecutar una capability.

    Equivale a:
        export interface ProviderArtifact {
            id:          string;
            type:        'image' | 'video' | 'audio' | 'mask' | 'transcript' | 'thumbnail' | 'other';
            mimeType:    string;
            url?:        string;
            path?:       string;
            width?:      number;
            height?:     number;
            durationMs?: number;
            metadata?:   Record<string, unknown>;
        }
    """

    id: str
    type: ArtifactType
    mime_type: str  # mimeType
    url: Optional[str] = None
    path: Optional[str] = None
    width: Optional[int] = None
    height: Optional[int] = None
    duration_ms: Optional[int] = None  # durationMs
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ProviderExecutionResult:
    """Resultado normalizado de cualquier ejecución de provider.

    Equivale a:
        export interface ProviderExecutionResult {
            jobId:      string;
            provider:   string;
            capability: string;
            status:     'queued' | 'running' | 'succeeded' | 'failed' | 'cancelled';
            artifacts:  ProviderArtifact[];
            metadata?:  Record<string, unknown>;
            warnings?:  string[];
            error?:     string;
        }
    """

    job_id: str  # jobId
    provider: str
    capability: str
    status: JobStatus
    artifacts: List[ProviderArtifact] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    warnings: List[str] = field(default_factory=list)
    error: Optional[str] = None


# ---------------------------------------------------------------------------
# Protocol (interface estructural)
# ---------------------------------------------------------------------------


@runtime_checkable
class MediaProvider(Protocol):
    """Contrato estructural de un Media Provider.

    Equivale a:
        export interface MediaProvider {
            id: string;
            supports(capability: string): boolean;
            healthCheck(): Promise<boolean>;
            execute(
                capability: string,
                payload:    unknown,
                context?:   ProviderExecutionContext,
            ): Promise<ProviderExecutionResult>;
            getJob?(jobId: string):   Promise<ProviderExecutionResult>;
            cancelJob?(jobId: string): Promise<boolean>;
        }

    Los métodos opcionales (getJob / cancelJob) se modelan como métodos
    regulares que el adaptador puede o no implementar; el type-checker los
    trata como opcionales gracias a que Protocol no obliga a declararlos
    como abstractmethod.
    """

    @property
    def id(self) -> str:
        """Identificador único del provider (ej: 'comfyui', 'replicate')."""
        ...

    def supports(self, capability: str) -> bool:
        """Retorna True si el provider soporta la capability dada."""
        ...

    async def health_check(self) -> bool:
        """Comprueba la disponibilidad del provider.

        Equivale a: healthCheck(): Promise<boolean>
        """
        ...

    async def execute(
        self,
        capability: str,
        payload: Any,
        context: Optional[ProviderExecutionContext] = None,
    ) -> ProviderExecutionResult:
        """Ejecuta una capability y devuelve el resultado normalizado.

        Equivale a:
            execute(capability, payload, context?): Promise<ProviderExecutionResult>
        """
        ...

    # Métodos opcionales — los adapters los implementan si aplica

    async def get_job(self, job_id: str) -> ProviderExecutionResult:
        """Consulta el estado de un job asíncrono.

        Equivale a: getJob?(jobId): Promise<ProviderExecutionResult>
        """
        ...

    async def cancel_job(self, job_id: str) -> bool:
        """Cancela un job en curso.

        Equivale a: cancelJob?(jobId): Promise<boolean>
        """
        ...


# ---------------------------------------------------------------------------
# Exports explícitos
# ---------------------------------------------------------------------------

__all__ = [
    # Value-objects
    "ProviderExecutionContext",
    "ProviderArtifact",
    "ProviderExecutionResult",
    # Tipos auxiliares
    "ArtifactType",
    "JobStatus",
    # Protocol
    "MediaProvider",
]
