# Api Rowboat — API híbrida local+remota para multimedia (v2)

API FastAPI para procesamiento de imagen, video y audio vía providers locales (ComfyUI) y remotos (Replicate).

---

## Dependencias del sistema

| Herramienta | Requerida | Para qué |
|---|---|---|
| Python ≥ 3.10 | ✅ Siempre | Runtime |
| [Poetry](https://python-poetry.org/docs/#installation) | ✅ Siempre | Gestión de paquetes |
| ffmpeg | Solo v1 `/video/process-basic` | Procesamiento de video local |
| whisper (openai-whisper) | Solo v1 `/audio/transcribe` local | STT local (alternativa a Replicate) |
| [ComfyUI](https://github.com/comfyanonymous/ComfyUI) | Opcional | Provider local de imagen |

## Tokens / Variables de entorno

Copia `.env.example` → `.env` y configura:

```bash
cp .env.example .env
```

| Variable | Descripción | Ejemplo |
|---|---|---|
| `REPLICATE_API_TOKEN` | Token de [replicate.com](https://replicate.com) | `r8_abc123...` |
| `REPLICATE_DEFAULT_MODEL_AUDIO_STT` | Modelo Whisper en Replicate | `openai/whisper:30414ee7c4fffc37e260fcab7842b5be470b9b840f2b608f5baa9bbef9a259ed` |
| `COMFYUI_BASE_URL` | URL de ComfyUI si está levantado localmente | `http://127.0.0.1:8188` |
| `COMFYUI_ENABLED` | Activar/desactivar ComfyUI | `true` / `false` |
| `REPLICATE_ENABLED` | Activar/desactivar Replicate | `true` / `false` |
| `HF_API_TOKEN` | Token HuggingFace para v1 `/image/generate` | `hf_abc...` |

---

## Instalación

```bash
# 1. Instalar dependencias Python
poetry install

# 2. Verificar la instalación con los tests
poetry run pytest

# 3. Levantar el servidor
poetry run uvicorn api_rowboat.app.main:app --reload --host 127.0.0.1 --port 8000
```

Accede a la documentación interactiva en: http://127.0.0.1:8000/docs

---

## Ciclo completo — ejemplo con `curl`

### 1. Verificar estado del servicio

```bash
curl -s http://127.0.0.1:8000/health | jq .
# {"status": "ok", "version": "0.1.0"}
```

### 2. Ver providers disponibles y su estado

```bash
curl -s http://127.0.0.1:8000/providers | jq .
curl -s http://127.0.0.1:8000/providers/replicate/health | jq .
```

### 3. Crear un job de imagen (requiere REPLICATE_API_TOKEN)

```bash
JOB=$(curl -s -X POST http://127.0.0.1:8000/media/image/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt": "a red sailboat at sunset, photorealistic"}')
echo $JOB | jq .

JOB_ID=$(echo $JOB | jq -r '.job_id')
echo "Job ID: $JOB_ID"
```

### 4. Consultar estado del job

```bash
curl -s http://127.0.0.1:8000/jobs/$JOB_ID | jq .
# {
#   "job_id": "...",
#   "status": "completed",   # pending → running → completed / failed / cancelled
#   "capability": "image.generate",
#   "outputs": {"image_path": "storage/jobs/.../outputs/..._generated.png"}
# }
```

### 5. Ver el manifest de outputs

```bash
curl -s http://127.0.0.1:8000/jobs/$JOB_ID/manifest | jq .
# {
#   "job_id": "...",
#   "files": {
#     "image_path": {
#       "basename": "..._generated.png",
#       "size_bytes": 123456,
#       "download_route": "/jobs/.../outputs/..._generated.png"
#     }
#   }
# }
```

### 6. Descargar el output

```bash
curl -s http://127.0.0.1:8000/jobs/$JOB_ID/outputs/$(curl -s http://127.0.0.1:8000/jobs/$JOB_ID/manifest | jq -r '.files | to_entries[0].value.basename') \
  -o resultado.png
```

O directamente con el basename:

```bash
curl -s "http://127.0.0.1:8000/jobs/$JOB_ID/outputs/${JOB_ID}_generated.png" -o resultado.png
```

### 7. Cancelar un job

```bash
curl -s -X POST http://127.0.0.1:8000/jobs/$JOB_ID/cancel | jq .
# {"status": "cancelled", ...}
```

---

## Flujo de estados de un job

```
pending → running → completed
                 ↘ failed
                 ↘ cancelled  ← POST /jobs/{id}/cancel
```

- Un job en estado terminal (`completed`, `failed`, `cancelled`) no puede cambiar de estado.
- `cancel` es idempotente: llamarlo en un job ya terminal devuelve el estado actual sin error.

---

## Endpoints v2 disponibles

| Endpoint | Método | Descripción |
|---|---|---|
| `/capabilities` | GET | Lista de capabilities soportadas |
| `/providers` | GET | Providers registrados con sus capabilities |
| `/providers/{id}/health` | GET | Estado de un provider |
| `/media/image/generate` | POST | Generar imagen desde prompt |
| `/media/image/edit` | POST | Editar imagen con prompt |
| `/media/image/inpaint` | POST | Inpainting con máscara |
| `/media/image/upscale` | POST | Upscale de imagen |
| `/media/image/face-swap` | POST | Face swap |
| `/media/video/generate` | POST | Generar video desde prompt |
| `/media/video/process` | POST | Procesar video |
| `/media/video/lip-sync` | POST | Lip sync video+audio |
| `/media/audio/tts` | POST | Text to speech |
| `/media/audio/stt` | POST | Speech to text |
| `/media/audio/enhance` | POST | Separación de fuentes de audio |
| `/jobs/{id}` | GET | Estado del job |
| `/jobs/{id}/manifest` | GET | Manifest de outputs |
| `/jobs/{id}/outputs/{basename}` | GET | Descarga de un output |
| `/jobs/{id}/cancel` | POST | Cancelar un job |

---

## Scripts reproducibles

```bash
# Instalar
poetry install

# Tests
poetry run pytest

# Tests con reporte de cobertura
poetry run pytest -v

# Servidor de desarrollo
poetry run uvicorn api_rowboat.app.main:app --reload --host 127.0.0.1 --port 8000

# Smoke test (Linux/Mac)
bash scripts/smoke.sh
```

---

## Errores — formato estándar

Todos los errores v2 siguen el formato:

```json
{
  "error": {
    "code": "NO_PROVIDER",
    "message": "No hay ningún provider disponible para la capability 'video.generate'. Configura REPLICATE_API_TOKEN o COMFYUI_BASE_URL en el .env."
  }
}
```

Códigos comunes:

| Código HTTP | Código | Significa |
|---|---|---|
| 422 | (Pydantic) | Payload inválido o campo faltante |
| 503 | `NO_PROVIDER` | Ningún provider disponible o configurado |
| 503 | `MISSING_CONFIG` | Variable de entorno requerida no configurada |
| 404 | — | Job, output o provider no encontrado |

---

## Estructura del repositorio

```
api_rowboat/
  app/
    api/
      routes.py          # v1 (audio/transcribe, image/generate, video/process-basic, jobs)
      routes_v2.py       # v2 (/media/*, /jobs/*, /capabilities, /providers)
    capabilities/
      capability_names.py
      dtos.py            # Schemas Pydantic con validación
    interfaces/
      provider.py        # Protocol MediaProvider
    providers2/
      registry.py
      adapters/
        replicate_adapter.py   # Todas las capabilities vía Replicate
        comfyui_adapter.py     # image.generate, inpaint, upscale, face_swap vía ComfyUI
    services/
      job_manager.py     # In-memory store + manifest.json
    services2/
      multimedia_orchestrator.py
      capability_router.py
      job_runner.py
storage/
  jobs/<job_id>/
    inputs/              # Archivos subidos
    outputs/             # Outputs generados + manifest.json
    temp/                # Temporales
tests/
  conftest.py
  test_health.py
  test_jobs_v1.py
  test_v2_media.py
  test_jobs_v2_outputs.py
```
