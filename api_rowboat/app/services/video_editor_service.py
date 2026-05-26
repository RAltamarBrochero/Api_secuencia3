from .job_manager import job_manager
from ..providers.ffmpeg_video_editor import FFmpegVideoEditor

video_editor = FFmpegVideoEditor()


def trim_job(job_id: str, path: str, start: float = 0.0,
             end: float = None, duration: float = None):
    job_manager.update_job(job_id, status="running")
    try:
        out_path = job_manager.job_output_path(job_id, f"{job_id}_trimmed.mp4")
        result = video_editor.trim(path, out_path, start, end, duration)
        job_manager.update_job(
            job_id, status="completed",
            result={"operation": "trim", "start": start, "end": end, "duration": duration},
            outputs={"video_path": result["output_path"]},
        )
    except Exception as e:
        job_manager.update_job(job_id, status="failed", result={"error": str(e)})
