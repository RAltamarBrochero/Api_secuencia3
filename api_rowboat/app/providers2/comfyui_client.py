"""Cliente HTTP mínimo para ComfyUI (sin exponer payloads crudos en API pública)."""

from __future__ import annotations

import copy
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests


def _workflows_dir() -> Path:
    return Path(__file__).resolve().parents[2] / "workflows"


def load_workflow(workflow_name: str) -> Dict[str, Any]:
    path = _workflows_dir() / f"{workflow_name}.json"
    if not path.is_file():
        raise FileNotFoundError(
            f"Workflow '{workflow_name}' no encontrado en {path}. "
            "Exporta un workflow API desde ComfyUI y guárdalo ahí."
        )
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def inject_prompt(workflow: Dict[str, Any], prompt: str, negative_prompt: Optional[str] = None) -> Dict[str, Any]:
    wf = copy.deepcopy(workflow)
    positive_set = False
    negative_set = False

    for node in wf.values():
        if not isinstance(node, dict):
            continue
        if node.get("class_type") != "CLIPTextEncode":
            continue
        inputs = node.setdefault("inputs", {})
        meta = node.get("_meta", {}) or {}
        title = str(meta.get("title", "")).lower()

        if not positive_set and ("negative" not in title and "neg" not in title):
            inputs["text"] = prompt
            positive_set = True
        elif negative_prompt and not negative_set and ("negative" in title or "neg" in title):
            inputs["text"] = negative_prompt
            negative_set = True

    if not positive_set:
        for node in wf.values():
            if isinstance(node, dict) and node.get("class_type") == "CLIPTextEncode":
                node.setdefault("inputs", {})["text"] = prompt
                break

    return wf


def check_available(base_url: str, timeout: float = 5.0) -> None:
    url = base_url.rstrip("/")
    try:
        r = requests.get(f"{url}/system_stats", timeout=timeout)
        if r.status_code >= 400:
            raise RuntimeError(f"ComfyUI respondió HTTP {r.status_code}")
    except requests.RequestException as e:
        raise RuntimeError(
            f"ComfyUI no responde en {url}. ¿Está levantado? (python main.py --listen 127.0.0.1 --port 8188)"
        ) from e


def queue_prompt(base_url: str, workflow: Dict[str, Any], client_id: str) -> str:
    url = base_url.rstrip("/")
    body = {"prompt": workflow, "client_id": client_id}
    r = requests.post(f"{url}/prompt", json=body, timeout=30)
    if r.status_code != 200:
        raise RuntimeError(f"ComfyUI /prompt error {r.status_code}: {r.text[:300]}")
    data = r.json()
    prompt_id = data.get("prompt_id")
    if not prompt_id:
        raise RuntimeError("ComfyUI no devolvió prompt_id")
    return prompt_id


def wait_for_image(
    base_url: str,
    prompt_id: str,
    *,
    timeout_sec: float = 300,
    poll_interval: float = 1.5,
) -> Tuple[str, str, str]:
    """Retorna (filename, subfolder, type)."""
    url = base_url.rstrip("/")
    deadline = time.time() + timeout_sec

    while time.time() < deadline:
        r = requests.get(f"{url}/history/{prompt_id}", timeout=30)
        if r.status_code == 200:
            history = r.json()
            entry = history.get(prompt_id) if isinstance(history, dict) else None
            if entry and entry.get("outputs"):
                for node_out in entry["outputs"].values():
                    images = node_out.get("images") or []
                    if images:
                        img = images[0]
                        return (
                            img.get("filename", ""),
                            img.get("subfolder", "") or "",
                            img.get("type", "output") or "output",
                        )
        time.sleep(poll_interval)

    raise RuntimeError(f"Timeout esperando imagen de ComfyUI (prompt_id={prompt_id})")


def download_image(
    base_url: str,
    filename: str,
    subfolder: str,
    file_type: str,
) -> bytes:
    url = base_url.rstrip("/")
    params = {"filename": filename, "subfolder": subfolder, "type": file_type}
    r = requests.get(f"{url}/view", params=params, timeout=60)
    if r.status_code != 200:
        raise RuntimeError(f"ComfyUI /view error {r.status_code}")
    return r.content


def generate_image_to_path(
    base_url: str,
    workflow_name: str,
    prompt: str,
    dest_path: str,
    *,
    negative_prompt: Optional[str] = None,
) -> Dict[str, Any]:
    check_available(base_url)
    workflow = load_workflow(workflow_name)
    workflow = inject_prompt(workflow, prompt, negative_prompt)
    client_id = f"rowboat-{uuid.uuid4().hex[:12]}"
    prompt_id = queue_prompt(base_url, workflow, client_id)
    filename, subfolder, file_type = wait_for_image(base_url, prompt_id)
    if not filename:
        raise RuntimeError("ComfyUI no devolvió imágenes en el workflow")

    data = download_image(base_url, filename, subfolder, file_type)
    os.makedirs(os.path.dirname(dest_path) or ".", exist_ok=True)
    with open(dest_path, "wb") as f:
        f.write(data)

    return {"prompt_id": prompt_id, "filename": filename}
