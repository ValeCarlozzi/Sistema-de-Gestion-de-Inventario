from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.models.domain import HistorialProducto, Movimiento, Producto, TipoMovimiento


class MovimientoRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_tipo_por_id(self, tipo_id: int) -> Optional[TipoMovimiento]:
        return self.db.query(TipoMovimiento).filter(TipoMovimiento.id == tipo_id).first()

    def obtener_tipos(self) -> List[TipoMovimiento]:
        return self.db.query(TipoMovimiento).order_by(TipoMovimiento.id.asc()).all()

    def crear_tipos_por_defecto(self) -> None:
        self.db.add_all([
            TipoMovimiento(tipo="entrada"),
            TipoMovimiento(tipo="salida"),
        ])
        self.db.commit()

    def obtener_producto_por_id_con_bloqueo(self, producto_id: int) -> Optional[Producto]:
        return (
            self.db.query(Producto)
            .with_for_update()
            .filter(Producto.id == producto_id)
            .first()
        )

    def crear_movimiento(self, movimiento: Movimiento) -> None:
        self.db.add(movimiento)

    def crear_historial_producto(self, historial: HistorialProducto) -> None:
        self.db.add(historial)

    def listar_movimientos(self, producto_id: Optional[int] = None, limite: int = 100) -> List[Movimiento]:
        query = (
            self.db.query(Movimiento)
            .options(joinedload(Movimiento.tipomovimiento))
            .order_by(Movimiento.fecha.desc())
        )
        if producto_id is not None:
            query = query.filter(Movimiento.producto_id == producto_id)
        return query.limit(limite).all()

    def listar_historial(self, producto_id: Optional[int] = None, limite: int = 100) -> List[HistorialProducto]:
        query = (
            self.db.query(HistorialProducto)
            .order_by(HistorialProducto.fecha_cambio.desc())
        )
        if producto_id is not None:
            query = query.filter(HistorialProducto.producto_id == producto_id)
        return query.limit(limite).all()

    def commit(self) -> None:
        self.db.commit()

    def rollback(self) -> None:
        self.db.rollback()

    def refresh(self, movimiento: Movimiento) -> None:
        self.db.refresh(movimiento)
