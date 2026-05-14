from sqlalchemy.orm import Session, contains_eager
from typing import List, Optional
from app.models.domain import Producto, Categoria

class ProductoRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_todos(self, categoria_filtro: Optional[str] = None) -> List[Producto]:
        # JOIN manual que sirve tanto para traer datos como para filtrar.
        # INNER JOIN porque las reglas de negocio dicen que todo producto tiene categoría.
        query = self.db.query(Producto).join(Producto.categoria)

        # Si hay filtro, agregamos el WHERE
        if categoria_filtro and categoria_filtro.strip():
            query = query.filter(Categoria.nombre.ilike(categoria_filtro.strip()))

        # SQLAlchemy reutiliza el JOIN para anidar el objeto
        query = query.options(contains_eager(Producto.categoria))

        return query.all()

    def obtener_por_id_con_bloqueo(self, producto_id: int) -> Optional[Producto]:
        """
        Obtiene un producto específico y bloquea la fila para evitar condiciones de carrera.
        Preparado para cuando haya que implementar el guardado de movimientos.
        """
        return self.db.query(Producto).with_for_update().filter(Producto.id == producto_id).first()

    def crear(self, producto: Producto) -> Producto:

        self.db.add(producto)
        self.db.commit()
        self.db.refresh(producto)
        return producto

    def eliminar(self, producto: Producto) -> None:
        self.db.delete(producto)
        self.db.commit()

    def commit(self) -> None:
        self.db.commit()