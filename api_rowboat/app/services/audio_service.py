import os

from .job_manager import job_manager
from ..providers.whisper_provider import WhisperProvider
from ..config import settings

whisper = WhisperProvider()



def transcribe_file_job(job_id: str, path: str):
    job_manager.update_job(job_id, status="running")
    try:
        text = whisper.transcribe(path)
        # Persistir siempre outputs en storage/jobs/<job_id>/outputs/
        out_path = job_manager.job_output_path(job_id, f"{job_id}_transcript.txt")
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(text)

        # Mantener compatibilidad: `outputs` como Dict[str, str] de rutas absolutas
        job_manager.update_job(
            job_id,
            status="completed",
            result={"text": text},
            outputs={"transcript_path": out_path},
        )
    except Exception as e:
        job_manager.update_job(job_id, status="failed", result={"error": str(e)})


def transcribe_sync(path: str):
    return whisper.transcribe(path)


class AudioService:
    def transcribe_file_job(self, job_id: str, path: str):
        return transcribe_file_job(job_id, path)


audio_service = AudioService()
