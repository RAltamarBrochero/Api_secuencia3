from __future__ import annotations

from typing import Any, Dict, Optional

from ..capabilities.capability_names import ALL_CAPABILITIES
from ..services2.capability_router import CapabilityRouter2
from ..providers2.registry import provider_registry2
from ..services.job_manager import job_manager


class MediaOrchestrator2:
    def __init__(self) -> None:
        self.router = CapabilityRouter2()

    def capability_to_job_type(self, capability: str) -> str:
        return f"media:{capability}"

    def _response_from_job(
        self,
        job: Dict[str, Any],
        capability: str,
        provider_id: Optional[str],
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        jid = job["id"]
        current = job_manager.get_job(jid) or job
        return {
            "job_id": jid,
            "status": current.get("status"),
            "capability": capability,
            "provider_id": provider_id,
            "outputs": current.get("outputs") or None,
            "error": error or (current.get("result") or {}).get("error"),
            "created_at": job.get("created_at"),
            "updated_at": current.get("updated_at"),
        }

    def schedule_media_job(
        self,
        *,
        capability: str,
        payload: Dict[str, Any],
    ) -> Dict[str, Any]:
        if capability not in ALL_CAPABILITIES:
            job = job_manager.create_job(
                self.capability_to_job_type(capability),
                {"capability": capability, "payload": payload},
            )
            job_manager.update_job(
                job["id"],
                status="failed",
                result={"error": f"Unknown capability: {capability}"},
            )
            return self._response_from_job(job, capability, None)

        provider_id = self.router.route_provider_id(capability)
        if not provider_id:
            job = job_manager.create_job(
                self.capability_to_job_type(capability),
                {"capability": capability, "payload": payload},
            )
            job_manager.update_job(
                job["id"],
                status="failed",
                result={"error": f"No provider found for capability: {capability}"},
            )
            return self._response_from_job(
                job, capability, None, f"No provider found for capability: {capability}"
            )

        job = job_manager.create_job(
            self.capability_to_job_type(capability),
            {
                "capability": capability,
                "provider_id": provider_id,
                "payload": payload,
            },
        )
        return self._response_from_job(job, capability, provider_id)

    def run_media_job(
        self,
        job_id: str,
        *,
        capability: str,
        payload: Dict[str, Any],
        input_paths: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        job = job_manager.get_job(job_id)
        if not job:
            return {
                "job_id": job_id,
                "status": "failed",
                "capability": capability,
                "provider_id": None,
                "outputs": None,
                "error": "job not found",
            }

        provider_id = (job.get("payload") or {}).get("provider_id") or self.router.route_provider_id(
            capability
        )
        if not provider_id:
            job_manager.update_job(
                job_id,
                status="failed",
                result={"error": f"No provider for {capability}"},
            )
            return self._response_from_job(job, capability, None)

        provider = provider_registry2.get(provider_id)
        if not provider:
            job_manager.update_job(
                job_id,
                status="failed",
                result={"error": "Provider not found in registry"},
            )
            return self._response_from_job(job, capability, provider_id)

        job_manager.update_job(job_id, status="running")
        result = provider.run_capability(
            capability,
            payload,
            job_id=job_id,
            input_paths=input_paths,
        )

        outputs = result.get("outputs")
        error = result.get("error")

        if error:
            job_manager.update_job(
                job_id,
                status="failed",
                result={"error": error},
                outputs=outputs,
            )
        else:
            job_manager.update_job(
                job_id,
                status="completed",
                result={"provider_result": result.get("provider_result")},
                outputs=outputs,
            )

        return self._response_from_job(
            job_manager.get_job(job_id) or job,
            capability,
            provider_id,
            error,
        )


media_orchestrator2 = MediaOrchestrator2()
