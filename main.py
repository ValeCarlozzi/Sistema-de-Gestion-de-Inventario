from pathlib import Path
from time import perf_counter
import logging
import logging.config
import os
import time

from fastapi import FastAPI, Request
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from app.api.v1.producto_routes import router as productos_router
from app.api.v1.categoria_routes import router as categorias_router
from app.api.v1.auth_routes import router as auth_router
from app.api.v1.movimiento_routes import router as movimientos_router
from app.models.domain import Base
from app.core.database import engine
from app.core.loki_handler import LokiHandler

def init_database_with_retry(max_attempts: int = 20, delay_seconds: int = 3) -> None:
    """Espera a PostgreSQL y crea tablas al iniciar el contenedor de API."""
    for attempt in range(1, max_attempts + 1):
        try:
            with engine.connect() as connection:
                connection.execute(text("SELECT 1"))
            Base.metadata.create_all(bind=engine)
            return
        except SQLAlchemyError:
            if attempt == max_attempts:
                raise
            time.sleep(delay_seconds)


# Inicializar la base de datos (crear tablas)
init_database_with_retry()

# Configure logging with dictConfig and rotating file handler
LOGS_DIR = Path("logs")
LOGS_DIR.mkdir(exist_ok=True)

LOGGING_CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            "datefmt": "%Y-%m-%d %H:%M:%S",
        },
        "json": {
            "()": "pythonjsonlogger.jsonlogger.JsonFormatter",
            "format": "%(asctime)s %(name)s %(levelname)s %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "default",
            "stream": "ext://sys.stdout",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "formatter": "json",
            "filename": str(LOGS_DIR / "app.log"),
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,  # Mantiene 5 archivos rotados
            "encoding": "utf-8",
        },
    },
    "loggers": {
        "watchfiles": {
            "level": "WARNING",
        },
        "uvicorn": {
            "level": "INFO",
        },
        "uvicorn.access": {
            "level": "WARNING",
        },
    },
    "root": {
        "level": "INFO",
        "handlers": ["console", "file"],
    },
}

logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger("inventory")

# Agregar handler de Loki si está configurado
LOKI_URL = os.getenv("LOKI_URL")
if LOKI_URL:
    loki_handler = LokiHandler(
        loki_url=LOKI_URL,
        labels={"app": "inventory", "environment": "docker"},
    )
    loki_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )
    logger.addHandler(loki_handler)

# Inicializamos la aplicación FastAPI
app = FastAPI(
    title="API de Gestión de Inventario",
    description="Evaluación Técnica - Desarrollador Junior Full Stack",
    version="1.0.0"
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start = perf_counter()

    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Unhandled error during %s %s", request.method, request.url.path)
        raise

    duration_ms = (perf_counter() - start) * 1000
    logger.info(
        "%s %s -> %s (%.2f ms)",
        request.method,
        request.url.path,
        response.status_code,
        duration_ms,
    )
    return response

# Conectamos el controlador (router) de productos, categorias y auth
app.include_router(productos_router)
app.include_router(categorias_router)
app.include_router(auth_router)
app.include_router(movimientos_router)

# (Opcional) Un endpoint de health-check para verificar que la API está viva
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "mensaje": "API de Inventario funcionando correctamente"}