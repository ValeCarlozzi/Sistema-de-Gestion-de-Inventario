from fastapi import FastAPI
from app.api.v1.producto_routes import router as productos_router
from app.api.v1.categoria_routes import router as categorias_router
from app.api.v1.auth_routes import router as auth_router
from app.models.domain import Base
from app.core.database import engine

# 0. Inicializar la base de datos (crear tablas)
Base.metadata.create_all(bind=engine)

# 1. Inicializamos la aplicación FastAPI
app = FastAPI(
    title="API de Gestión de Inventario",
    description="Evaluación Técnica - Desarrollador Junior Full Stack",
    version="1.0.0"
)

# 2. Conectamos el controlador (router) de productos y categorias
app.include_router(productos_router)
app.include_router(categorias_router)
app.include_router(auth_router)

# 3. (Opcional) Un endpoint de health-check para verificar que la API está viva
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "mensaje": "API de Inventario funcionando correctamente"}