# Sistema de Gestión de Inventario

## Autenticacion

La API expone un flujo OAuth2 con JWT en `/auth/token`.

Rutas disponibles:

- `POST /auth/register` para crear un usuario.
- `POST /auth/token` para obtener el access token.
- `GET /auth/me` para ver el usuario autenticado.

Los endpoints de productos y categorias requieren `Authorization: Bearer <token>`.
