def test_generic_job_fails_without_handler(client):
    r = client.post("/jobs", json={"type": "custom:noop", "payload": {}})
    assert r.status_code == 200
    job_id = r.json()["id"]
    detail = client.get(f"/jobs/{job_id}")
    assert detail.status_code == 200
    body = detail.json()
    assert body["status"] == "failed"
    assert "handler" in (body.get("result") or {}).get("error", "").lower()


def test_get_job_has_timestamps_and_dirs(client):
    r = client.post("/jobs", json={"type": "test", "payload": {}})
    job_id = r.json()["id"]
    j = client.get(f"/jobs/{job_id}").json()
    assert "created_at" in j
    assert "updated_at" in j
    assert "outputs_dir" in j
