CAPABILITY_IMAGE_GENERATE = "image.generate"
CAPABILITY_IMAGE_EDIT = "image.edit"
CAPABILITY_IMAGE_INPAINT = "image.inpaint"
CAPABILITY_IMAGE_UPSCALE = "image.upscale"
CAPABILITY_IMAGE_FACE_SWAP = "image.face_swap"

CAPABILITY_VIDEO_PROCESS = "video.process"
CAPABILITY_VIDEO_GENERATE = "video.generate"
CAPABILITY_VIDEO_LIP_SYNC = "video.lip_sync"

CAPABILITY_AUDIO_TTS = "audio.tts"
CAPABILITY_AUDIO_STT = "audio.stt"
CAPABILITY_AUDIO_ENHANCE = "audio.enhance"

# --- Type alias interno (contrato) ---
# Mantenerlo como constantes + ALL_CAPABILITIES para tipado en runtime y compat con Python.
# Equivalente a:
# type MediaCapability =
#   | 'image.generate'
#   | 'image.edit'
#   | 'image.inpaint'
#   | 'image.upscale'
#   | 'image.face_swap'
#   | 'video.process'
#   | 'video.generate'
#   | 'video.lip_sync'
#   | 'audio.tts'
#   | 'audio.stt'
#   | 'audio.enhance';


ALL_CAPABILITIES = [
    CAPABILITY_IMAGE_GENERATE,
    CAPABILITY_IMAGE_EDIT,
    CAPABILITY_IMAGE_INPAINT,
    CAPABILITY_IMAGE_UPSCALE,
    CAPABILITY_IMAGE_FACE_SWAP,
    CAPABILITY_VIDEO_PROCESS,
    CAPABILITY_VIDEO_GENERATE,
    CAPABILITY_VIDEO_LIP_SYNC,
    CAPABILITY_AUDIO_TTS,
    CAPABILITY_AUDIO_STT,
    CAPABILITY_AUDIO_ENHANCE,
]

