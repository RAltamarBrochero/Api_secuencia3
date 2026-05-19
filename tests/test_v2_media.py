"""Tests v2: providers, capabilities, jobs, outputs, states, cancel."""
import pytest


def test_providers_list(client):
    r = client.get("/providers")
    assert r.status_code == 200
    data = r.json()
    assert "providers" in data
    ids = [p["id"] for p in data["providers"]]
    assert "replicate" in ids
    assert "comfyui" in ids


def test_capabilities_list(client):
    r = client.get("/capabilities")
    assert r.status_code == 200
    caps = r.json()["capabilities"]
    assert "image.generate" in caps
    assert "audio.stt" in caps
    assert "video.process" in caps
    assert len(caps) == 11


def test_provider_health_replicate(client):
    r = client.get("/providers/replicate/health")
    assert r.status_code == 200
    data = r.json()
    assert "status" in data
    assert data["provider_id"] == "replicate"


def test_provider_health_comfyui(client):
    r = client.get("/providers/comfyui/health")
    assert r.status_code == 200
    data = r.json()
    assert data["provider_id"] == "comfyui"


def test_provider_health_not_found(client):
    r = client.get("/providers/does-not-exist/health")
    assert r.status_code == 404


def test_media_image_generate_returns_job(client):
    r = client.post("/media/image/generate", json={"prompt": "a red boat"})
    # 200 with job OR 503 if no provider configured — both are correct
    assert r.status_code in (200, 503)
    if r.status_code == 200:
        data = r.json()
        assert data["job_id"]
        assert data["status"] in ("pending", "failed", "running", "completed")
        assert data["capability"] == "image.generate"


def test_media_image_generate_empty_prompt_rejected(client):
    r = client.post("/media/image/generate", json={"prompt": "   "})
    assert r.status_code == 422


def test_media_image_generate_missing_prompt(client):
    r = client.post("/media/image/generate", json={})
    assert r.status_code == 422


def test_media_audio_tts_empty_text_rejected(client):
    r = client.post("/media/audio/tts", json={"text": "  "})
    assert r.status_code == 422


def test_media_image_upscale_scale_out_of_range(client):
    r = client.post("/media/image/upscale", json={"input_image": "http://example.com/img.png", "scale": 99})
    assert r.status_code == 422


def test_job_status_not_found(client):
    r = client.get("/jobs/00000000-0000-0000-0000-000000000000")
    assert r.status_code == 404


def test_job_cancel_not_found(client):
    r = client.post("/jobs/00000000-0000-0000-0000-000000000000/cancel")
    assert r.status_code == 404


def test_job_cancel_flow(client):
    """Create a job via v2, then cancel it."""
    # Use image.generate which may fail (no token) but creates a job
    r = client.post("/media/image/generate", json={"prompt": "test cancel"})
    if r.status_code != 200:
        pytest.skip("No provider configured — skip cancel flow test")
    job_id = r.json()["job_id"]

    # Cancel
    rc = client.post(f"/jobs/{job_id}/cancel")
    assert rc.status_code == 200
    data = rc.json()
    # Must be in terminal state
    assert data["status"] in ("cancelled", "completed", "failed")

    # Cancel again — idempotent
    rc2 = client.post(f"/jobs/{job_id}/cancel")
    assert rc2.status_code == 200


def test_job_outputs_download_not_found(client):
    r = client.get("/jobs/00000000-0000-0000-0000-000000000000/outputs/file.txt")
    assert r.status_code == 404


def test_job_manifest_not_found(client):
    r = client.get("/jobs/00000000-0000-0000-0000-000000000000/manifest")
    assert r.status_code == 404


def test_no_provider_returns_503_json(client, monkeypatch):
    """When no provider is wired, endpoint returns 503 with JSON error."""
    from api_rowboat.app.services2.capability_router import CapabilityRouter2
    monkeypatch.setattr(CapabilityRouter2, "route_provider_id", lambda self, cap: None)

    r = client.post("/media/video/generate", json={"prompt": "a waterfall"})
    assert r.status_code == 503
    data = r.json()
    assert "error" in data
    assert data["error"]["code"] == "NO_PROVIDER"
