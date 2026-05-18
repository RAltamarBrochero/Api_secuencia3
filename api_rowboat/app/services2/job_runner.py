from __future__ import annotations

from typing import Any, Dict, Optional

from .multimedia_orchestrator import media_orchestrator2


def run_media_job_by_background(
    job_id: str,
    capability: str,
    payload: Dict[str, Any],
    input_paths: Optional[Dict[str, str]] = None,
):
    return media_orchestrator2.run_media_job(
        job_id,
        capability=capability,
        payload=payload,
        input_paths=input_paths,
    )
