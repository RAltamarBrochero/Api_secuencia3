# Roadmap y funciones futuras

Prioridad y notas breves para futuras implementaciones:

- Upscaling (imagen/video): integrar modelos locales (Real-ESRGAN, GFPGAN) y servicios Remotos (Replicate).
- Inpainting / Masking: conectar ComfyUI local y endpoints de inpainting en HF/Replicate.
- Face-swap / Deepfake: pipeline opcional con controles de seguridad y consentimientos.
- Lip-sync: sincronización de audio y video para doblaje/clonación.
- TTS: añadir proveedores para Tacotron, Coqui TTS y servicios de pago.
- STT/Transcripción mejorada: soporte para Whisper large, servicios cloud y diarización.
- Separación de voz (source separation): integrar Spleeter / Demucs.
- Clonación de voz: integrar adaptadores a servicios de pay-per-use con consentimiento.
- Composición (pipeline multimodal): orquestador para combinar imagen/audio/video + jobs dependientes.

Notas técnicas:
- Migrar JobManager a cola persistente (Redis/RQ, Celery) para escala.
- Añadir autenticación y control de acceso (API keys, OAuth) para producción.
- Registrar métricas y telemetría (Prometheus, OpenTelemetry).
