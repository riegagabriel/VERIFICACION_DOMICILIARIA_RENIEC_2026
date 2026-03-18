import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import zipfile
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
# FUNCIONES DE CARGA
# ========================
@st.cache_data
def load_excel(path):
    try:
        return pd.read_excel(path)
    except:
        return pd.DataFrame()

@st.cache_data
def load_csv(path):
    try:
        return pd.read_csv(path, parse_dates=['fecha'])
    except:
        return pd.DataFrame()

# ========================
# CARGAR DATA
# ========================
value_box       = load_excel("data/value_box.xlsx")
box_situaciones = load_excel("data/box_situaciones.xlsx")
tabla_distrito  = load_excel("data/tabla_desagregada_distrito.xlsx")
data_dept       = load_excel("data/data_total_departamentos.xlsx")
data_dist       = load_excel("data/data_distritos.xlsx")
data_enc        = load_excel("data/data_encuestadores.xlsx")

# Asegurar que 'fecha' sea datetime
if not data_dept.empty:
    data_dept['fecha'] = pd.to_datetime(data_dept['fecha'])
if not data_dist.empty:
    data_dist['fecha'] = pd.to_datetime(data_dist['fecha'])
if not data_enc.empty:
    data_enc['fecha'] = pd.to_datetime(data_enc['fecha'])

# ========================
# TABS
# ========================
tab1, tab2, tab3, tab4 = st.tabs([
    "📈 Progreso General",
    "📍 Monitoreo por Departamento",
    "👤 Monitoreo por Encuestador",
    "🗺️ Mapa"
])

