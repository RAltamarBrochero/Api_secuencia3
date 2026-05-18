from .job_manager import job_manager
from ..providers.huggingface_provider import HuggingFaceProvider

hf = HuggingFaceProvider()


def generate_image_job(job_id: str, prompt: str):
    job_manager.update_job(job_id, status="running")
    try:
        out = hf.generate_image(prompt)
        b = out.get("image_bytes")
        if not b:
            raise RuntimeError("No se recibieron bytes de imagen del provider.")

        out_path = job_manager.job_output_path(job_id, f"{job_id}_image.png")
        with open(out_path, "wb") as f:
            f.write(b)

        job_manager.update_job(
            job_id,
            status="completed",
            result={"provider": "huggingface"},
            outputs={"image_path": out_path},
        )
    except Exception as e:
        job_manager.update_job(job_id, status="failed", result={"error": str(e)}, outputs=None)


class ImageService:
    def generate_image_job(self, job_id: str, prompt: str):
        return generate_image_job(job_id, prompt)


image_service = ImageService()
