from abc import ABC, abstractmethod


class ProviderBase(ABC):
    @abstractmethod
    def name(self) -> str:
        raise NotImplementedError()

    # Audio
    def transcribe(self, path: str) -> str:
        raise NotImplementedError()

    # Image
    def generate_image(self, prompt: str) -> dict:
        raise NotImplementedError()

    # Video
    def process_video(self, path: str) -> dict:
        raise NotImplementedError()
