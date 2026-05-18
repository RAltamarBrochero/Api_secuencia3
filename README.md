# Api_rowboat

API híbrida (local + remota) para **audio, imagen y video** con jobs en disco: `storage/jobs/<job_id>/`.

## Quick start (Windows)

### 1. Entorno

```powershell
cd C:\Users\Rafael\Desktop\Api_secuencia3
copy .env.example .env
```

Edita `.env` con tus tokens (opcional al inicio). **No subas `.env` a git.**

### 2. Instalar y arrancar

```powershell
poetry install
poetry run uvicorn api_rowboat.app.main:app --reload --host 127.0.0.1 --port 8000
```

O: `.\scripts\dev.ps1`

### 3. Probar

```powershell
curl http://127.0.0.1:8000/health
```

Documentación interactiva: http://127.0.0.1:8000/docs

### 4. Dashboard (3 pasos)

1. Arranca la API (paso 2).
2. Abre `frontend/index.html` en el navegador (doble clic).
3. Pulsa **↻ PING** — debe mostrar Online (`http://127.0.0.1:8000`).

## Qué funciona sin credenciales

| Función | Endpoint | Sin deps |
|---------|----------|----------|
| Health | `GET /health` | Sí |
| Listar jobs | `GET /jobs` | Sí |
| Job genérico | `POST /jobs` | `failed` (sin handler) |
| Providers / capabilities v2 | `GET /providers`, `GET /capabilities` | Sí |
| Imagen v1 | `POST /image/generate` | `failed` sin `HF_API_TOKEN` |
| Audio v1 | `POST /audio/transcribe` | `failed` sin whisper/ffmpeg |
| Video v1 | `POST /video/process-basic` | `failed` sin ffmpeg |
| Imagen v2 ComfyUI | `POST /media/image/generate` | `failed` sin ComfyUI/workflow |
| STT v2 Replicate | `POST /media/audio/stt` | `failed` sin `REPLICATE_API_TOKEN` |

## Requisitos por servicio

| Servicio | Variable / instalación |
|----------|-------------------------|
| Imagen v1 (Hugging Face) | `HF_API_TOKEN` en `.env` |
| Audio v1 (Whisper local) | `pip install openai-whisper` + **ffmpeg** en PATH |
| Video v1 | **ffmpeg** en PATH (`winget install Gyan.FFmpeg`) |
| Imagen v2 (ComfyUI) | ComfyUI en `8188` + `api_rowboat/workflows/image-generate-v1.json` |
| STT v2 (Replicate) | `REPLICATE_API_TOKEN` + `REPLICATE_DEFAULT_MODEL_AUDIO_STT` |

## API v1

- `GET /health`
- `GET /jobs`, `GET /jobs/{id}`, `GET /jobs/{id}/outputs/{basename}`
- `POST /jobs` — job genérico (sin handler → `failed`)
- `POST /audio/transcribe` — multipart `file`
- `POST /image/generate` — `{"prompt":"..."}`
- `POST /video/process-basic` — multipart `file`

## API v2

- `GET /providers`, `GET /providers/{id}/health`, `GET /capabilities`
- `POST /media/image/generate`, `/media/audio/stt`, … (ver `/docs`)
- `GET /jobs/{id}`, `POST /jobs/{id}/cancel`

Jobs v2 usan el mismo storage y `GET /jobs/{id}` v1 para descargar outputs.

## Ejemplos curl

```powershell
curl -X POST http://127.0.0.1:8000/image/generate -H "Content-Type: application/json" -d "{\"prompt\":\"a red boat\"}"
curl http://127.0.0.1:8000/jobs/JOB_ID
curl -O http://127.0.0.1:8000/jobs/JOB_ID/outputs/JOB_ID_image.png

curl -X POST http://127.0.0.1:8000/media/image/generate -H "Content-Type: application/json" -d "{\"prompt\":\"a red boat\"}"
curl -X POST http://127.0.0.1:8000/media/audio/stt -H "Content-Type: application/json" -d "{\"input_audio\":\"https://example.com/sample.wav\"}"
```

## Tests y smoke

```powershell
poetry run pytest -q
.\scripts\smoke.ps1
```

## Storage

- `storage/jobs/<job_id>/inputs/`
- `storage/jobs/<job_id>/outputs/`
- `storage/jobs/<job_id>/temp/`

## Futuro (no implementado)

- Redis/Celery — ver `docs/MIGRATION_TO_REDIS_CELERY.md`
- Autenticación API keys
- Resto de capabilities v2 (edit, tts, video.generate, …)