# ====================================================
# TAB 1: PROGRESO GENERAL
# ====================================================
with tab1:

    # --- Indicadores ---
    st.subheader("Indicadores")

    if not value_box.empty:
        indicadores = dict(zip(value_box["Variable"], value_box["Valor"]))
        dnis     = indicadores.get("ciudadanos_veri", 0)
        deps     = indicadores.get("departamentos", 0)
        provs    = indicadores.get("provincias", 0)
        dist     = indicadores.get("distritos", 0)
        fechas   = indicadores.get("fecha", 0)
        personal = indicadores.get("encuestadores", 0)
    else:
        dnis = deps = provs = dist = fechas = personal = 0

    col1, col2, col3, col4, col5, col6 = st.columns(6)
    col1.metric("🆔 Ciudadanos Verificados", f"{int(dnis):,}")
    col2.metric("🗺️ Departamentos",          int(deps))
    col3.metric("🏛️ Provincias",             int(provs))
    col4.metric("📍 Distritos",              int(dist))
    col5.metric("🗓️ Jornadas",               int(fechas))
    col6.metric("👷 Personal",               int(personal))

    # --- Gauge ---
    POB_TOTAL           = 65137
    porc_avance_general = round((dnis / POB_TOTAL) * 100, 2) if POB_TOTAL > 0 else 0
    pendientes          = POB_TOTAL - int(dnis)

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
                    {"range": [0, 33],   "color": "#f9e4e4"},
                    {"range": [33, 66],  "color": "#fef9e7"},
                    {"range": [66, 100], "color": "#eafaf1"},
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
        st.metric("🎯 Meta total",   f"{POB_TOTAL:,}")
        st.metric("✅ Verificados",   f"{int(dnis):,}")
        st.metric("⏳ Pendientes",    f"{pendientes:,}")
        st.metric("📈 % Completado",  f"{porc_avance_general}%")

    # --- Filtros ---
    st.subheader("Filtros")

    if not tabla_distrito.empty:

        col1, col2 = st.columns(2)

        with col1:
            deptos = ["Todos"] + sorted(tabla_distrito["REG"].unique())
            depto  = st.selectbox("Departamento", deptos, key="filtro_depto")

        with col2:
            if depto == "Todos":
                distritos = sorted(tabla_distrito["DIST"].unique())
            else:
                distritos = sorted(
                    tabla_distrito[tabla_distrito["REG"] == depto]["DIST"].unique()
                )
            distrito = st.selectbox("Distrito", ["Todos"] + distritos, key="filtro_distrito")

        df_filtrado = tabla_distrito.copy()
        if depto    != "Todos":
            df_filtrado = df_filtrado[df_filtrado["REG"]  == depto]
        if distrito != "Todos":
            df_filtrado = df_filtrado[df_filtrado["DIST"] == distrito]

    else:
        df_filtrado = pd.DataFrame()
        depto = distrito = "Todos"

    st.markdown("---")

    # --- Situaciones ---
    st.subheader("Situaciones de verificación")

    if distrito == "Todos" and depto == "Todos":
        situaciones = dict(zip(box_situaciones["Variable"], box_situaciones["Valor"]))
        A = situaciones.get("tipo_a", 0)
        B = situaciones.get("tipo_b", 0)
        C = situaciones.get("tipo_c", 0)
        Sin_causal = situaciones.get("tipo_sin_causal", 0)
    else:
        A = df_filtrado["A"].sum()
        B = df_filtrado["B"].sum()
        C = df_filtrado["C"].sum()
        Sin_causal = df_filtrado["Sin_causal"].sum()

    col1, col2, col3 = st.columns(3)
    col1.metric("Tipo A", f"{int(A):,}")
    col2.metric("Tipo B", f"{int(B):,}")
    col3.metric("Tipo C", f"{int(C):,}")
    col4.metric("Sin Causal", f"{int(Sin_causal):,}")

    fig_pie = go.Figure(data=[go.Pie(
        labels=["Tipo A", "Tipo B", "Tipo C","Sin Causal"],
        values=[A, B, C, Sin_Causal],
        hole=.55
    )])
    fig_pie.update_layout(height=400)
    st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")

    # --- Tabla distrito ---
    st.subheader("📋 Avance por distrito")

    if not df_filtrado.empty:
        df_filtrado["PORC_AVANCE"] = df_filtrado["PORC_AVANCE"].round(2)
        tabla  = df_filtrado.sort_values(by="PORC_AVANCE", ascending=False)
        buscar = st.text_input("🔎 Buscar distrito")

        if buscar:
            tabla = tabla[tabla["DIST"].str.contains(buscar, case=False)]

        st.dataframe(
            tabla[[
                "REG", "PROV", "DIST",
                "ciudadanos_verificados", "A", "B", "C",
                "MAX_POB_VERIFICAR", "PORC_AVANCE"
            ]].rename(columns={
                "REG":                    "Departamento",
                "PROV":                   "Provincia",
                "DIST":                   "Distrito",
                "ciudadanos_verificados": "Ciudadanos Verificados",
                "A":                      "Tipo A",
                "B":                      "Tipo B",
                "C":                      "Tipo C",
                "MAX_POB_VERIFICAR":      "Población a Verificar",
                "PORC_AVANCE":            "% Avance"
            }),
            use_container_width=True,
            hide_index=True
        )
    else:
        st.warning("No se encontró la tabla desagregada.")


