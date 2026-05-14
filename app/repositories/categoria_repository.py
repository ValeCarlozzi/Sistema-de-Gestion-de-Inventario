from sqlalchemy.orm import Session
from typing import List, Optional

from app.models.domain import Categoria


class CategoriaRepository:
    def __init__(self, db: Session):
        self.db = db

    def obtener_por_id(self, categoria_id: int) -> Optional[Categoria]:
        return self.db.query(Categoria).filter(Categoria.id == categoria_id).first()

    def tiene_productos(self, categoria_id: int) -> bool:
        return self.db.query(Categoria).filter(Categoria.id == categoria_id, Categoria.productos.any()).first() is not None

    def obtener_todas(self) -> List[Categoria]:
        return self.db.query(Categoria).order_by(Categoria.nombre.asc()).all()

    def crear(self, categoria: Categoria) -> Categoria:
        self.db.add(categoria)
        self.db.commit()
        self.db.refresh(categoria)
        return categoria

    def eliminar(self, categoria: Categoria) -> None:
        self.db.delete(categoria)
        self.db.commit()