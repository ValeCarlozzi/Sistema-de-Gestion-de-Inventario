import os
from collections import defaultdict

import altair as alt
import pandas as pd
import requests
import streamlit as st


API_BASE_URL = os.getenv("API_BASE_URL", "http://localhost:8000")
REQUEST_TIMEOUT = 12


st.set_page_config(
    page_title="Inventario UI",
    page_icon="I",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;700&family=Manrope:wght@400;600;700&display=swap');

        :root {
            --bg-main: radial-gradient(circle at 20% 20%, #e4f3ff 0%, #f9f6ec 45%, #fff 100%);
            --ink: #122430;
            --muted: #4f6471;
            --accent: #0f8b8d;
            --accent-2: #ff7f50;
            --card: rgba(255, 255, 255, 0.88);
            --border: rgba(18, 36, 48, 0.12);
        }

        html, body, [class*="css"] {
            font-family: 'Manrope', sans-serif;
            color: var(--ink);
        }

        .stApp {
            background: var(--bg-main);
        }

        .headline {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 2rem;
            font-weight: 700;
            margin-bottom: 0.2rem;
            letter-spacing: -0.02em;
        }

        .subhead {
            color: var(--muted);
            margin-bottom: 1.2rem;
        }

        .kpi-card {
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 1rem;
            background: var(--card);
            backdrop-filter: blur(6px);
            box-shadow: 0 8px 30px rgba(15, 139, 141, 0.12);
        }

        .kpi-title {
            color: var(--muted);
            font-size: 0.9rem;
        }

        .kpi-value {
            font-family: 'Space Grotesk', sans-serif;
            font-size: 1.6rem;
            font-weight: 700;
            color: var(--ink);
        }

        @media (max-width: 900px) {
            .headline {
                font-size: 1.5rem;
            }
        }
    </style>
    """,
    unsafe_allow_html=True,
)


def parse_error(response: requests.Response) -> str:
    try:
        payload = response.json()
        detail = payload.get("detail")
        if isinstance(detail, str):
            return detail
        return str(payload)
    except ValueError:
        return response.text or "Error inesperado"


def auth_headers() -> dict:
    token = st.session_state.get("token")
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}


def api_get(path: str, params: dict | None = None, requires_auth: bool = True):
    headers = auth_headers() if requires_auth else {}
    try:
        response = requests.get(
            f"{API_BASE_URL}{path}",
            params=params,
            headers=headers,
            timeout=REQUEST_TIMEOUT,
        )
    except requests.RequestException as exc:
        st.error(f"No se pudo conectar con la API: {exc}")
        return None

    if response.status_code == 401 and requires_auth:
        st.session_state["token"] = None
        st.session_state["user"] = None
        st.warning("Tu sesion expiro. Vuelve a iniciar sesion.")
        st.rerun()

    return response


def fetch_user() -> dict | None:
    response = api_get("/auth/me")
    if response is None or response.status_code != 200:
        return None
    return response.json()


def render_auth_page() -> None:
    st.markdown('<div class="headline">Sistema de Gestion de Inventario</div>', unsafe_allow_html=True)
    st.markdown('<div class="subhead">Ingresa con tu cuenta o crea una nueva para empezar.</div>', unsafe_allow_html=True)

    login_tab, register_tab = st.tabs(["Login", "Register"])

    with login_tab:
        with st.form("login_form"):
            username = st.text_input("Usuario", placeholder="ej: admin")
            password = st.text_input("Password", type="password")
            submit_login = st.form_submit_button("Entrar", use_container_width=True)

        if submit_login:
            if not username or not password:
                st.error("Usuario y password son obligatorios")
            else:
                try:
                    response = requests.post(
                        f"{API_BASE_URL}/auth/token",
                        data={"username": username, "password": password},
                        timeout=REQUEST_TIMEOUT,
                    )
                except requests.RequestException as exc:
                    st.error(f"No se pudo conectar con la API: {exc}")
                    return

                if response.status_code != 200:
                    st.error(parse_error(response))
                else:
                    payload = response.json()
                    st.session_state["token"] = payload.get("access_token")
                    st.session_state["user"] = fetch_user()
                    st.success("Login exitoso")
                    st.rerun()

    with register_tab:
        with st.form("register_form"):
            full_name = st.text_input("Nombre completo", placeholder="Tu nombre")
            reg_user = st.text_input("Nuevo usuario")
            reg_pass = st.text_input("Password", type="password")
            submit_register = st.form_submit_button("Crear cuenta", use_container_width=True)

        if submit_register:
            if not reg_user or not reg_pass:
                st.error("Usuario y password son obligatorios")
            else:
                response = requests.post(
                    f"{API_BASE_URL}/auth/register",
                    json={
                        "username": reg_user,
                        "password": reg_pass,
                        "nombre_completo": full_name or None,
                    },
                    timeout=REQUEST_TIMEOUT,
                )
                if response.status_code != 201:
                    st.error(parse_error(response))
                else:
                    st.success("Usuario creado. Ya puedes iniciar sesion.")


def render_kpi(col, title: str, value: str) -> None:
    col.markdown(
        f"""
        <div class="kpi-card">
            <div class="kpi-title">{title}</div>
            <div class="kpi-value">{value}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def get_categorias() -> list[dict]:
    response = api_get("/categorias")
    if response is None or response.status_code != 200:
        return []
    return response.json()


def get_productos(categoria_nombre: str | None = None) -> list[dict]:
    params = {"categoria": categoria_nombre} if categoria_nombre else None
    response = api_get("/productos", params=params)
    if response is None or response.status_code != 200:
        return []
    return response.json()


def dashboard_general() -> None:
    st.markdown('<div class="headline">Dashboard General</div>', unsafe_allow_html=True)
    st.markdown('<div class="subhead">Vista total de stock y valor por categoria.</div>', unsafe_allow_html=True)

    categorias = get_categorias()
    productos = get_productos()

    stock_por_categoria: dict[str, int] = defaultdict(int)
    valor_por_categoria: dict[str, float] = defaultdict(float)

    for producto in productos:
        categoria_nombre = producto["categoria"]["nombre"]
        stock = int(producto["stock_actual"])
        precio = float(producto["precio_unitario"])
        stock_por_categoria[categoria_nombre] += stock
        valor_por_categoria[categoria_nombre] += stock * precio

    total_stock = sum(stock_por_categoria.values())
    total_valor = sum(valor_por_categoria.values())

    k1, k2, k3 = st.columns(3)
    render_kpi(k1, "Categorias", str(len(categorias)))
    render_kpi(k2, "Stock total", str(total_stock))
    render_kpi(k3, "Valor estimado", f"${total_valor:,.2f}")

    rows = []
    for categoria in sorted(stock_por_categoria):
        rows.append(
            {
                "Categoria": categoria,
                "Stock": stock_por_categoria[categoria],
                "Valor": round(valor_por_categoria[categoria], 2),
            }
        )

    if not rows:
        st.info("No hay productos para mostrar aun.")
        return

    chart_df = pd.DataFrame(rows)

    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Stock por categoria")
        st.bar_chart(chart_df.set_index("Categoria")["Stock"], color="#0f8b8d")
    with c2:
        st.subheader("Valor por categoria")
        st.bar_chart(chart_df.set_index("Categoria")["Valor"], color="#ff7f50")

    low_stock_rows = []
    for producto in productos:
        stock_actual = int(producto.get("stock_actual", 0))
        stock_minimo = int(producto.get("stock_minimo", 10))
        if stock_actual < stock_minimo:
            low_stock_rows.append(
                {
                    "Producto": producto.get("nombre", "-"),
                    "Categoria": producto.get("categoria", {}).get("nombre", "-"),
                    "Stock": stock_actual,
                    "Stock Minimo": stock_minimo,
                }
            )

    st.subheader("Alertas de Stock Minimo")
    if not low_stock_rows:
        st.success("No hay productos debajo del stock minimo.")
    else:
        with st.expander(f"Productos debajo del minimo: {len(low_stock_rows)}", expanded=False):
            st.dataframe(pd.DataFrame(low_stock_rows), use_container_width=True, hide_index=True)

    st.subheader("Detalle")
    st.dataframe(chart_df, use_container_width=True, hide_index=True)


def dashboard_por_categoria() -> None:
    st.markdown('<div class="headline">Dashboard por Categoria</div>', unsafe_allow_html=True)
    st.markdown('<div class="subhead">Filtra una categoria y revisa sus productos.</div>', unsafe_allow_html=True)

    categorias = get_categorias()
    if not categorias:
        st.info("No hay categorias disponibles.")
        return

    categorias_nombres = [c["nombre"] for c in categorias]
    categoria = st.selectbox("Categoria", options=categorias_nombres, index=0)

    productos = get_productos(categoria)
    if not productos:
        st.warning("No hay productos para la categoria seleccionada.")
        return

    rows = []
    total_stock = 0
    total_valor = 0.0
    for p in productos:
        stock = int(p["stock_actual"])
        precio = float(p["precio_unitario"])
        total_stock += stock
        total_valor += stock * precio
        rows.append(
            {
                "ID": p["id"],
                "Producto": p["nombre"],
                "Stock": stock,
                "Precio Unitario": round(precio, 2),
                "Valor en inventario": round(stock * precio, 2),
            }
        )

    k1, k2 = st.columns(2)
    render_kpi(k1, "Stock total categoria", str(total_stock))
    render_kpi(k2, "Valor categoria", f"${total_valor:,.2f}")

    chart_data = pd.DataFrame(
        [
            {
                "Producto": p["nombre"],
                "Stock": int(p["stock_actual"]),
                "Stock Minimo": int(p.get("stock_minimo", 10)),
            }
            for p in productos
        ]
    )
    chart_data["Estado Stock"] = chart_data.apply(
        lambda row: "Bajo minimo" if row["Stock"] < row["Stock Minimo"] else "OK",
        axis=1,
    )

    stock_chart = (
        alt.Chart(chart_data)
        .mark_bar(cornerRadiusTopLeft=6, cornerRadiusTopRight=6)
        .encode(
            x=alt.X("Producto:N", sort="-y", title="Producto"),
            y=alt.Y("Stock:Q", title="Stock"),
            color=alt.Color(
                "Estado Stock:N",
                scale=alt.Scale(domain=["Bajo minimo", "OK"], range=["#d7263d", "#0f8b8d"]),
                legend=alt.Legend(title="Estado"),
            ),
            tooltip=["Producto", "Stock", "Stock Minimo", "Estado Stock"],
        )
    )
    st.subheader("Stock por Producto")
    col_bar, col_pie = st.columns(2)
    with col_bar:
        st.altair_chart(stock_chart, use_container_width=True)

    with col_pie:
        if total_stock == 0:
            st.info("No hay stock en esta categoria para calcular participaciones.")
        else:
            pie_data = chart_data.copy()
            pie_data["Porcentaje"] = (pie_data["Stock"] / total_stock) * 100

            pie_chart = (
                alt.Chart(pie_data)
                .mark_arc(innerRadius=40)
                .encode(
                    theta=alt.Theta("Stock:Q", title="Stock"),
                    color=alt.Color("Producto:N", legend=alt.Legend(title="Producto")),
                    tooltip=[
                        "Producto",
                        "Stock",
                        alt.Tooltip("Porcentaje:Q", format=".1f", title="Participacion (%)"),
                    ],
                )
            )
            st.altair_chart(pie_chart, use_container_width=True)

    st.subheader("Detalle")
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def get_tipos_movimiento() -> list[dict]:
    response = api_get("/movimientos/tipos")
    if response is None:
        return []
    if response.status_code != 200:
        st.error(parse_error(response))
        return []
    return response.json()


def registrar_movimientos() -> None:
    st.markdown('<div class="headline">Registrar Movimiento</div>', unsafe_allow_html=True)
    st.markdown('<div class="subhead">Registra entradas o salidas de productos y actualiza stock en tiempo real.</div>', unsafe_allow_html=True)

    productos = get_productos()
    tipos = get_tipos_movimiento()

    if not productos:
        st.warning("No hay productos para registrar movimientos.")
        return

    if not tipos:
        st.warning("No hay tipos de movimiento configurados en la API.")
        return

    producto_options = {
        f"#{p['id']} - {p['nombre']} ({p['categoria']['nombre']})": p["id"]
        for p in productos
    }
    tipo_options = {t["tipo"].title(): t["id"] for t in tipos}

    with st.form("movimiento_form"):
        producto_label = st.selectbox("Producto", options=list(producto_options.keys()))
        tipo_label = st.selectbox("Tipo de movimiento", options=list(tipo_options.keys()))
        cantidad = st.number_input("Cantidad", min_value=1, value=1, step=1)
        motivo = st.text_area("Motivo", placeholder="Ej: compra proveedor, ajuste por conteo, venta")
        submit = st.form_submit_button("Guardar movimiento", use_container_width=True)

    if submit:
        producto_id = producto_options[producto_label]
        tipo_id = tipo_options[tipo_label]

        response = requests.post(
            f"{API_BASE_URL}/movimientos/productos/{producto_id}",
            headers=auth_headers(),
            json={
                "tipo_id": tipo_id,
                "cantidad": int(cantidad),
                "motivo": motivo or None,
            },
            timeout=REQUEST_TIMEOUT,
        )

        if response.status_code != 201:
            st.error(parse_error(response))
        else:
            st.success("Movimiento registrado correctamente")
            st.rerun()

    st.subheader("Movimientos recientes")
    historial_producto_label = st.selectbox(
        "Producto para historial",
        options=list(producto_options.keys()),
        key="historial_producto_select",
    )
    selected_product_id = producto_options[historial_producto_label]
    response = api_get("/movimientos", params={"producto_id": selected_product_id, "limite": 20})
    if response is None or response.status_code != 200:
        return

    movimientos = response.json()
    if not movimientos:
        st.info("Sin movimientos recientes para el producto inicial de la lista.")
        return

    rows = []
    for m in movimientos:
        tipo_info = m.get("tipo_movimiento") or m.get("tipomovimiento") or {}
        rows.append(
            {
                "Fecha": m["fecha"],
                "Tipo": tipo_info.get("tipo", "-"),
                "Cantidad": m["cantidad"],
                "Motivo": m["motivo"] or "-",
                "Usuario": m["usuario"],
            }
        )

    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)


def render_main_app() -> None:
    user = st.session_state.get("user") or {}

    with st.sidebar:
        st.markdown("### Inventario")
        st.caption(f"API: {API_BASE_URL}")
        st.caption(f"Usuario: {user.get('username', 'N/A')}")
        selected_page = st.radio(
            "Navegacion",
            options=["Dashboard General", "Dashboard por Categoria", "Registrar Movimiento"],
        )
        if st.button("Cerrar sesion", use_container_width=True):
            st.session_state["token"] = None
            st.session_state["user"] = None
            st.rerun()

    if selected_page == "Dashboard General":
        dashboard_general()
    elif selected_page == "Dashboard por Categoria":
        dashboard_por_categoria()
    else:
        registrar_movimientos()


if "token" not in st.session_state:
    st.session_state["token"] = None
if "user" not in st.session_state:
    st.session_state["user"] = None

if not st.session_state["token"]:
    render_auth_page()
else:
    if st.session_state["user"] is None:
        st.session_state["user"] = fetch_user()
    if st.session_state["user"] is None:
        st.error("No se pudo validar la sesion actual.")
        st.session_state["token"] = None
        st.rerun()
    render_main_app()
