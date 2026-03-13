# streamlit_app.py
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# ========================
# CONFIGURACIÓN GENERAL
# ========================
st.set_page_config(
    page_title="Dashboard RENIEC – Verificación Domiciliaria 2026",
    layout="wide"
)

st.title("📊 Verificación Domiciliaria")
st.markdown("Monitoreo de avance de la verificación domiciliaria en distritos")

# ========================
# Helper: cargar excel
# ========================
@st.cache_data
def load_excel(path: str):
    try:
        return pd.read_excel(path)
    except:
        return pd.DataFrame()

# ========================
# Cargar DataFrames
# ========================
value_box = load_excel("data/value_box.xlsx")
situaciones_box = load_excel("data/box_situaciones.xlsx")

# ========================
# PESTAÑAS
# ========================
tab1, tab2, tab3 = st.tabs([
    "📈 Progreso General",
    "📍 Monitoreo por Departamento",
    "🗺️ Mapa"
])

# ===========================================
# TAB 1
# ===========================================
with tab1:

    st.subheader("Indicadores")

    if not value_box.empty:
        indicadores = dict(zip(value_box["Variable"], value_box["Valor"]))
    else:
        indicadores = {}

    dnis     = indicadores.get("ciudadanos_veri", 0)
    deps     = indicadores.get("departamentos", 0)
    provs    = indicadores.get("provincias", 0)
    dist     = indicadores.get("distritos", 0)
    fechas   = indicadores.get("fecha", 0)
    personal = indicadores.get("encuestadores", 0)

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("🆔 Ciudadanos Verificados", f"{int(dnis):,}")
    col2.metric("🗺️ Departamentos", int(deps))
    col3.metric("🏛️ Provincias", int(provs))
    col4.metric("📍 Distritos", int(dist))
    col5.metric("🗓️ Jornadas de trabajo", int(fechas))
    col6.metric("👷 Personal en campo", int(personal))

    st.markdown("---")

    # ========================
    # SITUACIONES
    # ========================
    st.subheader("Situaciones de verificación")

    if not situaciones_box.empty:

        situaciones = dict(zip(situaciones_box["Variable"], situaciones_box["Valor"]))

        A = situaciones.get("tipo_a", 0)
        B = situaciones.get("tipo_b", 0)
        C = situaciones.get("tipo_c", 0)

        col1, col2, col3 = st.columns(3)

        col1.metric("Tipo A", f"{int(A):,}")
        col2.metric("Tipo B", f"{int(B):,}")
        col3.metric("Tipo C", f"{int(C):,}")

        # ========================
        # Gráfico donut
        # ========================

        fig = go.Figure(data=[go.Pie(
            labels=["Tipo A", "Tipo B", "Tipo C"],
            values=[A, B, C],
            hole=.5
        )])

        fig.update_layout(height=400)

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No se encontró información de situaciones.")
