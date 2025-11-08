from fastapi import FastAPI
from api.v1.endpoints import router
from core.config import Settings
from db.session import Base, engine
import models.evento 

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(router.api_router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {"msg": "Backend FastAPI funcionando!"}

@app.get("/config")
def get_config():
    return {
        "project": Settings.PROJECT_NAME,
        "version": Settings.VERSION,
        "debug": Settings.DEBUG
    }