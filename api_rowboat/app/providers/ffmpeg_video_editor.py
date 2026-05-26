import os
import subprocess


class FFmpegVideoEditor:
    def name(self) -> str:
        return "ffmpeg_video_editor"

    def trim(self, path: str, output_path: str, start: float = 0.0,
             end: float = None, duration: float = None) -> dict:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Video no encontrado: {path}")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = ["ffmpeg", "-y", "-i", path]
        cmd.extend(["-ss", str(start)])
        if end is not None:
            cmd.extend(["-to", str(end)])
        elif duration is not None:
            cmd.extend(["-t", str(duration)])
        cmd.extend(["-c:v", "libx264", "-preset", "veryfast", "-c:a", "aac"])
        cmd.append(output_path)
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError as e:
            raise RuntimeError("ffmpeg no encontrado. Instálalo y añádelo al PATH.") from e
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode(errors="ignore") if e.stderr else str(e)
            raise RuntimeError(f"ffmpeg falló: {stderr[:500]}")
        if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError("ffmpeg no generó un archivo de salida válido.")
        return {"output_path": output_path}
