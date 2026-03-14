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
# FUNCION CARGA DE DATOS
# ========================
@st.cache_data
def load_excel(path):
    try:
        return pd.read_excel(path)
    except:
        return pd.DataFrame()

# ========================
# CARGAR DATA
# ========================
value_box = load_excel("data/value_box.xlsx")
box_situaciones = load_excel("data/box_situaciones.xlsx")
tabla_distrito = load_excel("data/tabla_desagregada_distrito.xlsx")

# ========================
# TABS
# ========================
tab1, tab2, tab3 = st.tabs([
    "📈 Progreso General",
    "📍 Monitoreo por Departamento",
    "🗺️ Mapa"
])

# ====================================================
# TAB 1
# ====================================================
with tab1:

    # ========================
    # INDICADORES
    # ========================
    st.subheader("Indicadores")

    if not value_box.empty:

        indicadores = dict(zip(value_box["Variable"], value_box["Valor"]))

        dnis = indicadores.get("ciudadanos_veri", 0)
        deps = indicadores.get("departamentos", 0)
        provs = indicadores.get("provincias", 0)
        dist = indicadores.get("distritos", 0)
        fechas = indicadores.get("fecha", 0)
        personal = indicadores.get("encuestadores", 0)

    else:
        dnis = deps = provs = dist = fechas = personal = 0

    col1,col2,col3,col4,col5,col6 = st.columns(6)

    col1.metric("🆔 Ciudadanos Verificados", f"{int(dnis):,}")
    col2.metric("🗺️ Departamentos", int(deps))
    col3.metric("🏛️ Provincias", int(provs))
    col4.metric("📍 Distritos", int(dist))
    col5.metric("🗓️ Jornadas", int(fechas))
    col6.metric("👷 Personal", int(personal))

    st.markdown("---")

    # ========================
    # FILTROS
    # ========================
    st.subheader("Filtros")

    if not tabla_distrito.empty:

        col1, col2 = st.columns(2)

        with col1:

            deptos = ["Todos"] + sorted(tabla_distrito["REG"].unique())

            depto = st.selectbox(
                "Departamento",
                deptos,
                key="filtro_depto"
            )

        with col2:

            if depto == "Todos":
                distritos = sorted(tabla_distrito["DIST"].unique())
            else:
                distritos = sorted(
                    tabla_distrito[tabla_distrito["REG"] == depto]["DIST"].unique()
                )

            distrito = st.selectbox(
                "Distrito",
                ["Todos"] + distritos,
                key="filtro_distrito"
            )

        df_filtrado = tabla_distrito.copy()

        if depto != "Todos":
            df_filtrado = df_filtrado[df_filtrado["REG"] == depto]

        if distrito != "Todos":
            df_filtrado = df_filtrado[df_filtrado["DIST"] == distrito]

    else:

        df_filtrado = pd.DataFrame()

    st.markdown("---")

    # ========================
    # SITUACIONES
    # ========================
    st.subheader("Situaciones de verificación")

    if distrito == "Todos" and depto == "Todos":

        situaciones = dict(zip(
            box_situaciones["Variable"],
            box_situaciones["Valor"]
        ))

        A = situaciones.get("tipo_a",0)
        B = situaciones.get("tipo_b",0)
        C = situaciones.get("tipo_c",0)

    else:

        A = df_filtrado["A"].sum()
        B = df_filtrado["B"].sum()
        C = df_filtrado["C"].sum()

    col1,col2,col3 = st.columns(3)

    col1.metric("Tipo A",f"{int(A):,}")
    col2.metric("Tipo B",f"{int(B):,}")
    col3.metric("Tipo C",f"{int(C):,}")

    fig = go.Figure(data=[go.Pie(
        labels=["Tipo A","Tipo B","Tipo C"],
        values=[A,B,C],
        hole=.55
    )])

    fig.update_layout(height=400)

    st.plotly_chart(fig,use_container_width=True)

    st.markdown("---")

    # ========================
    # TABLA DISTRITO
    # ========================
    st.subheader("📋 Avance por distrito")

    if not df_filtrado.empty:

        df_filtrado["PORC_AVANCE"] = df_filtrado["PORC_AVANCE"].round(2)

        tabla = df_filtrado.sort_values(
            by="PORC_AVANCE",
            ascending=False
        )

        buscar = st.text_input("🔎 Buscar distrito")

        if buscar:

            tabla = tabla[
                tabla["DIST"].str.contains(buscar,case=False)
            ]

        st.dataframe(
            tabla[
                [
                "REG",
                "PROV",
                "DIST",
                "ciudadanos_verificados",
                "A",
                "B",
                "C",
                "MAX_POB_VERIFICAR",
                "PORC_AVANCE"
                ]
            ],
            use_container_width=True,
            hide_index=True
        )

    else:

        st.warning("No se encontró la tabla desagregada.")

# ====================================================
# TAB 2
# ====================================================
with tab2:

    st.subheader("📍 Avance por departamento")

    if not tabla_distrito.empty:

        deptos = ["Todos"] + sorted(tabla_distrito["REG"].unique())

        depto2 = st.selectbox(
            "Seleccionar departamento",
            deptos,
            key="depto_tab2"
        )

        df = tabla_distrito.copy()

        if depto2 != "Todos":
            df = df[df["REG"] == depto2]

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

        st.plotly_chart(fig,use_container_width=True)

        st.markdown("---")

        col1,col2 = st.columns(2)

        with col1:

            st.subheader("🏆 Top distritos")

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

# ====================================================
# TAB 3
# ====================================================
with tab3:

    st.subheader("🗺️ Mapa de verificación")

    st.info(
        "Para visualizar el mapa se requiere un archivo con coordenadas de distritos."
    )