# ====================================================
# TAB 2: MONITOREO POR DEPARTAMENTO
# ====================================================
with tab2:

    st.subheader("📍 Avance por departamento")

    if not tabla_distrito.empty:

        deptos2 = ["Todos"] + sorted(tabla_distrito["REG"].unique())
        depto2  = st.selectbox("Seleccionar departamento", deptos2, key="depto_tab2")
        df_tab2 = tabla_distrito.copy()

        if depto2 != "Todos":
            df_tab2 = df_tab2[df_tab2["REG"] == depto2]

        df_bar = df_tab2.sort_values(by="PORC_AVANCE", ascending=False).head(15)

        fig_bar = px.bar(
            df_bar,
            x="PORC_AVANCE",
            y="DIST",
            orientation="h",
            text="PORC_AVANCE",
            title="Top distritos por avance"
        )
        fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown("---")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("🏆 Top distritos")
            st.dataframe(
                df_tab2.sort_values(by="PORC_AVANCE", ascending=False).head(10),
                hide_index=True,
                use_container_width=True
            )

        with col2:
            st.subheader("⚠️ Distritos con menor avance")
            st.dataframe(
                df_tab2.sort_values(by="PORC_AVANCE", ascending=True).head(10),
                hide_index=True,
                use_container_width=True
            )

    st.markdown("---")

    # --- Evolución diaria total por departamento ---
    st.subheader("📈 Evolución diaria por departamento")

    if not data_dept.empty:

        data_total_gral = (
            data_dept.groupby('fecha')['ciudadanos_verificados']
            .sum()
            .reset_index()
        )
        data_total_gral.columns = ['fecha', 'total_count']

        fig_dept = go.Figure()

        fig_dept.add_trace(go.Scatter(
            x=data_total_gral['fecha'],
            y=data_total_gral['total_count'],
            mode='lines+markers',
            name='TOTAL GENERAL',
            line=dict(color='red', width=3),
            marker=dict(size=8),
            hovertemplate='<b>TOTAL GENERAL</b><br>Fecha: %{x}<br>Ciudadanos: %{y}<extra></extra>'
        ))

        for dep in sorted(data_dept['DEPARTAMENTO'].unique()):
            df_d = data_dept[data_dept['DEPARTAMENTO'] == dep]
            fig_dept.add_trace(go.Scatter(
                x=df_d['fecha'],
                y=df_d['ciudadanos_verificados'],
                mode='lines+markers',
                name=dep,
                line=dict(width=1.5),
                marker=dict(size=5),
                visible='legendonly',
                hovertemplate=f'<b>{dep}</b><br>Fecha: %{{x}}<br>Ciudadanos: %{{y}}<extra></extra>'
            ))

        fig_dept.update_layout(
            title='Ciudadanos Verificados por Departamento y Fecha',
            xaxis_title='Fecha',
            yaxis_title='Ciudadanos Verificados',
            hovermode='x unified',
            legend=dict(
                title='Departamentos (clic para mostrar/ocultar)',
                yanchor="top", y=0.99,
                xanchor="left", x=1.01
            ),
            height=500,
            template='plotly_white'
        )
        st.plotly_chart(fig_dept, use_container_width=True)

    else:
        st.warning("No se encontró data_total_departamentos.xlsx")

    st.markdown("---")

    # --- Evolución diaria por distrito con filtro ---
    st.subheader("📍 Evolución diaria por distrito")

    if not data_dist.empty:

        departamentos_dist = sorted(data_dist['DEPARTAMENTO'].unique())
        depto_sel          = st.selectbox(
            "Seleccionar departamento",
            departamentos_dist,
            key="depto_dist_graf"
        )

        df_dist_sel  = data_dist[data_dist['DEPARTAMENTO'] == depto_sel]
        df_total_dep = (
            df_dist_sel.groupby('fecha')['ciudadanos_verificados']
            .sum()
            .reset_index()
        )
        df_total_dep.columns = ['fecha', 'total_count']

        fig_dist = go.Figure()

        fig_dist.add_trace(go.Scatter(
            x=df_total_dep['fecha'],
            y=df_total_dep['total_count'],
            mode='lines+markers',
            name=f'TOTAL {depto_sel}',
            line=dict(color='red', width=3),
            marker=dict(size=8),
            hovertemplate=f'<b>TOTAL {depto_sel}</b><br>Fecha: %{{x}}<br>Ciudadanos: %{{y}}<extra></extra>'
        ))

        for dist_name in sorted(df_dist_sel['DISTRITO'].unique()):
            df_d = df_dist_sel[df_dist_sel['DISTRITO'] == dist_name]
            fig_dist.add_trace(go.Scatter(
                x=df_d['fecha'],
                y=df_d['ciudadanos_verificados'],
                mode='lines+markers',
                name=dist_name,
                line=dict(width=1.5),
                marker=dict(size=5),
                visible='legendonly',
                hovertemplate=f'<b>{dist_name}</b><br>Fecha: %{{x}}<br>Ciudadanos: %{{y}}<extra></extra>'
            ))

        fig_dist.update_layout(
            title=f'Ciudadanos Verificados por Distrito — {depto_sel}',
            xaxis_title='Fecha',
            yaxis_title='Ciudadanos Verificados',
            hovermode='x unified',
            legend=dict(
                title='Distritos (clic para mostrar/ocultar)',
                yanchor="top", y=0.99,
                xanchor="left", x=1.01
            ),
            height=500,
            template='plotly_white'
        )
        st.plotly_chart(fig_dist, use_container_width=True)

    else:
        st.warning("No se encontró data_distritos.xlsx")


