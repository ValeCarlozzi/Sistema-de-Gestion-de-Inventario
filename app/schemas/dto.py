from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

# DTOs de Catálogos
class CategoriaResponseDTO(BaseModel):
    id: int
    nombre: str
    descripcion: Optional[str] = None

    class Config:
        from_attributes = True 

class TipoMovimientoResponseDTO(BaseModel):
    id: int
    tipo: str

    class Config:
        from_attributes = True

# DTOs de Productos
class ProductoResponseDTO(BaseModel):
    id: int
    nombre: str
    precio_unitario: Decimal = Field(..., gt=0, description="El precio debe ser mayor a 0")
    stock_actual: int
    categoria: CategoriaResponseDTO  

    class Config:
        from_attributes = True

# DTOs de Movimientos
class MovimientoResponseDTO(BaseModel):
    id: int
    producto_id: int
    cantidad: int
    fecha: datetime
    motivo: Optional[str]
    usuario: str
    tipo_movimiento: TipoMovimientoResponseDTO 

    class Config:
        from_attributes = True

class MovimientoCreateDTO(BaseModel):
    tipo_id: int = Field(..., description="ID del Tipo de Movimiento (ej. 1=entrada, 2=salida)")
    cantidad: int = Field(..., gt=0, description="La cantidad debe ser estrictamente positiva")
    motivo: Optional[str] = None
