from typing import List, Optional
from app.repositories.categoria_repository import CategoriaRepository
from app.repositories.producto_repository import ProductoRepository
from app.models.domain import Producto
from app.schemas.dto import ProductoCreateDTO

class ProductoService:
    def __init__(self, repository: ProductoRepository, categoria_repository: CategoriaRepository):
        self.repository = repository
        self.categoria_repository = categoria_repository

    def listar_productos(self, categoria_filtro: Optional[str] = None) -> List[Producto]:

        productos = self.repository.obtener_todos(categoria_filtro=categoria_filtro)
        
        # Aquí irían reglas de negocio de lectura si existieran.
        # Por ejemplo: if usuario_rol == "limitado", ocultar ciertos productos.
        
        return productos

    def crear_producto(self, producto_dto: ProductoCreateDTO) -> Producto:

        categoria = self.categoria_repository.obtener_por_id(producto_dto.categoria_id)
        if categoria is None:
            raise ValueError(f"La categoria con id {producto_dto.categoria_id} no existe")

        # Crear la instancia del modelo desde el DTO
        nuevo_producto = Producto(
            nombre=producto_dto.nombre,
            precio_unitario=producto_dto.precio_unitario,
            categoria_id=producto_dto.categoria_id,
            stock_actual=producto_dto.stock_actual,
            stock_minimo=producto_dto.stock_minimo
        )
        
        # Aquí irían reglas de negocio de creación si existieran.
        
        # Guardar en BD
        return self.repository.crear(nuevo_producto)

    def eliminar_producto(self, producto_id: int) -> None:
        producto = self.repository.obtener_por_id_con_bloqueo(producto_id)
        if producto is None:
            raise ValueError(f"El producto con id {producto_id} no existe")

        self.repository.eliminar(producto)

    def actualizar_stock_minimo(self, producto_id: int, stock_minimo: int) -> Producto:
        producto = self.repository.obtener_por_id_con_bloqueo(producto_id)
        if producto is None:
            raise ValueError(f"El producto con id {producto_id} no existe")
        
        producto.stock_minimo = stock_minimo
        self.repository.commit()
        return producto
        