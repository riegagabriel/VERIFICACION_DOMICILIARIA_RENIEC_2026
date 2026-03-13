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
st.markdown("Monitoreo de avance de la verificación domiciliaria en distritos)")

# ========================
# Helper: cargar excel con manejo de errores
# ========================
@st.cache_data
def load_excel(path: str, sheet_name=0):
    """
    Lee un Excel de forma robusta.
    - sheet_name por defecto es 0 (primera hoja).
    - Si ocurre un error devuelve DataFrame vacío.
    """
    try:
        # Forzamos sheet_name por defecto a 0 para evitar que read_excel devuelva dict()
        return pd.read_excel(path, sheet_name=sheet_name)
    except Exception as e:
        st.warning(f"Advertencia al leer {path} (sheet={sheet_name}): {e}")
        return pd.DataFrame()

# ========================
# Cargar DataFrames principales
# ========================
value_box = load_excel("data/value_box.xlsx")
situaciones_box = load_excel("data/value_box.xlsx")

data_graf = load_excel("data/data_graf.xlsx")
tabla_desagregada_mcp_merged = load_excel("data/tabla_desagregada_mcp_merged.xlsx")

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

    # Prevenir error si value_box vacío
    if not value_box.empty and ("Variable" in value_box.columns) and ("Valor" in value_box.columns):
        indicadores = dict(zip(value_box["Variable"], value_box["Valor"]))
    else:
        indicadores = {}

    # Extraer valores con fallback
    dnis = indicadores.get("ciudadanos_veri", 0)
    deps = indicadores.get("departamentos", 0)
    provs = indicadores.get("provincias", 0)
    dist = indicadores.get("distritos", 0)
    fechas = indicadores.get("fecha", 0)
    personal = indicadores.get("encuestadores", 0)

    # Value Boxes (Métricas)
    col1, col2, col3, col4, col5,col6 = st.columns(5)
    col1.metric("🆔 Ciudadanos Verificados", f"{int(dnis):,}" if pd.notna(dnis) else "0")
    col2.metric("🗺️ Departamentos", deps)
    col3.metric("🏛️ Provincias", provs)
    col4.metric("📍 Distritos", dist)
    col5.metric("🗓️ Jornadas de trabajo", fechas)
    col6.metric("🗓️ Personal en campo", personal)

    st.markdown("---")

