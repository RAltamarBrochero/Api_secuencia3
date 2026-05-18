import os
import subprocess

from .base import ProviderBase


class FFmpegProvider(ProviderBase):
    def name(self) -> str:
        return "ffmpeg"

    def process_basic(self, path: str, output_path: str) -> dict:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Video no encontrado: {path}")

        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = [
            "ffmpeg",
            "-y",
            "-i",
            path,
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            output_path,
        ]
        try:
            subprocess.run(
                cmd,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
        except FileNotFoundError as e:
            raise RuntimeError(
                "instala ffmpeg y añádelo al PATH de Windows."
            ) from e
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode(errors="ignore") if e.stderr else str(e)
            raise RuntimeError(f"ffmpeg falló: {stderr[:500]}")

        if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError("ffmpeg no generó un archivo de salida válido.")

        return {"output_path": output_path}
