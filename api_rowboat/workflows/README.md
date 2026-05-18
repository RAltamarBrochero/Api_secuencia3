# Workflows ComfyUI (API format)

Exporta desde ComfyUI: **Save (API Format)** y guarda aquí como:

- `image-generate-v1.json` (requerido para `POST /media/image/generate`)

Configura en `.env`:

```
COMFYUI_DEFAULT_WORKFLOW_IMAGE_GENERATE=image-generate-v1
```

El adapter inyecta el `prompt` del request en nodos `CLIPTextEncode`.
