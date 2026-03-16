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
value_box = load_excel("data/value_box.xlsx")
box_situaciones = load_excel("data/box_situaciones.xlsx")
tabla_distrito = load_excel("data/tabla_desagregada_distrito.xlsx")
data_dept = load_excel("data/data_total_departamentos.xlsx")
data_dist = load_excel("data/data_distritos.xlsx")
data_enc = load_excel("data/data_encuestadores.xlsx")

# Asegurar que 'fecha' sea datetime
if not data_dept.empty:
    data_dept['fecha'] = pd.to_datetime(data_dept['fecha'])

if not data_dist.empty:
    data_dist['fecha'] = pd.to_datetime(data_dist['fecha'])

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

    col1, col2, col3, col4, col5, col6 = st.columns(6)

    col1.metric("🆔 Ciudadanos Verificados", f"{int(dnis):,}")
    col2.metric("🗺️ Departamentos", int(deps))
    col3.metric("🏛️ Provincias", int(provs))
    col4.metric("📍 Distritos", int(dist))
    col5.metric("🗓️ Jornadas", int(fechas))
    col6.metric("👷 Personal", int(personal))

    # --- Gauge ---
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
                    {"range": [0, 33], "color": "#f9e4e4"},
                    {"range": [33, 66], "color": "#fef9e7"},
                    {"range": [66, 100], "color": "#eafaf1"},
                ],
                "threshold": {
                    "line": {"color": "#e74c3c", "width": 4},
                    "thickness": 0.75,
                    "value": 100
                }
            }
        ))

        fig_gauge.update_layout(
            height=300,
            margin=dict(t=60, b=20, l=30, r=30)
        )

        st.plotly_chart(fig_gauge, use_container_width=True)

    with col_resumen:

        st.markdown("### Resumen de avance general")
        st.markdown("---")

        st.metric("🎯 Meta total", f"{POB_TOTAL:,}")
        st.metric("✅ Verificados", f"{int(dnis):,}")
        st.metric("⏳ Pendientes", f"{pendientes:,}")
        st.metric("📈 % Completado", f"{porc_avance_general}%")

    st.markdown("---")

# ====================================================
# TAB 3: MONITOREO POR ENCUESTADOR
# ====================================================
with tab3:

    st.subheader("👤 Monitoreo por encuestador")

    if data_enc.empty:
        st.warning("No se encontró data_encuestadores.xlsx en la carpeta data/")
    else:

        st.markdown("## 🔥 Monitoreo individual — avance diario por encuestador")
        st.markdown("Detalle de ciudadanos verificados por encuestador y jornada.")

        col1, col2 = st.columns(2)

        with col1:
            deps_hm = sorted(data_enc['REG'].dropna().unique())
            dep_hm_sel = st.selectbox("Departamento", deps_hm, key="dep_hm")

        with col2:
            dists_hm = sorted(data_enc[data_enc['REG'] == dep_hm_sel]['DIST'].dropna().unique())
            dist_hm_sel = st.selectbox("Distrito", dists_hm, key="dist_hm")

        df_hm_f = data_enc[
            (data_enc['REG'] == dep_hm_sel) &
            (data_enc['DIST'] == dist_hm_sel)
        ]

        if df_hm_f.empty:
            st.warning("No hay datos para el distrito seleccionado.")

        else:

            # Crosstab: filas = encuestador, columnas = fecha
            crosstab = (
                df_hm_f
                .groupby(['nombre_encuestador', 'fecha'])['ciudadanos_verificados']
                .count()
                .unstack(fill_value=0)
                .sort_index()
            )

            crosstab_display = crosstab.copy()
            crosstab_display.columns = crosstab_display.columns.strftime('%d/%m/%Y')
            crosstab_display['TOTAL'] = crosstab_display.sum(axis=1)
            crosstab_display = crosstab_display.sort_values('TOTAL', ascending=False)

            st.markdown(f"**Avance diario — {dist_hm_sel} ({dep_hm_sel})**")
            st.dataframe(crosstab_display, use_container_width=True)

            x_labels = crosstab.columns.strftime('%d/%m/%Y')

            annot = crosstab.values.astype(str)
            annot[annot == '0'] = ''

            zmax_val = int(crosstab.values.max()) if crosstab.values.max() > 0 else 1

            fig_hm = go.Figure(
                data=go.Heatmap(
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
                )
            )

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
