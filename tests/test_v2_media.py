def test_providers_list(client):
    r = client.get("/providers")
    assert r.status_code == 200
    assert "providers" in r.json()


def test_capabilities_list(client):
    r = client.get("/capabilities")
    assert r.status_code == 200
    assert "image.generate" in r.json()["capabilities"]


def test_media_image_generate_returns_job(client):
    r = client.post("/media/image/generate", json={"prompt": "a red boat"})
    assert r.status_code == 200
    data = r.json()
    assert data["job_id"]
    assert data["status"] in ("pending", "failed", "running", "completed")
