from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.domain import Usuario
from app.repositories.movimiento_repository import MovimientoRepository
from app.schemas.dto import (
    MovimientoCreateDTO,
    MovimientoResponseDTO,
    TipoMovimientoResponseDTO,
    HistorialProductoResponseDTO,
)
from app.services.movimiento_service import MovimientoService


router = APIRouter(prefix="/movimientos", tags=["Movimientos"], dependencies=[Depends(get_current_user)])


def get_movimiento_service(db: Session = Depends(get_db)) -> MovimientoService:
    return MovimientoService(MovimientoRepository(db))


@router.get("/tipos", response_model=List[TipoMovimientoResponseDTO])
def listar_tipos_movimiento(service: MovimientoService = Depends(get_movimiento_service)):
    return service.listar_tipos_movimiento()


@router.get("", response_model=List[MovimientoResponseDTO])
def listar_movimientos(
    producto_id: Optional[int] = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
    service: MovimientoService = Depends(get_movimiento_service),
):
    return service.listar_movimientos(producto_id=producto_id, limite=limite)


@router.get("/historial", response_model=List[HistorialProductoResponseDTO])
def listar_historial(
    producto_id: Optional[int] = Query(default=None),
    limite: int = Query(default=100, ge=1, le=500),
    service: MovimientoService = Depends(get_movimiento_service),
):
    return service.listar_historial(producto_id=producto_id, limite=limite)


@router.post("/productos/{producto_id}", response_model=MovimientoResponseDTO, status_code=status.HTTP_201_CREATED)
def registrar_movimiento(
    producto_id: int,
    movimiento: MovimientoCreateDTO,
    current_user: Usuario = Depends(get_current_user),
    service: MovimientoService = Depends(get_movimiento_service),
):
    try:
        return service.registrar_movimiento(producto_id, movimiento, current_user.username)
    except LookupError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc)) from exc