# ====================================================
# TAB 3: MONITOREO POR ENCUESTADOR
# ====================================================
with tab3:

    st.subheader("👤 Monitoreo por encuestador")

    if data_enc.empty:
        st.warning("No se encontró data_encuestadores.xlsx en la carpeta data/")

    else:

        # ============================================================
        # SECCIÓN A: RENDIMIENTO TOTAL POR ENCUESTADOR
        # ============================================================
        st.markdown("##  Rendimiento total por encuestador")
        st.markdown("Registros acumulados durante toda la actividad, filtrado por distrito.")

        col1, col2 = st.columns(2)

        with col1:
            deps_enc    = sorted(data_enc['REG'].dropna().unique())
            dep_enc_sel = st.selectbox("Departamento", deps_enc, key="dep_enc_total")

        with col2:
            dists_enc = sorted(
                data_enc[data_enc['REG'] == dep_enc_sel]['DIST'].dropna().unique()
            )
            dist_enc_sel = st.selectbox("Distrito", dists_enc, key="dist_enc_total")

        df_enc_f = data_enc[
            (data_enc['REG']  == dep_enc_sel) &
            (data_enc['DIST'] == dist_enc_sel)
        ]

        df_total_enc = (
            df_enc_f.groupby('nombre_encuestador')['ciudadanos_verificados']
            .count()
            .reset_index()
            .rename(columns={'ciudadanos_verificados': 'total_verificados'})
            .sort_values('total_verificados', ascending=False)
        )

        if df_total_enc.empty:
            st.warning("No hay datos para el distrito seleccionado.")

        else:

            col_tabla, col_graf = st.columns([1, 2])

            with col_tabla:
                st.markdown(f"**{dist_enc_sel} — {dep_enc_sel}**")
                st.dataframe(
                    df_total_enc.rename(columns={
                        'nombre_encuestador': 'Encuestador',
                        'total_verificados':  'Total Verificados'
                    }),
                    hide_index=True,
                    use_container_width=True
                )

            with col_graf:
                fig_enc = go.Figure()
                fig_enc.add_trace(go.Bar(
                    x=df_total_enc['total_verificados'],
                    y=df_total_enc['nombre_encuestador'],
                    orientation='h',
                    marker=dict(color='#4A90E2'),
                    hovertemplate='<b>%{y}</b><br>Total: %{x}<extra></extra>'
                ))
                fig_enc.update_layout(
                    title=f'Registros totales por encuestador — {dist_enc_sel}',
                    xaxis_title='Ciudadanos Verificados',
                    yaxis_title='',
                    yaxis=dict(categoryorder='total ascending'),
                    height=max(400, len(df_total_enc) * 35),
                    template='plotly_white',
                    margin=dict(l=200)
                )
                st.plotly_chart(fig_enc, use_container_width=True)

        st.markdown("---")

        # ============================================================
        # SECCIÓN B: MONITOREO INDIVIDUAL — HEATMAP DIARIO
        # ============================================================
        st.markdown("##  Monitoreo individual — avance diario por encuestador")
        st.markdown("Detalle de ciudadanos verificados por encuestador y jornada.")

        col1, col2 = st.columns(2)

        with col1:
            deps_hm    = sorted(data_enc['REG'].dropna().unique())
            dep_hm_sel = st.selectbox("Departamento", deps_hm, key="dep_hm")

        with col2:
            dists_hm = sorted(
                data_enc[data_enc['REG'] == dep_hm_sel]['DIST'].dropna().unique()
            )
            dist_hm_sel = st.selectbox("Distrito", dists_hm, key="dist_hm")

        df_hm_f = data_enc[
            (data_enc['REG']  == dep_hm_sel) &
            (data_enc['DIST'] == dist_hm_sel)
        ]

        if df_hm_f.empty:
            st.warning("No hay datos para el distrito seleccionado.")

        else:

            # Crosstab: filas = encuestador, columnas = fecha
            crosstab = (
                df_hm_f.groupby(['nombre_encuestador', 'fecha'])['ciudadanos_verificados']
                .count()
                .unstack(fill_value=0)
                .sort_index()
            )

            # Tabla con totales
            crosstab_display = crosstab.copy()
            crosstab_display.columns = crosstab_display.columns.strftime('%d/%m/%Y')
            crosstab_display['TOTAL'] = crosstab_display.sum(axis=1)
            crosstab_display = crosstab_display.sort_values('TOTAL', ascending=False)

            st.markdown(f"**Avance diario — {dist_hm_sel} ({dep_hm_sel})**")
            st.dataframe(crosstab_display, use_container_width=True)

            # Heatmap
            x_labels = crosstab.columns.strftime('%d/%m/%Y')

            # Anotaciones: mostrar 0 como vacío
            annot               = crosstab.values.astype(str)
            annot[annot == '0'] = ''

            zmax_val = int(crosstab.values.max()) if crosstab.values.max() > 0 else 1

            fig_hm = go.Figure(data=go.Heatmap(
                z=crosstab.values,
                x=x_labels,
                y=crosstab.index.astype(str),
                text=annot,
                texttemplate="%{text}",
                colorscale="YlGnBu",
                zmin=0,
                zmax=zmax_val,
                colorbar=dict(title="Verificados"),
                hovertemplate=(
                    'Encuestador: %{y}<br>'
                    'Fecha: %{x}<br>'
                    'Verificados: %{z}<extra></extra>'
                )
            ))

            fig_hm.update_layout(
                title=f'Heatmap de avance diario — {dist_hm_sel}',
                xaxis_title='Fecha',
                yaxis_title='Encuestador',
                height=max(400, len(crosstab) * 40),
                template='plotly_white',
                margin=dict(l=200)
            )
            fig_hm.update_yaxes(automargin=True)

            st.plotly_chart(fig_hm, use_container_width=True)


# ====================================================
# TAB 4: MAPA
# ====================================================
with tab4:

    st.subheader("🗺️ Mapa de verificación")
    st.info("Seleccione el tipo de mapa para visualizar la planificación territorial.")

    mapa_tipo = st.selectbox(
        "Tipo de mapa",
        ["OpenStreetMap", "CartoDB", "Satélite", "Heatmap"]
    )

    mapa_archivos = {
        "OpenStreetMap": "mapa_osm.html",
        "CartoDB":       "mapa_carto.html",
        "Satélite":      "mapa_satelital.html",
        "Heatmap":       "mapa_heatmap.html"
    }

    archivo_html = mapa_archivos[mapa_tipo]
    zip_path     = "data/mapas_verificacion.zip"

    try:
        with zipfile.ZipFile(zip_path, "r") as z:
            html_content = z.read(archivo_html).decode("utf-8")
        components.html(html_content, height=650, scrolling=True)

    except FileNotFoundError:
        st.error("❌ No se encontró el archivo: data/mapas_verificacion.zip")

    except KeyError:
        st.error(f"❌ El archivo {archivo_html} no existe dentro del ZIP.")
