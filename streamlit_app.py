import streamlit as st
import pandas as pd

st.set_page_config(page_title="Verificación Domiciliaria 2026", layout="wide")

# -----------------------------
# Cargar datos
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data3.csv")
    return df

data3 = load_data()

# limpiar type_situation
data3["type_situation"] = data3["type_situation"].fillna("")

# -----------------------------
# INDICADORES
# -----------------------------
st.title("📊 Verificación Domiciliaria RENIEC 2026")

total = data3["id_participant"].nunique()
A = (data3["type_situation"] == "A").sum()
B = (data3["type_situation"] == "B").sum()
C = (data3["type_situation"] == "C").sum()

col1, col2, col3, col4 = st.columns(4)

col1.metric("Ciudadanos verificados", total)
col2.metric("Situación A", A)
col3.metric("Situación B", B)
col4.metric("Situación C", C)

st.divider()

# -----------------------------
# FILTROS
# -----------------------------
st.subheader("Filtros")

col1, col2 = st.columns(2)

deptos = ["Todos"] + sorted(data3["departamento_titular"].dropna().unique())

depto = col1.selectbox(
    "Departamento",
    deptos,
    key="filtro_departamento"
)

df_filtrado = data3.copy()

if depto != "Todos":
    df_filtrado = df_filtrado[df_filtrado["departamento_titular"] == depto]

distritos = ["Todos"] + sorted(df_filtrado["distrito_titular"].dropna().unique())

distrito = col2.selectbox(
    "Distrito",
    distritos,
    key="filtro_distrito"
)

if distrito != "Todos":
    df_filtrado = df_filtrado[df_filtrado["distrito_titular"] == distrito]

st.divider()

# -----------------------------
# TABLA DESAGREGADA
# -----------------------------
st.subheader("Tabla desagregada")

tabla_desagregada = (
    df_filtrado
    .groupby(
        ['departamento_titular','provincia_titular','distrito_titular','type_situation'],
        dropna=False
    )['id_participant']
    .nunique()
    .unstack(fill_value=0)
    .reset_index()
)

# asegurar columnas A B C
for col in ["A", "B", "C"]:
    if col not in tabla_desagregada.columns:
        tabla_desagregada[col] = 0

tabla_desagregada = tabla_desagregada[
    ['departamento_titular','provincia_titular','distrito_titular','A','B','C']
]

st.dataframe(tabla_desagregada, use_container_width=True)

# -----------------------------
# DESCARGA
# -----------------------------
csv = tabla_desagregada.to_csv(index=False).encode("utf-8")

st.download_button(
    "⬇ Descargar tabla",
    csv,
    "tabla_verificacion.csv",
    "text/csv",
    key="download-csv"
)
