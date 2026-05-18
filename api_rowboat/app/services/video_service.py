from .job_manager import job_manager
from ..providers.ffmpeg_provider import FFmpegProvider

ffmpeg = FFmpegProvider()


def process_basic_job(job_id: str, path: str):
    job_manager.update_job(job_id, status="running")
    try:
        out_path = job_manager.job_output_path(job_id, f"{job_id}_processed.mp4")
        out = ffmpeg.process_basic(path, out_path)
        job_manager.update_job(
            job_id,
            status="completed",
            result={"provider": "ffmpeg"},
            outputs={"video_path": out["output_path"]},
        )
    except Exception as e:
        job_manager.update_job(job_id, status="failed", result={"error": str(e)}, outputs=None)


class VideoService:
    def process_basic_job(self, job_id: str, path: str):
        return process_basic_job(job_id, path)


video_service = VideoService()
