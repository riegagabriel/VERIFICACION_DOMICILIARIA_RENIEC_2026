# streamlit_app.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

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
tabla_distrito = load_excel("data/tabla_desagregada_distrito.xlsx")

# ========================
# FILTROS GLOBALES
# ========================

if not tabla_distrito.empty:

    col1, col2 = st.columns(2)

    with col1:
        depto_filtro = st.selectbox(
            "Departamento",
            ["Todos"] + sorted(tabla_distrito["REG"].unique())
        )

    with col2:
        if depto_filtro == "Todos":
            distritos = sorted(tabla_distrito["DIST"].unique())
        else:
            distritos = sorted(
                tabla_distrito[tabla_distrito["REG"] == depto_filtro]["DIST"].unique()
            )

        distrito_filtro = st.selectbox(
            "Distrito",
            ["Todos"] + distritos
        )

    df_filtrado = tabla_distrito.copy()

    if depto_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["REG"] == depto_filtro]

    if distrito_filtro != "Todos":
        df_filtrado = df_filtrado[df_filtrado["DIST"] == distrito_filtro]

else:
    df_filtrado = pd.DataFrame()

# ========================
# PESTAÑAS
# ========================
tab1, tab2, tab3 = st.tabs([
    "📈 Progreso General",
    "📍 Monitoreo por Departamento",
    "🗺️ Mapa"
])

# ===========================================
# TAB 1: PROGRESO GENERAL
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

    if not df_filtrado.empty:

        A = df_filtrado["A"].sum()
        B = df_filtrado["B"].sum()
        C = df_filtrado["C"].sum()

        col1, col2, col3 = st.columns(3)

        col1.metric("Tipo A", f"{int(A):,}")
        col2.metric("Tipo B", f"{int(B):,}")
        col3.metric("Tipo C", f"{int(C):,}")

        fig = go.Figure(data=[go.Pie(
            labels=["Tipo A", "Tipo B", "Tipo C"],
            values=[A, B, C],
            hole=.55
        )])

        fig.update_layout(height=400)

        st.plotly_chart(fig, use_container_width=True)

    else:
        st.warning("No hay datos para el filtro seleccionado.")

    st.markdown("---")

# ========================
# TABLA DESAGREGADA
# ========================
st.subheader("📋 Avance por distrito")

if not df_filtrado.empty:

    df_filtrado["PORC_AVANCE"] = df_filtrado["PORC_AVANCE"].round(2)

    tabla_ordenada = df_filtrado.sort_values(
        by="PORC_AVANCE",
        ascending=False
    )

    buscar = st.text_input("🔎 Buscar distrito")

    if buscar:
        tabla_ordenada = tabla_ordenada[
            tabla_ordenada["DIST"].str.contains(buscar, case=False)
        ]

    st.dataframe(
        tabla_ordenada[
            ["REG","PROV","DIST","ciudadanos_verificados","A","B","C","MAX_POB_VERIFICAR","PORC_AVANCE"]
        ],
        use_container_width=True,
        hide_index=True
    )

else:
    st.warning("No se encontró la tabla desagregada.")

# ===========================================
# TAB 2: MONITOREO POR DEPARTAMENTO
# ===========================================
with tab2:

    st.subheader("📍 Avance por departamento")

    if not tabla_distrito.empty:

        deptos = ["Todos"] + sorted(tabla_distrito["REG"].unique())

        depto = st.selectbox(
            "Seleccionar departamento",
            deptos
        )

        df = tabla_distrito.copy()

        if depto != "Todos":
            df = df[df["REG"] == depto]

        df_bar = df.sort_values(
            by="PORC_AVANCE",
            ascending=False
        ).head(15)

        fig = px.bar(
            df_bar,
            x="PORC_AVANCE",
            y="DIST",
            orientation="h",
            text="PORC_AVANCE",
            title="Top distritos por avance"
        )

        fig.update_layout(
            yaxis={'categoryorder':'total ascending'}
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:

            st.subheader("🏆 Top 10 distritos con mayor avance")

            top = df.sort_values(
                by="PORC_AVANCE",
                ascending=False
            ).head(10)

            st.dataframe(
                top,
                hide_index=True,
                use_container_width=True
            )

        with col2:

            st.subheader("⚠️ Distritos con menor avance")

            bottom = df.sort_values(
                by="PORC_AVANCE",
                ascending=True
            ).head(10)

            st.dataframe(
                bottom,
                hide_index=True,
                use_container_width=True
            )

# ===========================================
# TAB 3: MAPA
# ===========================================
with tab3:

    st.subheader("🗺️ Mapa de verificación")

    st.info(
        "Para visualizar el mapa se requiere un archivo con coordenadas de distritos."
    )warning("No se encontró la tabla desagregada.")

# ===========================================
# TAB 2: MONITOREO POR DEPARTAMENTO
# ===========================================
with tab2:

    st.subheader("📍 Avance por departamento")

    if not tabla_distrito.empty:

        deptos = ["Todos"] + sorted(tabla_distrito["REG"].unique())

        depto = st.selectbox(
            "Seleccionar departamento",
            deptos
        )

        df = tabla_distrito.copy()

        if depto != "Todos":
            df = df[df["REG"] == depto]

        # gráfico de barras
        df_bar = df.sort_values(
            by="PORC_AVANCE",
            ascending=False
        ).head(15)

        fig = px.bar(
            df_bar,
            x="PORC_AVANCE",
            y="DIST",
            orientation="h",
            text="PORC_AVANCE",
            title="Top distritos por avance"
        )

        fig.update_layout(
            yaxis={'categoryorder':'total ascending'}
        )

        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # top y bottom
        col1, col2 = st.columns(2)

        with col1:

            st.subheader("🏆 Top 10 distritos con mayor avance")

            top = df.sort_values(
                by="PORC_AVANCE",
                ascending=False
            ).head(10)

            st.dataframe(
                top,
                hide_index=True,
                use_container_width=True
            )

        with col2:

            st.subheader("⚠️ Distritos con menor avance")

            bottom = df.sort_values(
                by="PORC_AVANCE",
                ascending=True
            ).head(10)

            st.dataframe(
                bottom,
                hide_index=True,
                use_container_width=True
            )

# ===========================================
# TAB 3: MAPA
# ===========================================
with tab3:

    st.subheader("🗺️ Mapa de verificación")

    st.info(
        "Para visualizar el mapa se requiere un archivo con coordenadas de distritos."
    )
