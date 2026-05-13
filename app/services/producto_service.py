from typing import List, Optional
from app.repositories.producto_repository import ProductoRepository
from app.models.domain import Producto

class ProductoService:
    def __init__(self, repository: ProductoRepository):
        self.repository = repository

    def listar_productos(self, categoria_filtro: Optional[str] = None) -> List[Producto]:

        productos = self.repository.obtener_todos(categoria_filtro=categoria_filtro)
        
        # Aquí irían reglas de negocio de lectura si existieran.
        # Por ejemplo: if usuario_rol == "limitado", ocultar ciertos productos.
        
        return productos

