import json
import os
import shutil
from copy import deepcopy
from datetime import datetime, timezone
from uuid import uuid4
from typing import Dict, Any, Optional
from fastapi import UploadFile

from ..config import settings


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


class JobManager:
    def __init__(self):
        self.jobs: Dict[str, Dict[str, Any]] = {}
        os.makedirs(settings.upload_dir, exist_ok=True)
        os.makedirs(settings.storage_dir, exist_ok=True)
        os.makedirs(settings.jobs_storage_dir, exist_ok=True)

    def _job_dirs(self, job_id: str) -> Dict[str, str]:
        inputs_dir = os.path.join(settings.jobs_storage_dir, job_id, "inputs")
        outputs_dir = os.path.join(settings.jobs_storage_dir, job_id, "outputs")
        tmp_dir = os.path.join(settings.jobs_storage_dir, job_id, "temp")
        os.makedirs(inputs_dir, exist_ok=True)
        os.makedirs(outputs_dir, exist_ok=True)
        os.makedirs(tmp_dir, exist_ok=True)
        return {
            "inputs_dir": inputs_dir,
            "outputs_dir": outputs_dir,
            "tmp_dir": tmp_dir,
        }

    def job_input_path(self, job_id: str, filename: str) -> str:
        dirs = self._job_dirs(job_id)
        safe_name = os.path.basename(filename) if filename else "upload"
        return os.path.join(dirs["inputs_dir"], safe_name)

    def job_output_path(self, job_id: str, filename: str) -> str:
        dirs = self._job_dirs(job_id)
        safe_name = os.path.basename(filename) if filename else "output"
        return os.path.join(dirs["outputs_dir"], safe_name)

    def job_tmp_path(self, job_id: str, filename: str) -> str:
        dirs = self._job_dirs(job_id)
        safe_name = os.path.basename(filename) if filename else "tmp"
        return os.path.join(dirs["tmp_dir"], safe_name)

    def create_job(self, type_: str, payload: Dict[str, Any] | None = None):
        job_id = str(uuid4())
        now = _now_iso()
        job = {
            "id": job_id,
            "type": type_,
            "status": "pending",
            "payload": payload or {},
            "result": None,
            "outputs": {},
            "created_at": now,
            "updated_at": now,
        }
        self.jobs[job_id] = job
        return job

    def list_jobs(self):
        return list(self.jobs.values())

    def get_job(self, job_id: str):
        return self.jobs.get(job_id)

    def update_job(self, job_id: str, **kwargs):
        job = self.jobs.get(job_id)
        if not job:
            return None
        outputs = kwargs.pop("outputs", None)
        if outputs:
            job_outputs = job.get("outputs") or {}
            job_outputs.update(outputs)
            job["outputs"] = job_outputs
            # Write / update manifest.json
            self._write_manifest(job_id, job_outputs)
        job.update(kwargs)
        job["updated_at"] = _now_iso()
        return job

    def _write_manifest(self, job_id: str, outputs: Dict[str, str]) -> None:
        """Write manifest.json to storage/jobs/<job_id>/outputs/manifest.json."""
        dirs = self._job_dirs(job_id)
        outputs_dir = dirs["outputs_dir"]
        manifest = {
            "job_id": job_id,
            "written_at": _now_iso(),
            "files": {},
        }
        for key, abs_path in outputs.items():
            if abs_path and isinstance(abs_path, str) and os.path.isfile(abs_path):
                basename = os.path.basename(abs_path)
                manifest["files"][key] = {
                    "basename": basename,
                    "size_bytes": os.path.getsize(abs_path),
                    "download_route": f"/jobs/{job_id}/outputs/{basename}",
                }
        manifest_path = os.path.join(outputs_dir, "manifest.json")
        with open(manifest_path, "w", encoding="utf-8") as f:
            json.dump(manifest, f, indent=2)

    def save_upload(self, job_id: str, upload: UploadFile):
        dest = self.job_input_path(job_id, upload.filename or "upload")
        with open(dest, "wb") as f:
            shutil.copyfileobj(upload.file, f)

        job = self.jobs.get(job_id)
        if job:
            job_inputs = job.get("inputs") or {}
            job_inputs["input_path"] = dest
            job_inputs.setdefault("input_files", {})
            job_inputs["input_files"][os.path.basename(dest)] = dest
            job["inputs"] = job_inputs
        return dest

    def run_job(self, job_id: str):
        job = self.jobs.get(job_id)
        if not job:
            return
        job_type = job.get("type", "")
        self.update_job(
            job_id,
            status="failed",
            result={
                "error": (
                    f"No hay handler para el tipo de job '{job_type}'. "
                    "Usa endpoints específicos: /audio/transcribe, /image/generate, "
                    "/video/process-basic o /media/* (v2)."
                )
            },
        )

    def enrich_job_for_api(self, job_id: str) -> Optional[Dict[str, Any]]:
        job = self.get_job(job_id)
        if not job:
            return None

        enriched = deepcopy(job)
        dirs = self._job_dirs(job_id)
        enriched["inputs_dir"] = dirs["inputs_dir"]
        enriched["outputs_dir"] = dirs["outputs_dir"]
        enriched["tmp_dir"] = dirs["tmp_dir"]

        inputs_meta = enriched.get("inputs") or {}
        if isinstance(inputs_meta, dict):
            enriched["input_path"] = inputs_meta.get("input_path", enriched.get("input_path"))
            enriched["input_files"] = inputs_meta.get("input_files", enriched.get("input_files"))

        output_files: Dict[str, str] = {}
        outputs_routes: Dict[str, str] = {}

        outputs_meta = enriched.get("outputs") or {}
        if isinstance(outputs_meta, dict):
            for _, abs_path in outputs_meta.items():
                if not abs_path or not isinstance(abs_path, str):
                    continue
                basename = os.path.basename(abs_path)
                output_files[basename] = abs_path
                outputs_routes[basename] = f"/jobs/{job_id}/outputs/{basename}"

        outputs_dir = dirs["outputs_dir"]
        if os.path.isdir(outputs_dir):
            for name in os.listdir(outputs_dir):
                if name == "manifest.json":
                    continue
                path = os.path.join(outputs_dir, name)
                if os.path.isfile(path):
                    output_files.setdefault(name, path)
                    outputs_routes.setdefault(name, f"/jobs/{job_id}/outputs/{name}")

        if output_files:
            enriched["output_files"] = output_files
        if outputs_routes:
            enriched["outputs_routes"] = outputs_routes

        return enriched


job_manager = JobManager()
