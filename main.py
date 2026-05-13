from fastapi import FastAPI
from app.api.v1.routes import router as productos_router

# 1. Inicializamos la aplicación FastAPI
app = FastAPI(
    title="API de Gestión de Inventario",
    description="Evaluación Técnica - Desarrollador Junior Full Stack",
    version="1.0.0"
)

# 2. Conectamos el controlador (router) de productos que armamos antes
app.include_router(productos_router)

# 3. (Opcional) Un endpoint de health-check para verificar que la API está viva
@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "mensaje": "API de Inventario funcionando correctamente"}