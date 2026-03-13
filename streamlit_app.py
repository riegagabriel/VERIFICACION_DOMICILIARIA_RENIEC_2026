# streamlit_app.py (archivo completo)
import os
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import streamlit.components.v1 as components

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
# Helper: cargar excel con manejo de errores
# ========================
@st.cache_data
def load_excel(path: str, sheet_name=0):
    try:
        return pd.read_excel(path, sheet_name=sheet_name)
    except Exception as e:
        st.warning(f"Advertencia al leer {path} (sheet={sheet_name}): {e}")
        return pd.DataFrame()

# ========================
# Cargar DataFrames principales
# ========================
value_box = load_excel("data/value_box.xlsx")
situaciones_box = load_excel("data/box_situaciones.xlsx")   # ← CORREGIDO (era value_box.xlsx)
#data_graf = load_excel("data/data_graf.xlsx")
#tabla_desagregada_mcp_merged = load_excel("data/tabla_desagregada_mcp_merged.xlsx")

# ========================
# PESTAÑAS
# ========================
tab1, tab2, tab3 = st.tabs([
    "📈 Progreso General",
    "📍 Monitoreo por MCP",
    "🗺️ Mapa de Empadronamiento"
])

# ===========================================
# 📈 TAB 1: PROGRESO GENERAL
# ===========================================
with tab1:
    st.subheader("Indicadores")

    if not value_box.empty and ("Variable" in value_box.columns) and ("Valor" in value_box.columns):
        indicadores = dict(zip(value_box["Variable"], value_box["Valor"]))
    else:
        indicadores = {}

    # Extraer valores con fallback
    dnis     = indicadores.get("ciudadanos_veri", 0)
    deps     = indicadores.get("departamentos", 0)
    provs    = indicadores.get("provincias", 0)
    dist     = indicadores.get("distritos", 0)
    fechas   = indicadores.get("fecha", 0)
    personal = indicadores.get("encuestadores", 0)

    # Value Boxes — CORREGIDO: eran 6 métricas en 5 columnas
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🆔 Ciudadanos Verificados", f"{int(dnis):,}" if pd.notna(dnis) else "0")
    col2.metric("🗺️ Departamentos", int(deps) if pd.notna(deps) else 0)
    col3.metric("🏛️ Provincias", int(provs) if pd.notna(provs) else 0)
    col4.metric("📍 Distritos", int(dist) if pd.notna(dist) else 0)
    col5.metric("🗓️ Jornadas de trabajo", int(fechas) if pd.notna(fechas) else 0)
    col6.metric("👷 Personal en campo", int(personal) if pd.notna(personal) else 0)

    st.markdown("---")

    # ── Gráfico de situaciones (box_situaciones) ──
    st.subheader("Situaciones")
    if not situaciones_box.empty and ("Variable" in situaciones_box.columns) and ("Valor" in situaciones_box.columns):
        fig = go.Figure(go.Bar(
            x=situaciones_box["Variable"],
            y=situaciones_box["Valor"],
            text=situaciones_box["Valor"],
            textposition="outside"
        ))
        fig.update_layout(
            xaxis_title="Tipo",
            yaxis_title="Cantidad",
            plot_bgcolor="rgba(0,0,0,0)",
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No hay datos de situaciones disponibles.")
