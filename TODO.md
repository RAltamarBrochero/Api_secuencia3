# TODO - Api_rowboat

## Fase 1 (v1) — completado

- [x] Quick start README + config/.env
- [x] Audio/imagen/video: failed claro sin deps; completed solo con output real
- [x] Jobs: enrich GET, POST /jobs → failed sin handler
- [x] Tests pytest
- [x] Dashboard + CORS

## Fase 2 — completado / parcial

- [x] Estructura capabilities/, providers2/, services2/, routes_v2
- [x] DTOs Pydantic + BackgroundTasks + job_id único
- [x] ComfyUI `image.generate` (HTTP real; requiere workflow JSON)
- [x] Replicate `audio.stt` (HTTP real; requiere token + modelo)
- [ ] Resto capabilities v2 (edit, inpaint, tts, video.*, …)
- [ ] MediaProvider async (`health_check` / `execute`)

## Futuro

- [ ] Redis + Celery — `docs/MIGRATION_TO_REDIS_CELERY.md`
- [ ] Autenticación
- [ ] Métricas / Docker
