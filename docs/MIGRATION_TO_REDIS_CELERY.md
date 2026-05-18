# Migración propuesta a Redis + Celery (no implementada)

Objetivo: mover el `JobManager` de la memoria y `BackgroundTasks` a una cola persistente y workers dedicados para tareas largas, retries y visibilidad.

Pasos de alto nivel:

1. Añadir Redis como broker y backend de resultados.
   - Configurar `REDIS_URL` en variables de entorno.
2. Reemplazar `JobManager` por una capa que: registre jobs en la base de datos (p. ej. Postgres o Redis hashes) y envíe tareas a Celery.
3. Definir tasks de Celery para `audio.transcribe`, `image.generate`, `video.process_basic`, etc.
4. Mantener en la API endpoints que creen/registren jobs y encolen tareas a Celery; devolver `job_id` inmediatamente.
5. Workers de Celery ejecutan providers y actualizan el store de jobs (status, outputs, result). Para archivos grandes, usar almacenamiento compartido (S3/local NFS) y guardar solo rutas/URLs en `outputs`.
6. Implementar retries y exponential backoff en tareas idempotentes.
7. Añadir un endpoint `GET /jobs/{id}` que lea el estado desde el store persistente.
8. Añadir observabilidad: métricas (Prometheus), trazas (OpenTelemetry) y logs estructurados.

Notas de diseño:
- Mantener la interfaz de `providers/` tal cual para reusabilidad entre workers y la API.
- Considerar usar `django-q` o `rq` si se prefiere menor complejidad que Celery.
- Planificar migración de datos: exportar jobs en memoria a Redis/DB al desplegar.
