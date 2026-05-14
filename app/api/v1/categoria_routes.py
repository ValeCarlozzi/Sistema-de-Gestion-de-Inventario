from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.repositories.categoria_repository import CategoriaRepository
from app.schemas.dto import CategoriaCreateDTO, CategoriaResponseDTO
from app.services.categoria_service import CategoriaService


router = APIRouter(prefix="/categorias", tags=["Categorias"])


def get_categoria_service(db: Session = Depends(get_db)) -> CategoriaService:
    repo = CategoriaRepository(db)
    return CategoriaService(repo)


@router.get("", response_model=List[CategoriaResponseDTO])
def listar_categorias(service: CategoriaService = Depends(get_categoria_service)):
    return service.listar_categorias()


@router.post("/nueva-categoria", response_model=CategoriaResponseDTO, status_code=201)
def crear_categoria(
    categoria: CategoriaCreateDTO,
    service: CategoriaService = Depends(get_categoria_service)
):
    return service.crear_categoria(categoria)


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT)
def eliminar_categoria(
    categoria_id: int,
    service: CategoriaService = Depends(get_categoria_service)
):
    try:
        service.eliminar_categoria(categoria_id)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except LookupError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    return Response(status_code=status.HTTP_204_NO_CONTENT)