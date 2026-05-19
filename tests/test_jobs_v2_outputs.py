"""Tests for job outputs, manifest.json, and download endpoint."""
import json
import os
import tempfile
import pytest

from api_rowboat.app.services.job_manager import job_manager
from api_rowboat.app.config import settings


def test_manifest_written_on_update(tmp_path, monkeypatch):
    """update_job with outputs must write manifest.json."""
    monkeypatch.setattr(settings, "jobs_storage_dir", str(tmp_path))
    job = job_manager.create_job("test:manifest", {})
    job_id = job["id"]

    # Create a fake output file
    dirs = job_manager._job_dirs(job_id)
    fake_out = os.path.join(dirs["outputs_dir"], "result.txt")
    with open(fake_out, "w") as f:
        f.write("hello")

    job_manager.update_job(job_id, status="completed", outputs={"result_path": fake_out})

    manifest_path = os.path.join(dirs["outputs_dir"], "manifest.json")
    assert os.path.isfile(manifest_path), "manifest.json debe existir tras update_job con outputs"
    with open(manifest_path) as f:
        m = json.load(f)
    assert m["job_id"] == job_id
    assert "result_path" in m["files"]
    assert m["files"]["result_path"]["basename"] == "result.txt"
    assert "/outputs/result.txt" in m["files"]["result_path"]["download_route"]


def test_download_output_via_endpoint(client, tmp_path, monkeypatch):
    """GET /jobs/{id}/outputs/{basename} serves real files."""
    monkeypatch.setattr(settings, "jobs_storage_dir", str(tmp_path))

    job = job_manager.create_job("test:download", {})
    job_id = job["id"]
    dirs = job_manager._job_dirs(job_id)
    fake_out = os.path.join(dirs["outputs_dir"], "output.txt")
    with open(fake_out, "w") as f:
        f.write("output content")

    job_manager.update_job(job_id, status="completed", outputs={"output_path": fake_out})

    r = client.get(f"/jobs/{job_id}/outputs/output.txt")
    assert r.status_code == 200
    assert b"output content" in r.content


def test_manifest_endpoint(client, tmp_path, monkeypatch):
    """GET /jobs/{id}/manifest returns manifest.json."""
    monkeypatch.setattr(settings, "jobs_storage_dir", str(tmp_path))

    job = job_manager.create_job("test:manifest_ep", {})
    job_id = job["id"]
    dirs = job_manager._job_dirs(job_id)
    fake_out = os.path.join(dirs["outputs_dir"], "audio.mp3")
    with open(fake_out, "wb") as f:
        f.write(b"\xff\xfb")  # fake mp3 header

    job_manager.update_job(job_id, status="completed", outputs={"audio_path": fake_out})

    r = client.get(f"/jobs/{job_id}/manifest")
    assert r.status_code == 200
    m = r.json()
    assert m["job_id"] == job_id
    assert "audio_path" in m["files"]
