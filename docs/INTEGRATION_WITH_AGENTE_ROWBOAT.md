# Integración con agente_rowboat

El diseño expone endpoints claros y un sistema de jobs que un agente puede usar para orquestar tareas.

Recomendaciones para el agente:

- Usar `POST /jobs` para crear trabajos orquestados con payload que refiera a endpoints específicos.
- Para transcripciones: subir archivo a `POST /audio/transcribe` y obtener `job_id`.
- Consultar `GET /jobs/{id}` para estado y resultados.
- Mantener credenciales en el store seguro del agente y pasarlas vía variables de entorno al servicio.

Ejemplo de flujo desde agente:

1. Agent sube archivo a `POST /audio/transcribe`.
2. Recibe `job_id` y consulta periódicamente `GET /jobs/{id}`.
3. Al completarse, el agente descarga el resultado y continúa el flujo.

Campos útiles en la respuesta del job:

- `outputs`: diccionario con rutas locales a archivos generados (p.ej. `transcript_path`, `image_path`, `video_path`).
- `result`: resultado crudo del proveedor (texto, metadatos u objeto JSON).
- `created_at` / `updated_at`: timestamps ISO.

Notas sobre descarga de outputs:

- En v1 `outputs` contiene rutas de archivo locales en el servidor (ruta relativa a `uploads/`). Un agente que corre en otra máquina debe acceder a esos archivos mediante un endpoint adicional (por ejemplo `/files/{name}`) o un mecanismo de intercambio (S3, compartido de red). Actualmente no se expone un endpoint de descarga; el agente puede solicitar que la API añada uno o montar el directorio `uploads` en un recurso compartido.
