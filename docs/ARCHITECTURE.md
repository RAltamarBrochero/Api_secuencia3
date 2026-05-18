# Arquitectura - Api_rowboat v0.1

Estructura por capas:

- `api` (endpoints)
- `services` (lógica de negocio y orquestación)
- `providers` (conectores intercambiables: local y remotos)
- `jobs` (gestor y cola simple)
- `config` (ajustes por entorno)

La API está diseñada para ser extensible por proveedores. Cada dominio (imagen, audio, video)
expone interfaces en `providers/base.py`. Implementaciones actuales:

- `ffmpeg_provider` (local)
- `whisper_provider` (local, opcional si está instalado)
- `huggingface_provider` (remoto via Inference API)

El `JobManager` es una cola en memoria para v1 y usa `BackgroundTasks` para ejecución asíncrona.

Futuras integraciones previstas: ComfyUI local, Replicate, adaptadores para TTS/STT, upscaling,
inpainting, face-swap, lip-sync.