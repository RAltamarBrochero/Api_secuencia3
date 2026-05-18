import requests

from .base import ProviderBase
from ..config import settings


class HuggingFaceProvider(ProviderBase):
    def name(self) -> str:
        return "huggingface"

    def generate_image(self, prompt: str) -> dict:
        token = (settings.hf_api_token or "").strip()
        if not token:
            raise RuntimeError(
                "HF_API_TOKEN no configurado. Añádelo en .env (copia desde .env.example)."
            )

        url = (settings.hf_api_url or "https://api-inference.huggingface.co").rstrip("/")
        headers = {"Authorization": f"Bearer {token}"}
        payload = {"inputs": prompt}

        resp = requests.post(
            f"{url}/models/stabilityai/stable-diffusion-2",
            json=payload,
            headers=headers,
            timeout=120,
        )
        if resp.status_code != 200:
            raise RuntimeError(f"Hugging Face error {resp.status_code}: {resp.text[:500]}")

        content = resp.content
        if not (content.startswith(b"\x89PNG") or content.startswith(b"\xff\xd8")):
            raise RuntimeError(
                "La respuesta de Hugging Face no parece una imagen PNG/JPEG válida."
            )

        return {"image_bytes": content}
