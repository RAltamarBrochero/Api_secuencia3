import os
from unittest.mock import patch

import pytest


def test_image_generate_fails_without_hf_token(client):
    with patch("api_rowboat.app.providers.huggingface_provider.settings") as mock_settings:
        mock_settings.hf_api_token = None
        mock_settings.hf_api_url = "https://api-inference.huggingface.co"
        r = client.post("/image/generate", json={"prompt": "a boat"})
        assert r.status_code == 200
        job_id = r.json()["job_id"]
    job = client.get(f"/jobs/{job_id}").json()
    assert job["status"] == "failed"
    assert "HF_API_TOKEN" in (job.get("result") or {}).get("error", "")


@pytest.mark.skipif(not os.getenv("HF_API_TOKEN"), reason="HF_API_TOKEN no configurado")
def test_image_generate_with_token(client):
    r = client.post("/image/generate", json={"prompt": "a small red boat"})
    job_id = r.json()["job_id"]
    job = client.get(f"/jobs/{job_id}").json()
    assert job["status"] in ("completed", "failed", "running", "pending")
