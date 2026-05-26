import os

from .job_manager import job_manager
from ..providers.ffmpeg_audio_editor import FFmpegAudioEditor

audio_editor = FFmpegAudioEditor()


def _output_ext(path: str) -> str:
    return os.path.splitext(path)[1] or ".mp3"


def denoise_job(job_id: str, path: str, intensity: float = 0.5):
    job_manager.update_job(job_id, status="running")
    try:
        ext = _output_ext(path)
        out_path = job_manager.job_output_path(job_id, f"{job_id}_denoised{ext}")
        result = audio_editor.denoise(path, out_path, intensity)
        job_manager.update_job(
            job_id, status="completed",
            result={"operation": "denoise", "intensity": intensity},
            outputs={"audio_path": result["output_path"]},
        )
    except Exception as e:
        job_manager.update_job(job_id, status="failed", result={"error": str(e)})


def trim_job(job_id: str, path: str, start: float = 0.0,
             end: float = None, duration: float = None):
    job_manager.update_job(job_id, status="running")
    try:
        ext = _output_ext(path)
        out_path = job_manager.job_output_path(job_id, f"{job_id}_trimmed{ext}")
        result = audio_editor.trim(path, out_path, start, end, duration)
        job_manager.update_job(
            job_id, status="completed",
            result={"operation": "trim", "start": start, "end": end, "duration": duration},
            outputs={"audio_path": result["output_path"]},
        )
    except Exception as e:
        job_manager.update_job(job_id, status="failed", result={"error": str(e)})


def normalize_job(job_id: str, path: str):
    job_manager.update_job(job_id, status="running")
    try:
        ext = _output_ext(path)
        out_path = job_manager.job_output_path(job_id, f"{job_id}_normalized{ext}")
        result = audio_editor.normalize(path, out_path)
        job_manager.update_job(
            job_id, status="completed",
            result={"operation": "normalize"},
            outputs={"audio_path": result["output_path"]},
        )
    except Exception as e:
        job_manager.update_job(job_id, status="failed", result={"error": str(e)})


def improve_job(job_id: str, path: str, intensity: float = 0.5):
    job_manager.update_job(job_id, status="running")
    try:
        ext = _output_ext(path)
        out_path = job_manager.job_output_path(job_id, f"{job_id}_improved{ext}")
        result = audio_editor.improve(path, out_path, intensity)
        job_manager.update_job(
            job_id, status="completed",
            result={"operation": "improve", "intensity": intensity},
            outputs={"audio_path": result["output_path"]},
        )
    except Exception as e:
        job_manager.update_job(job_id, status="failed", result={"error": str(e)})
