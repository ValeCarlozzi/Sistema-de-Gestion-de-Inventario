from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.schemas.dto import ProductoResponseDTO, ProductoCreateDTO, ProductoUpdateStockMinimoDTO
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.producto_repository import ProductoRepository
from app.services.producto_service import ProductoService


router = APIRouter(prefix="/productos", tags=["Productos"], dependencies=[Depends(get_current_user)])


def get_producto_service(db: Session = Depends(get_db)) -> ProductoService:
    repo = ProductoRepository(db)
    categoria_repo = CategoriaRepository(db)
    return ProductoService(repo, categoria_repo)


@router.get("", response_model=List[ProductoResponseDTO])
def listar_productos(
    categoria: Optional[str] = Query(None, description="Filtrar por nombre de categoría"),
    service: ProductoService = Depends(get_producto_service)
):
    #Endpoint para obtener el listado de productos con su stock y categoría
    return service.listar_productos(categoria_filtro=categoria)


@router.post("/nuevo-producto", response_model=ProductoResponseDTO, status_code=201)
def crear_producto(
    producto: ProductoCreateDTO,
    service: ProductoService = Depends(get_producto_service)
):
    #Endpoint para crear un nuevo producto con stock inicial
    try:
        return service.crear_producto(producto)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.delete("/{producto_id}", status_code=204)
def eliminar_producto(
    producto_id: int,
    service: ProductoService = Depends(get_producto_service)
):
    try:
        service.eliminar_producto(producto_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))


@router.patch("/{producto_id}/stock-minimo", response_model=ProductoResponseDTO)
def actualizar_stock_minimo(
    producto_id: int,
    data: ProductoUpdateStockMinimoDTO,
    service: ProductoService = Depends(get_producto_service)
):
    try:
        return service.actualizar_stock_minimo(producto_id, data.stock_minimo)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))