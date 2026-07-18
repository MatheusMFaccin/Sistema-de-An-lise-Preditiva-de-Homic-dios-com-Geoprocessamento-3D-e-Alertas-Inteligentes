import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api.v1.endpoints import router
from core.config import Settings
from db.session import Base, engine
import models  # Garante que todos os models sejam carregados antes do create_all

Base.metadata.create_all(bind=engine)

app = FastAPI()

# CORS para o frontend Vue acessar a API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router.api_router, prefix="/api/v1")

# Serve arquivos estaticos (GeoJSON, CSS, JS, o proprio Vue SPA)
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)

# Monta geojson, css, js como /static/
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Monta o mapa/geojson diretamente (caminho usado pelo Cesium)
mapa_geojson_dir = os.path.join(static_dir, "mapa", "geojson")
os.makedirs(mapa_geojson_dir, exist_ok=True)
app.mount("/mapa/geojson", StaticFiles(directory=mapa_geojson_dir), name="mapa_geojson")


@app.get("/config")
def get_config():
    return {
        "project": Settings.PROJECT_NAME,
        "version": Settings.VERSION,
        "debug": Settings.DEBUG
    }


@app.get("/")
async def serve_root():
    """Serve o SPA Vue.js na raiz."""
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"msg": "Backend FastAPI funcionando!"}


# Catch-all para client-side routing do Vue Router
# (ex: /municipio/sao-paulo -> index.html)
@app.get("/{full_path:path}")
async def serve_spa(full_path: str):
    # Rotas da API ja foram tratadas pelo include_router
    if full_path.startswith("api/") or full_path.startswith("static/") or full_path.startswith("mapa/"):
        return {"detail": "Not Found"}
    index_path = os.path.join(static_dir, "index.html")
    if os.path.exists(index_path):
        return FileResponse(index_path)
    return {"detail": "Not Found"}
