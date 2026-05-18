from .registry import provider_registry2

# Registro automático de adapters
from .adapters.comfyui_adapter import ComfyUIAdapter2
from .adapters.replicate_adapter import ReplicateAdapter2

provider_registry2.register(ComfyUIAdapter2())
provider_registry2.register(ReplicateAdapter2())

# Re-exporta contratos canónicos para conveniencia
from ..interfaces.provider import (  # noqa: E402
    ProviderExecutionContext,
    ProviderArtifact,
    ProviderExecutionResult,
    MediaProvider,
)

__all__ = [
    "provider_registry2",
    "ComfyUIAdapter2",
    "ReplicateAdapter2",
    "ProviderExecutionContext",
    "ProviderArtifact",
    "ProviderExecutionResult",
    "MediaProvider",
]
