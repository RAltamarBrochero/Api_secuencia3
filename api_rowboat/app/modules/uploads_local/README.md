# uploads_local

Módulo independiente para:
- `POST /v2/upload`: subir archivo local y guardarlo en `storage/uploads/`.
- Endpoints wrapper que aceptan `{ basename }` y lo copian a `storage/jobs/<job_id>/inputs/` para que los providers v2 consuman el archivo por basename.

## Rutas
- `POST /v2/upload` (multipart/form-data, campo `file`)
- `POST /media/audio/stt` body: `{ "basename": "..." }`
- `POST /media/video/process` body: `{ "basename": "..." }`
- `POST /media/image/process` body: `{ "basename": "..." }`

## Nota
`/media/image/process` depende de que exista una capability/proveedor para `CAPABILITY_IMAGE_PROCESS`. En el repo actual, v2 ya define image endpoints diferentes (generate/edit/inpaint/upscale/face-swap).
