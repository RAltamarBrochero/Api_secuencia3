# Api_rowboat - Fase 2: API multimedia híbrida y modular (aditiva)

## Objetivo
Extender la base v1 con una capa adicional de:
- **Providers** (ComfyUI local, Replicate remoto, etc.)
- **Capabilities** normalizadas (image.generate, audio.tts, etc.)
- **Capability router** (selección de provider)
- **Media orchestrator** (orquesta jobs y persistencia en disco usando el layout v1)

Restricciones cumplidas:
- No se rediseña la v1.
- Compatibilidad: los endpoints v1 y sus DTOs se mantienen.
- La lógica de provider no vive en controladores; vive en `services2/`.
- No se exponen payloads crudos de ComfyUI/Replicate como API pública.
- Diseño aditivo (carpetas `*2/` nuevas).

## Capabilities (contratos)
Se definen como strings estandarizados:
- `image.generate`
- `image.edit`
- `image.inpaint`
- `image.upscale`
- `image.face_swap`
- `video.process`
- `video.generate`
- `video.lip_sync`
- `audio.tts`
- `audio.stt`
- `audio.enhance`

## Estructura de código (nueva)
- `api_rowboat/app/capabilities/`
  - `capability_names.py`
  - `dtos.py`
- `api_rowboat/app/providers2/`
  - `base.py` (interface)
  - `registry.py` (provider registry)
  - `adapters/`
    - `comfyui_adapter.py`
    - `replicate_adapter.py`
- `api_rowboat/app/services2/`
  - `capability_router.py`
  - `multimedia_orchestrator.py`
  - `job_runner.py`
- `api_rowboat/app/api/routes_v2.py`

## Provider API (alto nivel)
- Cada adapter implementa capacidades soportadas.
- Internamente traduce un DTO normalizado a:
  - llamada HTTP (Replicate)
  - llamada a ComfyUI (local o remoto)
- Se devuelve **solo** un resultado normalizado (rutas a disco + metadata), sin payloads crudos.

## Prioridades de wiring real
- ComfyUI: `image.generate`, `image.inpaint`, `image.upscale`
- Replicate: `audio.stt`, `audio.tts`, `video.process`

## Stubs limpios
Si falta runtime (credenciales / servicios), el adapter:
- no lanza excepciones que rompan el servidor
- retorna un error normalizado con TODO
- deja el job en `failed` con `result.error`.

## Mapeo con jobs v1
- Se reutiliza `JobManager` de v1 para storage:
  - `storage/jobs/<job_id>/inputs/`
  - `storage/jobs/<job_id>/outputs/`
  - `storage/jobs/<job_id>/temp/`

Los endpoints fase 2 agregan:
- `GET /providers`
- `GET /providers/:id/health`
- `GET /capabilities`
- `POST /media/...`
- `GET /jobs/:jobId`
- `POST /jobs/:jobId/cancel`


