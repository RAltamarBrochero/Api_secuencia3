import os

from .base import ProviderBase


class WhisperNotAvailableError(RuntimeError):
    pass


class WhisperProvider(ProviderBase):
    def name(self) -> str:
        return "whisper"

    def transcribe(self, path: str) -> str:
        if not os.path.isfile(path):
            raise FileNotFoundError(f"Audio no encontrado: {path}")

        try:
            import whisper
        except ImportError as e:
            raise WhisperNotAvailableError(
                "openai-whisper no está instalado. Instala con: pip install openai-whisper "
                "(también necesitas ffmpeg en PATH)."
            ) from e

        model = whisper.load_model("base")
        result = model.transcribe(path)
        text = (result.get("text") or "").strip()
        if not text:
            raise RuntimeError("Whisper no devolvió texto para este archivo.")
        return text
