from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.schemas.dto import ProductoResponseDTO
from app.repositories.producto_repository import ProductoRepository
from app.services.producto_service import ProductoService

router = APIRouter(prefix="/productos", tags=["Productos"])

# La función get_producto_service automatiza la inyección de dependencias
def get_producto_service(db: Session = Depends(get_db)) -> ProductoService:
    repo = ProductoRepository(db)
    return ProductoService(repo)

@router.get("", response_model=List[ProductoResponseDTO])
def listar_productos(
    categoria: Optional[str] = Query(None, description="Filtrar por nombre de categoría"),
    service: ProductoService = Depends(get_producto_service)
):
    #Endpoint para obtener el listado de productos con su stock y categoría.
    return service.listar_productos(categoria_filtro=categoria)