from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

# DTOs de Categorías
class CategoriaCreateDTO(BaseModel):
    nombre: str = Field(..., min_length=1, description="Nombre de la categoría")
    descripcion: Optional[str] = Field(default=None, description="Descripción opcional")

    class Config:
        from_attributes = True

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
class ProductoCreateDTO(BaseModel):
    nombre: str = Field(..., min_length=1, description="Nombre del producto")
    precio_unitario: Decimal = Field(..., gt=0, description="El precio debe ser mayor a 0")
    #la categoria podria obtenerse por un string y aplicar logica para encontrar la categoria TODO
    categoria_id: int = Field(..., description="ID de la categoría")
    stock_actual: int = Field(default=0, ge=0, description="Stock inicial (default 0)")
    stock_minimo: int = Field(default=10, ge=0, description="Stock mínimo para alertas (default 10)")

    class Config:
        from_attributes = True

class ProductoResponseDTO(BaseModel):
    id: int
    nombre: str
    precio_unitario: Decimal = Field(..., gt=0, description="El precio debe ser mayor a 0")
    stock_actual: int
    stock_minimo: int
    categoria: CategoriaResponseDTO  

    class Config:
        from_attributes = True

class ProductoUpdateStockMinimoDTO(BaseModel):
    stock_minimo: int = Field(..., ge=0, description="Nuevo valor de stock mínimo")
    
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
    tipo_movimiento: TipoMovimientoResponseDTO = Field(alias="tipomovimiento")

    class Config:
        from_attributes = True

class MovimientoCreateDTO(BaseModel):
    tipo_id: int = Field(..., description="ID del Tipo de Movimiento (ej. 1=entrada, 2=salida)")
    cantidad: int = Field(..., gt=0, description="La cantidad debe ser estrictamente positiva")
    motivo: Optional[str] = None
