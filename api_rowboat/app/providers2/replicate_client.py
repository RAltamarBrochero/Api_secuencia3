"""Cliente HTTP mínimo para Replicate predictions."""

from __future__ import annotations

import os
import time
from typing import Any, Dict, Optional

import requests

REPLICATE_API = "https://api.replicate.com/v1"


def _headers(token: str) -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }


def _parse_version(model_ref: str) -> str:
    """Acepta 'owner/model:version_hash' o solo version hash."""
    if ":" in model_ref:
        return model_ref.split(":", 1)[1]
    return model_ref


def resolve_audio_input(
    input_audio: str,
    job_id: str,
    jobs_storage_dir: str,
) -> str:
    if input_audio.startswith("http://") or input_audio.startswith("https://"):
        return input_audio

    if os.path.isabs(input_audio) and os.path.isfile(input_audio):
        return input_audio

    basename = os.path.basename(input_audio)
    candidate = os.path.join(jobs_storage_dir, job_id, "inputs", basename)
    if os.path.isfile(candidate):
        return candidate

    raise FileNotFoundError(
        f"No se encontró el audio de entrada: {input_audio} "
        f"(probado {candidate})"
    )


def create_prediction(token: str, version: str, input_data: Dict[str, Any]) -> str:
    body = {"version": version, "input": input_data}
    r = requests.post(
        f"{REPLICATE_API}/predictions",
        headers=_headers(token),
        json=body,
        timeout=60,
    )
    if r.status_code not in (200, 201):
        raise RuntimeError(f"Replicate error {r.status_code}: {r.text[:500]}")
    data = r.json()
    pred_id = data.get("id")
    if not pred_id:
        raise RuntimeError("Replicate no devolvió prediction id")
    return pred_id


def wait_prediction(token: str, prediction_id: str, timeout_sec: float = 300) -> Any:
    deadline = time.time() + timeout_sec
    while time.time() < deadline:
        r = requests.get(
            f"{REPLICATE_API}/predictions/{prediction_id}",
            headers=_headers(token),
            timeout=30,
        )
        if r.status_code != 200:
            raise RuntimeError(f"Replicate poll error {r.status_code}: {r.text[:300]}")
        data = r.json()
        status = data.get("status")
        if status == "succeeded":
            return data.get("output")
        if status in ("failed", "canceled"):
            raise RuntimeError(data.get("error") or f"Replicate prediction {status}")
        time.sleep(2)
    raise RuntimeError(f"Timeout esperando Replicate (id={prediction_id})")


def extract_transcript(output: Any) -> str:
    if isinstance(output, str):
        return output.strip()
    if isinstance(output, dict):
        for key in ("text", "transcription", "transcript"):
            if output.get(key):
                return str(output[key]).strip()
    if isinstance(output, list) and output:
        return extract_transcript(output[0])
    raise RuntimeError("Replicate no devolvió un formato de transcripción reconocible.")


def run_stt(
    token: str,
    model_ref: str,
    audio_source: str,
) -> str:
    version = _parse_version(model_ref)
    input_data: Dict[str, Any] = {}

    if audio_source.startswith("http://") or audio_source.startswith("https://"):
        input_data["audio"] = audio_source
    else:
        with open(audio_source, "rb") as f:
            r = requests.post(
                f"{REPLICATE_API}/files",
                headers={"Authorization": f"Bearer {token}"},
                files={
                    "content": (
                        os.path.basename(audio_source),
                        f,
                        "application/octet-stream",
                    )
                },
                timeout=120,
            )
        if r.status_code not in (200, 201):
            raise RuntimeError(
                f"No se pudo subir el audio a Replicate ({r.status_code}). "
                "Usa una URL pública en input_audio o verifica el token."
            )
        file_url = (r.json() or {}).get("urls", {}).get("get")
        if not file_url:
            raise RuntimeError("Replicate file upload no devolvió URL")
        input_data["audio"] = file_url

    pred_id = create_prediction(token, version, input_data)
    output = wait_prediction(token, pred_id)
    return extract_transcript(output)
