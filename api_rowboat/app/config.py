try:
    from pydantic import BaseSettings, Field
except Exception:
    from pydantic_settings import BaseSettings
    from pydantic import Field


class Settings(BaseSettings):
    env: str = Field("development", env="ENV")
    host: str = Field("127.0.0.1", env="API_ROWBOAT_HOST")
    port: int = Field(8000, env="API_ROWBOAT_PORT")

    default_audio_provider: str = Field("whisper", env="DEFAULT_AUDIO_PROVIDER")
    default_image_provider: str = Field("huggingface", env="DEFAULT_IMAGE_PROVIDER")
    default_video_provider: str = Field("ffmpeg", env="DEFAULT_VIDEO_PROVIDER")

    hf_api_url: str = Field(
        "https://api-inference.huggingface.co",
        env="HF_API_URL",
    )
    hf_api_token: str | None = Field(None, env="HF_API_TOKEN")

    upload_dir: str = Field("uploads", env="UPLOAD_DIR")
    storage_dir: str = "storage"
    jobs_storage_dir: str = "storage/jobs"

    # ComfyUI
    comfyui_enabled: bool = Field(True, env="COMFYUI_ENABLED")
    comfyui_base_url: str | None = Field(None, env="COMFYUI_BASE_URL")
    comfyui_ws_url: str | None = Field(None, env="COMFYUI_WS_URL")
    comfyui_workflow_image_generate: str = Field(
        "image-generate-v1",
        env="COMFYUI_DEFAULT_WORKFLOW_IMAGE_GENERATE",
    )

    # Replicate
    replicate_enabled: bool = Field(True, env="REPLICATE_ENABLED")
    replicate_api_token: str | None = Field(None, env="REPLICATE_API_TOKEN")
    replicate_default_model_audio_stt: str | None = Field(
        None,
        env="REPLICATE_DEFAULT_MODEL_AUDIO_STT",
    )

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()
