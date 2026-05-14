from typing import List

from app.models.domain import Categoria
from app.repositories.categoria_repository import CategoriaRepository
from app.schemas.dto import CategoriaCreateDTO


class CategoriaService:
    def __init__(self, repository: CategoriaRepository):
        self.repository = repository

    def listar_categorias(self) -> List[Categoria]:
        return self.repository.obtener_todas()

    def eliminar_categoria(self, categoria_id: int) -> None:
        categoria = self.repository.obtener_por_id(categoria_id)
        if categoria is None:
            raise ValueError(f"La categoria con id {categoria_id} no existe")

        if self.repository.tiene_productos(categoria_id):
            raise LookupError(f"La categoria con id {categoria_id} no se puede eliminar porque tiene productos asociados")

        self.repository.eliminar(categoria)

    def crear_categoria(self, categoria_dto: CategoriaCreateDTO) -> Categoria:
        nueva_categoria = Categoria(
            nombre=categoria_dto.nombre,
            descripcion=categoria_dto.descripcion,
        )
        return self.repository.crear(nueva_categoria)