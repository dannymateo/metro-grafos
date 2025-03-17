from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import asyncio
import logging
from contextlib import asynccontextmanager

from app.routes import api
from app.services.weather_service import weather_monitoring_system

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir las rutas
app.include_router(api.router)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Iniciar la tarea de actualización del clima cuando la aplicación arranca
    weather_task = asyncio.create_task(weather_monitoring_system.update_weather_periodically())
    yield
    # Cancelar la tarea cuando la aplicación se detiene
    weather_task.cancel()
    try:
        await weather_task
    except asyncio.CancelledError:
        logger.info("Tarea de clima cancelada")

app.router.lifespan_context = lifespan

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 