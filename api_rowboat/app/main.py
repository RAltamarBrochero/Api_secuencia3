from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.routes import router
from .config import settings

# Fase 2 wiring (aditiva)
from .api.routes_v2 import router_v2
# Importa el registry para que se registren los adapters al arrancar
from .providers2 import provider_registry2  # noqa: F401



app = FastAPI(title="Api_rowboat", version="0.1.0")
app.include_router(router, prefix="")
app.include_router(router_v2, prefix="")

# Módulo independiente para uploads locales + endpoints wrapper híbridos
from .modules.uploads_local.router import router_uploads_local
app.include_router(router_uploads_local, prefix="")

# Editor de audio/video local (denoise, trim, normalize, improve)
from .api.routes_editor import router_editor
app.include_router(router_editor, prefix="")



# --- CORS (desarrollo local) ---
# Dashboard puede abrirse como archivo local (origin: "null") o desde http://localhost/127.0.0.1.
# Mantenerlo mínimo para v1, sin tocar endpoints ni lógica de negocio.
app.add_middleware(
    CORSMiddleware,
    allow_origin_regex=r"^(https?://(localhost|127\.0\.0\.1)(:\d+)?|null)$",
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def startup_event():
    # Placeholder for startup tasks (connect to services, warm providers)
    print("Api_rowboat starting, env=", settings.env)

