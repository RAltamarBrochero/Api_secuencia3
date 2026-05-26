import os
import subprocess


class FFmpegAudioEditor:
    def name(self) -> str:
        return "ffmpeg_audio_editor"

    def denoise(self, path: str, output_path: str, intensity: float = 0.5) -> dict:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Audio no encontrado: {path}")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", path,
            "-af", f"anlmdn=s={intensity:.2f}",
        ]
        cmd.extend(self._codec_args(output_path))
        cmd.append(output_path)
        self._run_ffmpeg(cmd)
        if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError("ffmpeg no generó un archivo de salida válido.")
        return {"output_path": output_path}

    def trim(self, path: str, output_path: str, start: float = 0.0,
             end: float = None, duration: float = None) -> dict:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Audio no encontrado: {path}")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = ["ffmpeg", "-y", "-i", path, "-ss", str(start)]
        if end is not None:
            cmd.extend(["-to", str(end)])
        elif duration is not None:
            cmd.extend(["-t", str(duration)])
        cmd.extend(self._codec_args(output_path))
        cmd.append(output_path)
        self._run_ffmpeg(cmd)
        if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError("ffmpeg no generó un archivo de salida válido.")
        return {"output_path": output_path}

    def normalize(self, path: str, output_path: str) -> dict:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Audio no encontrado: {path}")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", path,
            "-af", "dynaudnorm",
        ]
        cmd.extend(self._codec_args(output_path))
        cmd.append(output_path)
        self._run_ffmpeg(cmd)
        if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError("ffmpeg no generó un archivo de salida válido.")
        return {"output_path": output_path}

    def improve(self, path: str, output_path: str, intensity: float = 0.5) -> dict:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Audio no encontrado: {path}")
        os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
        cmd = [
            "ffmpeg", "-y",
            "-i", path,
            "-af", f"anlmdn=s={intensity:.2f},dynaudnorm",
        ]
        cmd.extend(self._codec_args(output_path))
        cmd.append(output_path)
        self._run_ffmpeg(cmd)
        if not os.path.isfile(output_path) or os.path.getsize(output_path) == 0:
            raise RuntimeError("ffmpeg no generó un archivo de salida válido.")
        return {"output_path": output_path}

    def _codec_args(self, output_path: str) -> list:
        ext = os.path.splitext(output_path)[1].lower()
        if ext == ".wav":
            return ["-c:a", "pcm_s16le"]
        elif ext == ".mp3":
            return ["-c:a", "libmp3lame", "-q:a", "2"]
        else:
            return ["-c:a", "aac", "-b:a", "192k"]

    def _run_ffmpeg(self, cmd: list):
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        except FileNotFoundError as e:
            raise RuntimeError("ffmpeg no encontrado. Instálalo y añádelo al PATH.") from e
        except subprocess.CalledProcessError as e:
            stderr = e.stderr.decode(errors="ignore") if e.stderr else str(e)
            raise RuntimeError(f"ffmpeg falló: {stderr[:500]}")
