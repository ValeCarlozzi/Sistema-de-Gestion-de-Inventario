# Sistema de Gestión de Inventario

## Autenticacion

La API expone un flujo OAuth2 con JWT en `/auth/token`.

Rutas disponibles:

- `POST /auth/register` para crear un usuario.
- `POST /auth/token` para obtener el access token.
- `GET /auth/me` para ver el usuario autenticado.

Los endpoints de productos y categorias requieren `Authorization: Bearer <token>`.

## Movimientos

Rutas disponibles:

- `GET /movimientos/tipos` para listar tipos de movimiento (entrada/salida).
- `GET /movimientos` para listar movimientos (`producto_id` y `limite` opcionales).
- `POST /movimientos/productos/{producto_id}` para registrar un movimiento y actualizar stock.

## Frontend con Streamlit

La UI esta en `streamlit_app.py` e incluye:

- Pantalla de login.
- Pantalla de registro.
- Dashboard principal con stock por categoria.
- Dashboard por categoria con stock y valor por producto.
- Pantalla para registrar movimientos de productos.

Ejecucion local:

1. Inicia la API FastAPI (por ejemplo en `http://localhost:8000`).
2. Instala dependencias: `pip install -r requirements.txt`
3. Levanta Streamlit:
	`streamlit run streamlit_app.py`

Opcional: para otra URL de API configura variable de entorno `API_BASE_URL`.
