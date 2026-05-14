# Sistema de Gestión de Inventario 

Un sistema Full Stack diseñado para registrar productos, gestionar el stock disponible y llevar un control de auditoría sobre los movimientos (entradas y salidas) del inventario.

## Stack

* **Backend:** Python 3.11, FastAPI, Pydantic
* **Base de Datos:** PostgreSQL, SQLAlchemy (ORM), Alembic (Migraciones)
* **Frontend:** Streamlit, Pandas, Altair
* **Infraestructura:** Docker & Docker Compose
* **Seguridad:** Passlib (Bcrypt), python-jose (JWT)

---

## Características Principales

### 1. Base de Datos
* Modelo relacional en PostgreSQL con integridad referencial estricta.
* Registro histórico (`historial_producto`) para auditar cambios de precio y nombre, implementado mediante triggers/lógica de dominio para no perder trazabilidad.
* Restricciones a nivel de base de datos para evitar stocks negativos.

### 2. Backend (API RESTful)
* **Arquitectura en Capas:** Separación estricta de responsabilidades en Controladores (`api/routes`), Lógica de Negocio (`services`) y Acceso a Datos (`repositories`).
* **Seguridad y Autenticación:** Control de Acceso Basado en Roles (RBAC) mediante tokens JWT. Contraseñas hasheadas con Bcrypt. Endpoints protegidos mediante el sistema de inyección de dependencias de FastAPI.
* **Observabilidad:** Gestión de logs estándar listos para ser consumidos por herramientas de monitoreo externas.
* **Optimización ORM:** Prevención del problema "N+1" y optimización de consultas SQL utilizando `contains_eager` para el anidamiento de categorías.

### 3. Frontend (Streamlit)
* **Dashboards Interactivos:** Visualización rápida del estado del inventario con gráficos de barras para detectar quiebres de stock.
* **Gestión Operativa:** Formularios interactivos para el registro de Entradas y Salidas, con validación en cliente para evitar envío de stocks inválidos.
* **Manejo de Sesión:** Integración completa con el flujo OAuth2 de la API.

---

## Endpoints Principales

La documentación Swagger UI estará disponible en `http://localhost:8000/docs` una vez levantado el servidor.

**Autenticación**
* `POST /auth/register`: Registro de nuevos usuarios.
* `POST /auth/token`: Generación de Access Token (JWT).
* `GET /auth/me`: Retorna los datos y rol del usuario autenticado actual.

**Productos e Inventario** (Requieren `Authorization: Bearer <token>`)
* `GET /productos`: Listado de productos con stock actual (Permite filtro por `?categoria=nombre`).
* `GET /movimientos`: Listado general de auditoría de movimientos.
* `POST /movimientos/productos/{producto_id}`: Registra una nueva entrada/salida y actualiza el stock de forma transaccional.

---

## Guía de Instalación y Ejecución

La forma más sencilla de ejecutar el proyecto es utilizando Docker. 

### Opción 1: Usando Docker Compose (Recomendado)

1. Clonar el repositorio:
```bash
   git clone [https://github.com/tu-usuario/sistema-gestion-inventario.git](https://github.com/tu-usuario/sistema-gestion-inventario.git)
   cd sistema-gestion-inventario
```

2. Construir y levantar los contenedores (Base de datos + API + Streamlit):
```bash
	docker compose up --build
```

3. Acceder a los servicios:
* API (Swagger): `http://localhost:8000/docs`
* Streamlit UI: `http://localhost:8501`

> Nota: La inicialización de tablas se realiza automáticamente al arrancar la API.

### Opción 2: Ejecución Local Manual
1. Instalar dependencias: pip install -r requirements.txt

2. Configurar la cadena de conexión a tu PostgreSQL local en un archivo .env (DATABASE_URL=...).

3. Crear las tablas: python init_db.py

4. Iniciar el servidor API: fastapi dev main.py

5. En otra terminal, iniciar el Frontend: streamlit run streamlit_app.py