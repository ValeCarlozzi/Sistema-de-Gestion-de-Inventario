from typing import List, Optional

from app.models.domain import HistorialProducto, Movimiento, TipoMovimiento
from app.repositories.movimiento_repository import MovimientoRepository
from app.schemas.dto import MovimientoCreateDTO


class MovimientoService:
    def __init__(self, repository: MovimientoRepository):
        self.repository = repository

    def listar_tipos_movimiento(self) -> List[TipoMovimiento]:
        tipos = self.repository.obtener_tipos()
        if tipos:
            return tipos

        # Bootstrap de tipos base para evitar una DB vacia en primeras ejecuciones.
        self.repository.crear_tipos_por_defecto()
        return self.repository.obtener_tipos()

    def listar_movimientos(self, producto_id: Optional[int] = None, limite: int = 100) -> List[Movimiento]:
        return self.repository.listar_movimientos(producto_id=producto_id, limite=limite)

    def listar_historial(self, producto_id: Optional[int] = None, limite: int = 100):
        return self.repository.listar_historial(producto_id=producto_id, limite=limite)

    def registrar_movimiento(self, producto_id: int, movimiento_dto: MovimientoCreateDTO, usuario: str) -> Movimiento:
        producto = self.repository.obtener_producto_por_id_con_bloqueo(producto_id)
        if producto is None:
            raise LookupError(f"El producto con id {producto_id} no existe")

        tipo = self.repository.obtener_tipo_por_id(movimiento_dto.tipo_id)
        if tipo is None:
            raise LookupError(f"El tipo de movimiento con id {movimiento_dto.tipo_id} no existe")

        valores_anteriores = {
            "stock_actual": int(producto.stock_actual),
        }

        tipo_normalizado = tipo.tipo.strip().lower()
        if tipo_normalizado == "entrada":
            producto.stock_actual += movimiento_dto.cantidad
        elif tipo_normalizado == "salida":
            if producto.stock_actual < movimiento_dto.cantidad:
                raise ValueError("No hay stock suficiente para registrar la salida")
            producto.stock_actual -= movimiento_dto.cantidad
        else:
            raise ValueError(f"Tipo de movimiento no soportado: {tipo.tipo}")

        movimiento = Movimiento(
            producto_id=producto.id,
            tipo_id=movimiento_dto.tipo_id,
            cantidad=movimiento_dto.cantidad,
            motivo=movimiento_dto.motivo,
            usuario=usuario,
        )

        valores_nuevos = {
            "stock_actual": int(producto.stock_actual),
            "tipo_movimiento": tipo.tipo,
            "cantidad": int(movimiento_dto.cantidad),
            "motivo": movimiento_dto.motivo,
        }
        historial = HistorialProducto(
            producto_id=producto.id,
            valores_anteriores=valores_anteriores,
            valores_nuevos=valores_nuevos,
            usuario=usuario,
        )

        try:
            self.repository.crear_movimiento(movimiento)
            self.repository.crear_historial_producto(historial)
            self.repository.commit()
        except Exception:
            self.repository.rollback()
            raise

        self.repository.refresh(movimiento)
        return movimiento
