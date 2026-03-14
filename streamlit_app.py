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

    # ========================
    # AVANCE GENERAL
    # ========================
    POB_TOTAL = 65137
    porc_avance_general = round((dnis / POB_TOTAL) * 100, 2) if POB_TOTAL > 0 else 0
    pendientes = POB_TOTAL - int(dnis)

    col_gauge, col_resumen = st.columns([2, 1])

    with col_gauge:

        fig_gauge = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=porc_avance_general,
            number={"suffix": "%", "font": {"size": 48}},
            delta={"reference": 100, "suffix": "%"},
            title={"text": "Avance General de Verificación", "font": {"size": 18}},
            gauge={
                "axis": {"range": [0, 100], "ticksuffix": "%"},
                "bar": {"color": "#2ecc71"},
                "steps": [
                    {"range": [0, 33],  "color": "#f9e4e4"},
                    {"range": [33, 66], "color": "#fef9e7"},
                    {"range": [66, 100],"color": "#eafaf1"},
                ],
                "threshold": {
                    "line": {"color": "#e74c3c", "width": 4},
                    "thickness": 0.75,
                    "value": 100
                }
            }
        ))

        fig_gauge.update_layout(height=300, margin=dict(t=60, b=20, l=30, r=30))
        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_resumen:

        st.markdown("### Resumen de avance general")
        st.markdown("---")
        st.metric("🎯 Meta total",         f"{POB_TOTAL:,}")
        st.metric("✅ Verificados",         f"{int(dnis):,}")
        st.metric("⏳ Pendientes",          f"{pendientes:,}")
        st.metric("📈 % Completado",        f"{porc_avance_general}%")

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
            ].rename(columns={
        "REG": "Departamento",
        "PROV": "Provincia",
        "DIST": "Distrito",
        "ciudadanos_verificados": "Ciudadanos Verificados",
        "A": "Tipo A",
        "B": "Tipo B",
        "C": "Tipo C",
        "MAX_POB_VERIFICAR": "Población a Verificar",
        "PORC_AVANCE": "% Avance"
    }),
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

    import zipfile
    import streamlit.components.v1 as components

    st.subheader("🗺️ Mapa de verificación")

    zip_path = "data/mapa_verificacion_departamentos.zip"

    try:

        with zipfile.ZipFile(zip_path, 'r') as zip_ref:

            html_files = [f for f in zip_ref.namelist() if f.endswith(".html")]

            if html_files:

                html_content = zip_ref.read(html_files[0]).decode("utf-8")

                components.html(
                    html_content,
                    height=700,
                    scrolling=True
                )

            else:
                st.warning("El archivo ZIP no contiene un HTML.")

    except FileNotFoundError:

        st.info("Mapa aún no disponible.")
